from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, EmailVerification
from app.services import generate_and_send_code
from app.forms import (
    RegisterForm, LoginForm, VerifyEmailForm,
    ForgotPasswordForm, ResetPasswordForm, AdminRegisterForm, AdminVerifyForm
)

auth_bp = Blueprint("auth", __name__)
admin_hidden_bp = Blueprint("admin_hidden", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()

    if form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        if User.query.filter_by(email=email).first():
            flash("Un compte existe déjà avec cet email.", "error")
            return redirect(url_for("auth.register"))

        user = User(name=name, email=email, role="user", is_verified=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Compte créé avec succès ! Vous pouvez vous connecter.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/verify-email", methods=["GET", "POST"])
def verify_email():
    purpose = request.args.get("purpose", "registration")
    email = session.get("pending_email")

    if not email:
        flash("Session expirée. Veuillez recommencer.", "error")
        return redirect(url_for("auth.register") if purpose == "registration" else url_for("auth.forgot_password"))

    form = VerifyEmailForm()

    if form.validate_on_submit():
        code = form.code.data.strip()

        verification = EmailVerification.query.filter_by(
            email=email, code=code, purpose=purpose, is_used=False
        ).order_by(EmailVerification.created_at.desc()).first()

        if not verification or verification.is_expired():
            flash("Code invalide ou expiré. Veuillez réessayer.", "error")
            return redirect(url_for("auth.verify_email", purpose=purpose))

        verification.is_used = True
        db.session.commit()

        if purpose == "registration":
            user = User.query.filter_by(email=email).first()
            if user:
                user.is_verified = True
                db.session.commit()
            session.pop("pending_email", None)
            flash("Email vérifié avec succès ! Vous pouvez vous connecter.", "success")
            return redirect(url_for("auth.login"))

        elif purpose == "admin_registration":
            session.pop("pending_email", None)
            session["admin_verified"] = True
            flash("Email vérifié. Créez votre compte administrateur.", "success")
            return redirect(url_for("admin_hidden.admin_create_account"))

        elif purpose == "password_reset":
            session["reset_verified"] = True
            flash("Code vérifié. Définissez votre nouveau mot de passe.", "success")
            return redirect(url_for("auth.reset_password"))

    return render_template("auth/verify_email.html", purpose=purpose, email=email, form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Connexion réussie.", "success")
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))

        flash("Email ou mot de passe incorrect.", "error")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/admin-verify", methods=["GET", "POST"])
@login_required
def admin_verify():
    if not session.get("admin_pending"):
        return redirect(url_for("main.index"))

    form = AdminVerifyForm()

    if form.validate_on_submit():
        from flask import current_app
        code = form.admin_code.data.strip()
        if code == current_app.config.get("ADMIN_REG_CODE", "12345"):
            session.pop("admin_pending", None)
            session["admin_authenticated"] = True
            flash("Accès administrateur confirmé.", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Code administrateur incorrect.", "error")

    return render_template("auth/admin_verify.html", form=form)


@admin_hidden_bp.route("/admin-register", methods=["GET", "POST"])
def admin_register():
    form = AdminRegisterForm()

    if form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        if User.query.filter_by(email=email).first():
            flash("Un compte existe déjà avec cet email.", "error")
            return redirect(url_for("admin_hidden.admin_register"))

        user = User(name=name, email=email, role="admin", is_verified=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Compte administrateur créé avec succès ! Connectez-vous.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/admin_register.html", form=form)


@admin_hidden_bp.route("/admin-create-account", methods=["GET", "POST"])
def admin_create_account():
    if not session.get("admin_verified"):
        flash("Veuillez d'abord vérifier votre email.", "error")
        return redirect(url_for("admin_hidden.admin_register"))

    if request.method == "POST":
        session.pop("admin_verified", None)
        flash("Compte administrateur créé avec succès ! Connectez-vous.", "success")
        return redirect(url_for("auth.login"))

    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            generate_and_send_code(email, "password_reset")
            session["pending_email"] = email
            flash("Un code de réinitialisation a été envoyé à votre email.", "success")
            return redirect(url_for("auth.verify_email", purpose="password_reset"))
        flash("Aucun compte trouvé avec cet email.", "error")

    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if not session.get("reset_verified"):
        flash("Veuillez d'abord vérifier votre code.", "error")
        return redirect(url_for("auth.forgot_password"))

    email = session.get("pending_email")
    form = ResetPasswordForm()

    if form.validate_on_submit():
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()

        session.pop("reset_verified", None)
        session.pop("pending_email", None)
        flash("Mot de passe réinitialisé avec succès ! Connectez-vous.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    session.pop("admin_authenticated", None)
    session.pop("admin_pending", None)
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for("main.index"))
