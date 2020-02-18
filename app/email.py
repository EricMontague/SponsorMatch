"""This module contains functions for sending emails

Functions:

Dependencies:
    Thread:
    current_app
    render_template
    Message
    mail: Flask-Mail extension

"""
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
    """Send an email to a recipient
	
	Args:
	    to (str): The email address of the recipient
	    subject (str): The subject of the email
	    template (str): The path of the email template to
	        use as the body of the email
	    **kwargs (optional): Allows for additional keyword-value
	        pairs to be used in the email template(s)
	
	Returns:
	    thread object
	"""
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
