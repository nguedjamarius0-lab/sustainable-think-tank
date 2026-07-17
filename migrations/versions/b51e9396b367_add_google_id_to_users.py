"""add_google_id_to_users

Revision ID: b51e9396b367
Revises: 7e7d69a6b10c
Create Date: 2026-07-17 13:39:02.684017

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b51e9396b367'
down_revision = '7e7d69a6b10c'
branch_labels = None
depends_on = None


def upgrade():
    # Drop email_verifications table if it exists
    op.execute("DROP TABLE IF EXISTS email_verifications")

    # Add google_id column to users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('google_id', sa.String(length=100), nullable=True))
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)
        batch_op.create_unique_constraint('uq_users_google_id', ['google_id'])


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_google_id', type_='unique')
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)
        batch_op.drop_column('google_id')
