"""change_temperature_to_decimal

Revision ID: 364ef5b2c019
Revises: 67e944f651e4
Create Date: 2024-12-12 19:13:25.616410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from alembic import op
import sqlalchemy as sa
from decimal import Decimal
import json
import os


# revision identifiers, used by Alembic.
revision: str = '364ef5b2c019'
down_revision: Union[str, None] = '67e944f651e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Primero modificamos los archivos JSON existentes
    recipe_dir = 'data/recipes'
    for filename in os.listdir(recipe_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(recipe_dir, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Convertir temperatura a Decimal con 2 decimales
                if 'temperature' in data:
                    data['temperature'] = str(round(Decimal(str(data['temperature'])), 2))
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)

def downgrade():
    recipe_dir = 'data/recipes'
    for filename in os.listdir(recipe_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(recipe_dir, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                if 'temperature' in data:
                    data['temperature'] = float(data['temperature'])
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)