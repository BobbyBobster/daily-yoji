import argparse
import sqlite3
import re
import requests
import time
import subprocess
import tempfile
import os
import datetime
import random


def createTable(cursor):
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS yojijukugo (
        id INTEGER PRIMARY KEY,
        kanji TEXT NOT NULL,
        reading TEXT NOT NULL,
        usage TEXT,
        meaning TEXT,
        is_wikipedia_link BOOLEAN NOT NULL DEFAULT 0,
        date TEXT UNIQUE,
        sentence_id INTEGER,
        FOREIGN KEY(sentence_id) REFERENCES sentence(id)
    );
    """
    )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS sentence (
        id INTEGER PRIMARY KEY,
        sentence_text TEXT NOT NULL,
        owner TEXT NOT NULL DEFAULT 'tatoeba',
        language TEXT DEFAULT 'jpn',
        translation_id INTEGER,
        FOREIGN KEY(translation_id) REFERENCES translation(id)
    );
    """
    )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS translation (
        id INTEGER PRIMARY KEY,
        translation_text TEXT NOT NULL,
        owner TEXT NOT NULL DEFAULT 'tatoeba',
        language TEXT DEFAULT 'eng'
    );
    """
    )


def populateDatabase(cursor):
    kanji_pattern = r"[\u4E00-\u9FFF々]+"
    hiragana_pattern = r"[\u3040-\u309F]+"
    katakana_pattern = r"[\u30A0-\u30FF]+"
    reading_pattern = r"[\u3040-\u309F\u30A0-\u30FF　]+"

    with open("data/utf8-4j324_sj.txt", "r") as f:
        for firstline in f:
            if firstline.startswith("「") or firstline == "" or firstline == "\n":
                continue

            kanji = re.search(kanji_pattern, firstline)
            readingMatch = re.search(r"\((" + reading_pattern + r")\)", firstline)
            reading = readingMatch[1].replace("\u3000", "")
            if "・" in reading:
                reading = reading[0 : reading.find("・")]

            secondline = next(f)
            usageMatch = re.match(r"\(([a-z\-,]+)\)", secondline)
            usage = usageMatch[1]

            meaning_start = secondline.find(" ") + 1
            meaning = re.match(r".*", secondline[meaning_start:])

            cursor.execute(
                """
                INSERT INTO yojijukugo 
                (kanji, reading, usage, meaning) VALUES (?, ?, ?, ?);""",
                (kanji[0], reading, usage, meaning[0]),
            )


def addSentences(cursor):
    # Add example sentences from tatoeba.org
    # TODO: If no translations exist for full-kanji use, try a version with hiragana
    cursor.execute("SELECT kanji FROM yojijukugo;")
    rows = cursor.fetchall()

    for row in rows:
        time.sleep(0.5)
        yoji = row[0]
        tatoeba_url_base = "https://api.tatoeba.org/v1/sentences"
        tatoeba_params = "?lang=jpn&sort=relevance&limit=5&is_unapproved=no&license=CC+BY+2.0+FR&trans%3Alang=eng&trans%3Ais_direct=yes&trans%3Ais_unapproved=no"
        tatoeba_response = requests.get(
            tatoeba_url_base + tatoeba_params + "&q=" + yoji
        )

        if tatoeba_response.ok and tatoeba_response.json()["data"]:
            print(tatoeba_response.json())
            s_data = tatoeba_response.json()["data"][0]
            t_data = s_data["translations"][0]

            s_data["owner"] = "tatoeba" if s_data["owner"] is None else s_data["owner"]
            t_data["owner"] = "tatoeba" if t_data["owner"] is None else t_data["owner"]

            cursor.execute(
                """
                INSERT INTO translation
                (id, translation_text, owner) VALUES (?, ?, ?);""",
                (t_data["id"], t_data["text"], t_data["owner"]),
            )

            cursor.execute(
                """
                INSERT INTO sentence
                (id, sentence_text, owner, translation_id) VALUES (?, ?, ?, ?);""",
                (s_data["id"], s_data["text"], s_data["owner"], t_data["id"]),
            )

            cursor.execute(
                """
                UPDATE yojijukugo
                SET sentence_id = ?
                WHERE kanji IN (?);""",
                (s_data["id"], yoji),
            )


def addLinks(cursor):
    cursor.execute("SELECT kanji FROM yojijukugo;")
    rows = cursor.fetchall()
    wiki_list = []

    with tempfile.NamedTemporaryFile(mode="wt", delete=False) as fp:
        for yoji in rows:
            fp.write("^" + yoji[0] + "$" + "\n")
        fp.close()

        wiki_yoji = subprocess.run(
            ["zgrep", "-f", fp.name, "data/jawiki-latest-all-titles-in-ns0.gz"],
            capture_output=True,
            text=True,
        )
        wiki_list = wiki_yoji.stdout.split()

    placeholders = ", ".join("?" for _ in wiki_list)

    cursor.execute(
        f"""
        UPDATE yojijukugo
        SET is_wikipedia_link = TRUE
        WHERE kanji IN ({placeholders});""",
        (wiki_list),
    )


def addDates(cursor):
    cursor.execute(
        """
    SELECT COUNT(*) FROM yojijukugo;"""
    )
    rowcount = cursor.fetchone()[0]

    indices = [idx for idx in range(1, rowcount + 1)]
    datelist = [
        datetime.date.today() + datetime.timedelta(days=day) for day in range(rowcount)
    ]
    random.shuffle(datelist)

    for idx, date in zip(indices, datelist):
        cursor.execute(
            """
        UPDATE yojijukugo
        SET date = ?
        WHERE id = ?""",
            (date, idx),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--create", action="store_true", help="create tables in database"
    )
    parser.add_argument(
        "--populate", action="store_true", help="populate database with extracted data"
    )
    parser.add_argument(
        "--sentences",
        action="store_true",
        help="add example sentences from Tatoeba.org",
    )
    parser.add_argument(
        "--links",
        action="store_true",
        help="check for entries in Wikipedia and/or yoji-jukugo.com",
    )
    parser.add_argument(
        "--dates", action="store_true", help="add random datestamps to all rows"
    )
    args = parser.parse_args()

    conn = sqlite3.connect("yoji.db")
    cursor = conn.cursor()

    if args.create:
        if os.path.exists("yoji.db"):
            os.remove("yoji.db")
            conn = sqlite3.connect("yoji.db")
            cursor = conn.cursor()

        createTable(cursor)
        conn.commit()

    if args.populate:
        populateDatabase(cursor)
        cursor.execute("delete from yojijukugo where id > 10;")
        conn.commit()

    if args.sentences:
        addSentences(cursor)
        conn.commit()

    if args.links:
        addLinks(cursor)
        conn.commit()

    if args.dates:
        addDates(cursor)
        conn.commit()

    cursor.execute("SELECT * FROM yojijukugo")
    rows = cursor.fetchall()
    for row in rows:
        pass
        # print(row)

    conn.close()
