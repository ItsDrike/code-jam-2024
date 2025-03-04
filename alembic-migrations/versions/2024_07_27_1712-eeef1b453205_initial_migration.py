"""Initial migration

Revision ID: eeef1b453205
Revises:
Create Date: 2024-07-27 17:12:52.289591
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "eeef1b453205"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table("movies", sa.Column("tvdb_id", sa.Integer(), nullable=False), sa.PrimaryKeyConstraint("tvdb_id"))
    op.create_table("series", sa.Column("tvdb_id", sa.Integer(), nullable=False), sa.PrimaryKeyConstraint("tvdb_id"))
    op.create_table(
        "users", sa.Column("discord_id", sa.Integer(), nullable=False), sa.PrimaryKeyConstraint("discord_id")
    )
    op.create_table(
        "episodes",
        sa.Column("tvdb_id", sa.Integer(), nullable=False),
        sa.Column("series_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["series_id"],
            ["series.tvdb_id"],
        ),
        sa.PrimaryKeyConstraint("tvdb_id"),
    )
    op.create_table(
        "user_lists",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "item_kind", sa.Enum("SERIES", "MOVIE", "EPISODE", "MEDIA", "ANY", name="userlistkind"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.discord_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="unique_user_list_name"),
    )
    with op.batch_alter_table("user_lists", schema=None) as batch_op:
        batch_op.create_index("ix_user_lists_user_id_name", ["user_id", "name"], unique=True)

    op.create_table(
        "user_list_items",
        sa.Column("list_id", sa.Integer(), nullable=False),
        sa.Column("tvdb_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.Enum("SERIES", "MOVIE", "EPISODE", name="userlistitemkind"), nullable=False),
        sa.ForeignKeyConstraint(
            ["list_id"],
            ["user_lists.id"],
        ),
        sa.PrimaryKeyConstraint("list_id", "tvdb_id", "kind"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_list_items")
    with op.batch_alter_table("user_lists", schema=None) as batch_op:
        batch_op.drop_index("ix_user_lists_user_id_name")

    op.drop_table("user_lists")
    op.drop_table("episodes")
    op.drop_table("users")
    op.drop_table("series")
    op.drop_table("movies")
    # ### end Alembic commands ###
