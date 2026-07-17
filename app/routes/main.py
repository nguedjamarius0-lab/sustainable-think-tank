from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect
from app.models import Publication, Event, NewsItem, TeamMember
from app.forms import NewsletterForm

main_bp = Blueprint("main", __name__)


@main_bp.app_context_processor
def inject_globals():
    return {
        "donation_url": current_app.config.get("DONATION_URL", "#"),
        "newsletter_form": NewsletterForm(),
    }


@main_bp.route("/")
def index():
    latest_publications = Publication.query.filter_by(is_featured=True).order_by(
        Publication.published_at.desc()
    ).limit(3).all()

    if not latest_publications:
        latest_publications = Publication.query.order_by(
            Publication.published_at.desc()
        ).limit(3).all()

    upcoming_event = Event.query.filter(
        Event.start_date >= datetime.now()
    ).order_by(Event.start_date.asc()).first()

    latest_news = NewsItem.query.filter_by(is_published=True).order_by(
        NewsItem.created_at.desc()
    ).limit(5).all()

    directors = TeamMember.query.filter_by(
        member_type="permanent", is_published=True
    ).order_by(TeamMember.display_order.asc()).limit(4).all()

    return render_template(
        "home/index.html",
        publications=latest_publications,
        upcoming_event=upcoming_event,
        news=latest_news,
        directors=directors,
    )


@main_bp.route("/set-language/<lang>")
def set_language(lang):
    if lang in ("fr", "en"):
        session["lang"] = lang
    return redirect(request.referrer or "/")
