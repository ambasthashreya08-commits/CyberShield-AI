
from backend.database import get_vulnerabilities
from backend.report_generator import generate_vapt_report

# Retrieve findings from SQLite
vulnerabilities = get_vulnerabilities()

# Generate the PDF
pdf_path = generate_vapt_report(vulnerabilities)

print("VAPT REPORT GENERATED SUCCESSFULLY!")
print("Report location:", pdf_path)
print("Total findings:", len(vulnerabilities))
