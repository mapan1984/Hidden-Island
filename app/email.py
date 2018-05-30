import os
import urllib
import threading

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Mail, Content

from flask import current_app, render_template

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


def send_email(to, subject, template, **kwargs):
    """异步发送邮件

    Args:
        to <string>: 收件者地址
        subject <string>: 邮件主题
        template <string>: 邮件模板路径
        kwargs: 模板填充键值对

    Returns:
        thr: 发送邮件的线程句柄
    """
    app = current_app._get_current_object()
    to_email = Email(to)
    from_email = Email(app.config['MAIL_SENDER'])
    subject = app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject
    content = Content("text/html", render_template(template + '.html', **kwargs))

    mail = Mail(from_email, subject, to_email, content)

    thr = threading.Thread(target=send, args=(mail,))
    thr.start()

    logger.info('sending email from {} to {}...'.format(from_email.email, to_email.email))

    return thr
