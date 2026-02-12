from backend.database.database import engine
from backend.database import models
import logging

logging.basicConfig(level=logging.INFO)

def test_schema_creation():
    try:
        print("Attempting to create tables in PostgreSQL...")
        models.Base.metadata.create_all(bind=engine)
        print("Successfully created tables!")
    except Exception as e:
        print(f"Error during schema creation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_schema_creation()
