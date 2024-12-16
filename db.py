from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker
import os
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'coffee.db')
RECIPES_DIR = os.path.join(DATA_DIR, 'recipes')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RECIPES_DIR, exist_ok=True)

engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)
metadata = MetaData()

# Definición de tablas
users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, unique=True, nullable=False),
    Column('email', String, unique=True, nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow)
)

recipes = Table('recipes', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('author_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('file_path', String, nullable=False),
    Column('difficulty_level', String, nullable=False)
)

ingredients = Table('ingredients', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('type', String, nullable=False),
    Column('origin', String),
    Column('roast_level', String),
    Column('created_at', DateTime, default=datetime.utcnow)
)

recipe_ingredients = Table('recipe_ingredients', metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'), primary_key=True),
    Column('quantity', Float, nullable=False),
    Column('unit', String, nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class CoffeeDB:
    def __init__(self):
        self.engine = engine
        metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def create_user(self, username, email):
        """Crear un nuevo usuario"""
        session = self.Session()
        try:
            result = session.execute(
                users.insert().values(
                    username=username,
                    email=email
                )
            )
            session.commit()
            return result.inserted_primary_key[0]
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_ingredients(self):
        """Obtener lista de ingredientes disponibles"""
        session = self.Session()
        try:
            result = session.execute(ingredients.select()).fetchall()
            return [dict(r._mapping) for r in result]
        finally:
            session.close()

    def create_recipe(self, recipe_data, author_id):
        """Crear una nueva receta"""
        try:
            session = self.Session()
            
            # Guardar la receta primero
            recipe_id = hash(f"{recipe_data['name']}_{datetime.utcnow().timestamp()}")
            file_name = f"recipe_{recipe_id}.json"
            file_path = os.path.join(RECIPES_DIR, file_name)
            
            # Separar los ingredientes del resto de los datos
            recipe_ingredients_data = recipe_data.pop('ingredients', [])
            
            with open(file_path, 'w') as f:
                json.dump(recipe_data, f, indent=4)
            
            result = session.execute(
                recipes.insert().values(
                    name=recipe_data['name'],
                    author_id=author_id,
                    file_path=file_path,
                    difficulty_level=recipe_data['difficulty_level']
                )
            )
            recipe_id = result.inserted_primary_key[0]
            
            # Agregar los ingredientes a la tabla intermedia
            for ingredient in recipe_ingredients_data:
                session.execute(
                    recipe_ingredients.insert().values(
                        recipe_id=recipe_id,
                        ingredient_id=ingredient['id'],
                        quantity=ingredient['quantity'],
                        unit=ingredient['unit']
                    )
                )
            
            session.commit()
            return recipe_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_recipe(self, recipe_id):
        """Obtener una receta por su ID"""
        try:
            session = self.Session()
            recipe = session.execute(
                recipes.select().where(recipes.c.id == recipe_id)
            ).first()
            
            if recipe is None:
                return None
                
            with open(recipe.file_path, 'r') as f:
                recipe_details = json.load(f)
            
            # Obtener ingredientes de la receta
            recipe_ingredients_result = session.execute("""
                SELECT i.name, i.type, i.origin, i.roast_level, 
                       ri.quantity, ri.unit
                FROM recipe_ingredients ri
                JOIN ingredients i ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = :recipe_id
            """, {'recipe_id': recipe_id}).fetchall()
            
            recipe_details.update({
                'id': recipe.id,
                'created_at': recipe.created_at,
                'ingredients': [{
                    'name': r.name,
                    'type': r.type,
                    'origin': r.origin,
                    'roast_level': r.roast_level,
                    'quantity': r.quantity,
                    'unit': r.unit
                } for r in recipe_ingredients_result]
            })
            
            return recipe_details
        finally:
            session.close()
            
if __name__ == "__main__":
    db = CoffeeDB()
    
    # Crear usuario de ejemplo
    user_id = db.create_user("barista_joe", "joe@coffee.com")
    
    # Crear receta
    recipe = {
        "name": "Classic Espresso",
        "temperature": 93.5,
        "pressure": 9.0,
        "grind_size": "fine",
        "dose": 18,
        "yield": 36,
        "time": 25
    }
    
    recipe_id = db.create_recipe(recipe, user_id)
    
    # Agregar review
    db.add_review(recipe_id, user_id, 5, "Perfect recipe!")
    
    # Recuperar receta con reviews
    stored_recipe = db.get_recipe(recipe_id)
    print("\nReceta guardada:")
    print(json.dumps(stored_recipe, indent=2, default=str))