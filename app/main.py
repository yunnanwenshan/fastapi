from fastapi import FastAPI, HTTPException
from starlette.responses import Response

from app.db.models import UserAnswer, Thread, ThreadCreate, ThreadUpdate
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


@app.post("/threads", status_code=201)
def create_thread(thread: ThreadCreate):
    """
    Create a new thread with the given data.
    
    Returns:
        The created thread data if successful.
        400 error if validation fails.
    """
    return api.create_thread(thread.dict())


@app.get("/threads")
def get_all_threads():
    """
    Get all threads.
    
    Returns:
        A list of all threads.
    """
    return api.get_all_threads()


@app.get("/threads/{thread_id}")
def get_thread_by_id(thread_id: int):
    """
    Get a specific thread by ID.
    
    Returns:
        The thread details if found, 404 error if not found.
    """
    return api.get_thread_by_id(thread_id)


@app.put("/threads/{thread_id}")
def update_thread(thread_id: int, thread: ThreadUpdate):
    """
    Update a specific thread by ID.
    
    Returns:
        The updated thread data if successful.
        404 error if thread not found.
        400 error if validation fails.
    """
    return api.update_thread(thread_id, thread.dict())


@app.delete("/threads/{thread_id}", status_code=204)
def delete_thread(thread_id: int):
    """
    Delete a specific thread by ID.
    
    Returns:
        204 No Content if successful.
        404 error if thread not found.
    """
    api.delete_thread(thread_id)
    return Response(status_code=204)