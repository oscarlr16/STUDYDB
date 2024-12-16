"""add_ingredients_tables

Revision ID: d622b5788e68
Revises: 364ef5b2c019
Create Date: 2024-12-16 16:52:21.750997

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd622b5788e68'
down_revision: Union[str, None] = '364ef5b2c019'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create ingredients table
    op.create_table(
        'ingredients',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),  # 'bean', 'additive', etc.
        sa.Column('origin', sa.String()),
        sa.Column('roast_level', sa.String()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # Create intermediate table for many-to-many relationship
    op.create_table(
        'recipe_ingredients',
        sa.Column('recipe_id', sa.Integer(), sa.ForeignKey('recipes.id'), primary_key=True),
        sa.Column('ingredient_id', sa.Integer(), sa.ForeignKey('ingredients.id'), primary_key=True),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),  # 'g', 'ml', etc.
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # Add some base ingredients
    op.execute("""
        INSERT INTO ingredients (name, type, origin, roast_level) VALUES 
        ('Arábica Colombia', 'bean', 'Colombia', 'medium'),
        ('Robusta Vietnam', 'bean', 'Vietnam', 'dark'),
        ('Arábica Ethiopia', 'bean', 'Ethiopia', 'light')
    """)

def downgrade():
    op.drop_table('recipe_ingredients')
    op.drop_table('ingredients')
