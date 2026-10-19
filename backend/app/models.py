import os
from pathlib import Path
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, JSON, ForeignKey, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_PATH = Path(__file__).resolve().parents[1] / 'lab.db'
engine = create_engine(os.getenv('DATABASE_URL', f'sqlite:///{DB_PATH}'), connect_args={'check_same_thread': False})
@event.listens_for(engine, 'connect')
def sqlite_config(conn, _):
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=5000')
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
class Base(DeclarativeBase): pass
class Question(Base):
    __tablename__ = 'questions'
    id = Column(String, primary_key=True)
    domain = Column(Integer, nullable=False, index=True)
    task = Column(String, nullable=False, index=True)
    family = Column(String, nullable=False)
    title = Column(String, nullable=False)
    scenario = Column(String, nullable=False)
    services = Column(JSON, nullable=False)
    concepts = Column(JSON, nullable=False)
    options = Column(JSON, nullable=False)
    correct = Column(JSON, nullable=False)
    explanation = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    references = Column(JSON, nullable=False)
    verification = Column(String, nullable=False)
    bookmarked = Column(Boolean, default=False, nullable=False)
    eligible = Column(Boolean, default=True, nullable=False)
    duplicate_of = Column(String)
    provenance = Column(JSON, default=dict, nullable=False)
class Exam(Base):
    __tablename__ = 'exams'
    id = Column(String, primary_key=True)
    mode = Column(String, nullable=False)
    status = Column(String, default='active', nullable=False)
    started_at = Column(Float, nullable=False)
    deadline = Column(Float)
    completed_at = Column(Float)
    simulated = Column(Boolean, nullable=False, default=False)
    score = Column(Float)
class ExamItem(Base):
    __tablename__ = 'exam_items'
    id = Column(Integer, primary_key=True)
    exam_id = Column(String, ForeignKey('exams.id'), nullable=False, index=True)
    question_id = Column(String, ForeignKey('questions.id'), nullable=False)
    position = Column(Integer, nullable=False)
    option_order = Column(JSON, nullable=False)
    selected = Column(JSON, default=list, nullable=False)
    flagged = Column(Boolean, default=False, nullable=False)
    scored = Column(Boolean, default=True, nullable=False)
    checked = Column(Boolean, default=False, nullable=False)
    correct = Column(Boolean)
class Setting(Base):
    __tablename__ = 'settings'
    key = Column(String, primary_key=True)
    value = Column(JSON, nullable=False)
class Flashcard(Base):
    __tablename__='flashcards'
    id=Column(String,primary_key=True)
    domain=Column(Integer,nullable=False,index=True)
    task=Column(String,nullable=False)
    chapter=Column(Integer,nullable=False,index=True)
    front=Column(String,nullable=False)
    back=Column(String,nullable=False)
    services=Column(JSON,nullable=False)
    source_page=Column(Integer,nullable=False)
    source_printed_page=Column(Integer,nullable=False)
    source_note=Column(String,nullable=False)
    references=Column(JSON,nullable=False)
    favorite=Column(Boolean,nullable=False,default=False)
    review_count=Column(Integer,nullable=False,default=0)
    remembered_count=Column(Integer,nullable=False,default=0)
    last_reviewed=Column(Float)
    due_at=Column(Float)
    interval_days=Column(Integer,nullable=False,default=0)
