"""PDF report generation endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.schemas import PDFRequest, PDFResponse
from app.services.pdf_service import pdf_service
from app.utils.exceptions import PDFGenerationError

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/pdf", response_model=PDFResponse)
async def generate_pdf(request: PDFRequest):
    """
    Generate PDF report from analysis text.

    Args:
        request: PDF generation request

    Returns:
        PDF file information
    """
    try:
        filepath = pdf_service.generate_report(
            agent_name=request.agent_name,
            check_id=request.check_id,
            report_text=request.report_text,
            language=request.language,
        )

        return PDFResponse(
            filename=filepath.name,
            download_url=f"/api/reports/download/{filepath.name}",
        )

    except PDFGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    """
    Download a generated PDF report.

    Args:
        filename: PDF filename

    Returns:
        PDF file
    """
    filepath = pdf_service.output_dir / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=filename,
    )
