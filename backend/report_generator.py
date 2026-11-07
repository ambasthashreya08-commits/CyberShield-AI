
from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)


# ==================================================
# PROJECT CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"


# ==================================================
# TEXT FORMATTING
# ==================================================

def safe_text(value):
    """Safely format database text for ReportLab paragraphs."""

    if value is None:
        return "Not provided"

    return escape(str(value)).replace("\n", "<br/>")


def make_paragraph(text, style):
    return Paragraph(safe_text(text), style)


# ==================================================
# PAGE HEADER AND FOOTER
# ==================================================

def add_page_header(canvas, document):

    canvas.saveState()

    width, height = A4

    canvas.setFillColor(colors.HexColor("#14213D"))
    canvas.rect(
        0,
        height - 18 * mm,
        width,
        18 * mm,
        fill=1,
        stroke=0
    )

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.drawString(
        18 * mm,
        height - 11 * mm,
        "CYBERSHIELD AI"
    )

    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.setFont("Helvetica", 8)

    canvas.drawString(
        18 * mm,
        10 * mm,
        "Confidential - Security Assessment Report"
    )

    canvas.drawRightString(
        width - 18 * mm,
        10 * mm,
        f"Page {document.page}"
    )

    canvas.restoreState()


# ==================================================
# PDF REPORT GENERATOR
# ==================================================

def generate_vapt_report(vulnerabilities, output_path=None):

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now()

    if output_path is None:

        filename = (
            "CyberShield_VAPT_Report_"
            + generated_at.strftime("%Y%m%d_%H%M%S")
            + ".pdf"
        )

        output_path = REPORTS_DIR / filename

    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path = Path(output_path)

    # --------------------------------------------------
    # DOCUMENT SETUP
    # --------------------------------------------------

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=25 * mm,
        bottomMargin=20 * mm,
        title="CyberShield AI - VAPT Report",
        author="CyberShield AI"
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#14213D"),
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=8
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=colors.HexColor("#14213D"),
        spaceBefore=14,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=14,
        spaceAfter=6,
        wordWrap="CJK"
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=body_style,
        fontSize=8,
        leading=11
    )

    finding_title_style = ParagraphStyle(
        "FindingTitle",
        parent=heading_style,
        fontSize=11,
        spaceBefore=8
    )

    story = []

    # --------------------------------------------------
    # NORMALIZE FINDINGS
    # --------------------------------------------------

    vulnerabilities = [
        dict(item) for item in vulnerabilities
    ]

    total = len(vulnerabilities)

    severity_counts = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
        "Informational": 0
    }

    status_counts = {}

    risk_scores = []

    for item in vulnerabilities:

        severity = str(
            item.get("severity", "Unknown")
        ).capitalize()

        if severity in severity_counts:
            severity_counts[severity] += 1

        status = item.get(
            "status",
            "Needs Validation"
        )

        status_counts[status] = (
            status_counts.get(status, 0) + 1
        )

        try:
            risk_scores.append(
                float(item.get("risk_score") or 0)
            )
        except (ValueError, TypeError):
            risk_scores.append(0)

    average_risk = (
        round(sum(risk_scores) / total, 2)
        if total else 0
    )

    highest_risk = max(risk_scores) if risk_scores else 0

    # --------------------------------------------------
    # COVER / TITLE SECTION
    # --------------------------------------------------

    story.append(Spacer(1, 35 * mm))

    story.append(
        Paragraph("VULNERABILITY ASSESSMENT", title_style)
    )

    story.append(
        Paragraph("AND PENETRATION TESTING REPORT", title_style)
    )

    story.append(
        Paragraph(
            "Generated by CyberShield AI",
            subtitle_style
        )
    )

    story.append(Spacer(1, 15 * mm))

    cover_data = [
        ["Report Information", "Details"],
        ["Project", "CyberShield AI"],
        ["Report Type", "Web Application Security Assessment"],
        [
            "Generated On",
            generated_at.strftime("%d %B %Y, %I:%M %p")
        ],
        ["Total Findings", str(total)]
    ]

    cover_table = Table(
        cover_data,
        colWidths=[55 * mm, 100 * mm]
    )

    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#14213D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5,
         colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 1), (-1, -1),
         colors.HexColor("#F8FAFC")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("PADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    story.append(cover_table)
    story.append(Spacer(1, 15 * mm))

    story.append(
        Paragraph(
            "This report summarizes security findings collected "
            "and analyzed by CyberShield AI. Findings should be "
            "reviewed by an authorized security professional.",
            body_style
        )
    )

    story.append(PageBreak())

    # --------------------------------------------------
    # EXECUTIVE SUMMARY
    # --------------------------------------------------

    story.append(
        Paragraph("1. Executive Summary", heading_style)
    )

    story.append(
        Paragraph(
            f"The assessment identified <b>{total}</b> "
            "vulnerability findings. The following section "
            "summarizes their severity, validation status, "
            "and risk scores.",
            body_style
        )
    )

    summary_data = [
        ["Metric", "Result"],
        ["Total Findings", str(total)],
        ["Average Risk Score", str(average_risk)],
        ["Highest Risk Score", str(highest_risk)],
        [
            "Confirmed",
            str(status_counts.get("Confirmed", 0))
        ],
        [
            "False Positives",
            str(status_counts.get("False Positive", 0))
        ],
        [
            "Needs Validation",
            str(status_counts.get("Needs Validation", 0))
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[85 * mm, 70 * mm]
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#14213D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5,
         colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 1), (-1, -1),
         colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("FONTSIZE", (0, 0), (-1, -1), 9)
    ]))

    story.append(summary_table)

    # --------------------------------------------------
    # SEVERITY DISTRIBUTION
    # --------------------------------------------------

    story.append(
        Paragraph("2. Severity Distribution", heading_style)
    )

    severity_data = [["Severity", "Number of Findings"]]

    for severity, count in severity_counts.items():
        severity_data.append([severity, str(count)])

    severity_table = Table(
        severity_data,
        colWidths=[85 * mm, 70 * mm]
    )

    severity_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#14213D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5,
         colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("FONTSIZE", (0, 0), (-1, -1), 9)
    ]))

    story.append(severity_table)

    # --------------------------------------------------
    # VALIDATION DISTRIBUTION
    # --------------------------------------------------

    story.append(
        Paragraph("3. Validation Status", heading_style)
    )

    status_data = [["Validation Status", "Number of Findings"]]

    for status, count in status_counts.items():
        status_data.append([status, str(count)])

    status_table = Table(
        status_data,
        colWidths=[85 * mm, 70 * mm]
    )

    status_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#14213D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5,
         colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("FONTSIZE", (0, 0), (-1, -1), 9)
    ]))

    story.append(status_table)

    # --------------------------------------------------
    # INDIVIDUAL FINDINGS
    # --------------------------------------------------

    story.append(
        Paragraph("4. Detailed Vulnerability Findings", heading_style)
    )

    if not vulnerabilities:

        story.append(
            Paragraph(
                "No vulnerability findings are currently available.",
                body_style
            )
        )

    for index, item in enumerate(vulnerabilities, start=1):

        finding_elements = []

        finding_name = item.get("name", "Unknown")

        finding_elements.append(
            Paragraph(
                f"Finding {index}: {safe_text(finding_name)}",
                finding_title_style
            )
        )

        details = [
            ["Field", "Details"],
            ["ID", item.get("id", "Not available")],
            ["Severity", item.get("severity", "Unknown")],
            ["Risk Score", item.get("risk_score", 0)],
            ["Status", item.get("status", "Needs Validation")],
            ["Affected URL", item.get("affected_url", "")],
            ["CWE ID", item.get("cwe_id", "Not mapped")]
        ]

        formatted_details = []

        for row_index, row in enumerate(details):

            if row_index == 0:
                formatted_details.append(row)
            else:
                formatted_details.append([
                    safe_text(row[0]),
                    Paragraph(
                        safe_text(row[1]),
                        small_style
                    )
                ])

        details_table = Table(
            formatted_details,
            colWidths=[38 * mm, 117 * mm]
        )

        details_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#334155")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (0, -1),
             colors.HexColor("#E2E8F0")),
            ("GRID", (0, 0), (-1, -1), 0.4,
             colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("FONTSIZE", (0, 0), (-1, -1), 8)
        ]))

        finding_elements.append(details_table)
        finding_elements.append(Spacer(1, 6))

        text_sections = [
            ("Description", item.get("description")),
            ("Evidence", item.get("evidence")),
            ("Remediation / Solution", item.get("solution")),
            ("AI Analysis", item.get("ai_analysis")),
            ("Analyst Notes", item.get("analyst_notes"))
        ]

        for heading, value in text_sections:

            if value:
                finding_elements.append(
                    Paragraph(
                        f"<b>{escape(heading)}:</b>",
                        small_style
                    )
                )

                finding_elements.append(
                    Paragraph(
                        safe_text(value),
                        body_style
                    )
                )

        story.append(KeepTogether(finding_elements))
        story.append(Spacer(1, 8))

    # --------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------

    story.append(
        Paragraph("5. Report Disclaimer", heading_style)
    )

    story.append(
        Paragraph(
            "Risk scores in this report are generated using the "
            "CyberShield AI custom risk-scoring methodology and "
            "should not be represented as official CVSS scores. "
            "AI-generated analysis is advisory and does not "
            "replace manual security verification. A finding "
            "marked Confirmed or False Positive reflects the "
            "analyst's recorded decision.",
            body_style
        )
    )

    # --------------------------------------------------
    # GENERATE PDF
    # --------------------------------------------------

    document.build(
        story,
        onFirstPage=add_page_header,
        onLaterPages=add_page_header
    )

    return output_path
