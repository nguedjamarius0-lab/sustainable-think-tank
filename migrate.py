#!/usr/bin/env python
"""Migration helper script."""
import sys
import os

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == "__main__":
    with app.app_context():
        if len(sys.argv) > 1:
            cmd = sys.argv[1]
            if cmd == "init":
                os.system("flask db init")
            elif cmd == "migrate":
                msg = sys.argv[2] if len(sys.argv) > 2 else "auto migration"
                os.system(f'flask db migrate -m "{msg}"')
            elif cmd == "upgrade":
                os.system("flask db upgrade")
            elif cmd == "downgrade":
                os.system("flask db downgrade")
            else:
                print(f"Unknown command: {cmd}")
                print("Available commands: init, migrate, upgrade, downgrade")
        else:
            print("Usage: python migrate.py [init|migrate|upgrade|downgrade]")
