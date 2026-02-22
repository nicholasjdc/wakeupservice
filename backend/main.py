import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

load_dotenv()

SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
NOTIFY_EMAIL = os.environ["NOTIFY_EMAIL"]

DATABASE_URL = "sqlite:///./survey.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    call_time = Column(String)
    max_attempts = Column(String)
    notes = Column(String)


Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/api")


class SurveySubmission(BaseModel):
    name: str
    phone: str
    call_time: str
    max_attempts: str
    notes: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def send_notification(submission: SurveySubmission):
    msg = EmailMessage()
    msg["Subject"] = f"New Survey Submission from {submission.name}"
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFY_EMAIL
    msg.set_content(
        f"Name: {submission.name}\n"
        f"Phone: {submission.phone}\n"
        f"When to call: {submission.call_time}\n"
        f"Max attempts: {submission.max_attempts}\n"
        f"Notes: {submission.notes}\n"
    )
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


@app.post("/submit")
def submit_survey(submission: SurveySubmission, db: Session = Depends(get_db)):
    row = Submission(**submission.model_dump())
    db.add(row)
    db.commit()
    print(f"Saved submission #{row.id}: {submission.name}")
    send_notification(submission)
    return {"status": "ok", "id": row.id}


@app.get("/submissions")
def list_submissions(db: Session = Depends(get_db)):
    rows = db.query(Submission).all()
    return [
        {"id": r.id, "name": r.name, "phone": r.phone,
         "call_time": r.call_time, "max_attempts": r.max_attempts,
         "notes": r.notes}
        for r in rows
    ]
