import logging

from app.email import send_email


class SendGridMailHandler(logging.Handler):
    """自定义logging handler，利用SendGrid发送log邮件
    """
    def __init__(self, *, recipient, subject):
        # run the regular Handler __init__
        logging.Handler.__init__(self)

        self.recipient = recipient
        self.subject = subject

    def emit(self, record):
        # record.message is the log message
        send_email(self.recipient, self.subject, self.format(record), type_='text/plain')


if __name__ == '__main__':
    from flask import Flask

    # Setup logging handler
    mail_handler = SendGridMailHandler(
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
