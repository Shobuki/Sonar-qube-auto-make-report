#!/usr/bin/env python3
import json
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

INPUT = "sonar_issues.json"
OUTPUT = "sonar_report.html"
OUTPUT_PDF = "sonar_report.pdf"
PROJECT_NAME = "ISI"

def html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )

def main():
    data = json.load(open(INPUT, encoding="utf-8"))
    issues = data.get("issues", [])
    total = len(issues)

    # GROUPING: SoftwareQuality -> ImpactSeverity -> List Issues
    groups = defaultdict(lambda: defaultdict(list))

    for i in issues:
        impacts = i.get("impacts", [])
        if impacts:
            sq = impacts[0].get("softwareQuality", "") or ""
            impsev = impacts[0].get("severity", "") or ""
        else:
            sq = ""
            impsev = ""
        groups[sq][impsev].append(i)

    # SORT KEYS WITHOUT HARDCODE
    sorted_sq = sorted(groups.keys())
    html_sections = []

    # BUILD HTML SECTIONS
    for sq in sorted_sq:
        html_sections.append(f"<h2>Software Quality: {html_escape(sq)}</h2>")

        sorted_impact = sorted(groups[sq].keys())

        for imp in sorted_impact:
            html_sections.append(f"<h3>Impact Severity: {html_escape(imp)}</h3>")

            # full table header (same as original)
            html_sections.append("""
            <table>
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Type</th>
                        <th>Component</th>
                        <th>Line</th>
                        <th>Rule</th>
                        <th class="message">Message</th>
                        <th>Software Quality</th>
                        <th>Impact Severity</th>
                    </tr>
                </thead>
                <tbody>
            """)

            for issue in groups[sq][imp]:
                severity = issue.get("severity", "")
                itype = issue.get("type", "")
                component = issue.get("component", "")
                line = issue.get("line", "")
                rule = issue.get("rule", "")
                message = issue.get("message", "")

                impacts = issue.get("impacts", [])
                if impacts:
                    software_quality = impacts[0].get("softwareQuality", "") or ""
                    impact_sev = impacts[0].get("severity", "") or ""
                else:
                    software_quality = ""
                    impact_sev = ""

                html_sections.append(
                    "<tr>"
                    f"<td>{html_escape(severity)}</td>"
                    f"<td>{html_escape(itype)}</td>"
                    f"<td>{html_escape(component)}</td>"
                    f"<td>{line}</td>"
                    f"<td>{html_escape(rule)}</td>"
                    f"<td class='message'>{html_escape(message)}</td>"
                    f"<td>{html_escape(software_quality)}</td>"
                    f"<td>{html_escape(impact_sev)}</td>"
                    "</tr>"
                )

            html_sections.append("</tbody></table><br>")

    # SUMMARY
    by_severity = Counter(i.get("severity", "UNKNOWN") for i in issues)
    by_type = Counter(i.get("type", "UNKNOWN") for i in issues)

    sev_html = "".join(
        f"<li><strong>{html_escape(k)}</strong>: {v}</li>"
        for k, v in sorted(by_severity.items())
    )
    type_html = "".join(
        f"<li><strong>{html_escape(k)}</strong>: {v}</li>"
        for k, v in sorted(by_type.items())
    )
    sq_counter = defaultdict(int)
    impact_counter = defaultdict(lambda: defaultdict(int))

    for i in issues:
        impacts = i.get("impacts", [])
        if impacts:
            sq = impacts[0].get("softwareQuality", "") or ""
            impsev = impacts[0].get("severity", "") or ""
        else:
            sq = ""
            impsev = ""

        sq_counter[sq] += 1
        impact_counter[sq][impsev] += 1

    sq_html = "".join(
        f"<li><strong>{html_escape(sq)}</strong>: {count}</li>"
        for sq, count in sorted(sq_counter.items())
    )

    impact_html = ""
    for sq in sorted(impact_counter.keys()):
        impact_html += f"<strong>{html_escape(sq)}</strong><ul>"
        for impsev, count in sorted(impact_counter[sq].items()):
            impact_html += f"<li>{html_escape(impsev)}: {count}</li>"
        impact_html += "</ul>"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # FINAL HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SonarQube Issues Report - {html_escape(PROJECT_NAME)}</title>
<style>
  body {{
    font-family: Arial, sans-serif;
    margin: 20px;
    font-size: 12px;
  }}
  h1, h2, h3 {{
    margin-bottom: 0.3em;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    table-layout: fixed;
    word-wrap: break-word;
    margin-bottom: 20px;
  }}
  th, td {{
    border: 1px solid #ccc;
    padding: 4px 6px;
    vertical-align: top;
  }}
  th {{
    background: #f0f0f0;
  }}
  th.message, td.message {{
    width: 30%;
  }}
</style>
</head>
<body>

  <h1>SonarQube Issues Report</h1>
  <div>
    <strong>Project:</strong> {html_escape(PROJECT_NAME)}<br>
    <strong>Total Issues:</strong> {total}<br>
    <strong>Generated:</strong> {html_escape(generated_at)}<br>
  </div>

  <h2>Summary</h2>
  <div style="display:flex; gap:40px;">
  <div><h3>By Severity</h3><ul>{sev_html}</ul></div>
  <div><h3>By Type</h3><ul>{type_html}</ul></div>
  <div><h3>Software Quality</h3><ul>{sq_html}</ul></div>
  <div><h3>Impact Severity (Grouped)</h3>{impact_html}</div>
</div>

  <hr>
  {''.join(html_sections)}
</body>
</html>
"""

    Path(OUTPUT).write_text(html, encoding="utf-8")
    print(f"Generated {OUTPUT}")

    # PDF GENERATION (from HTML)
    try:
        import pdfkit

        config = pdfkit.configuration(
            wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
        )

        pdfkit.from_file(OUTPUT, OUTPUT_PDF, configuration=config)
        print(f"Generated {OUTPUT_PDF}")

    except Exception as e:
        print("Gagal generate PDF otomatis. Pastikan wkhtmltopdf ter-install dan 'pip install pdfkit'.")
        print(e)

if __name__ == "__main__":
    main()
