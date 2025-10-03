"""
Simple mailer utilities: SMTP for email and Twilio for WhatsApp/SMS (optional).
Configure via environment variables for credentials. Designed to be optional and fail gracefully.
"""
import os
import smtplib
from email.message import EmailMessage
from typing import List

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except Exception:
    TWILIO_AVAILABLE = False


def send_email(smtp_server: str, smtp_port: int, username: str, password: str,
               subject: str, body: str, to_addresses: List[str], attachments: List[str] = None,
               use_tls: bool = True) -> dict:
    """Send an email with optional attachments. Returns a dict with status and message."""
    attachments = attachments or []
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = ', '.join(to_addresses)
        msg.set_content(body)

        for path in attachments:
            if not os.path.exists(path):
                continue
            with open(path, 'rb') as f:
                data = f.read()
            maintype = 'application'
            subtype = 'octet-stream'
            filename = os.path.basename(path)
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)

        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)

        server.login(username, password)
        server.send_message(msg)
        server.quit()

        return {'status': 'success', 'message': f'Email sent to {to_addresses}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def send_whatsapp_via_twilio(account_sid: str, auth_token: str, from_whatsapp: str, to_whatsapp: str, message: str, media_url: str = None) -> dict:
    """Send a WhatsApp message using Twilio. media_url is optional for attachments."""
    if not TWILIO_AVAILABLE:
        return {'status': 'error', 'message': 'Twilio library not installed'}

    try:
        client = Client(account_sid, auth_token)
        data = {
            'from_': f'whatsapp:{from_whatsapp}',
            'to': f'whatsapp:{to_whatsapp}',
            'body': message
        }
        if media_url:
            data['media_url'] = [media_url]

        msg = client.messages.create(**data)
        return {'status': 'success', 'sid': msg.sid}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
