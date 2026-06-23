from flask import jsonify, request
from sqlalchemy import text
import datetime
from app.api import bp
from app import engine


@bp.route("/")
@bp.route("/<int:max_id>")
def index(max_id=2):
    with engine.connect() as conn:
        query = text(
            """
            SELECT id, kanji FROM yojijukugo
            WHERE id < :max_id;"""
        )
        result = conn.execute(query, {"max_id": max_id})
        data = result.fetchall()
    return jsonify(dict(zip(("id", "kanji"), data[0]))), 200


@bp.route("/yoji/<int:id_>")
def yoji(id_):
    with engine.connect() as conn:
        cols = (
            "id",
            "kanji",
            "reading",
            "usage",
            "meaning",
            "is_wikipedia_link",
            "sentence_id",
        )
        query = text(
            f"""
            SELECT {', '.join(cols)} FROM yojijukugo
            WHERE id = :id;"""
        )
        result = conn.execute(query, {"id": id_})
        data = result.fetchall()
    return jsonify(dict(zip(cols, data[0]))), 200


@bp.route("/yoji/<string:q>")
def search_yoji(q):
    with engine.connect() as conn:
        query = text(
            """
            SELECT id, kanji FROM yojijukugo
            WHERE kanji = :q;"""
        )
        result = conn.execute(query, {"q": q})
        data = result.fetchall()
    return jsonify(dict(zip(("id", "kanji"), data[0]))), 200


@bp.route("/yoji")
def search_yoji_with_param():
    q = request.args.get("q")
    if q is None:
        abort(400, description='Missing required query parameter "q"')

    # Add actual search function
    return search_yoji(q)


@bp.route("/date/<string:date>")
def date_string(date):
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        return False

    cols = (
        "id",
        "kanji",
        "reading",
        "usage",
        "meaning",
        "is_wikipedia_link",
        "sentence_id",
        "date",
    )

    with engine.connect() as conn:
        query = text(
            f"""
            SELECT {', '.join(cols)} FROM yojijukugo
            WHERE date = :date;"""
        )
        result = conn.execute(query, {"date": date})
        data = result.fetchall()
    return jsonify(dict(zip(cols, data[0]))), 200


@bp.route("/date/<int:year>/<int:month>/<int:day>")
def date_url(year, month, day):
    return date_string(str(datetime.date(year, month, day)))


@bp.route("/sentence/<int:id_>")
def sentence(id_):
    cols = ("id", "sentence_text", "owner", "translation_id")

    with engine.connect() as conn:
        query = text(
            f"""
            SELECT {', '.join(cols)} FROM sentence
            WHERE id = :id;"""
        )
        result = conn.execute(query, {"id": id_})
        data = result.fetchall()
    return jsonify(dict(zip(cols, data[0]))), 200


@bp.route("/translation/<int:id_>")
def translation(id_):
    with engine.connect() as conn:
        query = text(
            """
            SELECT id, translation_text, owner from translation
            WHERE id = :id;"""
        )
        result = conn.execute(query, {"id": id_})
        data = result.fetchall()
    return jsonify(dict(zip(("id", "translation_text", "owner"), data[0]))), 200
