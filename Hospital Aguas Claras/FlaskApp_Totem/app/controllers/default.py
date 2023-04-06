
from app.controllers.wxs_functions import *
from flask.helpers import url_for
from app import app
from flask import render_template, request, redirect
from datetime import datetime


@app.route("/<h>/<txt>")
def liberado(h, txt):
    return(render_template("cover.html", h=h, txt=txt))


@app.route("/index", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
def keypad():
    if request.method == "POST":
        user = request.form["cpf"]
        hhd, txt = check_user(user)
        return(redirect(url_for("liberado",  h=hhd, txt=txt)))
    else:
        return(render_template("keypad.html"))

