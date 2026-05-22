
#setting up a connection to a database using SQLAlchemy and 
#preparing a way to safely use that connection in your application
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#This tells SQLAlchemy where your database is.
DATABASE_URL = "sqlite:///./tasks.db"

#The engine is the core connection to the database.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,#: You must manually commit changes (db.commit()).
    autoflush=False,#Changes are not automatically pushed to DB until needed.
    bind=engine #Connects sessions to your database.
)

Base = declarative_base()#This is used to define database tables as Python classes.


def get_db():
    db = SessionLocal()#It creates a new database session 
    try:
        yield db # gives that session to wherever it’s used 
    finally:
        db.close() #close the session.
        
"""
Connects your app to a SQLite database
Creates a way to talk to the database (sessions)
Defines a base for your tables
Provides a safe function (get_db) to open and close database connections automatically
"""