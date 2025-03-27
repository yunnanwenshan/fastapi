from fastapi import FastAPI, HTTPException
from starlette.responses import Response

from app.db.models import UserAnswer, UserLogin
from app.api import api

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Fast API in Python"}


@app.get("/helloworld")
def hello_world():
    return api.hello_world()


@app.get("/user")
def read_user():
    return api.read_user()


@app.get("/users/{user_id}")
def read_user_by_id(user_id: int):
    """
    Get a user by their ID.
    Returns user details if found, 404 error if not found.
    """
    return api.get_user_by_id(user_id)


@app.get("/question/{position}", status_code=200)
def read_questions(position: int, response: Response):
    question = api.read_questions(position)

    if not question:
        raise HTTPException(status_code=400, detail="Error")

    return question


@app.get("/alternatives/{question_id}")
def read_alternatives(question_id: int):
    return api.read_alternatives(question_id)


@app.post("/answer", status_code=201)
def create_answer(payload: UserAnswer):
    payload = payload.dict()

    return api.create_answer(payload)


@app.get("/result/{user_id}")
def read_result(user_id: int):
    return api.read_result(user_id)


@app.post("/login", status_code=200)
def login_user(payload: UserLogin):
    return api.login_user(email=payload.email, password=payload.password)