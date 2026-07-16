from functools import wraps
from flask import flash, redirect, url_for
from flask_login import login_required, current_user


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != "admin":
            flash("Accès réservé aux administrateurs.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def editor_or_admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role not in ("admin", "editor"):
            flash("Accès réservé aux administrateurs et éditeurs.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
