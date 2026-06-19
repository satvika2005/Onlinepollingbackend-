from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)


# Database connection
def get_db():
    conn = sqlite3.connect("polling.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create database tables
def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS polls(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS options(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poll_id INTEGER,
        option_name TEXT,
        votes INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


# Register User
@app.route("/register", methods=["POST"])
def register():

    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (
                data["name"],
                data["email"],
                data["password"]
            )
        )

        conn.commit()

        return jsonify({
            "message": "User registered successfully"
        })

    except:
        return jsonify({
            "message": "Email already exists"
        })

    finally:
        conn.close()



# Create Poll
@app.route("/polls", methods=["POST"])
def create_poll():

    data = request.json

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO polls(question) VALUES(?)",
        (data["question"],)
    )

    poll_id = cursor.lastrowid


    for option in data["options"]:

        cursor.execute(
            "INSERT INTO options(poll_id, option_name) VALUES(?,?)",
            (poll_id, option)
        )


    conn.commit()
    conn.close()


    return jsonify({
        "message":"Poll created",
        "poll_id":poll_id
    })



# Get All Polls
@app.route("/polls", methods=["GET"])
def get_polls():

    conn = get_db()
    cursor = conn.cursor()


    polls = cursor.execute(
        "SELECT * FROM polls"
    ).fetchall()


    result = []


    for poll in polls:

        options = cursor.execute(
            "SELECT * FROM options WHERE poll_id=?",
            (poll["id"],)
        ).fetchall()


        result.append({

            "id": poll["id"],

            "question": poll["question"],

            "options":[dict(option) for option in options]

        })


    conn.close()


    return jsonify(result)



# Vote
@app.route("/vote", methods=["POST"])
def vote():

    data = request.json


    conn = get_db()
    cursor = conn.cursor()


    cursor.execute(
        "UPDATE options SET votes=votes+1 WHERE id=?",
        (data["option_id"],)
    )


    conn.commit()
    conn.close()


    return jsonify({
        "message":"Vote submitted"
    })



# Poll Result
@app.route("/poll/<int:id>/result", methods=["GET"])
def result(id):

    conn = get_db()
    cursor = conn.cursor()


    results = cursor.execute(
        "SELECT option_name,votes FROM options WHERE poll_id=?",
        (id,)
    ).fetchall()


    conn.close()


    return jsonify(
        [dict(row) for row in results]
    )



# Start Server
if __name__ == "__main__":

    create_tables()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
