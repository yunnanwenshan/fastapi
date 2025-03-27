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