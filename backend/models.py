from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import uuid
import datetime
import enum
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class InterviewType(str, enum.Enum):
    HR = "HR"
    TECHNICAL = "TECHNICAL"
    DSA = "DSA"

class InterviewStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resumes = relationship("Resume", back_populates="user")
    interviews = relationship("Interview", back_populates="user")
    coding_attempts = relationship("CodingAttempt", back_populates="user")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    file_path = Column(String)
    parsed_text = Column(Text)
    ats_score = Column(Integer, nullable=True)
    skills = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="resumes")

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    interview_type = Column(Enum(InterviewType))
    status = Column(Enum(InterviewStatus), default=InterviewStatus.IN_PROGRESS)
    overall_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="interviews")
    dialogues = relationship("Dialogue", back_populates="interview")

class Dialogue(Base):
    __tablename__ = "dialogues"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    interview_id = Column(String, ForeignKey("interviews.id"))
    question = Column(Text)
    answer = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    interview = relationship("Interview", back_populates="dialogues")

class CodingAttempt(Base):
    __tablename__ = "coding_attempts"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    question_title = Column(String)
    code = Column(Text)
    language = Column(String)
    status = Column(String) # e.g. Accepted, Wrong Answer, Error
    ai_feedback = Column(Text, nullable=True)
    time_complexity = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="coding_attempts")
