from flask import Blueprint, render_template
from app.models import PressMention

media_bp = Blueprint("media", __name__)


@media_bp.route("/")
def index():
    press_mentions = PressMention.query.order_by(
        PressMention.publication_date.desc()
    ).all()

    return render_template(
        "media/index.html",
        press_mentions=press_mentions,
    )
