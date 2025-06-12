import os

# Determine the absolute path to the directory where this script is located
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Path to our SQLite database file
DATABASE = os.path.join(BASEDIR, 'data', 'crm.db')

# SQLAlchemy database URI
# 'sqlite:///' + DATABASE means a SQLite database located at the specified path
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE}'
SQLALCHEMY_TRACK_MODIFICATIONS = False # Suppresses a warning, good practice to set to False

# simple_crm/config.py
# ... (existing imports and variables) ...

# A secret key is required for session management (e.g., for flash messages)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-that-you-should-change-in-production'