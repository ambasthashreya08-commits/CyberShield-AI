
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .database import (
    initialize_database,
    save_vulnerability,
    get_vulnerabilities,
    update_vulnerability_status
)

from .risk_engine import calculate_risk
from .scanner import parse_zap_report
from .ai_engine import analyze_vulnerability
from .report_generator import generate_vapt_report


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="CyberShield AI",
    description=(
        "AI-Powered Web Application Vulnerability "
        "Assessment and Prioritization Platform"
    ),
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================
# INPUT MODELS
# ============================================================

class VulnerabilityInput(BaseModel):

    name: str
    severity: str

    description: str = ""
    affected_url: str = ""
    cwe_id: str = ""
    evidence: str = ""

    exploitability: float = Field(default=5, ge=0, le=10)
    business_impact: float = Field(default=5, ge=0, le=10)
    confidence: float = Field(default=5, ge=0, le=10)


class VulnerabilityStatusUpdate(BaseModel):

    status: str
    analyst_notes: str = ""


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Welcome to CyberShield AI",
        "status": "Running",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "application": "CyberShield AI"
    }


# ============================================================
# CREATE VULNERABILITY
# ============================================================

@app.post("/vulnerabilities")
def create_vulnerability(vulnerability: VulnerabilityInput):

    data = vulnerability.model_dump()

    risk_score = calculate_risk(
        data["severity"],
        data["exploitability"],
        data["business_impact"],
        data["confidence"]
    )

    data["risk_score"] = risk_score
    data["status"] = "Needs Validation"

    vulnerability_id = save_vulnerability(data)

    return {
        "success": True,
        "message": "Vulnerability added successfully",
        "id": vulnerability_id,
        "risk_score": risk_score
    }


# ============================================================
# GET ALL VULNERABILITIES
# ============================================================

@app.get("/vulnerabilities")
def list_vulnerabilities():

    vulnerabilities = get_vulnerabilities()

    return {
        "total": len(vulnerabilities),
        "vulnerabilities": vulnerabilities
    }


# ============================================================
# IMPORT OWASP ZAP JSON REPORT
# ============================================================

@app.post("/scan/import")
async def import_zap_report(file: UploadFile = File(...)):

    if (
        not file.filename
        or not file.filename.lower().endswith(".json")
    ):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid JSON report."
        )

    content = await file.read(10 * 1024 * 1024 + 1)

    if len(content) > 10 * 1024 * 1024:

        raise HTTPException(
            status_code=413,
            detail="Report size exceeds the 10 MB limit."
        )

    try:

        report = json.loads(content.decode("utf-8"))

    except (UnicodeDecodeError, json.JSONDecodeError):

        raise HTTPException(
            status_code=400,
            detail="Invalid JSON report."
        )

    try:

        parsed_vulnerabilities = parse_zap_report(report)

        imported_findings = []

        for vulnerability in parsed_vulnerabilities:

            vulnerability_id = save_vulnerability(vulnerability)

            imported_findings.append({
                "id": vulnerability_id,
                "name": vulnerability.get("name", "Unknown"),
                "severity": vulnerability.get("severity", "Unknown"),
                "risk_score": vulnerability.get("risk_score", 0),
                "affected_url": vulnerability.get("affected_url", ""),
                "status": vulnerability.get(
                    "status",
                    "Needs Validation"
                )
            })

        return {
            "success": True,
            "message": "ZAP report imported successfully",
            "total_imported": len(imported_findings),
            "vulnerabilities": imported_findings
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to import ZAP report: {str(e)}"
        )


# ============================================================
# VULNERABILITY ANALYTICS
# ============================================================

@app.get("/analytics")
def get_analytics():

    vulnerabilities = get_vulnerabilities()

    total = len(vulnerabilities)

    severity_distribution = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
        "Informational": 0
    }

    status_distribution = {}

    risk_scores = []

    for vulnerability in vulnerabilities:

        severity = str(
            vulnerability.get("severity", "Unknown")
        ).capitalize()

        if severity in severity_distribution:

            severity_distribution[severity] += 1

        status = vulnerability.get(
            "status",
            "Needs Validation"
        )

        status_distribution[status] = (
            status_distribution.get(status, 0) + 1
        )

        try:

            score = float(
                vulnerability.get("risk_score") or 0
            )

        except (ValueError, TypeError):

            score = 0

        risk_scores.append(score)

    average_risk_score = (
        round(sum(risk_scores) / total, 2)
        if total > 0 else 0
    )

    highest_risk_score = (
        max(risk_scores)
        if risk_scores else 0
    )

    top_5_risk_findings = sorted(
        vulnerabilities,
        key=lambda item: float(
            item.get("risk_score") or 0
        ),
        reverse=True
    )[:5]

    return {
        "total_vulnerabilities": total,
        "severity_distribution": severity_distribution,
        "status_distribution": status_distribution,
        "average_risk_score": average_risk_score,
        "highest_risk_score": highest_risk_score,
        "top_5_risk_findings": top_5_risk_findings
    }


# ============================================================
# AI-POWERED VULNERABILITY ANALYSIS
# ============================================================

@app.post("/vulnerabilities/{vulnerability_id}/analyze")
async def analyze_vulnerability_endpoint(
    vulnerability_id: int
):

    vulnerabilities = get_vulnerabilities()

    vulnerability = next(
        (
            item for item in vulnerabilities
            if int(item["id"]) == vulnerability_id
        ),
        None
    )

    if vulnerability is None:

        raise HTTPException(
            status_code=404,
            detail="Vulnerability not found."
        )

    try:

        ai_result = await analyze_vulnerability(vulnerability)

        return {
            "success": True,
            "vulnerability_id": vulnerability_id,
            "ai_analysis": ai_result
        }

    except Exception as e:

        raise HTTPException(
            status_code=502,
            detail=f"AI analysis failed: {str(e)}"
        )


# ============================================================
# MANUAL VULNERABILITY VALIDATION
# ============================================================

@app.patch("/vulnerabilities/{vulnerability_id}/status")
def update_vulnerability_validation(
    vulnerability_id: int,
    update: VulnerabilityStatusUpdate
):

    allowed_statuses = [
        "Needs Validation",
        "Confirmed",
        "False Positive"
    ]

    if update.status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid vulnerability status.",
                "allowed_statuses": allowed_statuses
            }
        )

    try:

        updated = update_vulnerability_status(
            vulnerability_id=vulnerability_id,
            status=update.status,
            analyst_notes=update.analyst_notes
        )

        if not updated:

            raise HTTPException(
                status_code=404,
                detail="Vulnerability not found."
            )

        return {
            "success": True,
            "message": "Vulnerability validation updated successfully.",
            "vulnerability_id": vulnerability_id,
            "status": update.status,
            "analyst_notes": update.analyst_notes
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Validation update failed: {str(e)}"
        )


# ============================================================
# PDF VAPT REPORT GENERATION AND DOWNLOAD
# ============================================================

@app.get("/reports/pdf")
def download_vapt_report():

    try:

        vulnerabilities = get_vulnerabilities()

        pdf_path = generate_vapt_report(vulnerabilities)

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=pdf_path.name
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"PDF report generation failed: {str(e)}"
        )
