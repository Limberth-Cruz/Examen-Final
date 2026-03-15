from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth.login"

admin_panel = Admin(name="Papelería Prisma")