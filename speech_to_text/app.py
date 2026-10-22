from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector

app = Flask(__name__)


# MySQL Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="web"
    )


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Save Transcription
@app.route("/save", methods=["POST"])
def save_transcription():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({
            "message": "Please enter some text."
        }), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO transcriptions (transcription) VALUES (%s)",
            (text,)
        )

        conn.commit()

        return jsonify({
            "message": "Transcription saved successfully!"
        }), 200

    except mysql.connector.Error:
        app.logger.exception("Error saving transcription")

        return jsonify({
            "message": "Could not save transcription. Please check MySQL."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


# Dashboard - View All Transcriptions
@app.route("/dashboard")
def dashboard():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM transcriptions ORDER BY id DESC"
        )

        records = cursor.fetchall()

        return render_template(
            "dashboard.html",
            records=records
        )

    except mysql.connector.Error:
        app.logger.exception("Error loading dashboard")

        return (
            "Unable to load transcription history. Please check MySQL.",
            500
        )

    finally:
        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


# Update Transcription
@app.route("/edit/<int:record_id>", methods=["POST"])
def edit_transcription(record_id):
    text = request.form.get("transcription", "").strip()

    if not text:
        return "Transcription cannot be empty.", 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE transcriptions
            SET transcription = %s
            WHERE id = %s
            """,
            (text, record_id)
        )

        conn.commit()

        # Check whether the record exists
        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT id FROM transcriptions WHERE id = %s",
                (record_id,)
            )

            record = cursor.fetchone()

            if record is None:
                return "Transcription record not found.", 404

        return redirect(url_for("dashboard"))

    except mysql.connector.Error:
        app.logger.exception("Error updating transcription")

        return "Unable to update transcription. Please check MySQL.", 500

    finally:
        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


# Delete Transcription
@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_transcription(record_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM transcriptions WHERE id = %s",
            (record_id,)
        )

        conn.commit()

        return redirect(url_for("dashboard"))

    except mysql.connector.Error:
        app.logger.exception("Error deleting transcription")

        return "Unable to delete transcription. Please check MySQL.", 500

    finally:
        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)