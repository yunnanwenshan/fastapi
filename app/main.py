from fastapi import FastAPI, HTTPException, status, Query, Path, Depends, Body
from starlette.responses import Response
from typing import List, Optional, Dict, Any

from app.db.models import UserAnswer, CreateUserModel, UpdateUserModel, UserResponse, Membership, CreateMembershipModel, UpdateMembershipModel, MembershipResponse, UserLogResponse, CreateLogModel, LogOperationType
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

# Membership endpoints
@app.get("/memberships", response_model=List[MembershipResponse])
def read_memberships(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum records to return"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    level: Optional[str] = Query(None, description="Filter by membership level")
):
    try:
        return api.get_all_memberships(skip=skip, limit=limit, user_id=user_id, level=level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memberships: {str(e)}")

@app.get("/memberships/{membership_id}", response_model=MembershipResponse)
def read_membership(membership_id: str = Path(..., description="Membership ID")):
    try:
        return api.get_membership(membership_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving membership: {str(e)}")

@app.post("/memberships", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
def create_membership(membership_data: CreateMembershipModel):
    try:
        return api.create_membership(membership_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create membership: {str(e)}")

@app.put("/memberships/{membership_id}", response_model=MembershipResponse)
def update_membership(
    membership_data: UpdateMembershipModel,
    membership_id: str = Path(..., description="Membership ID to update")
):
    try:
        return api.update_membership(membership_id, membership_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update membership: {str(e)}")

@app.delete("/memberships/{membership_id}", status_code=status.HTTP_200_OK)
def delete_membership(membership_id: str = Path(..., description="Membership ID to delete")):
    try:
        return api.delete_membership(membership_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete membership: {str(e)}")

@app.get("/users/{user_id}/memberships", response_model=List[MembershipResponse])
def read_user_memberships(user_id: str = Path(..., description="User ID to get memberships for")):
    try:
        return api.get_user_memberships(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user memberships: {str(e)}")

@app.post("/memberships/{membership_id}/points", response_model=MembershipResponse)
def add_membership_points(
    membership_id: str = Path(..., description="Membership ID to add points to"),
    points: int = Body(..., embed=True, description="Points to add")
):
    try:
        return api.add_membership_points(membership_id, points)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add points: {str(e)}")

# Log endpoints
@app.get("/logs", response_model=List[Dict[str, Any]])
def read_logs(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum records to return"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    operation_type: Optional[str] = Query(None, description="Filter by operation type"),
    start_date: Optional[str] = Query(None, description="Start date for filtering logs"),
    end_date: Optional[str] = Query(None, description="End date for filtering logs")
):
    """
    Retrieve system logs with filtering and pagination
    """
    try:
        return api.get_logs(
            skip=skip,
            limit=limit,
            user_id=user_id,
            operation_type=operation_type,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")

@app.get("/users/{user_id}/logs", response_model=List[Dict[str, Any]])
def read_user_logs(
    user_id: str = Path(..., description="User ID to retrieve logs for"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum records to return")
):
    """
    Get activity logs for a specific user
    """
    try:
        return api.get_user_logs(user_id, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user logs: {str(e)}")

@app.post("/logs", response_model=UserLogResponse, status_code=status.HTTP_201_CREATED)
def create_log_entry(log_data: CreateLogModel):
    """
    Create a new system log entry manually
    """
    try:
        return api.create_log(log_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create log entry: {str(e)}")

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
@app.get("/result/{user_id}")
def read_result_1(user_id: int):
    return api.read_result(user_id)
@app.get("/result/{user_id}")
def read_result_2(user_id: int):
    return api.read_result(user_id)
@app.get("/result/{user_id}")
def read_result_3(user_id: int):
    return api.read_result(user_id)
@app.get("/result/{user_id}")
def read_result_3(user_id: int):
    return api.read_result(user_id)