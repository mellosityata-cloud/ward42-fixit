

import os
import uuid
import re


from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    send_from_directory,
    jsonify
)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fixit.db"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# File upload settings
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

# Secure session cookie settings
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True when deployed over HTTPS

# Allowed photo extensions and content types
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

db = SQLAlchemy(app)

# Enable CSRF protection
csrf = CSRFProtect(app)

# Valid report categories
CATEGORIES = [
    "Pothole",
    "Water leak",
    "Streetlight",
    "Illegal dumping",
    "Other"
]


# Check allowed image extensions
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# Validate resident report details
def validate_report(form):
    errors = []

    category = form.get("category", "").strip()
    street = form.get("street", "").strip()
    description = form.get("description", "").strip()
    reporter_name = form.get("reporter_name", "").strip()
    reporter_cell = form.get("reporter_cell", "").strip()

    if category not in CATEGORIES:
        errors.append("Please choose a valid report category.")

    if not street or len(street) > 200:
        errors.append(
            "Please enter a street or landmark (maximum 200 characters)."
        )

    if not 10 <= len(description) <= 500:
        errors.append(
            "Your description must be between 10 and 500 characters."
        )

    if not reporter_name or len(reporter_name) > 100:
        errors.append(
            "Please enter your name (maximum 100 characters)."
        )

    if not re.fullmatch(r"0\d{9}", reporter_cell):
        errors.append(
            "Your cell number must contain 10 digits starting with 0."
        )

    return errors


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
# Add security headers to every response
@app.after_request
def add_security_headers(response):
    
    response.headers["Content-Security-Policy"] = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net; "
    "style-src 'self' https://cdn.jsdelivr.net; "
    "img-src 'self' data:; "
    "connect-src 'self' https://cdn.jsdelivr.net; "
    "frame-ancestors 'none'"
)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response

# Home page route
@app.route("/")
def index():
    return render_template("index.html")


# Report submission route
@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":

        # Validate all report fields before saving anything
        errors = validate_report(request.form)

        if errors:
            return render_template(
                "report.html",
                errors=errors
            ), 400

        photo = request.files.get("photo")
        photo_filename = None

        if photo and photo.filename:

            # Check both file extension and content type
            if (
                not allowed_file(photo.filename)
                or photo.mimetype not in ALLOWED_TYPES
            ):
                return (
                    render_template(
                        "report.html",
                        error="Invalid photo format. Please upload a JPG, JPEG, PNG or WEBP image."
                    ),
                    400
                )

            # Extract extension before sanitising filename
            extension = photo.filename.rsplit(".", 1)[1].lower()

            # Generate a unique and sanitised filename
            photo_filename = secure_filename(
                f"{uuid.uuid4().hex}.{extension}"
            )

            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

            photo.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    photo_filename
                )
            )

        # Generate report reference
        ref = "W42-" + str(Report.query.count() + 1).zfill(4)

        # Save validated and stripped values
        new_report = Report(
            reference=ref,
            category=request.form.get("category", "").strip(),
            street=request.form.get("street", "").strip(),
            description=request.form.get("description", "").strip(),
            reporter_name=request.form.get("reporter_name", "").strip(),
            reporter_cell=request.form.get("reporter_cell", "").strip(),
            photo_path=photo_filename
        )

        db.session.add(new_report)
        db.session.commit()

        return render_template(
            "confirmation.html",
            reference=ref
        )

    return render_template("report.html")



# Check report status route
@app.route("/status")
def status():
    reference = request.args.get("reference")
    report = None

    if reference:
        report = Report.query.filter_by(
            reference=reference.strip()
        ).first()

    return render_template(
        "status.html",
        reference=reference,
        report=report
    )


# Coordinator login route
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = Coordinator.query.filter_by(
            username=request.form["username"]
        ).first()

        if user and check_password_hash(
            user.password_hash,
            request.form["password"]
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

    return render_template(
        "reports.html",
        reports=all_reports
    )
# Coordinator dashboard route
@app.route("/dashboard")
def dashboard():
    if "coordinator_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")

# Reports analytics API
@app.route("/api/reports/summary")
def reports_summary():

    # Only logged-in coordinators can access the API
    if "coordinator_id" not in session:
        return jsonify({
            "error": "Login required"
        }), 401

    # Count reports by category
    by_category = db.session.query(
        Report.category,
        func.count(Report.id)
    ).group_by(Report.category).all()

    # Count reports by status
    by_status = db.session.query(
        Report.status,
        func.count(Report.id)
    ).group_by(Report.status).all()

    # Return the results as JSON
    return jsonify({
        "by_category": dict(by_category),
        "by_status": dict(by_status),
        "total": Report.query.count()
    })

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


# Handle files that exceed the 2 MB upload limit
@app.errorhandler(413)
def request_entity_too_large(error):
    return (
        render_template(
            "report.html",
            error="Your upload is too large. Please select an image smaller than 2 MB."
        ),
        413
    )


# Display uploaded photos to logged-in coordinators
@app.route("/uploads/<filename>")
def uploaded_photo(filename):
    if "coordinator_id" not in session:
        return redirect(url_for("login"))

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# View individual report details
@app.route("/report/<int:report_id>")
def report_detail(report_id):
    if "coordinator_id" not in session:
        return redirect(url_for("login"))

    report = Report.query.get_or_404(report_id)

    return render_template(
        "report_detail.html",
        report=report
    )





    