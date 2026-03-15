from flask_login import current_user
from flask import redirect, url_for, request, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose

from .extensions import admin_panel, db
from .models import User, Producto, Categoria, Proveedor, Cliente, Venta, DetalleVenta
from .ai_chat import client

# =========================
# CRUD protegido para admin
# =========================
class SecurityModelView(ModelView):
    column_exclude_list = ["password","ventas"]


    
    # Opcional: también puedes definir campos que se puedan editar
    form_excluded_columns = ["ventas"]  # evita que aparezca en Create/Edit
    def is_accessible(self):
        return current_user.is_authenticated



    def inaccessible_callback(self, name, **kwargs):
        flash("No tienes permisos para acceder a esta sección", "warning")
        return redirect(url_for("auth.login"))
    


# por defecto rol aqui
class RoleModelView(ModelView):

    allowed_roles = ["admin", "vendedor", "cajero"]  

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role in self.allowed_roles
    


class ClienteAdmin(RoleModelView):

    column_exclude_list = ["ventas"]
    form_excluded_columns = ["ventas"]




# =========================
# Vista personalizada para vender
# =========================
class VenderView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        productos = Producto.query.all()
        clientes = Cliente.query.all()
        usuarios = User.query.all()  

        if request.method == 'POST':
            # Productos seleccionados
            carrito_ids = request.form.getlist('producto')
            id_cliente = request.form.get('cliente')
            id = request.form.get('user')  

            # Tomar cantidades según los productos seleccionados
            cantidades = []
            for pid in carrito_ids:
                cantidad = int(request.form.get(f'cantidad_{pid}', 0))
                cantidades.append(cantidad)

            # Validar que haya al menos un producto con cantidad > 0
            if not carrito_ids or not any(c > 0 for c in cantidades):
                flash('Seleccione productos y cantidades', 'danger')
                return redirect(url_for('.index'))

            # Crear la venta
            venta = Venta(
                fecha=db.func.current_date(),
                id_cliente=id_cliente,
                id=current_user.id,  # <-- usuario logueado
                total=0
            )
            db.session.add(venta)
            db.session.flush()  # para obtener id_venta

            total = 0
            for pid, cantidad in zip(carrito_ids, cantidades):
                if cantidad <= 0:
                    continue

                producto = Producto.query.get(pid)
                if not producto or producto.stock < cantidad:
                    continue

                subtotal = producto.precio_venta * cantidad

                detalle = DetalleVenta(
                    id_venta=venta.id_venta,
                    id_producto=producto.id_producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta,
                    subtotal=subtotal
                )
                db.session.add(detalle)

                # Actualizar stock
                producto.stock -= cantidad
                total += subtotal

            venta.total = total
            db.session.commit()

            # Redirigir al ticket con la venta recién creada
            return self.render('ticket.html', venta=venta, detalles=venta.detalles)

        # GET: mostrar formulario
        return self.render(
            'venta.html',
            productos=productos,
            clientes=clientes,
            usuarios=usuarios  # <-- pasar usuarios
        )


class VentasRealizadasView(BaseView):
    @expose('/')
    def index(self):
        # Traer todas las ventas
        ventas = Venta.query.order_by(Venta.fecha.desc()).all()

        return self.render('admin/ventas_realizadas.html', ventas=ventas)
    
class ChatbotView(BaseView):

    @expose('/')
    def index(self):
        return self.render('admin/chatbot.html')


class AnalisisIAView(BaseView):

    @expose('/')
    def index(self):

        productos = Producto.query.all()
        clientes = Cliente.query.all()
        ventas = Venta.query.all()
        categorias = Categoria.query.all()

        # =========================
        # LISTAS
        # =========================
        lista_productos = ""
        for p in productos:
            lista_productos += f"{p.nombre_producto} stock:{p.stock} precio:{p.precio_venta}\n"

        lista_clientes = ""
        for c in clientes:
            lista_clientes += f"{c.nombre}\n"

        lista_categorias = ""
        for c in categorias:
            lista_categorias += f"{c.nombre_categoria}\n"

        lista_ventas = ""
        for v in ventas:
            lista_ventas += f"venta {v.id_venta} total:{v.total}\n"

        # =========================
        # PROMPT IA
        # =========================
        prompt = f"""
Eres un analista de datos.

PRODUCTOS:
{lista_productos}

CLIENTES:
{lista_clientes}

CATEGORÍAS:
{lista_categorias}

VENTAS:
{lista_ventas}



Genera un reporte corto con:
1. Total de productos
2. Productos con poco stock
3. Observaciones de ventas
4. Recomendaciones
5. Conclusión
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        analisis = response.choices[0].message.content

        return self.render(
            'admin/analisis_ia.html',
            analisis=analisis
        )

# =========================
# Registrar todas las vistas en admin
# =========================
def configuracion_admin():
    # CRUD normales
    # Solo admin ve usuarios
    admin_panel.add_view(SecurityModelView(User, db.session))
    admin_panel.add_view(SecurityModelView(Proveedor, db.session))
    

    # Vistas que pueden ver admin, vendedor o cajero
    admin_panel.add_view(ClienteAdmin(Cliente, db.session))
    admin_panel.add_view(RoleModelView(Categoria, db.session))
    admin_panel.add_view(RoleModelView(Producto, db.session))

    # Vista personalizada de ventas también visible para estos roles
    admin_panel.add_view(VenderView(name='Vender', endpoint='vender'))

    admin_panel.add_view(VentasRealizadasView(name='Ventas Realizadas', endpoint='ventas_realizadas'))


