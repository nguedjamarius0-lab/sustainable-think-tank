from flask import Blueprint, render_template, request, abort
from app import cache
from app.models import Publication

publications_bp = Blueprint("publications", __name__)

CATEGORIES = {
    "rapport": "Rapports",
    "policy_brief": "Policy Briefs",
    "note_analyse": "Notes d'analyse",
    "tribune": "Tribunes",
}

THEMES = {
    "economie": "Économie",
    "politique_publique": "Politique publique",
    "finance": "Finance",
    "numerique": "Numérique",
    "affaires": "Affaires",
}


@publications_bp.route("/")
@cache.cached(timeout=120, query_string=True)
def list_publications():
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category", "")
    theme = request.args.get("theme", "")
    search = request.args.get("search", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")

    query = Publication.query

    if category:
        query = query.filter_by(category=category)
    if theme:
        query = query.filter_by(theme=theme)
    if search:
        query = query.filter(
            (Publication.title_fr.ilike(f"%{search}%")) |
            (Publication.title_en.ilike(f"%{search}%")) |
            (Publication.author_name.ilike(f"%{search}%")) |
            (Publication.summary_fr.ilike(f"%{search}%"))
        )
    if date_from:
        from datetime import datetime
        try:
            dt = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Publication.published_at >= dt)
        except ValueError:
            pass
    if date_to:
        from datetime import datetime
        try:
            dt = datetime.strptime(date_to, "%Y-%m-%d")
            query = query.filter(Publication.published_at <= dt)
        except ValueError:
            pass

    publications = query.order_by(Publication.published_at.desc()).paginate(
        page=page, per_page=9, error_out=False
    )

    return render_template(
        "publications/list.html",
        publications=publications,
        categories=CATEGORIES,
        themes=THEMES,
        current_category=category,
        current_theme=theme,
        current_search=search,
        current_date_from=date_from,
        current_date_to=date_to,
    )


@publications_bp.route("/<slug>")
def detail(slug):
    publication = Publication.query.filter_by(slug=slug).first_or_404()
    related = Publication.query.filter(
        Publication.theme == publication.theme,
        Publication.id != publication.id
    ).limit(3).all()

    return render_template(
        "publications/detail.html",
        publication=publication,
        related=related,
    )
