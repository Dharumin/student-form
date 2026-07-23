"""
database.py
------------
Database layer for the Student Details System.

Uses SQLAlchemy ORM with SQLite by default (easy to run locally with zero setup).
On Railway, attach a Postgres plugin and it will set DATABASE_URL for you
automatically — no code changes needed.
"""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Enum,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import enum
import os

# ---------------------------------------------------------------------------
# 1. Database connection setup
# ---------------------------------------------------------------------------

# In production (Railway), set the DATABASE_URL environment variable to your
# Postgres connection string (Railway's Postgres plugin sets this for you
# automatically, usually as DATABASE_URL or DATABASE_PUBLIC_URL).
# Locally, it falls back to a SQLite file so you don't need Postgres running
# on your own machine to develop.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./student_details.db")

# Railway/Heroku-style URLs sometimes start with "postgres://" but SQLAlchemy
# needs "postgresql://" — normalize it.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# check_same_thread is only needed/valid for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ---------------------------------------------------------------------------
# 2. Enums for controlled/fixed choice fields
# ---------------------------------------------------------------------------

class Gender(str, enum.Enum):
    male = "Male"
    female = "Female"
    other = "Other"


class BloodGroup(str, enum.Enum):
    a_pos = "A+"
    a_neg = "A-"
    b_pos = "B+"
    b_neg = "B-"
    ab_pos = "AB+"
    ab_neg = "AB-"
    o_pos = "O+"
    o_neg = "O-"


# ---------------------------------------------------------------------------
# 3. Model
# ---------------------------------------------------------------------------

class Student(Base):
    """
    A single student's registration/enrollment record.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    # Identification
    roll_number = Column(String(20), nullable=False, unique=True, index=True)

    # Personal details
    full_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    blood_group = Column(Enum(BloodGroup), nullable=True)
    nationality = Column(String(50), nullable=False, default="Indian")

    # Contact details
    email = Column(String(100), nullable=False, unique=True, index=True)
    phone = Column(String(15), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    pincode = Column(String(10), nullable=False)

    # Academic details
    course = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False, index=True)
    admission_date = Column(Date, nullable=False)
    current_year = Column(Integer, nullable=False, default=1)

    # Guardian details
    guardian_name = Column(String(100), nullable=False)
    guardian_relation = Column(String(30), nullable=False)
    guardian_phone = Column(String(15), nullable=False)

    # Meta
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------------------------------------------------------------------------
# 4. Helper functions
# ---------------------------------------------------------------------------

def init_db():
    """Create all tables (call once on app startup)."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Running `python database.py` directly just sets up the DB tables.
    init_db()
    print("Database initialized successfully.")
