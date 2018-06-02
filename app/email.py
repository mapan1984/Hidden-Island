import os
import urllib
import threading

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Mail, Content

from flask import current_app

from app import logger


sg = SendGridAPIClient(apikey=os.getenv("SENDGRID_API_KEY"))


def send(email):
    """Send `email` via SendGrid

    Send wraps SendGrid's API client, and makes a POST request to
    the api/v3/mail/send endpoint with `email`.

    Args:
        email <sendgrid.helpers.mail.Mail>: single mail object.
    """
    try:
        response = sg.client.mail.send.post(request_body=email.get())
        if response.status_code < 300:
            logger.info(
                f"Email processed, status code: {response.status_code}"
            )
        else:
            logger.error(
                f"Email processed, status code: {response.status_code}"
            )
    except urllib.error.HTTPError as error:
        logger.error(
            f"Email process failed, Error: {error}"
        )


def send_email(recipient, subject, message, sender=None, async_=True, type_="text/html"):
    """发送邮件

    Args:
        recipient <string>: 收件者地址
        subject <string>: 邮件主题
        message <string>: 邮件内容
        sender <string>: 发件人地址
        async_ <bool>: 是否异步发送
        type_  <string>: 邮件内容类型
    """
    app = current_app._get_current_object()

    sender = Email(sender) if sender else Email(app.config['MAIL_SENDER'])
    recipient = Email(recipient)
    subject = app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject
    content = Content(type_, message)
    mail = Mail(sender, subject, recipient, content)

    logger.info(f'sending email from {sender.email} to {recipient.email}...')
    if async_:
        thr = threading.Thread(target=send, args=(mail,))
        thr.start()
    else:
        send(mail)
