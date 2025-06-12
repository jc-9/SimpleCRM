# simple_crm/models.py
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import SQLALCHEMY_DATABASE_URI

# Base class for our declarative models
Base = declarative_base()

# Define the Customer model
class Customer(Base):
    __tablename__ = 'customers' # Name of the table in the database

    id = Column(Integer, primary_key=True)
    customer_name = Column(String(255), nullable=False, unique=True)
    primary_contact_name = Column(String(255), nullable=False)
    primary_contact_email = Column(String(255), nullable=False)

    # Relationship to Event model: A customer can have many events
    # backref='customer' creates a 'customer' attribute on the Event object
    # cascade="all, delete-orphan" ensures events are deleted if a customer is deleted
    events = relationship("Event", backref='customer', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer {self.customer_name}>"

# Define the Event model
class Event(Base):
    __tablename__ = 'events' # Name of the table in the database

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    event_type = Column(String(100), nullable=False) # e.g., 'Call', 'Meeting', 'Email', 'Demo'
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Event {self.event_type} for Customer ID {self.customer_id}>"

# This part will be used by database.py to create the engine and session
# We include it here to centralize the SQLAlchemy Base, but the actual
# engine creation and session management will be in database.py
# Engine and Session are not created here directly to avoid circular imports.