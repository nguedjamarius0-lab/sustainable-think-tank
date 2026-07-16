import secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app import db
from app.models import ResearchTeam, TeamMemberDraft, TeamMember
from app.forms import TeamStep1Form, TeamStep2Form, TeamMemberForm, TeamStep4Form

TEAM_ROLES = [
    ("Directeur Général", "Responsable de la vision et de la stratégie globale"),
    ("Directeur de la Recherche", "Supervise les travaux de recherche et publications"),
    ("Directeur des Opérations", "Gestion administrative et opérationnelle"),
    ("Chef de Projet", "Planification et coordination des projets"),
    ("Chercheur Senior", "Recherche avancée et mentorat"),
    ("Chercheur", "Participation active aux projets de recherche"),
    ("Analyste", "Analyse de données et rédaction de rapports"),
    ("Chargé de Communication", "Relations publiques et médias"),
    ("Chargé de Développement", "Partenariats et financement"),
    ("Coordinateur", "Coordination logistique et administrative"),
    ("Conseiller Stratégique", "Conseil et orientation stratégique"),
    ("Expert Technique", "Expertise technique spécialisée"),
]

THEMES = [
    "Économie", "Politique publique", "Finance", "Numérique", "Affaires",
]

team_bp = Blueprint("team", __name__, url_prefix="/equipe")


@team_bp.route("/")
def index():
    validated_teams = ResearchTeam.query.filter_by(status="validated").order_by(
        ResearchTeam.created_at.desc()
    ).all()
    user_teams = []
    if current_user.is_authenticated:
        user_teams = ResearchTeam.query.filter_by(
            created_by=current_user.id
        ).order_by(ResearchTeam.created_at.desc()).all()
    return render_template(
        "team/index.html",
        teams=validated_teams,
        user_teams=user_teams,
    )


@team_bp.route("/creer", methods=["GET", "POST"])
@login_required
def create():
    step = int(request.args.get("step", 1))

    if request.method == "POST":
        action = request.form.get("action", "next")

        if action == "next":
            if step == 1:
                form = TeamStep1Form()
                if form.validate_on_submit():
                    session["team_step1"] = {
                        "name": form.name.data.strip(),
                        "theme": form.theme.data.strip(),
                        "description": form.description.data.strip() if form.description.data else "",
                        "vision": form.vision.data.strip() if form.vision.data else "",
                    }
                    return redirect(url_for("team.create", step=2))
                flash("Veuillez corriger les erreurs du formulaire.", "error")

            elif step == 2:
                form = TeamStep2Form()
                if form.validate_on_submit():
                    count = form.member_count.data
                    session["team_step2"] = {"member_count": min(max(count, 1), 20)}
                    return redirect(url_for("team.create", step=3))
                flash("Veuillez corriger les erreurs du formulaire.", "error")

            elif step == 3:
                members = []
                for i in range(1, session.get("team_step2", {}).get("member_count", 1) + 1):
                    members.append({
                        "name": request.form.get(f"member_{i}_name", "").strip(),
                        "whatsapp": request.form.get(f"member_{i}_whatsapp", "").strip(),
                        "role": request.form.get(f"member_{i}_role", "").strip(),
                        "bio": request.form.get(f"member_{i}_bio", "").strip(),
                    })
                session["team_step3"] = members
                return redirect(url_for("team.create", step=4))

            elif step == 4:
                form = TeamStep4Form()
                if form.validate_on_submit():
                    session["team_step4"] = {"charter_accepted": True}
                    return redirect(url_for("team.create", step=5))
                flash("Vous devez accepter la charte pour continuer.", "error")

        elif action == "back":
            if step > 1:
                return redirect(url_for("team.create", step=step - 1))

        elif action == "submit":
            if not session.get("team_step4", {}).get("charter_accepted"):
                flash("Vous devez accepter la charte.", "error")
                return redirect(url_for("team.create", step=4))

            s1 = session.get("team_step1", {})
            s2 = session.get("team_step2", {})
            s3 = session.get("team_step3", [])

            team = ResearchTeam(
                name=s1.get("name", ""),
                theme=s1.get("theme", ""),
                description=s1.get("description", ""),
                vision=s1.get("vision", ""),
                created_by=current_user.id,
                charter_accepted=True,
            )
            db.session.add(team)
            db.session.flush()

            for m in s3:
                if m.get("name"):
                    member = TeamMemberDraft(
                        team_id=team.id,
                        name=m["name"],
                        whatsapp=m.get("whatsapp", ""),
                        role=m.get("role", ""),
                        bio=m.get("bio", ""),
                    )
                    db.session.add(member)

            db.session.commit()

            for key in ["team_step1", "team_step2", "team_step3", "team_step4"]:
                session.pop(key, None)

            flash("Votre équipe a été soumise pour validation par un administrateur.", "success")
            return redirect(url_for("team.index"))

    return render_template(
        "team/create.html",
        step=step,
        step1=session.get("team_step1", {}),
        step2=session.get("team_step2", {}),
        step3=session.get("team_step3", []),
        step4=session.get("team_step4", {}),
        roles=TEAM_ROLES,
        themes=THEMES,
    )


@team_bp.route("/<int:team_id>")
def detail(team_id):
    team = ResearchTeam.query.get_or_404(team_id)
    members = TeamMemberDraft.query.filter_by(team_id=team_id).all()
    return render_template("team/detail.html", team=team, members=members)


@team_bp.route("/<int:team_id>/modifier", methods=["GET", "POST"])
@login_required
def edit(team_id):
    team = ResearchTeam.query.get_or_404(team_id)
    if team.created_by != current_user.id and current_user.role != "admin":
        flash("Vous ne pouvez modifier que vos propres équipes.", "error")
        return redirect(url_for("team.index"))

    if team.status != "pending":
        flash("Vous ne pouvez modifier qu'une équipe en attente de validation.", "error")
        return redirect(url_for("team.detail", team_id=team.id))

    from app.forms import TeamStep1Form
    form = TeamStep1Form(obj=team)

    if form.validate_on_submit():
        team.name = form.name.data.strip()
        team.theme = form.theme.data.strip()
        team.description = form.description.data.strip() if form.description.data else ""
        team.vision = form.vision.data.strip() if form.vision.data else ""
        db.session.commit()
        flash("Équipe mise à jour.", "success")
        return redirect(url_for("team.detail", team_id=team.id))

    return render_template("team/edit.html", team=team, form=form)


@team_bp.route("/<int:team_id>/supprimer", methods=["POST"])
@login_required
def delete(team_id):
    team = ResearchTeam.query.get_or_404(team_id)
    if team.created_by != current_user.id and current_user.role != "admin":
        flash("Vous ne pouvez supprimer que vos propres équipes.", "error")
        return redirect(url_for("team.index"))

    TeamMemberDraft.query.filter_by(team_id=team.id).delete()
    db.session.delete(team)
    db.session.commit()
    flash("Équipe supprimée.", "success")
    return redirect(url_for("team.index"))
