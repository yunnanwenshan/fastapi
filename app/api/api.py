import json
import os.path
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from passlib.hash import bcrypt
from fastapi import HTTPException

from app.db.models import User, CreateUserModel, UpdateUserModel, UserResponse, Membership, CreateMembershipModel, UpdateMembershipModel, MembershipResponse


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    return bcrypt.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.verify(plain_password, hashed_password)


def create_user(user_data: CreateUserModel) -> UserResponse:
    """
    Create a new user.
    
    Args:
        user_data: User data from CreateUserModel
        
    Returns:
        Newly created user information (UserResponse)
        
    Raises:
        HTTPException: 400 error if email already exists
    """
    # Check if email already exists
    with open('data/users.json') as stream:
        users = json.load(stream)
    
    for user in users:
        if user.get('mail') == user_data.mail:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user with hashed password
    now = datetime.now()
    new_user = {
        "id": str(uuid.uuid4()),
        "name": user_data.name,
        "mail": user_data.mail,
        "phone": user_data.phone,
        "password_hash": hash_password(user_data.password),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    users.append(new_user)
    
    # Save updated users list
    with open('data/users.json', 'w') as stream:
        json.dump(users, stream, indent=2)
    
    # Return user data without password hash
    return UserResponse(
        id=new_user["id"],
        name=new_user["name"],
        mail=new_user["mail"],
        phone=new_user["phone"],
        created_at=now,
        updated_at=now
    )


def update_user(user_id: str, user_data: UpdateUserModel) -> UserResponse:
    """
    Update an existing user.
    
    Args:
        user_id: ID of the user to update
        user_data: User data from UpdateUserModel
        
    Returns:
        Updated user information (UserResponse)
        
    Raises:
        HTTPException: 404 error if user not found
        HTTPException: 400 error if trying to update to an email that already exists
    """
    # Load current users
    with open('data/users.json') as stream:
        users = json.load(stream)
    
    # Find user to update
    found = False
    updated_user = None
    
    for i, user in enumerate(users):
        # Check if trying to update email to one that already exists
        if user_data.mail and user_data.mail != users[i].get('mail'):
            for existing_user in users:
                if existing_user.get('mail') == user_data.mail and str(existing_user.get('id')) != user_id:
                    raise HTTPException(status_code=400, detail="Email already registered by another user")
        
        if str(user.get('id')) == user_id:
            found = True
            
            # Update fields if provided
            if user_data.name is not None:
                users[i]['name'] = user_data.name
            if user_data.mail is not None:
                users[i]['mail'] = user_data.mail
            if user_data.phone is not None:
                users[i]['phone'] = user_data.phone
            if user_data.password is not None:
                users[i]['password_hash'] = hash_password(user_data.password)
            
            # Update the updated_at timestamp
            users[i]['updated_at'] = datetime.now().isoformat()
            updated_user = users[i]
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Save updated users list
    with open('data/users.json', 'w') as stream:
        json.dump(users, stream, indent=2)
    
    # Return updated user data
    return UserResponse(
        id=updated_user["id"],
        name=updated_user["name"],
        mail=updated_user["mail"],
        phone=updated_user["phone"],
        created_at=datetime.fromisoformat(updated_user["created_at"]),
        updated_at=datetime.fromisoformat(updated_user["updated_at"])
    )


def delete_user(user_id: str) -> Dict[str, str]:
    """
    Delete a user.
    
    Args:
        user_id: ID of the user to delete
        
    Returns:
        Confirmation message
        
    Raises:
        HTTPException: 404 error if user not found
    """
    # Load current users
    with open('data/users.json') as stream:
        users = json.load(stream)
    
    # Find and remove user
    initial_length = len(users)
    users = [user for user in users if str(user.get('id')) != user_id]
    
    if len(users) == initial_length:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Save updated users list
    with open('data/users.json', 'w') as stream:
        json.dump(users, stream, indent=2)
    
    return {"message": "User deleted successfully"}


def get_user_by_id(user_id: str) -> Dict[str, Any]:
    """
    Get a user by ID.
    
    Args:
        user_id: ID of the user to retrieve
        
    Returns:
        User information
        
    Raises:
        HTTPException: 404 error if user not found
    """
    try:
        with open('data/users.json') as stream:
            users = json.load(stream)

        for user in users:
            if str(user.get('id')) == user_id:
                # Convert ISO date strings to datetime objects for response
                user_copy = user.copy()
                if 'password_hash' in user_copy:
                    del user_copy['password_hash']
                if 'created_at' in user_copy:
                    user_copy['created_at'] = datetime.fromisoformat(user_copy['created_at'])
                if 'updated_at' in user_copy:
                    user_copy['updated_at'] = datetime.fromisoformat(user_copy['updated_at'])
                return user_copy

        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")


def get_all_users(skip: int = 0, limit: int = 100, name: Optional[str] = None, mail: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all users with optional filtering and pagination.
    
    Args:
        skip: Number of users to skip (for pagination)
        limit: Maximum number of users to return
        name: Filter users by name (case-insensitive substring match)
        mail: Filter users by email (case-insensitive substring match)
        
    Returns:
        List of users matching criteria
    """
    try:
        with open('data/users.json') as stream:
            users = json.load(stream)
        
        # Apply filters if provided
        filtered_users = users
        
        if name:
            name_lower = name.lower()
            filtered_users = [user for user in filtered_users if name_lower in user.get('name', '').lower()]
        
        if mail:
            mail_lower = mail.lower()
            filtered_users = [user for user in filtered_users if mail_lower in user.get('mail', '').lower()]
        
        # Apply pagination
        paginated_users = filtered_users[skip:skip+limit]
        
        # Remove password hashes and convert date strings for response
        result = []
        for user in paginated_users:
            user_copy = user.copy()
            if 'password_hash' in user_copy:
                del user_copy['password_hash']
            if 'created_at' in user_copy:
                user_copy['created_at'] = datetime.fromisoformat(user_copy['created_at'])
            if 'updated_at' in user_copy:
                user_copy['updated_at'] = datetime.fromisoformat(user_copy['updated_at'])
            result.append(user_copy)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")


def hello_world():
    return 'Hello World'


def read_user():
    return get_all_users()


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

# Membership-related functions
def create_membership(membership_data: CreateMembershipModel) -> MembershipResponse:
    """Create a new membership for a user"""
    # Validate user exists
    with open('data/users.json') as stream:
        users = json.load(stream)
    user_exists = any(str(u.get('id')) == membership_data.user_id for u in users)
    if not user_exists:
        raise HTTPException(status_code=400, detail="User does not exist")

    # Generate membership data
    now = datetime.now()
    membership_id = str(uuid.uuid4())
    new_membership = {
        "id": membership_id,
        "user_id": membership_data.user_id,
        "level": membership_data.level,
        "points": membership_data.points,
        "valid_from": membership_data.valid_from.isoformat(),
        "valid_until": membership_data.valid_until.isoformat(),
        "is_active": membership_data.is_active,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }

    # Save to memberships.json
    with open('data/memberships.json') as stream:
        memberships = json.load(stream)
    memberships.append(new_membership)
    with open('data/memberships.json', 'w') as stream:
        json.dump(memberships, stream, indent=2)

    return MembershipResponse(**new_membership)

def update_membership(membership_id: str, membership_data: UpdateMembershipModel) -> MembershipResponse:
    """Update an existing membership"""
    with open('data/memberships.json') as stream:
        memberships = json.load(stream)

    updated = False
    for i, m in enumerate(memberships):
        if m['id'] == membership_id:
            # Update provided fields
            if membership_data.user_id is not None:
                memberships[i]['user_id'] = membership_data.user_id
            if membership_data.level is not None:
                memberships[i]['level'] = membership_data.level
            if membership_data.points is not None:
                memberships[i]['points'] = membership_data.points
            if membership_data.valid_from is not None:
                memberships[i]['valid_from'] = membership_data.valid_from.isoformat()
            if membership_data.valid_until is not None:
                memberships[i]['valid_until'] = membership_data.valid_until.isoformat()
            if membership_data.is_active is not None:
                memberships[i]['is_active'] = membership_data.is_active
            
            memberships[i]['updated_at'] = datetime.now().isoformat()
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Membership not found")

    with open('data/memberships.json', 'w') as stream:
        json.dump(memberships, stream, indent=2)

    return MembershipResponse(**memberships[i])

def delete_membership(membership_id: str) -> Dict[str, str]:
    """Delete a membership by ID"""
    with open('data/memberships.json') as stream:
        memberships = json.load(stream)
    
    original_count = len(memberships)
    memberships = [m for m in memberships if m['id'] != membership_id]
    
    if len(memberships) == original_count:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    with open('data/memberships.json', 'w') as stream:
        json.dump(memberships, stream, indent=2)
    
    return {"message": "Membership deleted successfully"}

def get_membership(membership_id: str) -> Dict[str, Any]:
    """Get a single membership by ID"""
    with open('data/memberships.json') as stream:
        memberships = json.load(stream)
    
    for m in memberships:
        if m['id'] == membership_id:
            # Convert date strings to datetime objects
            m_copy = m.copy()
            m_copy['valid_from'] = datetime.fromisoformat(m['valid_from'])
            m_copy['valid_until'] = datetime.fromisoformat(m['valid_until'])
            m_copy['created_at'] = datetime.fromisoformat(m['created_at'])
            m_copy['updated_at'] = datetime.fromisoformat(m['updated_at'])
            return m_copy
    
    raise HTTPException(status_code=404, detail="Membership not found")

def get_all_memberships(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    level: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get all memberships with filtering and pagination"""
    with open('data/memberships.json') as stream:
        memberships = json.load(stream)
    
    # Apply filters
    filtered = memberships
    if user_id:
        filtered = [m for m in filtered if m['user_id'] == user_id]
    if level:
        filtered = [m for m in filtered if m['level'].lower() == level.lower()]
    
    # Apply pagination
    paginated = filtered[skip : skip + limit]
    
    # Convert date fields
    result = []
    for m in paginated:
        m_copy = m.copy()
        m_copy['valid_from'] = datetime.fromisoformat(m['valid_from'])
        m_copy['valid_until'] = datetime.fromisoformat(m['valid_until'])
        m_copy['created_at'] = datetime.fromisoformat(m['created_at'])
        m_copy['updated_at'] = datetime.fromisoformat(m['updated_at'])
        result.append(m_copy)
    
    return result

def get_user_memberships(user_id: str) -> List[Dict[str, Any]]:
    """Get all memberships for a specific user"""
    return get_all_memberships(user_id=user_id)

def add_membership_points(membership_id: str, points: int) -> MembershipResponse:
    """Add points to a membership and update level"""
    with open('data/memberships.json') as stream:
        memberships = json.load(stream)
    
    updated = False
    for i, m in enumerate(memberships):
        if m['id'] == membership_id:
            # Update points
            memberships[i]['points'] += points
            
            # Update level based on points
            new_points = memberships[i]['points']
            if new_points >= 1000:
                level = "platinum"
            elif new_points >= 500:
                level = "gold"
            elif new_points >= 200:
                level = "silver"
            else:
                level = "bronze"
            memberships[i]['level'] = level
            
            memberships[i]['updated_at'] = datetime.now().isoformat()
            updated = True
            break
    
    if not updated:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    with open('data/memberships.json', 'w') as stream:
        json.dump(memberships, stream, indent=2)
    
    return MembershipResponse(**memberships[i])