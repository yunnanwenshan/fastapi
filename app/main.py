from fastapi import FastAPI, HTTPException, status, Query, Path, Depends
from starlette.responses import Response
from typing import List, Optional, Dict, Any

from app.db.models import UserAnswer, CreateUserModel, UpdateUserModel, UserResponse
from app.api import api

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Fast API in Python"}


@app.get("/helloworld")
def hello_world():
    return api.hello_world()


@app.get("/users", response_model=List[Dict[str, Any]])
def read_users(
    skip: int = Query(0, description="Number of records to skip for pagination"),
    limit: int = Query(100, description="Maximum number of records to return"),
    name: Optional[str] = Query(None, description="Filter users by name (case-insensitive)"),
    mail: Optional[str] = Query(None, description="Filter users by email (case-insensitive)")
):
    """
    Get all users with pagination and filtering options.
    
    Returns:
        List of user objects that match the filter criteria.
    """
    return api.get_all_users(skip=skip, limit=limit, name=name, mail=mail)


@app.get("/users/{user_id}", response_model=Dict[str, Any])
def read_user_by_id(user_id: str = Path(..., description="The ID of the user to retrieve")):
    """
    Get a user by their ID.
    
    Returns:
        User details if found, 404 error if not found.
    """
    return api.get_user_by_id(user_id)


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: CreateUserModel):
    """
    Create a new user.
    
    Returns:
        Newly created user information.
        
    Raises:
        HTTPException: 400 error if email already exists.
    """
    try:
        return api.create_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_data: UpdateUserModel,
    user_id: str = Path(..., description="The ID of the user to update")
):
    """
    Update an existing user.
    
    Returns:
        Updated user information.
        
    Raises:
        HTTPException: 404 error if user not found.
        HTTPException: 400 error if trying to update to an email that already exists.
    """
    try:
        return api.update_user(user_id, user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


@app.delete("/users/{user_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def delete_user(user_id: str = Path(..., description="The ID of the user to delete")):
    """
    Delete a user.
    
    Returns:
        Confirmation message.
        
    Raises:
        HTTPException: 404 error if user not found.
    """
    try:
        return api.delete_user(user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


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