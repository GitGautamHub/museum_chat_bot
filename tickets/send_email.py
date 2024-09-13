import yagmail
import os
from dotenv import load_dotenv

load_dotenv()

def send_email_with_pdf(to_email, subject, body, attachment_path):
    app_password = os.getenv('GMAIL_APP_PASSWORD')

    if not app_password:
        print("Gmail App Password is missing. Please set it in the environment variables.")
        return

    yag = yagmail.SMTP('gautamk8760@gmail.com', app_password)

    try:
        yag.send(
            to=to_email,
            subject=subject,
            contents=body,
            attachments=attachment_path
        )
        print('Email sent successfully!')
    except Exception as e:
        print('Failed to send email:', str(e))
