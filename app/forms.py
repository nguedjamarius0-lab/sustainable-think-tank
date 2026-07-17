from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField,
    BooleanField, IntegerField, HiddenField, DateTimeLocalField, DateField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Optional, NumberRange
)


class RegisterForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(), EqualTo("password", message="Les mots de passe ne correspondent pas.")]
    )


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Nouveau mot de passe", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(), EqualTo("password", message="Les mots de passe ne correspondent pas.")]
    )


class AdminRegisterForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])


class ContactForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    subject = StringField("Sujet", validators=[DataRequired(), Length(min=2, max=300)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10, max=5000)])


class NewsletterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Nom", validators=[Optional(), Length(max=150)])


class JoinApplicationForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    application_type = SelectField(
        "Type de candidature",
        choices=[
            ("chercheur", "Chercheur"),
            ("professionnel", "Professionnel"),
            ("etudiant", "Étudiant"),
            ("benevole", "Bénévole"),
            ("partenaire", "Partenaire"),
        ],
        validators=[DataRequired()]
    )
    motivation = TextAreaField("Motivation", validators=[Optional(), Length(max=5000)])
    organization = StringField("Organisation", validators=[Optional(), Length(max=200)])
    phone = StringField("Téléphone", validators=[Optional(), Length(max=30)])


class TeamStep1Form(FlaskForm):
    name = StringField("Nom de l'équipe", validators=[DataRequired(), Length(min=2, max=200)])
    theme = SelectField(
        "Thème",
        choices=[
            ("Économie", "Économie"),
            ("Politique publique", "Politique publique"),
            ("Finance", "Finance"),
            ("Numérique", "Numérique"),
            ("Affaires", "Affaires"),
        ],
        validators=[DataRequired()]
    )
    description = TextAreaField("Description", validators=[Optional(), Length(max=2000)])
    vision = TextAreaField(
        "Vision et idéologie de l'équipe",
        validators=[DataRequired(message="Décrivez la vision et l'idéologie de votre équipe."), Length(min=20, max=5000, message="Minimum 20 caractères.")],
        description="Dans quoi l'équipe souhaite-t-elle contribuer ? Quel est son apport au développement d'une nation ?"
    )


class TeamStep2Form(FlaskForm):
    member_count = IntegerField(
        "Nombre de membres",
        validators=[DataRequired(), NumberRange(min=5, max=20, message="Minimum 5 membres, maximum 20")]
    )


class TeamMemberForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[Optional(), Email()])
    role = StringField("Rôle", validators=[DataRequired(), Length(min=2, max=100)])
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=2000)])


class TeamStep4Form(FlaskForm):
    charter_accepted = BooleanField(
        "J'accepte la charte",
        validators=[DataRequired(message="Vous devez accepter la charte pour continuer.")]
    )


class VideoForm(FlaskForm):
    title = StringField("Titre", validators=[DataRequired(), Length(min=2, max=300)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=2000)])
    video_url = StringField("URL de la vidéo", validators=[DataRequired(), Length(min=5, max=500)])
    thumbnail_url = StringField("URL de la miniature", validators=[Optional(), Length(max=500)])


class VideoCommentForm(FlaskForm):
    content = TextAreaField("Commentaire", validators=[DataRequired(), Length(min=1, max=2000)])


class UserRoleForm(FlaskForm):
    role = SelectField(
        "Rôle",
        choices=[
            ("user", "Utilisateur"),
            ("editor", "Éditeur"),
            ("admin", "Administrateur"),
        ],
        validators=[DataRequired()]
    )


class TeamValidationForm(FlaskForm):
    pass


# ─── Admin CRUD Forms ────────────────────────────────────────────────


class PublicationForm(FlaskForm):
    title_fr = StringField("Titre (FR)", validators=[DataRequired(), Length(min=2, max=300)])
    title_en = StringField("Titre (EN)", validators=[DataRequired(), Length(min=2, max=300)])
    category = SelectField(
        "Catégorie",
        choices=[
            ("rapport", "Rapport"),
            ("policy_brief", "Policy Brief"),
            ("article", "Article"),
            ("working_paper", "Working Paper"),
            ("note", "Note"),
        ],
        validators=[DataRequired()]
    )
    theme = SelectField(
        "Thème",
        choices=[
            ("Économie", "Économie"),
            ("Politique publique", "Politique publique"),
            ("Finance", "Finance"),
            ("Numérique", "Numérique"),
            ("Affaires", "Affaires"),
            ("Environnement", "Environnement"),
            ("Santé", "Santé"),
            ("Éducation", "Éducation"),
        ],
        validators=[DataRequired()]
    )
    author_name = StringField("Auteur", validators=[DataRequired(), Length(min=2, max=150)])
    author_bio = TextAreaField("Bio de l'auteur", validators=[Optional(), Length(max=2000)])
    summary_fr = TextAreaField("Résumé (FR)", validators=[DataRequired(), Length(min=10, max=5000)])
    summary_en = TextAreaField("Résumé (EN)", validators=[DataRequired(), Length(min=10, max=5000)])
    executive_summary_fr = TextAreaField("Résumé exécutif (FR)", validators=[Optional(), Length(max=10000)])
    executive_summary_en = TextAreaField("Résumé exécutif (EN)", validators=[Optional(), Length(max=10000)])
    citation_apa = TextAreaField("Citation APA", validators=[Optional(), Length(max=1000)])
    citation_mla = TextAreaField("Citation MLA", validators=[Optional(), Length(max=1000)])
    is_featured = BooleanField("À la une")
    pdf_file = FileField("Fichier PDF", validators=[FileAllowed(['pdf'], 'PDF uniquement')])
    slides_file = FileField("Diaporama", validators=[FileAllowed(['pdf', 'pptx', 'ppt'], 'PDF ou PowerPoint')])
    cover_image = FileField("Image de couverture", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images uniquement')])


class EventForm(FlaskForm):
    title_fr = StringField("Titre (FR)", validators=[DataRequired(), Length(min=2, max=300)])
    title_en = StringField("Titre (EN)", validators=[DataRequired(), Length(min=2, max=300)])
    event_type = SelectField(
        "Type",
        choices=[
            ("conference", "Conférence"),
            ("webinar", "Webinaire"),
            ("workshop", "Atelier"),
            ("roundtable", "Table ronde"),
            ("colloque", "Colloque"),
            ("autre", "Autre"),
        ],
        validators=[DataRequired()]
    )
    description_fr = TextAreaField("Description (FR)", validators=[DataRequired(), Length(min=10, max=10000)])
    description_en = TextAreaField("Description (EN)", validators=[DataRequired(), Length(min=10, max=10000)])
    location = StringField("Lieu", validators=[Optional(), Length(max=300)])
    start_date = DateTimeLocalField("Date de début", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    end_date = DateTimeLocalField("Date de fin", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    is_published = BooleanField("Publié", default=True)
    cover_image = FileField("Image de couverture", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])
    report_file = FileField("Rapport", validators=[FileAllowed(['pdf'])])
    presentation_file = FileField("Présentation", validators=[FileAllowed(['pdf', 'pptx', 'ppt'])])


class TeamMemberAdminForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=150)])
    role_fr = StringField("Rôle (FR)", validators=[DataRequired(), Length(min=2, max=200)])
    role_en = StringField("Rôle (EN)", validators=[DataRequired(), Length(min=2, max=200)])
    bio_fr = TextAreaField("Bio (FR)", validators=[Optional(), Length(max=2000)])
    bio_en = TextAreaField("Bio (EN)", validators=[Optional(), Length(max=2000)])
    email = StringField("Email", validators=[Optional(), Email()])
    linkedin_url = StringField("LinkedIn", validators=[Optional(), Length(max=300)])
    member_type = SelectField(
        "Type",
        choices=[
            ("permanent", "Permanent"),
            ("associate", "Associé"),
            ("senior", "Senior"),
            ("junior", "Junior"),
        ],
        validators=[DataRequired()]
    )
    display_order = IntegerField("Ordre d'affichage", validators=[Optional(), NumberRange(min=0)])
    is_published = BooleanField("Publié", default=True)
    photo = FileField("Photo", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])


class PartnerForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(min=2, max=200)])
    website_url = StringField("Site web", validators=[Optional(), Length(max=300)])
    partner_type = SelectField(
        "Type",
        choices=[
            ("institution", "Institution"),
            ("ong", "ONG"),
            ("entreprise", "Entreprise"),
            ("universite", "Université"),
            ("autre", "Autre"),
        ],
        validators=[DataRequired()]
    )
    display_order = IntegerField("Ordre", validators=[Optional(), NumberRange(min=0)])
    logo = FileField("Logo", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])


class PressMentionForm(FlaskForm):
    title = StringField("Titre", validators=[DataRequired(), Length(min=2, max=300)])
    source_name = StringField("Source", validators=[DataRequired(), Length(min=2, max=200)])
    source_url = StringField("URL", validators=[DataRequired(), Length(min=5, max=500)])
    publication_date = DateField("Date de publication", format="%Y-%m-%d", validators=[Optional()])
    description = TextAreaField("Description", validators=[Optional(), Length(max=2000)])


class NewsItemForm(FlaskForm):
    title_fr = StringField("Titre (FR)", validators=[DataRequired(), Length(min=2, max=300)])
    title_en = StringField("Titre (EN)", validators=[DataRequired(), Length(min=2, max=300)])
    content_fr = TextAreaField("Contenu (FR)", validators=[DataRequired(), Length(min=10, max=20000)])
    content_en = TextAreaField("Contenu (EN)", validators=[DataRequired(), Length(min=10, max=20000)])
    source_url = StringField("Source URL", validators=[Optional(), Length(max=500)])
    is_published = BooleanField("Publié", default=True)


class ActivityReportForm(FlaskForm):
    year = IntegerField("Année", validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    title_fr = StringField("Titre (FR)", validators=[DataRequired(), Length(min=2, max=300)])
    title_en = StringField("Titre (EN)", validators=[DataRequired(), Length(min=2, max=300)])
    pdf_file = FileField("Fichier PDF", validators=[DataRequired(), FileAllowed(['pdf'], 'PDF uniquement')])
