from typing import Annotated
from fastapi import FastAPI, Request, HttpException, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas import Studentcreate, studentresponse, Stdcreate, Stdresponse

import models
from database import base, engine, get_db
from sqlalchemy import Select
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)  #this will create the tables if not already created. and if already it does nothing. it will not delete the existing tables or data.



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")





@app.get("/")
@app.get("/students", response_model=list[studentresponse])
def get_students(request: Request):
    return templates.TemplateResponse(request, "stuss.html", {"students": students})


@app.get("/links", include_in_schema=False)
def get_links(request: Request):
    return templates.TemplateResponse(request, "home.html", {"links": links})


@app.post("/users", response_model=Stdresponse, status_code=status.HTTP_201_CREATED)
def create_user(user: Stdcreate, db: Annotated[Session, Depends(get_db)]):
    # checking username uniqueness
    result = db.execute(Select(models.student).where(models.student.username == user.username)).first()

    existing_user = result.scalars().first() 
    if existing_user:
        raise HttpException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists"
        )

    # checking email uniqueness
    result = db.execute(Select(models.student).where(models.student.useremail == user.useremail)).first()

    existing_email = result.scalars().first() 
    if existing_email:
        raise HttpException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    #now creating the user
    new_user = models.student(
        username=user.username,
        useremail=user.useremail
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/students/{student_id}", response_model=studentresponse)
def get_student(request: Request, student_id: int):

    for student in students:
        if student["id"] == student_id:
            return templates.TemplateResponse(
                request,
                "single.html",
                {"single": student}
            )

    return {"error": "Student not founded"}