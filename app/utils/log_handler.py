import os
import logging
import urllib

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Mail, Content


class SendGridMailHandler(logging.Handler):
    """自定义logging handler，利用SendGrid发送log邮件
    """
    def __init__(self, *, api_key, sender, recipient, subject):
        # run the regular Handler __init__
        logging.Handler.__init__(self)

        self.sg = SendGridAPIClient(apikey=api_key)

        self.sender = Email(sender)
        self.recipient = Email(recipient)
        self.subject = subject

    def emit(self, record):
        # record.message is the log message
        print(record.message)

        content = Content('text/plain', self.format(record))

        print(content)

        mail = Mail(self.sender, self.subject, self.recipient, content)

        print(mail)

        try:
            response = self.sg.client.mail.send.post(request_body=mail.get())
            if response.status_code < 300:
                print("Email processed", response.body, response.status_code)
        except urllib.error.HTTPError as e:
            e.read()


if __name__ == '__main__':
    from flask import Flask

    # Setup logging handler
    mail_handler = SendGridMailHandler(
        api_key=os.getenv("SENDGRID_API_KEY"),
        sender='mapan1024@gmail.com',
        recipient='mapan1984@outlook.com',
        subject='Application error!'
    )
    mail_handler.setFormatter(logging.Formatter('''
        Message type:       %(levelname)s
        Location:           %(pathname)s:%(lineno)d
        Module:             %(module)s
        Function:           %(funcName)s
        Time:               %(asctime)s

        Message:

        %(message)s
    '''))
    mail_handler.setLevel(logging.ERROR)
    app = Flask(__name__)
    app.logger.addHandler(mail_handler)

    @app.route('/error')
    def error():
        raise Exception("Beds are burning!")

    # app.run(debug=True) # Handler isn't executed if app is run in debug mode
    app.run()