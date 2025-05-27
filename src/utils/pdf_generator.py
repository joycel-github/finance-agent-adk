from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import os


def generate_pdf_report(report_data: dict, output_filename: str):
    """
    Generate a PDF report from the given report data (dict) and save it under the agents/sample_reports folder.

    Args:
        report_data (dict): Dictionary with keys for each report section.
            Expected keys (in order):
                - executive_summary
                - company_overview
                - industry_analysis
                - fundamental_analysis
                - technical_analysis
                - sentiment_analysis
                - risk_analysis
                - investment_recommendations
                - risk_factors
                - conclusion
        output_filename (str): The name of the output PDF file.
    """
    output_dir = os.path.join("..", "agents_sample_reports")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=30
    )
    section_title_style = styles['Heading2']
    body_style = styles["Normal"]

    # Define the order and display names of sections
    sections = [
        ("executive_summary", "Executive Summary"),
        ("company_overview", "Company Overview"),
        ("industry_analysis", "Industry Analysis"),
        ("fundamental_analysis", "Fundamental Analysis"),
        ("technical_analysis", "Technical Analysis"),
        ("sentiment_analysis", "Sentiment Analysis"),
        ("risk_analysis", "Risk Analysis"),
        ("investment_recommendations", "Investment Recommendations"),
        ("risk_factors", "Risk Factors"),
        ("conclusion", "Conclusion")
    ]

    story = []
    # Add a main title
    story.append(Paragraph("Investment Research Report", title_style))
    story.append(Spacer(1, 24))

    for key, display_name in sections:
        content = report_data.get(key, "")
        if content:
            story.append(Paragraph(display_name, section_title_style))
            story.append(Spacer(1, 8))
            story.append(Paragraph(content, body_style))
            story.append(Spacer(1, 16))

    # Build the PDF
    doc.build(story)
    print(f"PDF report generated: {output_path}")


if __name__ == "__main__":
    # Example usage
    sample_report_data = {
        "executive_summary": "This is a sample executive summary.",
        "company_overview": "Overview of the company.",
        "industry_analysis": "Industry trends and analysis.",
        "fundamental_analysis": "Fundamental analysis details.",
        "technical_analysis": "Technical analysis details.",
        "sentiment_analysis": "Sentiment analysis details.",
        "risk_analysis": "Risk analysis details.",
        "investment_recommendations": "Buy, Sell, or Hold recommendations.",
        "risk_factors": "Potential risks involved.",
        "conclusion": "Final conclusion of the report."
    }
    generate_pdf_report(sample_report_data, "sample_report.pdf") 