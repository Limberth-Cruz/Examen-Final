from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Crear usuario admin si no existe
        if not User.query.filter_by(username="admin").first():
            usuario = User(
                username="admin",
                name="Limberth Cruz",
                role="admin"
            )
            usuario.set_password('1234')
            db.session.add(usuario)

        # Crear usuario Pablo si no existe
        if not User.query.filter_by(username="pablo").first():
            vendedor = User(
                username="pablo",
                name="Pablo Vargas",
                role="vendedor"
            )
            vendedor.set_password('pablo1234')  # contraseña cifrada
            db.session.add(vendedor)

        # Crear usuario Pablo si no existe
        if not User.query.filter_by(username="marco").first():
            vendedor = User(
                username="marco",
                name="Marco Copa",
                role="cajero"
            )
            vendedor.set_password('marco1234')  # contraseña cifrada
            db.session.add(vendedor)

        db.session.commit()  # Guardar ambos usuarios

    app.run(debug=True)