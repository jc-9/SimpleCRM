# simple_crm/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base # Import Base from models.py
from config import SQLALCHEMY_DATABASE_URI as DATABASE_URI

# Create an engine that stores data in the local directory's crm.db file.
engine = create_engine(DATABASE_URI, echo=False) # echo=True for SQL logging (useful for debugging)

# Create a configured "Session" class
# scoped_session ensures that each thread gets its own Session
Session = scoped_session(sessionmaker(bind=engine))

def init_db():
    """
    Initializes the database.
    Creates tables based on models.py if they don't already exist.
    """
    print(f"Initializing database at {DATABASE_URI}...")
    Base.metadata.create_all(engine)
    print("Database tables created (if they didn't exist).")

def get_db():
    """
    Provides a database session.
    It's designed to be used in Flask's application context.
    """
    return Session()

def close_db(e=None):
    """
    Closes the database session.
    This function should be called at the end of a request in Flask.
    """
    db_session = Session.remove() # Remove the session from the current scope
    if db_session:
        db_session.close()

# Example usage (for testing, not part of the Flask app flow)
if __name__ == '__main__':
    # This block will only run when database.py is executed directly
    # e.g., `python simple_crm/database.py`
    init_db()
    print("Database initialization script finished.")