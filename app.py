# app.py
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from db import db
from models import User, Challenge, Submission, GlobalSettings
from forms import LoginForm, RegisterForm, ChallengeForm, SubmissionForm, ChangePasswordForm
#from routes import create_routes

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"  # Replace with a strong secret key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ctf.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

with app.app_context():
    db.create_all()

@app.before_request
def initialize_global_settings():
    with app.app_context():
        settings = GlobalSettings.query.first()
        if settings is None:
            # If no settings exist, create a default one
            new_settings = GlobalSettings(limit_submissions=False)
            db.session.add(new_settings)
            db.session.commit()


# Initialize the database
@app.before_request
def create_admin():
    with app.app_context():
        print("Checking for admin user...")
        admin = User.query.filter_by(username='admin').first()
        if admin is None:
            print("Creating admin user...")
            hashed_password = generate_password_hash('Admin@123')
            new_admin = User(username='admin', password=hashed_password, is_admin=True)  # Include a password field
            db.session.add(new_admin)
            db.session.commit()
        else:
            print("Admin user already exists.")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@login_required
def index():
    # Retrieve the toggle limit from GlobalSettings
    settings = GlobalSettings.query.first()
    toggle_limit = settings.limit_submissions if settings else False
    challenges = Challenge.query.all()
    return render_template("index.html", challenges=challenges, toggle_limit=toggle_limit) # pass details to HTML


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists. Please choose another.", "danger")
            return redirect(url_for("register"))
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data, password=hashed_password, is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Logged in successfully.", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

# Admin Routes
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))

    challenges = Challenge.query.all()
    global_settings = GlobalSettings.query.first()  # Fetch the global settings

    return render_template("admin_dashboard.html", challenges=challenges, global_settings=global_settings)


@app.route("/admin/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))

    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Hash the new password and update it
        hashed_password = generate_password_hash(form.new_password.data)
        current_user.password = hashed_password
        db.session.commit()
        flash("Password updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("change_password.html", form=form)

@app.route("/admin/toggle_limit", methods=["POST"])
@login_required
def toggle_limit():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))

    settings = GlobalSettings.query.first()
    if settings:
        # Update the setting based on the checkbox value
        settings.limit_submissions = 'limit_submissions' in request.form
        db.session.commit()
        flash("Global settings updated successfully.", "success")
    else:
        flash("Error: Global settings not found.", "danger")

    # Reset all correct submissions to allow participants to re-submit
    Submission.query.delete()
    db.session.commit()

    return redirect(url_for("admin_dashboard"))



@app.route("/admin/create_challenge", methods=["GET", "POST"])
@login_required
def create_challenge():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))
    form = ChallengeForm()
    if form.validate_on_submit():
        challenge = Challenge(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            hint=form.hint.data,
            answer_info=form.answer_info.data,
            flag=form.flag.data,  # The correct answer/flag
        )
        db.session.add(challenge)
        db.session.commit()
        flash("Challenge created successfully.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("create_challenge.html", form=form)

@app.route("/admin/edit_challenge/<int:challenge_id>", methods=["GET", "POST"])
@login_required
def edit_challenge(challenge_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))

    challenge = Challenge.query.get_or_404(challenge_id)
    form = ChallengeForm(obj=challenge)

    if form.validate_on_submit():
        challenge.title = form.title.data
        challenge.description = form.description.data
        challenge.category = form.category.data
        challenge.hint = form.hint.data
        challenge.answer_info=form.answer_info.data
        challenge.flag = form.flag.data

        db.session.commit()
        flash("Challenge updated successfully.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_challenge.html", form=form, challenge=challenge)

@app.route("/admin/rankings")
@login_required
def rankings():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))

    # Query to count correct submissions and sort by score first, then time
    rankings = (
        db.session.query(
            User.username,
            db.func.count(Submission.id).label("score"),
            db.func.max(Submission.timestamp).label("last_solved_time")
        )
        .join(Submission)
        .filter(Submission.is_correct == True)  # Only correct submissions
        .group_by(User.id)
        .order_by(db.desc("score"), db.asc("last_solved_time"))  # Rank by score first, then by time
        .all()
    )

    return render_template("rankings.html", rankings=rankings)

@app.route("/admin/unlock_all", methods=["POST"])
@login_required
def unlock_all():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))
    # Reset all correct submissions to allow participants to re-submit
    Submission.query.delete()
    db.session.commit()
    # Reset the global setting for submission limit to its default value (False)
    global_settings = GlobalSettings.query.first()
    if global_settings:
        global_settings.limit_submissions = False  # Set the submission limit toggle to default (False)
        db.session.commit()
    flash("All challenges have been unlocked for participants.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/flush_challenges", methods=["POST"])
@login_required
def flush_challenges():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("index"))

    # Delete all challenges and submissions from the database
    try:
        # First, delete all submissions (rankings)
        Submission.query.delete()
        # Then, delete all challenges
        Challenge.query.delete()
        db.session.commit()

        # Reset the global setting for submission limit to its default value (False)
        global_settings = GlobalSettings.query.first()
        if global_settings:
           global_settings.limit_submissions = False  # Set the submission limit toggle to default (False)
           db.session.commit()

        flash("All challenges and rankings have been successfully flushed.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while flushing challenges and rankings: {str(e)}", "danger")

    return redirect(url_for("admin_dashboard"))


# Participant Routes
@app.route("/submit/<int:challenge_id>", methods=["POST"])
@login_required
def submit_flag(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    form = SubmissionForm()

    # Fetch global settings
    global_settings = GlobalSettings.query.first()

    if global_settings and global_settings.limit_submissions:
        # Check how many wrong submissions the user has made for this challenge
        wrong_attempts = Submission.query.filter_by(
            user_id=current_user.id, challenge_id=challenge_id, is_correct=False
        ).count()

        if wrong_attempts >= 5:
            flash("You have reached the maximum number of incorrect submissions for this challenge.", "danger")
            return redirect(url_for("challenge_detail", challenge_id=challenge_id))

    if form.validate_on_submit():
        # Check if the user has already submitted a correct flag for this challenge
        existing_submission = Submission.query.filter_by(
            user_id=current_user.id, challenge_id=challenge_id, is_correct=True
        ).first()

        if existing_submission:
            flash(
                "You have already solved this challenge. Please wait for admin to unlock it.",
                "warning",
            )
            return redirect(url_for("challenge_detail", challenge_id=challenge_id, solved=True))

        # Check if the user has any submission for this challenge
        user_submission = Submission.query.filter_by(
            user_id=current_user.id, challenge_id=challenge_id
        ).first()

        if user_submission and user_submission.is_correct:
            flash(
                "You have already solved this challenge. Please wait for admin to unlock it.",
                "warning",
            )
            return redirect(url_for("challenge_detail", challenge_id=challenge_id, solved=True))

        # Get the submitted flag, trim spaces, and compare it in a case-insensitive way
        submitted_flag = form.flag.data.strip()  # Remove leading/trailing spaces
        is_correct = submitted_flag.lower() == challenge.flag.strip().lower()  # Case-insensitive comparison

        submission = Submission(
            user_id=current_user.id,
            challenge_id=challenge_id,
            submitted_flag=form.flag.data.strip(),
            is_correct=is_correct,
            timestamp=datetime.utcnow(),
        )

        db.session.add(submission)
        db.session.commit()

        if is_correct:
            flash("Correct flag! Challenge solved.", "success")
            # Redirect to the challenge detail page with a success flag
            return redirect(url_for("challenge_detail", challenge_id=challenge_id, solved=True))
        else:
            flash("Incorrect flag. Try again!", "danger")

    # If the form isn't valid, redirect back to the challenge detail page
    return redirect(url_for("challenge_detail", challenge_id=challenge_id))

@app.route("/challenge/<int:challenge_id>", methods=["GET", "POST"])
@login_required
def challenge_detail(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    submission = Submission.query.filter_by(
        user_id=current_user.id, challenge_id=challenge_id, is_correct=True
    ).first()
    form = SubmissionForm()
    if form.validate_on_submit():
        # Redirect to submit_flag route
        return redirect(url_for("submit_flag", challenge_id=challenge_id))
    return render_template(
        "challenge_detail.html", challenge=challenge, submission=submission, form=form
    )

#create_routes(app)

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=7000, debug=True)
