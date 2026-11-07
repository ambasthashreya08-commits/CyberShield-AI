
SEVERITY_WEIGHTS = {
    "Critical": 10,
    "High": 8,
    "Medium": 5,
    "Low": 2,
    "Informational": 0
}

def calculate_risk(
    severity,
    exploitability,
    business_impact,
    confidence
):
    score = (
        SEVERITY_WEIGHTS[severity] * 0.30
        + exploitability * 0.25
        + business_impact * 0.25
        + confidence * 0.20
    ) * 10

    return round(score, 2)
