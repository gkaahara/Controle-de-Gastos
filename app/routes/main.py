import os
from flask import Blueprint, render_template, redirect, request, jsonify

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return redirect("/app/dashboard")

@main_bp.route("/app/categorias")
def categorias():
    return render_template("categorias.html")

@main_bp.route("/app/salarios")
def salarios():
    return render_template("salarios.html")

@main_bp.route("/app/gastos_casa")
def gastos_casa():
    return render_template("gastos_casa.html")

@main_bp.route("/app/cartoes")
def cartoes():
    return render_template("cartoes.html")

@main_bp.route("/app/relatorios")
def relatorios():
    return render_template("relatorios.html")

@main_bp.route("/app/dashboard")
def dashboard():
    return render_template("index.html")

@main_bp.route("/shutdown", methods=["POST"])
def shutdown():
    os._exit(0)
    return jsonify({"ok": True})
