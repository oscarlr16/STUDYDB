from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker
import os
import json
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'coffee.db')
RECIPES_DIR = os.path.join(DATA_DIR, 'recipes')

# Crear directorios necesarios
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RECIPES_DIR, exist_ok=True)

# Configuración de la base de datos
engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)
metadata = MetaData()

# Definición de tablas
recipes = Table('recipes', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('author', String),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('file_path', String, nullable=False)  # Ruta al archivo JSON
)

class CoffeeDB:
    def __init__(self):
        self.engine = engine
        metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def create_recipe(self, recipe_data):
        """
        Crea una nueva receta guardando los metadatos en SQLite y los detalles en JSON
        """
        try:
            # Crear archivo JSON
            recipe_id = hash(f"{recipe_data['name']}_{datetime.utcnow().timestamp()}")
            file_name = f"recipe_{recipe_id}.json"
            file_path = os.path.join(RECIPES_DIR, file_name)
            
            # Guardar detalles completos en JSON
            with open(file_path, 'w') as f:
                json.dump(recipe_data, f, indent=4)
            
            # Guardar metadatos en SQLite
            session = self.Session()
            new_recipe = {
                'name': recipe_data['name'],
                'author': recipe_data.get('author', 'Anonymous'),
                'file_path': file_path
            }
            
            result = session.execute(recipes.insert().values(**new_recipe))
            session.commit()
            logger.info(f"Recipe created with ID: {result.inserted_primary_key[0]}")
            
            return result.inserted_primary_key[0]
            
        except Exception as e:
            logger.error(f"Error creating recipe: {e}")
            session.rollback()
            raise
        finally:
            session.close()

    def get_recipe(self, recipe_id):
        """
        Obtiene una receta combinando datos de SQLite y JSON
        """
        try:
            session = self.Session()
            result = session.execute(
                recipes.select().where(recipes.c.id == recipe_id)
            ).first()
            
            if result is None:
                return None
                
            # Leer el archivo JSON
            with open(result.file_path, 'r') as f:
                recipe_details = json.load(f)
                
            # Combinar con metadatos de la base de datos
            recipe_details.update({
                'id': result.id,
                'created_at': result.created_at
            })
            
            return recipe_details
            
        except Exception as e:
            logger.error(f"Error getting recipe: {e}")
            raise
        finally:
            session.close()

# Ejemplo de uso
if __name__ == "__main__":
    db = CoffeeDB()
    
    # Crear una receta de ejemplo
    recipe = {
        "name": "Classic Espresso",
        "author": "Barista Joe",
        "temperature": 93.5,
        "pressure": 9.0,
        "grind_size": "fine",
        "dose": 18,
        "yield": 36,
        "time": 25
    }
    
    # Guardar la receta
    recipe_id = db.create_recipe(recipe)
    print(f"Created recipe with ID: {recipe_id}")
    
    # Recuperar la receta
    stored_recipe = db.get_recipe(recipe_id)
    print("\nRecuperando receta guardada:")
    print(json.dumps(stored_recipe, indent=2, default=str))