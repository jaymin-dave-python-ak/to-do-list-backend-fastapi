"""fix_reminder_timezone

Revision ID: c234b7722ac5
Revises: 0fbce04659ae
Create Date: 2026-03-20 11:14:11.370582

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c234b7722ac5"
down_revision: Union[str, Sequence[str], None] = "0fbce04659ae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Changes TIMESTAMP to TIMESTAMPTZ
    op.execute(
        "ALTER TABLE items ALTER COLUMN remind_me_at TYPE TIMESTAMPTZ USING remind_me_at AT TIME ZONE 'UTC'"
    )


def downgrade():
    # Reverts back to TIMESTAMP (without timezone)
    op.execute(
        "ALTER TABLE items ALTER COLUMN remind_me_at TYPE TIMESTAMP WITHOUT TIME ZONE"
    )