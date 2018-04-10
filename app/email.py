from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from app import mail


def send_async_email(app_, msg):
    with app_.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app_ = current_app._get_current_object()  # 获取current_app
    msg = Message(app_.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app_.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app_, msg])
    thr.start()
    return thr
