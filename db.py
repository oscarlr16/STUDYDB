from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
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
    Column('file_path', String, nullable=False)
)

reviews = Table('reviews', metadata,
    Column('id', Integer, primary_key=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('rating', Integer, nullable=False),
    Column('comment', String),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class CoffeeDB:
    def __init__(self):
        self.engine = engine
        metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def create_user(self, username, email):
        try:
            session = self.Session()
            result = session.execute(
                users.insert().values(username=username, email=email)
            )
            session.commit()
            return result.inserted_primary_key[0]
        finally:
            session.close()

    def create_recipe(self, recipe_data, author_id):
        try:
            recipe_id = hash(f"{recipe_data['name']}_{datetime.utcnow().timestamp()}")
            file_name = f"recipe_{recipe_id}.json"
            file_path = os.path.join(RECIPES_DIR, file_name)
            
            with open(file_path, 'w') as f:
                json.dump(recipe_data, f, indent=4)
            
            session = self.Session()
            result = session.execute(
                recipes.insert().values(
                    name=recipe_data['name'],
                    author_id=author_id,
                    file_path=file_path
                )
            )
            session.commit()
            return result.inserted_primary_key[0]
        finally:
            session.close()

    def add_review(self, recipe_id, user_id, rating, comment=None):
        try:
            session = self.Session()
            result = session.execute(
                reviews.insert().values(
                    recipe_id=recipe_id,
                    user_id=user_id,
                    rating=rating,
                    comment=comment
                )
            )
            session.commit()
            return result.inserted_primary_key[0]
        finally:
            session.close()

    def get_recipe(self, recipe_id):
        try:
            session = self.Session()
            result = session.execute(
                recipes.select().where(recipes.c.id == recipe_id)
            ).first()
            
            if result is None:
                return None
                
            with open(result.file_path, 'r') as f:
                recipe_details = json.load(f)
            
            reviews_result = session.execute(
                reviews.select().where(reviews.c.recipe_id == recipe_id)
            ).fetchall()
            
            recipe_details.update({
                'id': result.id,
                'created_at': result.created_at,
                'reviews': [{
                    'id': r.id,
                    'recipe_id': r.recipe_id,
                    'user_id': r.user_id,
                    'rating': r.rating,
                    'comment': r.comment,
                    'created_at': r.created_at
                } for r in reviews_result]
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