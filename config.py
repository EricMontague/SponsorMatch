import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base class for application configuration"""

    # stored in a .flaskenv file
    # hard to guess string is used only for development.
    # A real key is generated for production
    SECRET_KEY = os.environ.get("SECRET KEY", "hard to guess string")
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SUBJECT_PREFIX = "[SponsorMatch]"
    MAIL_SENDER = "montaguepython55@gmail.com"
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EVENTS_PER_PAGE = 12
    UPLOADED_IMAGES_DEST = os.environ.get(
        "UPLOADS_URL", os.path.join(basedir, "app/static/images")
    )
    SSL_REDIRECT = False


class DevelopmentConfig(Config):
    """Class to setup the development configuration for the application"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")


class TestingConfig(Config):
    """Class to setup the testing configuration for the application"""

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite://"


class ProductionConfig(Config):
    """Class to setop the production configuration for the application"""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data.sqlite")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrator
        import logging
        from logging.handlers import SMTPHandler

        credentials = None
        secure = None
        if getattr(cls, "MAIL_USERNAME", None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, "MAIL_USE_TLS", None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_SENDER,
            toaddrs=[cls.ADMIN_EMAIL],
            subtject=cls.MAIL_SUBJECT_PREFIX + " Application Error",
            credentials=credentials,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    """Class to setup configurations for heroku."""

    SSL_REDIRECT = True if os.environ.get("DYNO") else False

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler

        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # handle reverse proxy server headers
        from werkzeug.contrib.fixers import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
    "heroku": HerokuConfig
}
