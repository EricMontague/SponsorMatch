"""This module contains extensions for the application."""


from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, patch_request_class
from flask_migrate import Migrate


bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
images = UploadSet("images", extensions=["jpg", "jpeg", "png"])
migrate = Migrate()
