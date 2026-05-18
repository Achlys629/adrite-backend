import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models import *
from app.utils.logger import logger

def init_db():
    try:
        print("Initializing database...")
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully!")
        logger.info("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        logger.error(f"Database initialization failed: {e}")
        raise e

if __name__ == "__main__":
    init_db()