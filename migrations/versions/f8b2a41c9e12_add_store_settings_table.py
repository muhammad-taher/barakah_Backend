"""add store settings table

Revision ID: f8b2a41c9e12
Revises: e7cad3107f3f
Create Date: 2026-09-22 00:05:21.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8b2a41c9e12'
down_revision = 'e7cad3107f3f'
branch_labels = None
depends_on = None


def upgrade():
    # Use raw SQL with IF NOT EXISTS since the table may already exist
    # (e.g. created via db.create_all() or create_tables.py)
    op.execute("""
        CREATE TABLE IF NOT EXISTS store_settings (
            id INTEGER NOT NULL PRIMARY KEY,
            key VARCHAR(100) NOT NULL UNIQUE,
            value TEXT
        )
    """)
    # Add image_url to products if it doesn't already exist
    try:
        op.add_column('products', sa.Column('image_url', sa.String(length=500), nullable=True))
    except Exception:
        pass  # Column already exists


def downgrade():
    op.drop_column('products', 'image_url')
    op.drop_table('store_settings')
