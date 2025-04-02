import json
import hashlib
import secrets
from datetime import datetime
from fastapi import HTTPException
from typing import List, Dict, Any, Optional

from app.db.models import (
    User, UserLogin, UserRegister, UserResponse, UserDetailResponse,
    Member, MemberType, CorporateMember, PersonalMember, 
    MemberCreate, MemberResponse
)


def hello_world():
    return 'Hello World'


def read_user():
    with open('data/users.json') as stream:
        users = json.load(stream)

    return users


def get_user_by_id(user_id: int):
    with open('data/users.json') as stream:
        users = json.load(stream)

    for user in users:
        if user['id'] == user_id:
            return user

    raise HTTPException(status_code=404, detail="User not found")


def read_questions(position: int):
    with open('data/questions.json') as stream:
        questions = json.load(stream)

    for question in questions:
        if question['position'] == position:
            return question


def read_alternatives(question_id: int):
    alternatives_question = []
    with open('data/alternatives.json') as stream:
        alternatives = json.load(stream)

    for alternative in alternatives:
        if alternative['question_id'] == question_id:
            alternatives_question.append(alternative)

    return alternatives_question


def create_answer(payload):
    answers = []
    result = []

    with open('data/alternatives.json') as stream:
        alternatives = json.load(stream)

    for question in payload['answers']:
        for alternative in alternatives:
            if alternative['question_id'] == question['question_id']:
                answers.append(alternative['alternative'])
                break

    with open('data/cars.json') as stream:
        cars = json.load(stream)

    for car in cars:
        if answers[0] in car.values() and answers[1] in car.values() and answers[2] in car.values():
            result.append(car)

    return result


def read_result(user_id: int):
    user_result = []

    with open('data/results.json') as stream:
        results = json.load(stream)

    with open('data/users.json') as stream:
        users = json.load(stream)

    with open('data/cars.json') as stream:
        cars = json.load(stream)

    for result in results:
        if result['user_id'] == user_id:
            for user in users:
                if user['id'] == result['user_id']:
                    user_result.append({'user': user})
                    break

        for car_id in result['cars']:
            for car in cars:
                if car_id == car['id']:
                    user_result.append(car)

    return user_result


def get_user_details(user_id: int):
    """
    Get detailed information for a specific user along with their matched cars.
    
    Args:
        user_id: The ID of the user to retrieve details for.
        
    Returns:
        A dictionary containing user information and matched car details.
        
    Raises:
        HTTPException: 404 error if user not found.
    """
    # Get user information
    user_info = None
    with open('data/users.json') as stream:
        users = json.load(stream)
    
    for user in users:
        if user['id'] == user_id:
            user_info = user
            break
    
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's car results
    user_cars = []
    with open('data/results.json') as stream:
        results = json.load(stream)
    
    car_ids = []
    for result in results:
        if result['user_id'] == user_id:
            car_ids = result['cars']
            break
    
    # Get detailed car information
    if car_ids:
        with open('data/cars.json') as stream:
            cars = json.load(stream)
        
        for car in cars:
            if car['id'] in car_ids:
                user_cars.append(car)
    
    # Combine user info and car details
    return {
        "user": user_info,
        "matched_cars": user_cars
    }


# Helper functions
def hash_password(password: str) -> str:
    """
    Generates a SHA-256 hash of the given password with a salt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password as a string
    """
    salt = secrets.token_hex(8)
    pwdhash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    return f"{salt}${pwdhash}"


def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Verifies the provided password against the stored hashed password.
    
    Args:
        stored_password: The hashed password from the database
        provided_password: The plain text password to verify
        
    Returns:
        True if the password matches, False otherwise
    """
    salt, hashed = stored_password.split('$')
    verification_hash = hashlib.sha256(f"{provided_password}{salt}".encode()).hexdigest()
    return hashed == verification_hash


def get_next_user_id() -> int:
    """Gets the next available user ID"""
    with open('data/users.json') as stream:
        users = json.load(stream)
    
    if not users:
        return 1
    return max(user['id'] for user in users) + 1


def get_next_member_id() -> int:
    """Gets the next available member ID"""
    with open('data/members.json') as stream:
        members = json.load(stream)
    
    if not members:
        return 1
    return max(member['member_id'] for member in members) + 1


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Returns user data if email exists, None otherwise"""
    with open('data/users.json') as stream:
        users = json.load(stream)
    
    for user in users:
        if user['mail'] == email:
            return user
    return None


# User authentication functions
def register_user(user_data: UserRegister) -> UserResponse:
    """
    Registers a new user.
    
    Args:
        user_data: The user data for registration
        
    Returns:
        UserResponse object with the new user data
        
    Raises:
        HTTPException: 400 if the email is already registered
    """
    # Check if email already exists
    if get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Get next user id
    user_id = get_next_user_id()
    
    # Create new user entry
    now = datetime.now()
    new_user = {
        "id": user_id,
        "name": user_data.name,
        "mail": user_data.email,
        "phone": user_data.phone,
        "password": hash_password(user_data.password),
        "registered_date": now.isoformat(),
        "last_login": None,
        "member_ids": []
    }
    
    # Save to users.json
    with open('data/users.json') as stream:
        users = json.load(stream)
    
    users.append(new_user)
    
    with open('data/users.json', 'w') as stream:
        json.dump(users, stream, indent=2)
    
    # Return user data without password
    return UserResponse(
        id=user_id,
        name=new_user["name"],
        mail=new_user["mail"],
        phone=new_user["phone"],
        registered_date=now,
        last_login=None
    )


def login_user(login_data: UserLogin) -> UserResponse:
    """
    Authenticates a user and returns user data on success.
    
    Args:
        login_data: The user login credentials
        
    Returns:
        UserResponse object with the user data
        
    Raises:
        HTTPException: 401 for invalid credentials
    """
    user = get_user_by_email(login_data.email)
    
    if not user or not verify_password(user["password"], login_data.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Update last login time
    now = datetime.now()
    
    with open('data/users.json') as stream:
        users = json.load(stream)
    
    for u in users:
        if u["id"] == user["id"]:
            u["last_login"] = now.isoformat()
            break
    
    with open('data/users.json', 'w') as stream:
        json.dump(users, stream, indent=2)
    
    # Return user data
    return UserResponse(
        id=user["id"],
        name=user["name"],
        mail=user["mail"],
        phone=user["phone"],
        registered_date=datetime.fromisoformat(user["registered_date"]),
        last_login=now
    )


def get_user_detail(user_id: int) -> UserDetailResponse:
    """
    Retrieves detailed user information including member IDs.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        UserDetailResponse object with user details
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = get_user_by_id(user_id)
    
    # Convert dates if present
    registered_date = datetime.fromisoformat(user.get("registered_date", datetime.now().isoformat()))
    last_login = None
    if user.get("last_login"):
        last_login = datetime.fromisoformat(user["last_login"])
    
    return UserDetailResponse(
        id=user["id"],
        name=user["name"],
        mail=user["mail"],
        phone=user["phone"],
        registered_date=registered_date,
        last_login=last_login,
        member_ids=user.get("member_ids", [])
    )


# Member functions
def create_member(member_data: MemberCreate) -> MemberResponse:
    """
    Creates a new member (corporate or personal).
    
    Args:
        member_data: The member data to create
        
    Returns:
        MemberResponse object with the new member data
        
    Raises:
        HTTPException: 400 for invalid data or 404 if user not found
    """
    # Verify user exists
    user = get_user_by_id(member_data.user_id)
    
    # Validate member type and associated data
    if member_data.member_type == MemberType.CORPORATE and not member_data.corporate_data:
        raise HTTPException(status_code=400, detail="Corporate member requires corporate data")
    
    if member_data.member_type == MemberType.PERSONAL and not member_data.personal_data:
        raise HTTPException(status_code=400, detail="Personal member requires personal data")
    
    # Get next member ID
    member_id = get_next_member_id()
    now = datetime.now()
    
    # Create base member data
    new_member = {
        "member_id": member_id,
        "user_id": member_data.user_id,
        "member_type": member_data.member_type,
        "created_date": now.isoformat()
    }
    
    # Add type-specific data
    if member_data.member_type == MemberType.CORPORATE:
        corporate_data = member_data.corporate_data.dict()
        new_member.update({
            "company_name": corporate_data["company_name"],
            "business_id": corporate_data["business_id"],
            "industry": corporate_data["industry"],
            "employees_count": corporate_data.get("employees_count"),
            "website": corporate_data.get("website")
        })
    else:
        personal_data = member_data.personal_data.dict()
        new_member.update({
            "first_name": personal_data["first_name"],
            "last_name": personal_data["last_name"],
            "occupation": personal_data["occupation"],
            "birth_date": personal_data.get("birth_date")
        })
        if new_member.get("birth_date"):
            new_member["birth_date"] = new_member["birth_date"].isoformat()
    
    # Save member to file
    with open('data/members.json') as stream:
        members = json.load(stream)
    
    members.append(new_member)
    
    with open('data/members.json', 'w') as stream:
        json.dump(members, stream, indent=2)
    
    # Update user's member_ids
    with open('data/users.json') as stream:
        users = json.load(stream)
    
    for u in users:
        if u["id"] == member_data.user_id:
            if "member_ids" not in u:
                u["member_ids"] = []
            u["member_ids"].append(member_id)
            break
    
    with open('data/users.json', 'w') as stream:
        json.dump(users, stream, indent=2)
    
    # Prepare response
    response = MemberResponse(
        member_id=member_id,
        user_id=member_data.user_id,
        member_type=member_data.member_type,
        created_date=now
    )
    
    if member_data.member_type == MemberType.CORPORATE:
        response.corporate_data = member_data.corporate_data
    else:
        response.personal_data = member_data.personal_data
    
    return response


def get_member(member_id: int) -> MemberResponse:
    """
    Gets a member by ID.
    
    Args:
        member_id: The ID of the member
        
    Returns:
        MemberResponse object with member data
        
    Raises:
        HTTPException: 404 if member not found
    """
    with open('data/members.json') as stream:
        members = json.load(stream)
    
    for member in members:
        if member["member_id"] == member_id:
            # Create response based on member type
            created_date = datetime.fromisoformat(member["created_date"])
            
            response = MemberResponse(
                member_id=member["member_id"],
                user_id=member["user_id"],
                member_type=member["member_type"],
                created_date=created_date
            )
            
            if member["member_type"] == MemberType.CORPORATE:
                response.corporate_data = {
                    "company_name": member["company_name"],
                    "business_id": member["business_id"],
                    "industry": member["industry"],
                    "employees_count": member.get("employees_count"),
                    "website": member.get("website")
                }
            else:
                response.personal_data = {
                    "first_name": member["first_name"],
                    "last_name": member["last_name"],
                    "occupation": member["occupation"],
                    "birth_date": None
                }
                if member.get("birth_date"):
                    response.personal_data.birth_date = datetime.fromisoformat(member["birth_date"])
            
            return response
    
    raise HTTPException(status_code=404, detail="Member not found")


def get_user_members(user_id: int) -> List[MemberResponse]:
    """
    Gets all members associated with a user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        List of MemberResponse objects
        
    Raises:
        HTTPException: 404 if user not found
    """
    # Verify user exists
    user = get_user_by_id(user_id)
    
    member_ids = user.get("member_ids", [])
    members_list = []
    
    if not member_ids:
        return members_list
    
    # Get all members for the user
    with open('data/members.json') as stream:
        all_members = json.load(stream)
    
    for member in all_members:
        if member["user_id"] == user_id:
            # Create member response
            created_date = datetime.fromisoformat(member["created_date"])
            
            member_response = MemberResponse(
                member_id=member["member_id"],
                user_id=member["user_id"],
                member_type=member["member_type"],
                created_date=created_date
            )
            
            if member["member_type"] == MemberType.CORPORATE:
                member_response.corporate_data = {
                    "company_name": member["company_name"],
                    "business_id": member["business_id"],
                    "industry": member["industry"],
                    "employees_count": member.get("employees_count"),
                    "website": member.get("website")
                }
            else:
                member_response.personal_data = {
                    "first_name": member["first_name"],
                    "last_name": member["last_name"],
                    "occupation": member["occupation"],
                    "birth_date": None
                }
                if member.get("birth_date"):
                    member_response.personal_data.birth_date = datetime.fromisoformat(member["birth_date"])
            
            members_list.append(member_response)
    
    return members_list