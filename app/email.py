from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app, msg):
    """Helper function to send asynchronous email"""
    # applcation context needs to be manually pushed since it is
    # thread local
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """Send an email to a recipient"""
    app = current_app._get_current_object()
    # subject, sender and recipients
    msg = Message(
        app.config["MAIL_SUBJECT_PREFIX"] + " " + subject,
        sender=app.config["MAIL_SENDER"],
        recipients=[to],
    )
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return thread
