"""AI analysis API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime

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
from app.db.session import get_db
from app.repositories.analysis_repository import AnalysisRepository
from app.config import settings

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("", response_model=AnalysisResponse)
async def analyze_check(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyze a single SCA check using AI with intelligent caching.

    This endpoint:
    1. Checks for cached analysis (if enabled)
    2. Returns cached result if valid
    3. Performs new analysis if no cache or cache expired
    4. Saves new analysis to history

    Args:
        request: Analysis request parameters
        db: Database session

    Returns:
        AI-generated analysis report (cached or fresh)
    """
    start_time = datetime.utcnow()
    repo = AnalysisRepository(db)

    try:
        # Get check details from Wazuh
        check = await wazuh_client.get_check_details(
            request.agent_id, request.policy_id, request.check_id
        )

        # Get agent information for context
        agents = await wazuh_client.get_agents()
        agent_info = next((a for a in agents if a["id"] == request.agent_id), None)
        agent_name = agent_info.get("name") if agent_info else request.agent_id

        # Try to get cached analysis first
        # Strategy: 1) Try agent-specific cache, 2) Try shared cache by title
        cached = None
        cache_type = None

        if settings.enable_analysis_cache:
            # 1. Try agent-specific cache first (exact match)
            cached = repo.find_cached_analysis(
                agent_id=request.agent_id,
                check_id=request.check_id,
                language=request.language,
            )

            if cached:
                cache_type = "agent-specific"
            else:
                # 2. Try shared cache by check_id (reuse from other agents)
                cached = repo.find_cached_analysis_by_check_id(
                    check_id=request.check_id,
                    language=request.language,
                    exclude_agent_id=request.agent_id,  # Exclude current agent
                )
                if cached:
                    cache_type = "shared"

            if cached:
                logger.info(
                    f"✅ Returning CACHED analysis ({cache_type}): "
                    f"check={request.check_id}, "
                    f"age={(datetime.utcnow() - cached.analysis_date).total_seconds() / 3600:.1f}h"
                    + (f", original_agent={cached.agent_name}" if cache_type == "shared" else "")
                )

                # Reconstruct script data if available
                cached_script = None
                if cached.remediation_script:
                    import json
                    metadata = {}
                    if cached.script_metadata:
                        try:
                            metadata = json.loads(cached.script_metadata)
                        except (json.JSONDecodeError, TypeError):
                            pass

                    cached_script = {
                        "script_content": cached.remediation_script,
                        "script_language": cached.script_language,
                        "validation_command": cached.validation_command,
                        **metadata
                    }

                # IMPORTANT: If using shared cache, save a new entry for THIS agent
                # This allows the analysis to appear in this agent's history
                if cache_type == "shared":
                    execution_time = (datetime.utcnow() - start_time).total_seconds()
                    repo.save_analysis(
                        agent_id=request.agent_id,
                        agent_name=agent_name,
                        policy_id=request.policy_id,
                        check_id=request.check_id,
                        check_title=check.get("title", "Unknown"),
                        check_description=check.get("description"),
                        language=request.language,
                        ai_provider=cached.ai_provider,
                        report_text=cached.report_text,
                        status="completed",
                        execution_time=execution_time,
                        remediation_script=cached_script,
                    )
                    logger.info(
                        f"📝 Saved shared cache analysis to current agent's history: {agent_name}"
                    )

                return AnalysisResponse(
                    check_id=request.check_id,
                    report=cached.report_text,
                    remediation_script=cached_script,
                    ai_provider=cached.ai_provider,
                    language=request.language,
                    cached_from_agent=cached.agent_name if cache_type == "shared" else None,
                )

        # No cache - perform new analysis
        logger.info(
            f"🔍 NEW analysis: check={request.check_id}, agent={agent_name}, "
            f"provider={request.ai_provider.upper()}, language={request.language}"
        )

        # Create AI service and analyze
        ai_service = AIServiceFactory.create(request.ai_provider)
        analysis_result = await ai_service.analyze_check(
            check,
            language=request.language,
            agent_info=agent_info
        )

        # Extract report and script from result
        report = analysis_result["report"]
        script_data = analysis_result.get("remediation_script")

        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        # Save to history (including script if generated)
        repo.save_analysis(
            agent_id=request.agent_id,
            agent_name=agent_name,
            policy_id=request.policy_id,
            check_id=request.check_id,
            check_title=check.get("title", "Unknown"),
            check_description=check.get("description"),
            language=request.language,
            ai_provider=request.ai_provider,
            report_text=report,
            status="completed",
            execution_time=execution_time,
            remediation_script=script_data,
        )

        logger.info(
            f"✅ Analysis completed in {execution_time:.2f}s and saved to history"
            + (f" with script ({script_data['script_language']})" if script_data else "")
        )

        return AnalysisResponse(
            check_id=request.check_id,
            report=report,
            remediation_script=script_data,
            ai_provider=request.ai_provider,
            language=request.language,
            cached_from_agent=None,
        )

    except CheckNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (WazuhAPIError, AIServiceError) as e:
        # Save failed analysis to history
        if agent_info:
            try:
                repo.save_analysis(
                    agent_id=request.agent_id,
                    agent_name=agent_info.get("name", request.agent_id),
                    policy_id=request.policy_id,
                    check_id=request.check_id,
                    check_title=check.get("title", "Unknown") if 'check' in locals() else "Unknown",
                    language=request.language,
                    ai_provider=request.ai_provider,
                    report_text="",
                    status="failed",
                    error_message=str(e),
                )
            except Exception as save_error:
                logger.error(f"Failed to save error to history: {save_error}")

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

        # Get agent information for context
        agents = await wazuh_client.get_agents()
        agent_info = next((a for a in agents if a["id"] == request.agent_id), None)

        # Create AI service
        ai_service = AIServiceFactory.create(request.ai_provider)

        # Stream analysis
        async def generate():
            async for chunk in ai_service.analyze_check_stream(
                check,
                language=request.language,
                agent_info=agent_info
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

    # Get agent information once for context
    try:
        agents = await wazuh_client.get_agents()
        agent_info = next((a for a in agents if a["id"] == request.agent_id), None)
    except Exception as e:
        logger.warning(f"Failed to get agent info: {e}. Continuing without agent context.")
        agent_info = None

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
            analysis_result = await ai_service.analyze_check(
                check,
                language=request.language,
                agent_info=agent_info
            )

            # Extract report and script from result
            report = analysis_result["report"]
            script_data = analysis_result.get("remediation_script")

            results.append(
                AnalysisResponse(
                    check_id=check_id,
                    report=report,
                    remediation_script=script_data,
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
                    remediation_script=None,
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


@router.get("/system-status")
async def get_system_status():
    """
    Get comprehensive system status including Wazuh API and AI providers.

    Returns:
        Complete system status
    """
    from app.config import settings
    import httpx

    status = {
        "wazuh": {
            "available": False,
            "url": settings.wazuh_api_url,
            "error": None,
        },
        "ai_mode": settings.ai_mode,
        "vllm": {
            "available": False,
            "enabled": settings.ai_mode in ["local", "mixed"],
            "url": settings.vllm_api_url,
            "model": settings.vllm_model,
            "type": "Local LLM",
            "error": None,
        },
        "openai": {
            "available": bool(settings.openai_api_key),
            "enabled": settings.ai_mode in ["external", "mixed"],
            "model": settings.openai_model if settings.openai_api_key else None,
            "type": "Cloud API",
            "error": None,
        },
    }

    # Test Wazuh API connection
    try:
        token = await wazuh_client._get_token()
        if token:
            status["wazuh"]["available"] = True
    except Exception as e:
        status["wazuh"]["error"] = str(e)
        logger.error(f"Wazuh API health check failed: {e}")

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

    # Test OpenAI API if configured
    if settings.ai_mode in ["external", "mixed"] and settings.openai_api_key:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            # Simple test to verify API key
            models = await client.models.list()
            if models:
                status["openai"]["available"] = True
        except Exception as e:
            status["openai"]["error"] = str(e)
            status["openai"]["available"] = False

    return status
