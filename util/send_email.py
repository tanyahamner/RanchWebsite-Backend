from sendgrid import SendGridAPIClient
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

API_KEY = os.environ.get('SENDGRID_API_KEY', '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')
FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'foundation@devpipeline.com')

def send_email(to_email, subject, content):

    sg = SendGridAPIClient(api_key=API_KEY)
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=content
    )

    response = sg.send(message)
    print(response.status_code)
    print(response.headers)
