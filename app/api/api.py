import json
import os.path
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from collections import defaultdict

from passlib.hash import bcrypt
from fastapi import HTTPException

from app.db.models import (
    User, CreateUserModel, UpdateUserModel, UserResponse, Membership, CreateMembershipModel,
    UpdateMembershipModel, MembershipResponse, UserLog, CreateLogModel, UserLogResponse, LogOperationType,
    UserRegistration, EmailVerification, MembershipStatistics, LevelDistribution, MembershipTrend,
    PointsDistribution, MembershipTimeFrame, MembershipStatsResponse
)

import random
import string
import re
import smtplib
from email.mime.text import MIMEText


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


def generate_verification_code() -> str:
    return ''.join(random.choices(string.digits, k=6))

def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?/~`-]', password):
        return False
    return True

def send_verification_email(email: str, code: str) -> bool:
    msg = MIMEText(f'Your verification code is: {code}')
    msg['Subject'] = 'Email Verification Code'
    msg['From'] = 'noreply@example.com'
    msg['To'] = email
    
    try:
        with smtplib.SMTP('localhost', 1025) as server:
            server.sendmail('noreply@example.com', [email], msg.as_string())
        return True
    except Exception:
        return False

def create_verification(email: str) -> str:
    with open('data/email_verifications.json') as f:
        verifications = json.load(f)
    
    code = generate_verification_code()
    now = datetime.now()
    expires_at = now + timedelta(hours=24)
    
    new_verification = {
        "email": email,
        "code": code,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "verified": False
    }
    
    verifications.append(new_verification)
    with open('data/email_verifications.json', 'w') as f:
        json.dump(verifications, f, indent=2)
    
    return code

def verify_email(email: str, code: str) -> bool:
    with open('data/email_verifications.json') as f:
        verifications = json.load(f)
    
    for entry in verifications:
        if (entry['email'] == email and 
            entry['code'] == code and 
            not entry['verified'] and 
            datetime.now() < datetime.fromisoformat(entry['expires_at'])):
            
            entry['verified'] = True
            with open('data/email_verifications.json', 'w') as f:
                json.dump(verifications, f, indent=2)
            return True
    return False


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
    
    _log_user_action(
        user_id=new_user["id"],
        operation_type="create",
        description="User account created",
        metadata={"source": "api"}
    )
    
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
    
    _log_user_action(
        user_id=user_id,
        operation_type="update",
        description="User profile updated",
        metadata={"fields_updated": list(user_data.dict(exclude_unset=True).keys())}
    )
    
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
    
    _log_user_action(
        user_id=user_id,
        operation_type="delete",
        description="User account deleted"
    )
    
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


def register_user(user_data: UserRegistration) -> Dict[str, Any]:
    if not is_valid_email(user_data.mail):
        raise HTTPException(400, "Invalid email format")
    
    with open('data/users.json') as f:
        if any(u['mail'] == user_data.mail for u in json.load(f)):
            raise HTTPException(400, "Email already registered")
    
    if not is_strong_password(user_data.password):
        raise HTTPException(400, "Password does not meet security requirements")
    
    if user_data.password != user_data.confirm_password:
        raise HTTPException(400, "Passwords do not match")
    
    code = create_verification(user_data.mail)
    if not send_verification_email(user_data.mail, code):
        raise HTTPException(500, "Failed to send verification email")
    
    return {
        "message": "Verification code sent to email",
        "verification_required": True
    }

def finalize_registration(email: str, code: str) -> UserResponse:
    if not verify_email(email, code):
        raise HTTPException(400, "Invalid verification code")
    
    with open('data/email_verifications.json') as f:
        verification = next(
            (v for v in json.load(f) 
             if v['email'] == email and v['code'] == code and v['verified']),
            None
        )
    
    if not verification:
        raise HTTPException(400, "Verification not found")
    
    with open('data/users.json') as f:
        users = json.load(f)
        user_data = next(
            (u for u in users if u['mail'] == email),
            None
        )
    
    if user_data:
        return UserResponse(**user_data)
    
    raise HTTPException(400, "User registration not completed")


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

# Log-related functions
def create_log(log_data: CreateLogModel) -> UserLogResponse:
    """Create a new user activity log entry"""
    log_id = str(uuid.uuid4())
    now = datetime.now()
    
    new_log = {
        "id": log_id,
        "user_id": log_data.user_id,
        "operation_type": log_data.operation_type.value,
        "description": log_data.description,
        "created_at": now.isoformat(),
        "ip_address": log_data.ip_address,
        "metadata": log_data.metadata
    }

    with open('data/user_logs.json') as stream:
        logs = json.load(stream)
    logs.append(new_log)
    
    with open('data/user_logs.json', 'w') as stream:
        json.dump(logs, stream, indent=2)

    return UserLogResponse(**new_log)

def get_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    operation_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Retrieve filtered logs with pagination"""
    with open('data/user_logs.json') as stream:
        logs = json.load(stream)

    filtered = logs
    if user_id:
        filtered = [log for log in filtered if log['user_id'] == user_id]
    if operation_type:
        filtered = [log for log in filtered if log['operation_type'].lower() == operation_type.lower()]
    if start_date:
        filtered = [log for log in filtered if datetime.fromisoformat(log['created_at']) >= start_date]
    if end_date:
        filtered = [log for log in filtered if datetime.fromisoformat(log['created_at']) <= end_date]

    paginated = filtered[skip:skip+limit]
    return [{
        **log,
        "created_at": datetime.fromisoformat(log["created_at"])
    } for log in paginated]

def get_user_logs(user_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get logs for a specific user"""
    return get_logs(user_id=user_id, skip=skip, limit=limit)

def _log_user_action(
    user_id: str,
    operation_type: str,
    description: str,
    metadata: Optional[dict] = None
):
    """Helper to log user actions silently"""
    try:
        create_log(CreateLogModel(
            user_id=user_id,
            operation_type=LogOperationType(operation_type),
            description=description,
            metadata=metadata
        ))
    except Exception as e:
        pass

def get_membership_statistics(
    time_frame: MembershipTimeFrame = None,
    calculate_trends: bool = True,
    calculate_points_distribution: bool = True
) -> MembershipStatsResponse:
    with open('data/memberships.json') as f:
        memberships = [Membership(**m) for m in json.load(f)]

    now = datetime.now()
    filtered = memberships
    
    if time_frame:
        if time_frame.start_date:
            filtered = [m for m in filtered if m.created_at >= time_frame.start_date]
        if time_frame.end_date:
            filtered = [m for m in filtered if m.created_at <= time_frame.end_date]
        if time_frame.level:
            filtered = [m for m in filtered if m.level == time_frame.level]

    total = len(filtered)
    active = sum(1 for m in filtered if m.is_active and m.valid_until > now)
    inactive = total - active
    avg_points = sum(m.points for m in filtered)/total if total > 0 else 0
    levels = [m.level for m in filtered]
    top_level = max(set(levels), key=levels.count) if levels else "none"
    
    newest_count = sum(1 for m in filtered if (now - m.created_at).days < 30)
    expiring_soon = sum(1 for m in filtered if (m.valid_until - now).days < 30)

    stats = MembershipStatistics(
        total_members=total,
        active_members=active,
        inactive_members=inactive,
        average_points=round(avg_points, 2),
        top_level=top_level,
        newest_members_count=newest_count,
        expiring_soon_count=expiring_soon,
        created_at=datetime.now()
    )

    level_dist = calculate_level_distribution(filtered)
    trends = calculate_membership_trends(filtered) if calculate_trends else []
    points_dist = calculate_points_distribution(filtered) if calculate_points_distribution else []

    return MembershipStatsResponse(
        overall=stats,
        level_distribution=level_dist,
        trends=trends,
        points_distribution=points_dist
    )

def calculate_level_distribution(memberships: List[Membership]) -> List[LevelDistribution]:
    level_counts = defaultdict(int)
    total = len(memberships)
    
    for m in memberships:
        level_counts[m.level] += 1

    return [
        LevelDistribution(
            level=level,
            count=count,
            percentage=round(count/total*100, 2) if total > 0 else 0
        )
        for level, count in level_counts.items()
    ]

def calculate_membership_trends(memberships: List[Membership]) -> List[MembershipTrend]:
    trends = defaultdict(lambda: {'new': 0, 'churned': 0, 'total': 0})
    current_date = datetime.now()
    
    for m in memberships:
        month_key = m.created_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        trends[month_key]['new'] += 1

    for m in memberships:
        if m.valid_until < current_date:
            churn_month = m.valid_until.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            trends[churn_month]['churned'] += 1

    sorted_months = sorted(trends.keys())
    running_total = 0
    trends_list = []
    
    for month in sorted_months:
        running_total += trends[month]['new'] - trends[month]['churned']
        trends_list.append(MembershipTrend(
            date=month,
            new_members=trends[month]['new'],
            churned_members=trends[month]['churned'],
            net_growth=trends[month]['new'] - trends[month]['churned'],
            total_members=running_total
        ))
    
    return trends_list

def calculate_points_distribution(memberships: List[Membership]) -> List[PointsDistribution]:
    ranges = [
        (0, 100), (101, 500), 
        (501, 1000), (1001, 5000), 
        (5001, float('inf'))
    ]
    dist = []
    total = len(memberships)
    
    for r_start, r_end in ranges:
        count = sum(1 for m in memberships if r_start <= m.points <= r_end)
        percentage = round(count/total*100, 2) if total > 0 else 0
        dist.append(PointsDistribution(
            range_start=r_start,
            range_end=r_end if r_end != float('inf') else 10000,
            count=count,
            percentage=percentage
        ))
    
    return dist

def get_membership_growth_rate(start_date: datetime, end_date: datetime) -> float:
    with open('data/memberships.json') as f:
        memberships = json.load(f)
    
    initial = sum(1 for m in memberships if datetime.fromisoformat(m['created_at']) < start_date)
    final = sum(1 for m in memberships if datetime.fromisoformat(m['created_at']) <= end_date)
    
    return round((final - initial)/initial*100, 2) if initial > 0 else 0

def get_member_retention_rate(start_date: datetime, end_date: datetime) -> float:
    with open('data/memberships.json') as f:
        memberships = [Membership(**m) for m in json.load(f)]
    
    cohort = [m for m in memberships if start_date <= m.created_at <= end_date]
    retained = sum(1 for m in cohort if m.valid_until > end_date and m.is_active)
    
    return round(retained/len(cohort)*100, 2) if cohort else 0