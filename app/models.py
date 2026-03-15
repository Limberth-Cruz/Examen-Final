from flask_login import UserMixin
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


# =========================
# TABLA USUARIO
# =========================
class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(250), nullable=False)

    name = db.Column(db.String(150), nullable=False)  

    role = db.Column(db.String(50), default="user")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)




# =========================
# TABLA PROVEEDOR
# =========================
class Proveedor(db.Model):

    __tablename__ = "proveedor"

    id_proveedor = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(150), nullable=False)

    telefono = db.Column(db.String(20))

    direccion = db.Column(db.String(200))

    productos = db.relationship("Producto", backref="proveedor")

    def __repr__(self):
        return self.nombre


# =========================
# TABLA CLIENTE
# =========================
class Cliente(db.Model):

    __tablename__ = "cliente"

    id_cliente = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(100))

    telefono = db.Column(db.String(20))


    def __repr__(self):
        return self.nombre
    


# TABLA CATEGORIA
class Categoria(db.Model):

    __tablename__ = "categoria"

    id_categoria = db.Column(db.Integer, primary_key=True)

    nombre_categoria = db.Column(db.String(100), nullable=False)

    productos = db.relationship("Producto", backref="categoria")

    def __repr__(self):
        return self.nombre_categoria


# TABLA PRODUCTO
class Producto(db.Model):

    __tablename__ = "producto"

    id_producto = db.Column(db.Integer, primary_key=True)

    nombre_producto = db.Column(db.String(200), nullable=False)

    id_categoria = db.Column(
        db.Integer,
        db.ForeignKey("categoria.id_categoria")
    )

    id_proveedor = db.Column(
        db.Integer,
        db.ForeignKey("proveedor.id_proveedor")
    )

    precio_compra = db.Column(db.Numeric(10,2))

    precio_venta = db.Column(db.Numeric(10,2))

    stock = db.Column(db.Integer, default=0)

    def __repr__(self):
        return self.nombre_producto




# TABLA VENTA
# =========================
class Venta(db.Model):
    __tablename__ = "venta"

    id_venta = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id_cliente"))
    id = db.Column(db.Integer, db.ForeignKey("user.id"))  # <-- apunta a User.id
    total = db.Column(db.Numeric(10,2))

    detalles = db.relationship("DetalleVenta", backref="venta")

    # Relaciones para acceder a nombre directamente
    cliente = db.relationship("Cliente", backref="ventas")
    user = db.relationship("User", backref="ventas")  # <-- relación con User



# TABLA DETALLE_VENTA
# =========================
class DetalleVenta(db.Model):

    __tablename__ = "detalle_venta"

    id_detalle = db.Column(db.Integer, primary_key=True)

    id_venta = db.Column(
        db.Integer,
        db.ForeignKey("venta.id_venta")
    )

    id_producto = db.Column(
        db.Integer,
        db.ForeignKey("producto.id_producto")
    )

    cantidad = db.Column(db.Integer, nullable=False)

    precio_unitario = db.Column(db.Numeric(10,2))

    subtotal = db.Column(db.Numeric(10,2))

    producto = db.relationship("Producto")

