from flask import Flask, render_template, request, redirect, url_for, flash
import re

app = Flask(__name__)
app.secret_key = "student-management-secret"

students = []


@app.route("/")
def index():
    return render_template("index.html", students=students)


@app.route("/students")
def show_students():
    return render_template("students.html", students=students)


@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        # Receive form data
        name = request.form.get("name", "").strip()
        student_id = request.form.get("student_id", "").strip()
        email = request.form.get("email", "").strip()

        # 1. Check required fields
        if not name or not student_id or not email:
            flash("All fields are required!", "error")
            return render_template("add_student.html")

        # 2. Check duplicate student ID
        for student in students:
            if student["id"].lower() == student_id.lower():
                flash("Student ID already exists!", "error")
                return render_template("add_student.html")

        # 3. Check duplicate email
        for student in students:
            if student["email"].lower() == email.lower():
                flash("Email already exists!", "error")
                return render_template("add_student.html")

        # 4. Validate email format
        pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

        if not re.fullmatch(pattern, email):
            flash("Invalid email format!", "error")
            return render_template("add_student.html")

        # 5. Add student
        new_student = {
            "name": name,
            "id": student_id,
            "email": email
        }

        students.append(new_student)

        flash("Student added successfully!", "success")

        return redirect(url_for("show_students"))

    return render_template("add_student.html")


if __name__ == "main":
    app.run(debug=True)