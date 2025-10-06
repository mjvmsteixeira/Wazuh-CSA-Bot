"""PDF generation service."""

from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from app.utils.logger import logger
from app.utils.exceptions import PDFGenerationError


class PDFService:
    """Service for generating PDF reports."""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_report(
        self,
        agent_name: str,
        check_id: int,
        report_text: str,
        language: str = "en",
    ) -> Path:
        """
        Generate PDF report.

        Args:
            agent_name: Name of the Wazuh agent
            check_id: SCA check ID
            report_text: Analysis report text
            language: Report language

        Returns:
            Path to generated PDF file
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"SCA_Report_{agent_name}_Check_{check_id}_{timestamp}.pdf"
            filepath = self.output_dir / filename

            # Create PDF
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            story = []

            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor="#1a5490",
                spaceAfter=30,
                alignment=TA_CENTER,
            )
            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=14,
                textColor="#2c5282",
                spaceAfter=12,
            )
            body_style = ParagraphStyle(
                "CustomBody",
                parent=styles["BodyText"],
                fontSize=11,
                alignment=TA_LEFT,
                spaceAfter=12,
            )

            # Title
            title_text = (
                f"Relatório de Análise SCA"
                if language == "pt"
                else "SCA Analysis Report"
            )
            story.append(Paragraph(title_text, title_style))
            story.append(Spacer(1, 0.3 * inch))

            # Metadata
            meta_info = f"""
            <b>Agent:</b> {agent_name}<br/>
            <b>Check ID:</b> {check_id}<br/>
            <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
            """
            story.append(Paragraph(meta_info, body_style))
            story.append(Spacer(1, 0.5 * inch))

            # Report content
            # Split by lines and format
            for line in report_text.split("\n"):
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 0.1 * inch))
                    continue

                # Check if it's a heading (starts with ###, ##, or #)
                if line.startswith("###"):
                    story.append(Paragraph(line[3:].strip(), heading_style))
                elif line.startswith("##"):
                    story.append(Paragraph(line[2:].strip(), heading_style))
                elif line.startswith("#"):
                    story.append(Paragraph(line[1:].strip(), heading_style))
                elif line.startswith("**") and line.endswith("**"):
                    # Bold text
                    story.append(
                        Paragraph(f"<b>{line[2:-2]}</b>", body_style)
                    )
                elif line.startswith("-") or line.startswith("•"):
                    # Bullet point
                    story.append(
                        Paragraph(f"• {line[1:].strip()}", body_style)
                    )
                elif line.startswith(tuple(str(i) for i in range(10))):
                    # Numbered list
                    story.append(Paragraph(line, body_style))
                else:
                    # Regular text
                    story.append(Paragraph(line, body_style))

            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}")


# Singleton instance
pdf_service = PDFService()
