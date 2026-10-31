import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fixit.db"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

db = SQLAlchemy(app)


# Report database model
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    street = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    reporter_name = db.Column(db.String(100), nullable=False)
    reporter_cell = db.Column(db.String(10), nullable=False)
    photo_path = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False, default="Open")
    created_at = db.Column(db.DateTime, server_default=db.func.now())


# Coordinator database model
class Coordinator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)


# Create database tables
with app.app_context():
    db.create_all()


# Home page route
@app.route("/")
def index():
    return render_template("index.html")


# Report submission route
@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        ref = "W42-" + str(Report.query.count() + 1).zfill(4)

        new_report = Report(
            reference=ref,
            category=request.form["category"],
            street=request.form["street"],
            description=request.form["description"],
            reporter_name=request.form["reporter_name"],
            reporter_cell=request.form["reporter_cell"]
        )

        db.session.add(new_report)
        db.session.commit()

        return render_template("confirmation.html", reference=ref)

    return render_template("report.html")


# Check report status route
@app.route("/status")
def status():
    reference = request.args.get("reference")
    report = None

    if reference:
        report = Report.query.filter_by(reference=reference.strip()).first()

    return render_template("status.html", reference=reference, report=report)

# Coordinator login route
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = Coordinator.query.filter_by(
            username=request.form["username"]
        ).first()

        if user and check_password_hash(
            user.password_hash, request.form["password"]
        ):
            session.clear()
            session["coordinator_id"] = user.id
            return redirect(url_for("reports"))

        error = "Incorrect username or password."

    return render_template("login.html", error=error)

# Coordinator logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# Coordinator reports page
@app.route("/reports")
def reports():
    if "coordinator_id" not in session:
        return redirect(url_for("login"))

    all_reports = Report.query.order_by(
        Report.created_at.desc()
    ).all()

    return render_template("reports.html", reports=all_reports)

# Update report status route
@app.route("/report/<int:report_id>/status", methods=["POST"])
def update_status(report_id):
    if "coordinator_id" not in session:
        return redirect(url_for("login"))

    report = Report.query.get_or_404(report_id)

    new_status = request.form.get("status")

    if new_status in ["Open", "In progress", "Closed"]:
        report.status = new_status
        db.session.commit()

    return redirect(url_for("reports"))


    