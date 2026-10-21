import os
import sqlite3
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-dev-secret")
DB_PATH = os.environ.get("DATABASE_PATH", "/data/internships.db")


def get_db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS internships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT NOT NULL DEFAULT '',
                applied_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route("/")
def index():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM internships").fetchone()[0]
        applied = conn.execute("SELECT COUNT(*) FROM internships WHERE status='Applied'").fetchone()[0]
        interviews = conn.execute("SELECT COUNT(*) FROM internships WHERE status='Interview'").fetchone()[0]
        selected = conn.execute("SELECT COUNT(*) FROM internships WHERE status='Selected'").fetchone()[0]
        recent = conn.execute("SELECT * FROM internships ORDER BY id DESC LIMIT 5").fetchall()
    return render_template("index.html", total=total, applied=applied,
                           interviews=interviews, selected=selected, recent=recent)


@app.route("/add", methods=["GET", "POST"])
def add_internship():
    if request.method == "POST":
        company = request.form.get("company", "").strip()
        role = request.form.get("role", "").strip()
        location = request.form.get("location", "").strip()
        applied_date = request.form.get("applied_date", "").strip() or date.today().isoformat()
        status = request.form.get("status", "Applied")
        notes = request.form.get("notes", "").strip()
        allowed_statuses = {"Applied", "Interview", "Selected", "Rejected", "Withdrawn"}
        if not company or not role:
            flash("Company name and role are required.", "error")
            return render_template("add_internship.html", form=request.form)
        if status not in allowed_statuses:
            abort(400)
        with get_db() as conn:
            conn.execute(
                """INSERT INTO internships (company, role, location, applied_date, status, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (company, role, location, applied_date, status, notes)
            )
        flash("Internship application added successfully.", "success")
        return redirect(url_for("applications"))
    return render_template("add_internship.html", form={})


@app.route("/applications")
def applications():
    search = request.args.get("q", "").strip()
    with get_db() as conn:
        if search:
            rows = conn.execute(
                """SELECT * FROM internships
                   WHERE company LIKE ? OR role LIKE ? OR location LIKE ?
                   ORDER BY applied_date DESC, id DESC""",
                (f"%{search}%", f"%{search}%", f"%{search}%")
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM internships ORDER BY applied_date DESC, id DESC").fetchall()
    return render_template("applications.html", applications=rows, q=search)


@app.route("/applications/<int:internship_id>/delete", methods=["POST"])
def delete_internship(internship_id):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM internships WHERE id = ?", (internship_id,))
        if cur.rowcount == 0:
            abort(404)
    flash("Internship application deleted.", "success")
    return redirect(url_for("applications"))


@app.route("/health")
def health():
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        return {"status": "healthy"}, 200
    except sqlite3.Error:
        return {"status": "unhealthy"}, 500


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
