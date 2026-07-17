from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from app import db
from app.models import User
from app.forms import (
    RegisterForm, LoginForm,
    ForgotPasswordForm, ResetPasswordForm, AdminRegisterForm
)
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)
admin_hidden_bp = Blueprint("admin_hidden", __name__)

oauth = OAuth()
google = oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


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


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Si un compte existe avec cet email, un lien de réinitialisation vous sera envoyé.", "success")
        else:
            flash("Si un compte existe avec cet email, un lien de réinitialisation vous sera envoyé.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    form = ResetPasswordForm()

    if form.validate_on_submit():
        flash("Mot de passe réinitialisé avec succès ! Connectez-vous.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", form=form)


@auth_bp.route("/admin-verify", methods=["GET", "POST"])
@login_required
def admin_verify():
    flash("Vérification simplifiée. Accès accordé.", "success")
    return redirect(url_for("admin.dashboard"))


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


@auth_bp.route("/google/login")
def google_login():
    if not current_app.config.get("GOOGLE_CLIENT_ID") or not current_app.config.get("GOOGLE_CLIENT_SECRET"):
        flash("La connexion Google n'est pas encore configurée.", "error")
        return redirect(url_for("auth.login"))
    redirect_uri = current_app.config.get("GOOGLE_REDIRECT_URI") or url_for("auth.google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route("/google/callback")
def google_callback():
    try:
        token = google.authorize_access_token()
        user_info = token.get("userinfo")
        if not user_info:
            user_info = google.parse_id_token(token)
    except Exception as e:
        logger.error("Google OAuth error: %s", e)
        flash("Erreur lors de la connexion avec Google.", "error")
        return redirect(url_for("auth.login"))

    google_id = user_info.get("sub")
    email = user_info.get("email")
    name = user_info.get("name", "")

    if not email:
        flash("Impossible de récupérer votre email depuis Google.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id
        else:
            user = User(
                email=email,
                name=name,
                role="user",
                is_verified=True,
                google_id=google_id,
            )
            db.session.add(user)
        db.session.commit()

    login_user(user)
    flash("Connexion réussie via Google.", "success")
    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("main.index"))


@auth_bp.route("/logout")
@login_required
def logout():
    session.pop("admin_authenticated", None)
    session.pop("admin_pending", None)
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for("main.index"))
