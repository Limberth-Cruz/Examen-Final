from flask import Blueprint, redirect, url_for, render_template, request, jsonify
from flask_login import login_user, logout_user, login_required
from .models import User, Producto
from .extensions import login_manager
from .ai_chat import client, preguntar_chatbot

auth_bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ----------- inicio -----------

@auth_bp.route("/")
def inicio():
    return redirect(url_for("auth.login"))


# ----------- login -----------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = User.query.filter_by(
            username=request.form.get("nombreusuario")
        ).first()

        if usuario and usuario.check_password(
            request.form.get("contrasenia")
        ):
            login_user(usuario)
            return redirect("/admin")

    return render_template("login.html")


# ----------- logout -----------

@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("auth.login"))
    
# -------------------------
# API chatbot (usada por admin/chatbot.html)
# -------------------------
@auth_bp.route("/chatbot", methods=["POST"])
@login_required
def chatbot():

    data = request.json

    pregunta = data.get("mensaje")

    respuesta = preguntar_chatbot(pregunta)

    return jsonify({
        "respuesta": respuesta
    })




# -------------------------
# API chatbot (usada por admin/chatbot.html)
# -------------------------
@auth_bp.route("/chatbot", methods=["POST"])
@login_required
def chatbot():

    data = request.json

    pregunta = data.get("mensaje")

    respuesta = preguntar_chatbot(pregunta)

    return jsonify({
        "respuesta": respuesta
    })

