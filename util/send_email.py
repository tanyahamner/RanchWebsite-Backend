from sendgrid import SendGridAPIClient
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

API_KEY = os.environ.get('SENDGRID_API_KEY', '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')
FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'autumn.e.gehring@gmail.com')

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
