from flask import Blueprint, render_template, request
from app import cache
from app.models import Event
from datetime import datetime, timezone

events_bp = Blueprint("events", __name__)


@events_bp.route("/")
@cache.cached(timeout=120, query_string=True)
def list_events():
    now = datetime.now(timezone.utc)
    tab = request.args.get("tab", "upcoming")

    if tab == "past":
        events = Event.query.filter(
            Event.start_date < now, Event.is_published == True
        ).order_by(Event.start_date.desc()).all()
    else:
        events = Event.query.filter(
            Event.start_date >= now, Event.is_published == True
        ).order_by(Event.start_date.asc()).all()

    return render_template(
        "events/list.html",
        events=events,
        current_tab=tab,
    )


@events_bp.route("/<slug>")
def detail(slug):
    event = Event.query.filter_by(slug=slug).first_or_404()
    return render_template("events/detail.html", event=event)
