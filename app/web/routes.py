from flask import render_template, send_file
from app import API_URL
from app.web import bp


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html", API_URL=API_URL)


@bp.route("/manifest.json")
def serve_manifest():
    return send_file("static/manifest.json", mimetype="application/manifest+json")


@bp.route("/sw.js")
def serve_sw():
    return send_file("static/sw.js", mimetype="application/javascript")
