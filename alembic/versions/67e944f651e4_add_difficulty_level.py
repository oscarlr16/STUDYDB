"""add_difficulty_level

Revision ID: 67e944f651e4
Revises: 
Create Date: 2024-12-12 18:43:11.247852

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67e944f651e4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the column with a default value
    with op.batch_alter_table("recipes") as batch_op:
        batch_op.add_column(sa.Column("difficulty_level", sa.String(), nullable=True))

    # Update existing records with a default value
    op.execute(
        "UPDATE recipes SET difficulty_level = 'intermediate' WHERE difficulty_level IS NULL"
    )

    # Make the column non-nullable after updating it
    with op.batch_alter_table("recipes") as batch_op:
        batch_op.alter_column(
            "difficulty_level", existing_type=sa.String(), nullable=False
        )


def downgrade():
    with op.batch_alter_table("recipes") as batch_op:
        batch_op.drop_column("difficulty_level")
