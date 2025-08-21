import json
from fastapi import HTTPException


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


def create_thread(thread_data):
    """
    Create a new thread.
    
    Args:
        thread_data: Dictionary containing thread information.
        
    Returns:
        The created thread data.
    """
    # For demo purposes, we'll just return the created thread with a mock ID
    # In a real application, this would save to a database
    import datetime
    
    new_thread = {
        "id": 1,  # In real app, this would be auto-generated
        "title": thread_data["title"],
        "content": thread_data["content"],
        "author": thread_data["author"],
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": None
    }
    
    return new_thread


def get_all_threads():
    """
    Get all threads.
    
    Returns:
        A list of all threads.
    """
    # For demo purposes, return sample threads
    # In a real application, this would query a database
    return [
        {
            "id": 1,
            "title": "Welcome Thread",
            "content": "This is a welcome thread for the FastAPI example.",
            "author": "admin",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": None
        }
    ]


def get_thread_by_id(thread_id: int):
    """
    Get a specific thread by ID.
    
    Args:
        thread_id: The ID of the thread to retrieve.
        
    Returns:
        The thread data if found.
        
    Raises:
        HTTPException: 404 error if thread not found.
    """
    # For demo purposes, return a sample thread if ID is 1
    # In a real application, this would query a database
    if thread_id == 1:
        return {
            "id": 1,
            "title": "Welcome Thread",
            "content": "This is a welcome thread for the FastAPI example.",
            "author": "admin",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": None
        }
    else:
        raise HTTPException(status_code=404, detail="Thread not found")


def update_thread(thread_id: int, thread_data):
    """
    Update a specific thread by ID.
    
    Args:
        thread_id: The ID of the thread to update.
        thread_data: Dictionary containing updated thread information.
        
    Returns:
        The updated thread data.
        
    Raises:
        HTTPException: 404 error if thread not found.
    """
    import datetime
    
    # For demo purposes, only allow updating thread ID 1
    # In a real application, this would update the database
    if thread_id == 1:
        updated_thread = {
            "id": 1,
            "title": thread_data.get("title", "Welcome Thread"),
            "content": thread_data.get("content", "This is a welcome thread for the FastAPI example."),
            "author": "admin",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": datetime.datetime.now().isoformat()
        }
        return updated_thread
    else:
        raise HTTPException(status_code=404, detail="Thread not found")


def delete_thread(thread_id: int):
    """
    Delete a specific thread by ID.
    
    Args:
        thread_id: The ID of the thread to delete.
        
    Raises:
        HTTPException: 404 error if thread not found.
    """
    # For demo purposes, only allow deleting thread ID 1
    # In a real application, this would delete from the database
    if thread_id != 1:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # If we get here, the deletion was "successful"