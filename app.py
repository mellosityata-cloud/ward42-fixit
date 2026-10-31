from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fixit.db"

db = SQLAlchemy(app)

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
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

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

@app.route("/status")
def status():
    reference = request.args.get("reference")
    report = None

    if reference:
        report = Report.query.filter_by(reference=reference.strip()).first()

    return render_template("status.html", reference=reference, report=report)

    