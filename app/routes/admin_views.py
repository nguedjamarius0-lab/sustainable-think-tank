import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import (
    User, Publication, Event, TeamMember, Partner,
    PressMention, NewsletterSubscriber, ContactMessage,
    ActivityReport, NewsItem, JoinApplication,
    Video, ResearchTeam, TeamMemberDraft,
)
from app.forms import (
    UserRoleForm, TeamValidationForm,
    PublicationForm, EventForm, TeamMemberAdminForm,
    PartnerForm, PressMentionForm, NewsItemForm, ActivityReportForm,
)
from app.routes.decorators import admin_required, editor_or_admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ALLOWED_IMAGE = {"jpg", "jpeg", "png", "webp"}
ALLOWED_DOC = {"pdf", "pptx", "ppt"}


def _save_upload(file_field, subfolder="uploads"):
    if not file_field or not file_field.data:
        return None
    f = file_field.data
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.config.get("UPLOAD_FOLDER", "app/static/uploads"), subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    f.save(os.path.join(upload_dir, filename))
    return f"{subfolder}/{filename}"


def _delete_file(filepath):
    if not filepath:
        return
    full = os.path.join(current_app.config.get("UPLOAD_FOLDER", "app/static/uploads"), filepath)
    if os.path.exists(full):
        os.remove(full)


# ─── Dashboard ──────────────────────────────────────────────────────

@admin_bp.route("/")
@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    stats = {
        "users": User.query.count(),
        "publications": Publication.query.count(),
        "events": Event.query.count(),
        "messages": ContactMessage.query.filter_by(is_read=False).count(),
        "newsletter": NewsletterSubscriber.query.filter_by(is_active=True).count(),
        "applications": JoinApplication.query.filter_by(is_processed=False).count(),
        "videos": Video.query.count(),
        "pending_teams": ResearchTeam.query.filter_by(status="pending").count(),
        "partners": Partner.query.count(),
        "press": PressMention.query.count(),
        "news": NewsItem.query.count(),
        "reports": ActivityReport.query.count(),
    }
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    pending_teams = ResearchTeam.query.filter_by(status="pending").order_by(ResearchTeam.created_at.desc()).limit(5).all()
    pending_applications = JoinApplication.query.filter_by(is_processed=False).order_by(JoinApplication.created_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent_users=recent_users, recent_messages=recent_messages, pending_teams=pending_teams, pending_applications=pending_applications)


# ─── Users ──────────────────────────────────────────────────────────

@admin_bp.route("/utilisateurs")
@admin_required
def users_list():
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    query = User.query
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template("admin/users_list.html", users=users, search=search)


@admin_bp.route("/utilisateurs/<int:user_id>")
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    messages = ContactMessage.query.filter_by(email=user.email).order_by(ContactMessage.created_at.desc()).all()
    applications = JoinApplication.query.filter_by(email=user.email).order_by(JoinApplication.created_at.desc()).all()
    newsletter = NewsletterSubscriber.query.filter_by(email=user.email).first()
    role_form = UserRoleForm(obj=user)
    return render_template("admin/user_detail.html", user=user, messages=messages, applications=applications, newsletter=newsletter, role_form=role_form)


@admin_bp.route("/utilisateurs/<int:user_id>/delete", methods=["POST"])
@admin_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Vous ne pouvez pas supprimer votre propre compte.", "error")
        return redirect(url_for("admin.users_list"))
    db.session.delete(user)
    db.session.commit()
    flash("Utilisateur supprimé.", "success")
    return redirect(url_for("admin.users_list"))


@admin_bp.route("/utilisateurs/<int:user_id>/role", methods=["POST"])
@admin_required
def user_role(user_id):
    user = User.query.get_or_404(user_id)
    form = UserRoleForm()
    if form.validate_on_submit():
        new_role = form.role.data
        if new_role in ("user", "editor", "admin"):
            user.role = new_role
            db.session.commit()
            flash(f"Rôle de {user.name} mis à jour : {new_role}", "success")
        else:
            flash("Rôle invalide.", "error")
    return redirect(url_for("admin.user_detail", user_id=user.id))


# ─── Publications CRUD ──────────────────────────────────────────────

@admin_bp.route("/publications")
@admin_required
def publications():
    pubs = Publication.query.order_by(Publication.created_at.desc()).all()
    return render_template("admin/publications.html", publications=pubs)


@admin_bp.route("/publications/ajouter", methods=["GET", "POST"])
@editor_or_admin_required
def publication_create():
    form = PublicationForm()
    if form.validate_on_submit():
        slug = Publication.generate_slug(form.title_fr.data)
        existing = Publication.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        pub = Publication(
            title_fr=form.title_fr.data.strip(),
            title_en=form.title_en.data.strip(),
            slug=slug,
            category=form.category.data,
            theme=form.theme.data,
            author_name=form.author_name.data.strip(),
            author_bio=form.author_bio.data or "",
            summary_fr=form.summary_fr.data.strip(),
            summary_en=form.summary_en.data.strip(),
            executive_summary_fr=form.executive_summary_fr.data or "",
            executive_summary_en=form.executive_summary_en.data or "",
            citation_apa=form.citation_apa.data or "",
            citation_mla=form.citation_mla.data or "",
            is_featured=form.is_featured.data,
        )
        pub.pdf_file = _save_upload(form.pdf_file, "publications/pdf")
        pub.slides_file = _save_upload(form.slides_file, "publications/slides")
        pub.cover_image = _save_upload(form.cover_image, "publications/covers")
        db.session.add(pub)
        db.session.commit()
        flash("Publication créée avec succès.", "success")
        return redirect(url_for("admin.publications"))
    return render_template("admin/publication_form.html", form=form, title="Ajouter une publication")


@admin_bp.route("/publications/<int:pub_id>/modifier", methods=["GET", "POST"])
@editor_or_admin_required
def publication_edit(pub_id):
    pub = Publication.query.get_or_404(pub_id)
    form = PublicationForm(obj=pub)
    if form.validate_on_submit():
        pub.title_fr = form.title_fr.data.strip()
        pub.title_en = form.title_en.data.strip()
        pub.category = form.category.data
        pub.theme = form.theme.data
        pub.author_name = form.author_name.data.strip()
        pub.author_bio = form.author_bio.data or ""
        pub.summary_fr = form.summary_fr.data.strip()
        pub.summary_en = form.summary_en.data.strip()
        pub.executive_summary_fr = form.executive_summary_fr.data or ""
        pub.executive_summary_en = form.executive_summary_en.data or ""
        pub.citation_apa = form.citation_apa.data or ""
        pub.citation_mla = form.citation_mla.data or ""
        pub.is_featured = form.is_featured.data
        if form.pdf_file.data:
            _delete_file(pub.pdf_file)
            pub.pdf_file = _save_upload(form.pdf_file, "publications/pdf")
        if form.slides_file.data:
            _delete_file(pub.slides_file)
            pub.slides_file = _save_upload(form.slides_file, "publications/slides")
        if form.cover_image.data:
            _delete_file(pub.cover_image)
            pub.cover_image = _save_upload(form.cover_image, "publications/covers")
        db.session.commit()
        flash("Publication mise à jour.", "success")
        return redirect(url_for("admin.publications"))
    return render_template("admin/publication_form.html", form=form, title="Modifier la publication", pub=pub)


@admin_bp.route("/publications/<int:pub_id>/supprimer", methods=["POST"])
@editor_or_admin_required
def publication_delete(pub_id):
    pub = Publication.query.get_or_404(pub_id)
    _delete_file(pub.pdf_file)
    _delete_file(pub.slides_file)
    _delete_file(pub.cover_image)
    db.session.delete(pub)
    db.session.commit()
    flash("Publication supprimée.", "success")
    return redirect(url_for("admin.publications"))


# ─── Events CRUD ────────────────────────────────────────────────────

@admin_bp.route("/evenements")
@admin_required
def events():
    evts = Event.query.order_by(Event.created_at.desc()).all()
    return render_template("admin/events.html", events=evts)


@admin_bp.route("/evenements/ajouter", methods=["GET", "POST"])
@editor_or_admin_required
def event_create():
    form = EventForm()
    if form.validate_on_submit():
        slug = Publication.generate_slug(form.title_fr.data)
        existing = Event.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        evt = Event(
            title_fr=form.title_fr.data.strip(),
            title_en=form.title_en.data.strip(),
            slug=slug,
            event_type=form.event_type.data,
            description_fr=form.description_fr.data.strip(),
            description_en=form.description_en.data.strip(),
            location=form.location.data or "",
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_published=form.is_published.data,
        )
        evt.cover_image = _save_upload(form.cover_image, "events/covers")
        evt.report_file = _save_upload(form.report_file, "events/reports")
        evt.presentation_file = _save_upload(form.presentation_file, "events/presentations")
        db.session.add(evt)
        db.session.commit()
        flash("Événement créé avec succès.", "success")
        return redirect(url_for("admin.events"))
    return render_template("admin/event_form.html", form=form, title="Ajouter un événement")


@admin_bp.route("/evenements/<int:event_id>/modifier", methods=["GET", "POST"])
@editor_or_admin_required
def event_edit(event_id):
    evt = Event.query.get_or_404(event_id)
    form = EventForm(obj=evt)
    if form.validate_on_submit():
        evt.title_fr = form.title_fr.data.strip()
        evt.title_en = form.title_en.data.strip()
        evt.event_type = form.event_type.data
        evt.description_fr = form.description_fr.data.strip()
        evt.description_en = form.description_en.data.strip()
        evt.location = form.location.data or ""
        evt.start_date = form.start_date.data
        evt.end_date = form.end_date.data
        evt.is_published = form.is_published.data
        if form.cover_image.data:
            _delete_file(evt.cover_image)
            evt.cover_image = _save_upload(form.cover_image, "events/covers")
        if form.report_file.data:
            _delete_file(evt.report_file)
            evt.report_file = _save_upload(form.report_file, "events/reports")
        if form.presentation_file.data:
            _delete_file(evt.presentation_file)
            evt.presentation_file = _save_upload(form.presentation_file, "events/presentations")
        db.session.commit()
        flash("Événement mis à jour.", "success")
        return redirect(url_for("admin.events"))
    return render_template("admin/event_form.html", form=form, title="Modifier l'événement", event=evt)


@admin_bp.route("/evenements/<int:event_id>/supprimer", methods=["POST"])
@editor_or_admin_required
def event_delete(event_id):
    evt = Event.query.get_or_404(event_id)
    _delete_file(evt.cover_image)
    _delete_file(evt.report_file)
    _delete_file(evt.presentation_file)
    db.session.delete(evt)
    db.session.commit()
    flash("Événement supprimé.", "success")
    return redirect(url_for("admin.events"))


# ─── Team Members CRUD ──────────────────────────────────────────────

@admin_bp.route("/equipe")
@admin_required
def team():
    members = TeamMember.query.order_by(TeamMember.display_order.asc()).all()
    return render_template("admin/team.html", members=members)


@admin_bp.route("/equipe/ajouter", methods=["GET", "POST"])
@admin_required
def team_create():
    form = TeamMemberAdminForm()
    if form.validate_on_submit():
        member = TeamMember(
            name=form.name.data.strip(),
            role_fr=form.role_fr.data.strip(),
            role_en=form.role_en.data.strip(),
            bio_fr=form.bio_fr.data or "",
            bio_en=form.bio_en.data or "",
            email=form.email.data or "",
            linkedin_url=form.linkedin_url.data or "",
            member_type=form.member_type.data,
            display_order=form.display_order.data or 0,
            is_published=form.is_published.data,
        )
        member.photo = _save_upload(form.photo, "team")
        db.session.add(member)
        db.session.commit()
        flash("Membre ajouté avec succès.", "success")
        return redirect(url_for("admin.team"))
    return render_template("admin/team_form.html", form=form, title="Ajouter un membre")


@admin_bp.route("/equipe/<int:member_id>/modifier", methods=["GET", "POST"])
@admin_required
def team_edit(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = TeamMemberAdminForm(obj=member)
    if form.validate_on_submit():
        member.name = form.name.data.strip()
        member.role_fr = form.role_fr.data.strip()
        member.role_en = form.role_en.data.strip()
        member.bio_fr = form.bio_fr.data or ""
        member.bio_en = form.bio_en.data or ""
        member.email = form.email.data or ""
        member.linkedin_url = form.linkedin_url.data or ""
        member.member_type = form.member_type.data
        member.display_order = form.display_order.data or 0
        member.is_published = form.is_published.data
        if form.photo.data:
            _delete_file(member.photo)
            member.photo = _save_upload(form.photo, "team")
        db.session.commit()
        flash("Membre mis à jour.", "success")
        return redirect(url_for("admin.team"))
    return render_template("admin/team_form.html", form=form, title="Modifier le membre", member=member)


@admin_bp.route("/equipe/<int:member_id>/supprimer", methods=["POST"])
@admin_required
def team_delete(member_id):
    member = TeamMember.query.get_or_404(member_id)
    _delete_file(member.photo)
    db.session.delete(member)
    db.session.commit()
    flash("Membre supprimé.", "success")
    return redirect(url_for("admin.team"))


# ─── Partners CRUD ──────────────────────────────────────────────────

@admin_bp.route("/partenaires")
@admin_required
def partners():
    items = Partner.query.order_by(Partner.display_order.asc()).all()
    return render_template("admin/partners.html", partners=items)


@admin_bp.route("/partenaires/ajouter", methods=["GET", "POST"])
@admin_required
def partner_create():
    form = PartnerForm()
    if form.validate_on_submit():
        partner = Partner(
            name=form.name.data.strip(),
            website_url=form.website_url.data or "",
            partner_type=form.partner_type.data,
            display_order=form.display_order.data or 0,
        )
        partner.logo = _save_upload(form.logo, "partners")
        db.session.add(partner)
        db.session.commit()
        flash("Partenaire ajouté.", "success")
        return redirect(url_for("admin.partners"))
    return render_template("admin/partner_form.html", form=form, title="Ajouter un partenaire")


@admin_bp.route("/partenaires/<int:partner_id>/modifier", methods=["GET", "POST"])
@admin_required
def partner_edit(partner_id):
    partner = Partner.query.get_or_404(partner_id)
    form = PartnerForm(obj=partner)
    if form.validate_on_submit():
        partner.name = form.name.data.strip()
        partner.website_url = form.website_url.data or ""
        partner.partner_type = form.partner_type.data
        partner.display_order = form.display_order.data or 0
        if form.logo.data:
            _delete_file(partner.logo)
            partner.logo = _save_upload(form.logo, "partners")
        db.session.commit()
        flash("Partenaire mis à jour.", "success")
        return redirect(url_for("admin.partners"))
    return render_template("admin/partner_form.html", form=form, title="Modifier le partenaire", partner=partner)


@admin_bp.route("/partenaires/<int:partner_id>/supprimer", methods=["POST"])
@admin_required
def partner_delete(partner_id):
    partner = Partner.query.get_or_404(partner_id)
    _delete_file(partner.logo)
    db.session.delete(partner)
    db.session.commit()
    flash("Partenaire supprimé.", "success")
    return redirect(url_for("admin.partners"))


# ─── Press Mentions CRUD ───────────────────────────────────────────

@admin_bp.route("/presse")
@admin_required
def press():
    items = PressMention.query.order_by(PressMention.created_at.desc()).all()
    return render_template("admin/press.html", mentions=items)


@admin_bp.route("/presse/ajouter", methods=["GET", "POST"])
@admin_required
def press_create():
    form = PressMentionForm()
    if form.validate_on_submit():
        mention = PressMention(
            title=form.title.data.strip(),
            source_name=form.source_name.data.strip(),
            source_url=form.source_url.data.strip(),
            publication_date=form.publication_date.data,
            description=form.description.data or "",
        )
        db.session.add(mention)
        db.session.commit()
        flash("Mention presse ajoutée.", "success")
        return redirect(url_for("admin.press"))
    return render_template("admin/press_form.html", form=form, title="Ajouter une mention presse")


@admin_bp.route("/presse/<int:mention_id>/modifier", methods=["GET", "POST"])
@admin_required
def press_edit(mention_id):
    mention = PressMention.query.get_or_404(mention_id)
    form = PressMentionForm(obj=mention)
    if form.validate_on_submit():
        mention.title = form.title.data.strip()
        mention.source_name = form.source_name.data.strip()
        mention.source_url = form.source_url.data.strip()
        mention.publication_date = form.publication_date.data
        mention.description = form.description.data or ""
        db.session.commit()
        flash("Mention presse mise à jour.", "success")
        return redirect(url_for("admin.press"))
    return render_template("admin/press_form.html", form=form, title="Modifier la mention", mention=mention)


@admin_bp.route("/presse/<int:mention_id>/supprimer", methods=["POST"])
@admin_required
def press_delete(mention_id):
    mention = PressMention.query.get_or_404(mention_id)
    db.session.delete(mention)
    db.session.commit()
    flash("Mention presse supprimée.", "success")
    return redirect(url_for("admin.press"))


# ─── News CRUD ──────────────────────────────────────────────────────

@admin_bp.route("/actualites")
@admin_required
def news():
    items = NewsItem.query.order_by(NewsItem.created_at.desc()).all()
    return render_template("admin/news.html", news=items)


@admin_bp.route("/actualites/ajouter", methods=["GET", "POST"])
@admin_required
def news_create():
    form = NewsItemForm()
    if form.validate_on_submit():
        item = NewsItem(
            title_fr=form.title_fr.data.strip(),
            title_en=form.title_en.data.strip(),
            content_fr=form.content_fr.data.strip(),
            content_en=form.content_en.data.strip(),
            source_url=form.source_url.data or "",
            is_published=form.is_published.data,
        )
        db.session.add(item)
        db.session.commit()
        flash("Actualité créée.", "success")
        return redirect(url_for("admin.news"))
    return render_template("admin/news_form.html", form=form, title="Ajouter une actualité")


@admin_bp.route("/actualites/<int:news_id>/modifier", methods=["GET", "POST"])
@admin_required
def news_edit(news_id):
    item = NewsItem.query.get_or_404(news_id)
    form = NewsItemForm(obj=item)
    if form.validate_on_submit():
        item.title_fr = form.title_fr.data.strip()
        item.title_en = form.title_en.data.strip()
        item.content_fr = form.content_fr.data.strip()
        item.content_en = form.content_en.data.strip()
        item.source_url = form.source_url.data or ""
        item.is_published = form.is_published.data
        db.session.commit()
        flash("Actualité mise à jour.", "success")
        return redirect(url_for("admin.news"))
    return render_template("admin/news_form.html", form=form, title="Modifier l'actualité", news=item)


@admin_bp.route("/actualites/<int:news_id>/supprimer", methods=["POST"])
@admin_required
def news_delete(news_id):
    item = NewsItem.query.get_or_404(news_id)
    db.session.delete(item)
    db.session.commit()
    flash("Actualité supprimée.", "success")
    return redirect(url_for("admin.news"))


# ─── Activity Reports CRUD ─────────────────────────────────────────

@admin_bp.route("/rapports")
@admin_required
def reports():
    items = ActivityReport.query.order_by(ActivityReport.year.desc()).all()
    return render_template("admin/reports.html", reports=items)


@admin_bp.route("/rapports/ajouter", methods=["GET", "POST"])
@admin_required
def report_create():
    form = ActivityReportForm()
    if form.validate_on_submit():
        report = ActivityReport(
            year=form.year.data,
            title_fr=form.title_fr.data.strip(),
            title_en=form.title_en.data.strip(),
        )
        report.pdf_file = _save_upload(form.pdf_file, "reports")
        db.session.add(report)
        db.session.commit()
        flash("Rapport ajouté.", "success")
        return redirect(url_for("admin.reports"))
    return render_template("admin/report_form.html", form=form, title="Ajouter un rapport")


@admin_bp.route("/rapports/<int:report_id>/modifier", methods=["GET", "POST"])
@admin_required
def report_edit(report_id):
    report = ActivityReport.query.get_or_404(report_id)
    form = ActivityReportForm(obj=report)
    if form.validate_on_submit():
        report.year = form.year.data
        report.title_fr = form.title_fr.data.strip()
        report.title_en = form.title_en.data.strip()
        if form.pdf_file.data:
            _delete_file(report.pdf_file)
            report.pdf_file = _save_upload(form.pdf_file, "reports")
        db.session.commit()
        flash("Rapport mis à jour.", "success")
        return redirect(url_for("admin.reports"))
    return render_template("admin/report_form.html", form=form, title="Modifier le rapport", report=report)


@admin_bp.route("/rapports/<int:report_id>/supprimer", methods=["POST"])
@admin_required
def report_delete(report_id):
    report = ActivityReport.query.get_or_404(report_id)
    _delete_file(report.pdf_file)
    db.session.delete(report)
    db.session.commit()
    flash("Rapport supprimé.", "success")
    return redirect(url_for("admin.reports"))


# ─── Messages ───────────────────────────────────────────────────────

@admin_bp.route("/messages")
@admin_required
def messages():
    msgs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin/messages.html", messages=msgs)


@admin_bp.route("/messages/<int:msg_id>/read", methods=["POST"])
@admin_required
def mark_read(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    flash("Message marqué comme lu.", "success")
    return redirect(url_for("admin.messages"))


@admin_bp.route("/messages/<int:msg_id>/supprimer", methods=["POST"])
@admin_required
def message_delete(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash("Message supprimé.", "success")
    return redirect(url_for("admin.messages"))


# ─── Applications ───────────────────────────────────────────────────

@admin_bp.route("/candidatures")
@admin_required
def applications():
    apps = JoinApplication.query.order_by(JoinApplication.created_at.desc()).all()
    return render_template("admin/applications.html", applications=apps)


@admin_bp.route("/candidatures/<int:app_id>/traiter", methods=["POST"])
@admin_required
def application_process(app_id):
    app = JoinApplication.query.get_or_404(app_id)
    app.is_processed = True
    db.session.commit()
    flash("Candidature marquée comme traitée.", "success")
    return redirect(url_for("admin.applications"))


# ─── Videos ─────────────────────────────────────────────────────────

@admin_bp.route("/videos")
@editor_or_admin_required
def videos():
    vids = Video.query.order_by(Video.created_at.desc()).all()
    return render_template("admin/videos.html", videos=vids)


@admin_bp.route("/videos/<int:video_id>/modifier", methods=["GET", "POST"])
@editor_or_admin_required
def video_edit(video_id):
    video = Video.query.get_or_404(video_id)
    from app.forms import VideoForm
    form = VideoForm(obj=video)
    if form.validate_on_submit():
        video.title = form.title.data.strip()
        video.description = form.description.data or ""
        video.video_url = form.video_url.data.strip()
        video.thumbnail_url = form.thumbnail_url.data or ""
        db.session.commit()
        flash("Vidéo mise à jour.", "success")
        return redirect(url_for("admin.videos"))
    return render_template("admin/video_form.html", form=form, title="Modifier la vidéo", video=video)


@admin_bp.route("/videos/<int:video_id>/delete", methods=["POST"])
@editor_or_admin_required
def video_delete(video_id):
    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    flash("Vidéo supprimée.", "success")
    return redirect(url_for("admin.videos"))


# ─── Research Teams ─────────────────────────────────────────────────

@admin_bp.route("/equipes-valider")
@admin_required
def pending_teams():
    teams = ResearchTeam.query.filter_by(status="pending").order_by(ResearchTeam.created_at.desc()).all()
    return render_template("admin/teams.html", teams=teams, status="pending")


@admin_bp.route("/equipes-valider/<int:team_id>", methods=["GET"])
@admin_required
def team_detail(team_id):
    team = ResearchTeam.query.get_or_404(team_id)
    members = TeamMemberDraft.query.filter_by(team_id=team_id).all()
    return render_template("admin/team_detail.html", team=team, members=members)


@admin_bp.route("/equipes-valider/<int:team_id>/<action>", methods=["POST"])
@admin_required
def validate_team(team_id, action):
    team = ResearchTeam.query.get_or_404(team_id)
    form = TeamValidationForm()
    if form.validate_on_submit():
        if action == "validate":
            team.status = "validated"
            team.validated_by = current_user.id
            from datetime import datetime, timezone
            team.validated_at = datetime.now(timezone.utc)
            flash(f"Équipe '{team.name}' validée.", "success")
        elif action == "reject":
            team.status = "rejected"
            flash(f"Équipe '{team.name}' rejetée.", "info")
        db.session.commit()
    return redirect(url_for("admin.pending_teams"))


@admin_bp.route("/equipes/<int:team_id>/supprimer", methods=["POST"])
@admin_required
def research_team_delete(team_id):
    team = ResearchTeam.query.get_or_404(team_id)
    TeamMemberDraft.query.filter_by(team_id=team_id).delete()
    db.session.delete(team)
    db.session.commit()
    flash("Équipe supprimée.", "success")
    return redirect(url_for("admin.pending_teams"))
