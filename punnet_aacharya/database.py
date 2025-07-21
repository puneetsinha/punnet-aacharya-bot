from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import logging
from config import DATABASE_URL

logger = logging.getLogger(__name__)

Base = declarative_base()
logger.info(f"Initializing database with URL: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.info("Database session maker configured")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    name = Column(String)
    birth_date = Column(DateTime)
    birth_time = Column(DateTime)
    birth_place = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    timezone = Column(String)
    chart_data = Column(Text)  # JSON string of calculated chart
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    onboarding_complete = Column(Boolean, default=False)

class Consultation(Base):
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    question_type = Column(String)  # 'marriage' or 'career'
    question = Column(Text)
    prediction = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
logger.info("Creating database tables")
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    raise

def get_db():
    """Get database session with logging"""
    logger.debug("Creating new database session")
    db = SessionLocal()
    try:
        logger.debug("Database session created successfully")
        yield db
    except Exception as e:
        logger.error(f"Error in database session: {str(e)}")
        db.rollback()
        raise
    finally:
        logger.debug("Closing database session")
        db.close() 