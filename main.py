"""
main.py
-------
FastAPI backend for the Student Details System.

Run with:
    uvicorn main:app --reload

Requires: fastapi, uvicorn, sqlalchemy, pydantic
Install:  pip install -r requirements.txt --break-system-packages
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import date
import re
import os

from database import (
    init_db,
    get_db,
    SessionLocal,
    Student,
    Gender,
    BloodGroup,
)

app = FastAPI(title="Student Details API", version="1.0.0")

# Allow the frontend (GitHub Pages, or a different port locally) to call this API.
# Set the FRONTEND_ORIGIN env var to your GitHub Pages URL in production, e.g.
# FRONTEND_ORIGIN=https://dharumin.github.io
# Falls back to "*" (allow all) for easy local development.
frontend_origin = os.environ.get("FRONTEND_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin] if frontend_origin != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


# ---------------------------------------------------------------------------
# Pydantic schemas (request/response validation)
# ---------------------------------------------------------------------------

class StudentCreate(BaseModel):
    roll_number: str
    full_name: str
    date_of_birth: date
    gender: Gender
    blood_group: Optional[BloodGroup] = None
    nationality: str = "Indian"
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    pincode: str
    course: str
    department: str
    admission_date: date
    current_year: int
    guardian_name: str
    guardian_relation: str
    guardian_phone: str

    @field_validator("phone", "guardian_phone")
    @classmethod
    def validate_phone(cls, v):
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("Phone number must be exactly 10 digits")
        return v

    @field_validator("current_year")
    @classmethod
    def validate_year(cls, v):
        if v not in (1, 2, 3, 4, 5):
            raise ValueError("Current year must be between 1 and 5")
        return v

    @field_validator(
        "roll_number", "full_name", "nationality", "address", "city", "state",
        "pincode", "course", "department", "guardian_name", "guardian_relation",
    )
    @classmethod
    def validate_not_blank(cls, v):
        if not str(v).strip():
            raise ValueError("Field cannot be blank")
        return v.strip()


class StudentOut(BaseModel):
    id: int
    roll_number: str
    full_name: str
    date_of_birth: date
    gender: Gender
    blood_group: Optional[BloodGroup] = None
    nationality: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    pincode: str
    course: str
    department: str
    admission_date: date
    current_year: int
    guardian_name: str
    guardian_relation: str
    guardian_phone: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "Student Details API is running"}


@app.get("/students", response_model=List[StudentOut], tags=["students"])
def list_students(db: Session = Depends(get_db)):
    """Return all students, most recently added first."""
    return db.query(Student).order_by(Student.created_at.desc()).all()


@app.get("/students/{student_id}", response_model=StudentOut, tags=["students"])
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.post(
    "/students",
    response_model=StudentOut,
    status_code=status.HTTP_201_CREATED,
    tags=["students"],
)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    student = Student(**payload.model_dump())
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Roll number or email already exists")
    db.refresh(student)
    return student


@app.put("/students/{student_id}", response_model=StudentOut, tags=["students"])
def update_student(student_id: int, payload: StudentCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    for field, value in payload.model_dump().items():
        setattr(student, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Roll number or email already exists")
    db.refresh(student)
    return student


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["students"])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return None
