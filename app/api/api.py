import json
import time
from fastapi import HTTPException


def hello_world():
    return 'Hello World'


def read_user():
    with open('data/users.json') as stream:
        users = json.load(stream)

    return users


def get_user_by_id(user_id: int):
    # Get basic user information
    with open('data/users.json') as stream:
        users = json.load(stream)

    user_found = None
    for user in users:
        if user['id'] == user_id:
            user_found = user
            break

    if not user_found:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's answer history
    user_answers = []
    with open('data/answers.json') as stream:
        answers = json.load(stream)
    
    for answer in answers:
        if answer['user_id'] == user_id:
            user_answers.append(answer)
    
    # Get user's recommended cars
    recommended_car_ids = []
    with open('data/results.json') as stream:
        results = json.load(stream)
    
    for result in results:
        if result['user_id'] == user_id:
            recommended_car_ids = result['cars']
            break
    
    # Get detailed information for recommended cars
    recommended_cars = []
    with open('data/cars.json') as stream:
        cars = json.load(stream)
    
    for car in cars:
        if car['id'] in recommended_car_ids:
            recommended_cars.append(car)
    
    # Create enhanced user profile
    enhanced_user = {
        "user": user_found,
        "answers": user_answers,
        "recommended_cars": recommended_cars
    }
    
    return enhanced_user


def login_user(email: str, password: str):
    # Read user data
    with open('data/users.json') as stream:
        users = json.load(stream)
    
    user_found = None
    for user in users:
        if user['mail'] == email:
            user_found = user
            break
    
    # Check if user exists
    if not user_found:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Simple password validation - using 'password' as default password for all accounts
    if password != 'password':
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate a simple token
    timestamp = int(time.time())
    token = f"{user_found['id']}_{timestamp}"
    
    # Return user info with token
    return {
        "user": user_found,
        "token": token,
        "login_time": timestamp
    }


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