from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройка базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:mysecretpassword@postgres-service:5432/postgres")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель для SQLAlchemy
class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    status = Column(String)

Base.metadata.create_all(bind=engine)

# Модель для Pydantic
class Task(BaseModel):
    id: int
    text: str
    status: str  # "todo", "in-progress", "done"

app = FastAPI()

# CRUD-операции
@app.get("/tasks", response_model=List[Task])
def read_tasks():
    db = SessionLocal()
    tasks = db.query(TaskModel).all()
    db.close()
    return tasks

@app.post("/tasks", response_model=Task)
def create_task(text: str, status: str = "todo"):
    db = SessionLocal()
    db_task = TaskModel(text=text, status=status)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return db_task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, new_status: str):
    db = SessionLocal()
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = new_status
    db.commit()
    db.refresh(task)
    db.close()
    return task
