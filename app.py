import os
import re
import sqlite3
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, jsonify, g
)

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "mevi-workshop-development-key"
)

# Database configuration
os.makedirs(app.instance_path, exist_ok=True)

DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(app.instance_path, "management.db")
)

EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


# Database connection
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row

    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


# Create database table
def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                course TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


# Initialize the schema for both direct runs and Flask CLI deployments.
init_db()


# Dashboard
@app.route("/")
def dashboard():
    db = get_db()

    total_students = db.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_courses = db.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    ).fetchone()[0]

    new_this_month = db.execute(
        """
        SELECT COUNT(*) FROM students
        WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        """
    ).fetchone()[0]

    course_breakdown = db.execute(
        """
        SELECT course, COUNT(*) AS student_count
        FROM students
        GROUP BY course
        ORDER BY student_count DESC, course COLLATE NOCASE
        LIMIT 5
        """
    ).fetchall()

    recent_students = db.execute(
        "SELECT * FROM students ORDER BY id DESC LIMIT 5"
    ).fetchall()

    return render_template(
        "index.html",
        total_students=total_students,
        total_courses=total_courses,
        new_this_month=new_this_month,
        course_breakdown=course_breakdown,
        recent_students=recent_students
    )


# Student management page
@app.route("/students")
def students():
    db = get_db()

    all_students = db.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    return render_template(
        "student.html",
        students=all_students
    )


# Add student
@app.route("/students/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    course = request.form.get("course", "").strip()

    if not name or not email or not course:
        flash("Please fill in all fields.", "error")
        return redirect(url_for("students"))

    if not EMAIL_PATTERN.fullmatch(email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("students"))

    if len(name) > 120 or len(course) > 120 or len(email) > 254:
        flash("Name and course must be 120 characters or fewer; email must be 254 or fewer.", "error")
        return redirect(url_for("students"))

    db = get_db()

    existing_student = db.execute(
        "SELECT 1 FROM students WHERE email = ? COLLATE NOCASE LIMIT 1",
        (email,)
    ).fetchone()

    if existing_student:
        flash("This email address is already registered.", "error")
        return redirect(url_for("students"))

    try:
        db.execute(
            """
            INSERT INTO students (name, email, course)
            VALUES (?, ?, ?)
            """,
            (name, email, course)
        )
        db.commit()

        flash("Student added successfully!", "success")

    except sqlite3.IntegrityError:
        db.rollback()
        existing_student = db.execute(
            "SELECT 1 FROM students WHERE email = ? COLLATE NOCASE LIMIT 1",
            (email,)
        ).fetchone()

        if existing_student:
            flash("This email address is already registered.", "error")
        else:
            raise

    return redirect(url_for("students"))


# Delete student
@app.route("/students/<int:student_id>/delete", methods=["POST"])
def delete_student(student_id):
    db = get_db()

    cursor = db.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    if cursor.rowcount == 0:
        db.rollback()
        flash("Student record was not found or has already been deleted.", "error")
        return redirect(url_for("students"))

    db.commit()

    flash("Student record deleted.", "success")

    return redirect(url_for("students"))


# JSON API
@app.route("/api/students")
def students_api():
    db = get_db()

    records = db.execute(
        "SELECT id, name, email, course FROM students ORDER BY id DESC"
    ).fetchall()

    return jsonify([
        dict(record) for record in records
    ])


# Health check
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "MEVI Management Portal"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )