import secrets
from datetime import datetime, timezone
from flask import current_app
from flask_mail import Message
from app import mail, db
from app.models import EmailVerification


def generate_and_send_code(email, purpose):
    """Generate a 6-digit code and send it by email."""
    code = ''.join(secrets.choice('0123456789') for _ in range(6))

    verification = EmailVerification(
        email=email,
        code=code,
        purpose=purpose,
    )
    db.session.add(verification)
    db.session.commit()

    subject_map = {
        "registration": "Tendereo - Vérifiez votre adresse email",
        "admin_registration": "Tendereo - Code d'inscription administrateur",
        "password_reset": "Tendereo - Réinitialisation de votre mot de passe",
    }

    body_map = {
        "registration": f"Votre code de vérification est : {code}\nCe code expire dans 10 minutes.",
        "admin_registration": f"Votre code de vérification administrateur est : {code}\nCe code expire dans 10 minutes.",
        "password_reset": f"Votre code de réinitialisation est : {code}\nCe code expire dans 10 minutes.",
    }

    html_map = {
        "registration": f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 30px;">
            <h2 style="color: #1B5E3B;">Tendereo Sustainability Institute</h2>
            <p>Bonjour,</p>
            <p>Voici votre code de vérification :</p>
            <div style="background: #f0f0f0; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #0E7C86;">{code}</span>
            </div>
            <p style="color: #666; font-size: 14px;">Ce code expire dans 10 minutes. Si vous n'avez pas demandé cette vérification, ignorez cet email.</p>
        </div>
        """,
        "admin_registration": f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 30px;">
            <h2 style="color: #1B5E3B;">Tendereo - Administration</h2>
            <p>Bonjour,</p>
            <p>Voici votre code de vérification administrateur :</p>
            <div style="background: #f0f0f0; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #0E7C86;">{code}</span>
            </div>
            <p style="color: #666; font-size: 14px;">Ce code expire dans 10 minutes.</p>
        </div>
        """,
        "password_reset": f"""
        <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 30px;">
            <h2 style="color: #1B5E3B;">Tendereo - Réinitialisation</h2>
            <p>Bonjour,</p>
            <p>Voici votre code de réinitialisation de mot de passe :</p>
            <div style="background: #f0f0f0; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #0E7C86;">{code}</span>
            </div>
            <p style="color: #666; font-size: 14px;">Ce code expire dans 10 minutes. Si vous n'avez pas demandé de réinitialisation, ignorez cet email.</p>
        </div>
        """,
    }

    try:
        msg = Message(
            subject=subject_map.get(purpose, "Tendereo - Code de vérification"),
            recipients=[email],
            body=body_map.get(purpose, f"Votre code est : {code}"),
            html=html_map.get(purpose, f"<p>Votre code est : <strong>{code}</strong></p>"),
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        print(f"\n{'='*50}")
        print(f"  CODE DE VÉRIFICATION (mode développement)")
        print(f"  Email : {email}")
        print(f"  Code  : {code}")
        print(f"  Usage : {purpose}")
        print(f"{'='*50}\n")
        return True
