"""AI analysis API endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
)
from app.services.wazuh_client import wazuh_client
from app.services.ai import AIServiceFactory
from app.utils.exceptions import WazuhAPIError, AIServiceError, CheckNotFoundError
from app.utils.logger import logger

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("", response_model=AnalysisResponse)
async def analyze_check(request: AnalysisRequest):
    """
    Analyze a single SCA check using AI.

    Args:
        request: Analysis request parameters

    Returns:
        AI-generated analysis report
    """
    try:
        # Get check details from Wazuh
        check = await wazuh_client.get_check_details(
            request.agent_id, request.policy_id, request.check_id
        )

        # Create AI service
        ai_service = AIServiceFactory.create(request.ai_provider)

        # Log which AI provider is being used
        logger.info(
            f"Analyzing check {request.check_id} using {request.ai_provider.upper()} "
            f"(language: {request.language})"
        )

        # Analyze check
        report = await ai_service.analyze_check(check, language=request.language)

        logger.info(f"Analysis completed using {request.ai_provider.upper()}")

        return AnalysisResponse(
            check_id=request.check_id,
            report=report,
            ai_provider=request.ai_provider,
            language=request.language,
        )

    except CheckNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (WazuhAPIError, AIServiceError) as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def analyze_check_stream(request: AnalysisRequest):
    """
    Analyze a check with streaming response.

    Args:
        request: Analysis request parameters

    Returns:
        Server-sent events stream of analysis
    """
    try:
        # Get check details
        check = await wazuh_client.get_check_details(
            request.agent_id, request.policy_id, request.check_id
        )

        # Create AI service
        ai_service = AIServiceFactory.create(request.ai_provider)

        # Stream analysis
        async def generate():
            async for chunk in ai_service.analyze_check_stream(
                check, language=request.language
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except CheckNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (WazuhAPIError, AIServiceError) as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchAnalysisResponse)
async def analyze_batch(request: BatchAnalysisRequest):
    """
    Analyze multiple SCA checks.

    Args:
        request: Batch analysis request

    Returns:
        Results for all checks
    """
    results = []
    successful = 0
    failed = 0

    # Create AI service once
    try:
        ai_service = AIServiceFactory.create(request.ai_provider)
    except AIServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Analyze each check
    for check_id in request.check_ids:
        try:
            check = await wazuh_client.get_check_details(
                request.agent_id, request.policy_id, check_id
            )
            report = await ai_service.analyze_check(check, language=request.language)

            results.append(
                AnalysisResponse(
                    check_id=check_id,
                    report=report,
                    ai_provider=request.ai_provider,
                    language=request.language,
                )
            )
            successful += 1

        except Exception as e:
            logger.error(f"Failed to analyze check {check_id}: {e}")
            results.append(
                AnalysisResponse(
                    check_id=check_id,
                    report=f"Error: {str(e)}",
                    ai_provider=request.ai_provider,
                    language=request.language,
                )
            )
            failed += 1

    return BatchAnalysisResponse(
        results=results, total=len(request.check_ids), successful=successful, failed=failed
    )


@router.get("/providers")
async def get_ai_providers():
    """
    Get list of available AI providers.

    Returns:
        List of available AI provider names
    """
    return {"providers": AIServiceFactory.get_available_providers()}


@router.get("/status")
async def get_ai_status():
    """
    Get status of AI providers based on AI_MODE configuration.

    Returns:
        Status of each AI provider
    """
    from app.config import settings
    import httpx

    status = {
        "ai_mode": settings.ai_mode,
        "vllm": {
            "available": False,
            "enabled": settings.ai_mode in ["local", "mixed"],
            "url": settings.vllm_api_url,
            "model": settings.vllm_model,
            "type": "Local LLM",
        },
        "openai": {
            "available": bool(settings.openai_api_key),
            "enabled": settings.ai_mode in ["external", "mixed"],
            "model": settings.openai_model if settings.openai_api_key else None,
            "type": "Cloud API",
        },
    }

    # Test vLLM connection only if enabled
    if settings.ai_mode in ["local", "mixed"]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.vllm_api_url}/models")
                if response.status_code == 200:
                    status["vllm"]["available"] = True
                    status["vllm"]["models"] = response.json().get("data", [])
        except Exception as e:
            status["vllm"]["error"] = str(e)

    return status
