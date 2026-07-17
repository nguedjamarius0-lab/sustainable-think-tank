from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default="user")  # user, admin, editor
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    google_id = db.Column(db.String(100), nullable=True, unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can_publish(self):
        return self.role in ("admin", "editor")


class Publication(db.Model):
    __tablename__ = "publications"
    id = db.Column(db.Integer, primary_key=True)
    title_fr = db.Column(db.String(300), nullable=False)
    title_en = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)
    theme = db.Column(db.String(100), nullable=False)
    author_name = db.Column(db.String(150), nullable=False)
    author_bio = db.Column(db.Text)
    summary_fr = db.Column(db.Text, nullable=False)
    summary_en = db.Column(db.Text, nullable=False)
    executive_summary_fr = db.Column(db.Text)
    executive_summary_en = db.Column(db.Text)
    pdf_file = db.Column(db.String(300))
    slides_file = db.Column(db.String(300))
    cover_image = db.Column(db.String(300))
    citation_apa = db.Column(db.Text)
    citation_mla = db.Column(db.Text)
    is_featured = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @staticmethod
    def generate_slug(title):
        import re
        import unicodedata
        slug = unicodedata.normalize("NFKD", title)
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.lower().strip("-")


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title_fr = db.Column(db.String(300), nullable=False)
    title_en = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False)
    description_fr = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(300))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    cover_image = db.Column(db.String(300))
    video_replay = db.Column(db.String(300))
    report_file = db.Column(db.String(300))
    presentation_file = db.Column(db.String(300))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class TeamMember(db.Model):
    __tablename__ = "team_members"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    role_fr = db.Column(db.String(200), nullable=False)
    role_en = db.Column(db.String(200), nullable=False)
    bio_fr = db.Column(db.Text)
    bio_en = db.Column(db.Text)
    photo = db.Column(db.String(300))
    publications_list = db.Column(db.Text)
    linkedin_url = db.Column(db.String(300))
    email = db.Column(db.String(120))
    member_type = db.Column(db.String(50), default="permanent")
    display_order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)


class Partner(db.Model):
    __tablename__ = "partners"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    logo = db.Column(db.String(300))
    website_url = db.Column(db.String(300))
    partner_type = db.Column(db.String(50), default="institution")
    display_order = db.Column(db.Integer, default=0)


class PressMention(db.Model):
    __tablename__ = "press_mentions"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    source_name = db.Column(db.String(200), nullable=False)
    source_url = db.Column(db.String(500), nullable=False)
    publication_date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class NewsletterSubscriber(db.Model):
    __tablename__ = "newsletter_subscribers"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    subscribed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(300), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class ActivityReport(db.Model):
    __tablename__ = "activity_reports"
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    title_fr = db.Column(db.String(300), nullable=False)
    title_en = db.Column(db.String(300), nullable=False)
    pdf_file = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class NewsItem(db.Model):
    __tablename__ = "news_items"
    id = db.Column(db.Integer, primary_key=True)
    title_fr = db.Column(db.String(300), nullable=False)
    title_en = db.Column(db.String(300), nullable=False)
    content_fr = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class JoinApplication(db.Model):
    __tablename__ = "join_applications"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    application_type = db.Column(db.String(50), nullable=False)
    motivation = db.Column(db.Text)
    organization = db.Column(db.String(200))
    phone = db.Column(db.String(30))
    is_processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Video(db.Model):
    __tablename__ = "videos"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500))
    views = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    creator = db.relationship("User", backref="videos")
    likes = db.relationship("VideoLike", backref="video", lazy="dynamic")
    comments = db.relationship("VideoComment", backref="video", lazy="dynamic")

    def get_like_count(self):
        return self.likes.count()

    def get_comment_count(self):
        return self.comments.count()

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return VideoLike.query.filter_by(video_id=self.id, user_id=user.id).first() is not None

    def get_embed_url(self):
        url = self.video_url
        if "youtube.com/watch" in url:
            video_id = url.split("v=")[1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        if "vimeo.com/" in url:
            video_id = url.split("vimeo.com/")[1].split("?")[0]
            return f"https://player.vimeo.com/video/{video_id}"
        return url


class VideoLike(db.Model):
    __tablename__ = "video_likes"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", backref="video_likes")

    __table_args__ = (db.UniqueConstraint("video_id", "user_id"),)


class VideoComment(db.Model):
    __tablename__ = "video_comments"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("video_comments.id"), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", backref="video_comments")
    replies = db.relationship("VideoComment", backref=db.backref("parent", remote_side=[id]), lazy="dynamic")


class ResearchTeam(db.Model):
    __tablename__ = "research_teams"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    theme = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    vision = db.Column(db.Text, nullable=False, default="")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(20), default="pending")  # pending, validated, rejected
    charter_accepted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    validated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    validated_at = db.Column(db.DateTime, nullable=True)

    creator = db.relationship("User", foreign_keys=[created_by], backref="created_teams")
    validator = db.relationship("User", foreign_keys=[validated_by], backref="validated_teams")
    members = db.relationship("TeamMemberDraft", backref="team", lazy="dynamic")


class TeamMemberDraft(db.Model):
    __tablename__ = "team_member_drafts"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("research_teams.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    whatsapp = db.Column(db.String(30))
    role = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    photo = db.Column(db.String(300))
