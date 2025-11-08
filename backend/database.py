"""Database configuration and models for CHIKA"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database URL (defaults to SQLite, override with DATABASE_URL env var)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chika.db")

# Fix for Render PostgreSQL URLs (postgres:// → postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# === MODELS === #

class WaitlistEntry(Base):
    """Waitlist signup entry"""
    __tablename__ = "waitlist"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    signup_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)
    utm_source = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    
    def to_dict(self):
        """Convert to dict for API responses"""
        return {
            "id": self.id,
            "email": self.email,
            "timestamp": self.signup_timestamp.isoformat(),
            "email_sent": self.email_sent,
            "email_sent_at": self.email_sent_at.isoformat() if self.email_sent_at else None,
            "ip": self.ip_address,
            "user_agent": self.user_agent
        }


# Create tables
def init_db():
    """Initialize database (create tables)"""
    Base.metadata.create_all(bind=engine)


# Dependency for routes
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
