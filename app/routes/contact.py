from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mail import Message
from app import db, mail, limiter
from app.models import ContactMessage, NewsletterSubscriber
from app.forms import ContactForm, NewsletterForm

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def index():
    form = ContactForm()

    if form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data.strip()
        subject = form.subject.data.strip()
        message_text = form.message.data.strip()

        msg_entry = ContactMessage(
            name=name, email=email, subject=subject, message=message_text
        )
        db.session.add(msg_entry)
        db.session.commit()

        try:
            msg = Message(
                subject=f"[Tendereo Contact] {subject}",
                recipients=[current_app.config.get("MAIL_DEFAULT_SENDER", "info@tendereo.org")],
                body=f"Nom: {name}\nEmail: {email}\n\n{message_text}",
                reply_to=email,
            )
            mail.send(msg)
        except Exception:
            pass

        flash("Votre message a bien été envoyé. Nous vous répondrons rapidement.", "success")
        return redirect(url_for("contact.index"))

    return render_template("contact/index.html", form=form)


@contact_bp.route("/newsletter", methods=["POST"])
@limiter.limit("5 per hour")
def newsletter():
    form = NewsletterForm()

    if form.validate_on_submit():
        email = form.email.data.strip()
        name = form.name.data.strip() if form.name.data else ""

        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        if existing:
            if existing.is_active:
                flash("Vous êtes déjà inscrit à notre newsletter.", "info")
            else:
                existing.is_active = True
                db.session.commit()
                flash("Votre inscription a été réactivée !", "success")
        else:
            sub = NewsletterSubscriber(email=email, name=name)
            db.session.add(sub)
            db.session.commit()
            flash("Merci ! Vous êtes maintenant inscrit à notre newsletter.", "success")
    else:
        flash("Veuillez entrer une adresse email valide.", "error")

    return redirect(request.referrer or url_for("main.index"))
