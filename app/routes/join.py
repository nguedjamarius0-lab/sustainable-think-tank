from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db, limiter
from app.models import JoinApplication
from app.forms import JoinApplicationForm

join_bp = Blueprint("join", __name__)


@join_bp.route("/", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def index():
    form = JoinApplicationForm()

    if form.validate_on_submit():
        application = JoinApplication(
            name=form.name.data.strip(),
            email=form.email.data.strip(),
            application_type=form.application_type.data.strip(),
            motivation=form.motivation.data.strip() if form.motivation.data else "",
            organization=form.organization.data.strip() if form.organization.data else "",
            phone=form.phone.data.strip() if form.phone.data else "",
        )
        db.session.add(application)
        db.session.commit()

        flash("Votre demande a bien été envoyée. Nous vous contacterons bientôt.", "success")
        return redirect(url_for("join.index"))

    return render_template("join/index.html", form=form)
