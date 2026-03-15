import pymysql
pymysql.install_as_MySQLdb()

from .ventas import ventas_bp

from flask import Flask
from config import Config

from .extensions import db, login_manager, admin_panel
from .auth import auth_bp
from .admin import configuracion_admin

from datetime import date
from .models import Venta, Producto, Cliente


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    login_manager.init_app(app)

    admin_panel.init_app(app)

    app.register_blueprint(auth_bp)

    app.register_blueprint(ventas_bp)

    configuracion_admin()

    # =========================
    # DATOS PARA DASHBOARD
    # =========================
    @app.context_processor
    def dashboard_data():

        ventas_hoy = Venta.query.filter(
            Venta.fecha == date.today()
        ).count()

        total_ventas = Venta.query.count()
        total_productos = Producto.query.count()
        total_clientes = Cliente.query.count()

        return dict(
            ventas_hoy=ventas_hoy,
            total_ventas=total_ventas,
            total_productos=total_productos,
            total_clientes=total_clientes
        )

    return app