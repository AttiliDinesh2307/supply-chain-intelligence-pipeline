from fpdf import FPDF
from datetime import datetime
import os


class SupplyChainReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Supply Chain Intelligence Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        date_str = datetime.now().strftime("%B %d, %Y - %H:%M")
        self.cell(0, 8, date_str, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_pdf_report(report_data, save_path=None):
    """
    Generates a PDF report combining the risk summary and chart images.
    """
    if save_path is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        save_path = f"reports/SCM_Report_{date_str}.pdf"

    pdf = SupplyChainReport()
    pdf.add_page()

    # --- Risk Summary Section ---
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Risk Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 11)
    summary_lines = [
        f"City: {report_data['city']}",
        f"Weather Condition: {report_data['weather_condition']}",
        f"Weather Risk Score: {report_data['weather_risk_score']} / 10",
        f"Base Currency: {report_data['base_currency']}",
        f"INR Rate: {report_data['inr_rate']}",
        f"Forex Risk Score: {report_data['forex_risk_score']} / 10",
        f"Overall Risk Score: {report_data['overall_risk_score']} / 10",
        f"Risk Level: {report_data['risk_level']}"
    ]
    for line in summary_lines:
        pdf.cell(0, 8, line, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)

    # --- Charts Section ---
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Visual Analysis", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    chart_paths = [
        "reports/temperature_trend.png",
        "reports/exchange_rate_trend.png",
        "reports/risk_breakdown.png"
    ]

    for chart_path in chart_paths:
        if os.path.exists(chart_path):
            pdf.image(chart_path, w=170)
            pdf.ln(5)
        else:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 8, f"[Chart not found: {chart_path}]", new_x="LMARGIN", new_y="NEXT")

    pdf.output(save_path)
    print(f"PDF report saved: {save_path}")
    return save_path


if __name__ == "__main__":
    from analyzer import generate_risk_report

    report = generate_risk_report()
    generate_pdf_report(report)