import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv()


def send_report_email(pdf_path, subject=None, body=None):
    """
    Sends the generated PDF report as an email attachment via Gmail SMTP.
    Returns True if sent successfully, False otherwise.
    """
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")

    if not all([sender, password, receiver]):
        print("Email credentials missing in .env — skipping email send.")
        return False

    if subject is None:
        subject = "Supply Chain Intelligence Report"

    if body is None:
        body = (
            "Hi,\n\n"
            "Please find attached the latest automated Supply Chain Intelligence Report.\n\n"
            "This report includes current weather conditions, currency exchange rates, "
            "logistics route data, and a calculated supply chain risk score.\n\n"
            "Regards,\n"
            "Automated Supply Chain Pipeline"
        )

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with open(pdf_path, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="pdf")
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(pdf_path)
            )
            msg.attach(attachment)
    except FileNotFoundError:
        print(f"PDF not found at {pdf_path} — cannot send email.")
        return False

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print(f"Email sent successfully to {receiver}.")
        return True

    except smtplib.SMTPAuthenticationError:
        print("Email authentication failed. Check EMAIL_SENDER and EMAIL_PASSWORD (must be a Gmail App Password, not your regular password).")
        return False
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


if __name__ == "__main__":
    from analyzer import generate_risk_report
    from report_generator import generate_pdf_report

    report = generate_risk_report()
    pdf_path = generate_pdf_report(report)
    send_report_email(pdf_path)