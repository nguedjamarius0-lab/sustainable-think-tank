"""Seed script — creates admin account only."""
import os
from app import create_app, db
from app.models import User

config_name = os.environ.get("FLASK_CONFIG", "development")
app = create_app(config_name)

with app.app_context():
    db.create_all()

    if not User.query.first():
        admin = User(email="admin@tendereo.org", name="Admin Tendereo", role="admin", is_verified=True)
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin account created: admin@tendereo.org / admin123")
    else:
        print("Admin already exists.")
