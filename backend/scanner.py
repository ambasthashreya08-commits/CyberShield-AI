
import re
import json
from pathlib import Path
from html import unescape

from .risk_engine import calculate_risk


def clean_html(value):
    """Remove HTML tags from ZAP descriptions."""
    if not value:
        return ""

    value = re.sub(r"<[^>]+>", " ", str(value))
    value = unescape(value)
    return " ".join(value.split())


def normalize_severity(risk_description):
    """Convert ZAP risk descriptions into standard severity labels."""
    risk = str(risk_description or "").strip().lower()

    if risk.startswith("critical"):
        return "Critical"
    elif risk.startswith("high"):
        return "High"
    elif risk.startswith("medium"):
        return "Medium"
    elif risk.startswith("low"):
        return "Low"

    return "Informational"


def normalize_confidence(confidence):
    """Convert ZAP confidence values into a 0-10 score."""
    confidence = str(confidence or "").strip().lower()

    confidence_map = {
        "0": 1,
        "false positive": 1,
        "1": 4,
        "low": 4,
        "2": 7,
        "medium": 7,
        "3": 9,
        "high": 9,
        "4": 10,
        "user confirmed": 10
    }

    return confidence_map.get(confidence, 5)


def get_exploitability(severity):
    """Initial heuristic, not an official CVSS metric."""
    values = {
        "Critical": 10,
        "High": 8,
        "Medium": 6,
        "Low": 3,
        "Informational": 1
    }

    return values.get(severity, 1)


def get_business_impact(severity):
    """Initial heuristic for project-level prioritization."""
    values = {
        "Critical": 10,
        "High": 9,
        "Medium": 6,
        "Low": 3,
        "Informational": 1
    }

    return values.get(severity, 1)


def normalize_cwe(cwe_value):
    """Safely format a CWE identifier."""
    try:
        cwe_number = int(cwe_value)
        if cwe_number > 0:
            return f"CWE-{cwe_number}"
    except (ValueError, TypeError):
        pass

    return "Not mapped"


def parse_zap_report(report):
    """Extract vulnerability findings from a ZAP JSON report."""

    if isinstance(report, str):
        report = json.loads(report)

    if not isinstance(report, dict):
        raise ValueError("The report must contain a JSON object.")

    sites = report.get("site", [])

    if not isinstance(sites, list):
        raise ValueError("Invalid ZAP report: 'site' must be a list.")

    vulnerabilities = []

    for site in sites:
        if not isinstance(site, dict):
            continue

        site_url = site.get("name", "")
        alerts = site.get("alerts", [])

        for alert in alerts:
            if not isinstance(alert, dict):
                continue

            severity = normalize_severity(
                alert.get("riskdesc", "Informational")
            )

            confidence = normalize_confidence(
                alert.get("confidence", "")
            )

            exploitability = get_exploitability(severity)
            business_impact = get_business_impact(severity)

            risk_score = calculate_risk(
                severity,
                exploitability,
                business_impact,
                confidence
            )

            instances = alert.get("instances", [])

            if not isinstance(instances, list) or not instances:
                instances = [{}]

            for instance in instances:
                if not isinstance(instance, dict):
                    continue

                cwe_id = normalize_cwe(alert.get("cweid"))

                finding = {
                    "name": alert.get(
                        "alert",
                        alert.get("name", "Unknown vulnerability")
                    ),
                    "severity": severity,
                    "description": clean_html(alert.get("desc", "")),
                    "affected_url": instance.get("uri", site_url),
                    "cwe_id": cwe_id,
                    "evidence": instance.get(
                        "evidence",
                        "No evidence provided"
                    ),
                    "risk_score": risk_score,
                    "status": "Needs Validation",
                    "solution": clean_html(alert.get("solution", ""))
                }

                vulnerabilities.append(finding)

    return vulnerabilities


def import_zap_report(file_path):
    """Read a ZAP JSON report and parse its findings."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Report not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    return parse_zap_report(report)
