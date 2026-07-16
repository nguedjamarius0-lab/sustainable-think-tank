from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Video, VideoLike, VideoComment, User
from app.forms import VideoForm, VideoCommentForm
from app.routes.decorators import editor_or_admin_required

reseau_bp = Blueprint("reseau", __name__)


@reseau_bp.route("/")
def index():
    videos = Video.query.filter_by(is_published=True).order_by(Video.created_at.desc()).all()
    return render_template("reseau/index.html", videos=videos)


@reseau_bp.route("/profil/<int:user_id>")
def profile(user_id):
    user = User.query.get_or_404(user_id)
    videos = Video.query.filter_by(created_by=user_id, is_published=True).order_by(
        Video.created_at.desc()
    ).all()
    total_likes = sum(v.get_like_count() for v in videos)
    total_views = sum(v.views for v in videos)
    return render_template(
        "reseau/profile.html",
        user=user,
        videos=videos,
        total_likes=total_likes,
        total_views=total_views,
    )


@reseau_bp.route("/publish", methods=["GET", "POST"])
@editor_or_admin_required
def publish():
    form = VideoForm()
    if form.validate_on_submit():
        video = Video(
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else "",
            video_url=form.video_url.data.strip(),
            thumbnail_url=form.thumbnail_url.data.strip() if form.thumbnail_url.data else "",
            created_by=current_user.id,
        )
        db.session.add(video)
        db.session.commit()
        flash("Vidéo publiée avec succès !", "success")
        return redirect(url_for("reseau.index"))
    return render_template("reseau/publish.html", form=form)


@reseau_bp.route("/<int:video_id>/edit", methods=["GET", "POST"])
@editor_or_admin_required
def edit(video_id):
    video = Video.query.get_or_404(video_id)
    form = VideoForm(obj=video)
    if form.validate_on_submit():
        video.title = form.title.data.strip()
        video.description = form.description.data or ""
        video.video_url = form.video_url.data.strip()
        video.thumbnail_url = form.thumbnail_url.data or ""
        db.session.commit()
        flash("Vidéo mise à jour.", "success")
        return redirect(url_for("reseau.detail", video_id=video.id))
    return render_template("reseau/publish.html", form=form, editing=True)


@reseau_bp.route("/<int:video_id>")
def detail(video_id):
    video = Video.query.get_or_404(video_id)
    video.views += 1
    db.session.commit()
    comments = VideoComment.query.filter_by(video_id=video_id, parent_id=None).order_by(
        VideoComment.created_at.desc()
    ).all()
    form = VideoCommentForm()
    return render_template("reseau/video.html", video=video, comments=comments, form=form)


@reseau_bp.route("/<int:video_id>/like", methods=["POST"])
@login_required
def like(video_id):
    video = Video.query.get_or_404(video_id)
    existing = VideoLike.query.filter_by(video_id=video_id, user_id=current_user.id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(VideoLike(video_id=video_id, user_id=current_user.id))
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"liked": not existing, "count": video.get_like_count()})
    return redirect(url_for("reseau.detail", video_id=video_id))


@reseau_bp.route("/<int:video_id>/comment", methods=["POST"])
@login_required
def comment(video_id):
    Video.query.get_or_404(video_id)
    form = VideoCommentForm()

    if form.validate_on_submit():
        comment = VideoComment(
            video_id=video_id,
            user_id=current_user.id,
            content=form.content.data.strip(),
        )
        db.session.add(comment)
        db.session.commit()
        flash("Commentaire ajouté.", "success")
    else:
        flash("Le commentaire ne peut pas être vide.", "error")

    return redirect(url_for("reseau.detail", video_id=video_id))


@reseau_bp.route("/comment/<int:comment_id>/reply", methods=["POST"])
@login_required
def reply(comment_id):
    parent = VideoComment.query.get_or_404(comment_id)
    form = VideoCommentForm()

    if form.validate_on_submit():
        reply = VideoComment(
            video_id=parent.video_id,
            user_id=current_user.id,
            parent_id=comment_id,
            content=form.content.data.strip(),
        )
        db.session.add(reply)
        db.session.commit()
        flash("Réponse ajoutée.", "success")
    else:
        flash("La réponse ne peut pas être vide.", "error")

    return redirect(url_for("reseau.detail", video_id=parent.video_id))
