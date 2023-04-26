"""create clan table and add result hash

Revision ID: 647a0a778eef
Revises: 61d131a3f80a
Create Date: 2023-04-26 04:37:46.469399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "647a0a778eef"
down_revision = "61d131a3f80a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clan",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tag", sa.String(3), nullable=False),
        sa.Column("name", sa.String(50)),
    )

    op.add_column("player", sa.Column("clan_id", sa.Integer))
    op.create_foreign_key(
        "fk_player_clan",
        "player",
        "clan",
        ["clan_id"],
        ["id"],
    )

    op.add_column("match_result", sa.Column("hash", sa.String(), nullable=True))
    op.execute("UPDATE match_result SET hash = 'UPDATE_ME'")
    op.alter_column("match_result", "hash", nullable=False)


def downgrade() -> None:
    op.drop_table("clan")
    op.drop_column("player", "clan_id")
