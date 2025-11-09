"""Room Models - Chat room with multi-AI collaboration

Models for rooms, messages, and AI discussions.
"""
from sqlalchemy import String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import List
import json

class Base(DeclarativeBase):
    pass

class Room(Base):
    """Chat room with user + multiple AIs"""
    __tablename__ = "rooms"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    user_id: Mapped[str] = mapped_column(String(100))
    active_ais: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages: Mapped[List["Message"]] = relationship(back_populates="room", cascade="all, delete-orphan")
    discussions: Mapped[List["AIDiscussion"]] = relationship(back_populates="room", cascade="all, delete-orphan")
    
    @property
    def ai_list(self) -> list:
        """Parse active_ais JSON"""
        return json.loads(self.active_ais) if self.active_ais else []
    
    @ai_list.setter
    def ai_list(self, value: list) -> None:
        """Set active_ais as JSON"""
        self.active_ais = json.dumps(value)


class Message(Base):
    """Message in a room (from user or AI)"""
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    role: Mapped[str] = mapped_column(String(20))
    author: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    mentions: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    discussion_id: Mapped[int | None] = mapped_column(ForeignKey("ai_discussions.id"), nullable=True)
    
    # Relationships
    room: Mapped["Room"] = relationship(back_populates="messages")
    discussion: Mapped["AIDiscussion"] = relationship(foreign_keys=[discussion_id])
    
    @property
    def mention_list(self) -> list:
        """Parse mentions JSON"""
        return json.loads(self.mentions) if self.mentions else []
    
    @mention_list.setter
    def mention_list(self, value: list) -> None:
        """Set mentions as JSON"""
        self.mentions = json.dumps(value)


class AIDiscussion(Base):
    """Private discussion between AIs (not shown to user by default)"""
    __tablename__ = "ai_discussions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    participants: Mapped[str] = mapped_column(Text)
    topic: Mapped[str] = mapped_column(String(500))
    messages: Mapped[str] = mapped_column(Text)
    consensus: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ongoing")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationship
    room: Mapped["Room"] = relationship(back_populates="discussions")
    
    @property
    def participant_list(self) -> list:
        return json.loads(self.participants) if self.participants else []
    
    @participant_list.setter
    def participant_list(self, value: list) -> None:
        self.participants = json.dumps(value)
    
    @property
    def message_list(self) -> list:
        return json.loads(self.messages) if self.messages else []
    
    @message_list.setter
    def message_list(self, value: list) -> None:
        self.messages = json.dumps(value)
    
    def add_message(self, ai_name: str, content: str) -> None:
        """Add a message to the discussion"""
        msgs = self.message_list
        msgs.append({
            'ai': ai_name,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.message_list = msgs


class DemoSession(Base):
    """Demo session - tracks anonymous users with cookie-based persistence
    
    RATE LIMITING: 10 queries per day (resets daily at midnight UTC)
    SAFEGUARD: Daily reset prevents permanent lockout
    """
    __tablename__ = "demo_sessions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    query_count: Mapped[int] = mapped_column(Integer, default=0)
    max_queries: Mapped[int] = mapped_column(Integer, default=10)
    last_query_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_activity: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Relationship
    room: Mapped["Room"] = relationship(foreign_keys=[room_id])
    
    def reset_if_new_day(self) -> bool:
        """
        Reset query count if it's a new day
        
        SAFEGUARD: Daily reset prevents users from being permanently locked out
        Returns True if reset occurred
        """
        today = datetime.utcnow().strftime("%Y-%m-%d")
        if self.last_query_date != today:
            self.query_count = 0
            self.last_query_date = today
            return True
        return False
    
    @property
    def queries_remaining(self) -> int:
        """Calculate remaining queries for today"""
        return max(0, self.max_queries - self.query_count)
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired (30 days)"""
        from datetime import timedelta
        return (datetime.utcnow() - self.created_at) > timedelta(days=30)


# Database setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

DATABASE_URL = "sqlite:///./chika.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Initialize database"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
