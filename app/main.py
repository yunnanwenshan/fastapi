from fastapi import FastAPI, HTTPException
from starlette.responses import Response

from app.db.models import UserAnswer, UserLogin, UserRegister, MemberCreate
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


@app.get("/users/{user_id}/details")
def get_user_details(user_id: int):
    """
    Get detailed information for a specific user along with their matched cars.
    
    Returns:
        A dictionary containing user information and detailed car information that match user preferences.
        If the user is not found, returns a 404 error.
    """
    return api.get_user_details(user_id)


@app.post("/users/register")
def register_user(user_data: UserRegister):
    """
    Register a new user.
    
    Returns:
        User data excluding password. 400 error if email already exists.
    """
    return api.register_user(user_data)


@app.post("/users/login")
def login_user(login_data: UserLogin):
    """
    Authenticate a user with email and password.
    
    Returns:
        User data on success. 401 error if credentials are invalid.
    """
    return api.login_user(login_data)


@app.get("/users/{user_id}/detail")
def get_user_detail(user_id: int):
    """
    Get detailed user information including associated member IDs.
    
    Returns:
        Detailed user data including member IDs. 404 error if user not found.
    """
    return api.get_user_detail(user_id)


@app.get("/users/{user_id}/members")
def get_user_members(user_id: int):
    """
    Get all members associated with a specific user.
    
    Returns:
        List of member objects. Empty list if no members. 404 error if user not found.
    """
    return api.get_user_members(user_id)


@app.post("/members")
def create_member(member_data: MemberCreate):
    """
    Create a new member (corporate or personal) associated with a user.
    
    Returns:
        Member data on success. 400 error if data invalid, 404 error if user not found.
    """
    return api.create_member(member_data)


@app.get("/members/{member_id}")
def get_member(member_id: int):
    """
    Get information for a specific member.
    
    Returns:
        Member data on success. 404 error if member not found.
    """
    return api.get_member(member_id)


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