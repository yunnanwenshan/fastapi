# fastapi-example [![CircleCI](https://circleci.com/gh/marciovrl/fastapi-example.svg?style=svg)](https://circleci.com/gh/marciovrl/fastapi-example)

A simple example of using Fast API in Python.

## Preconditions:

- Python 3

## Clone the project

```
git clone https://github.com/marciovrl/fastapi-example.git
```

## Run local

### Install dependencies

```
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the root of your project and include the following configurations:

```
DATABASE_URL=<your_database_url>
REDIS_URL=<your_redis_url>
```

Make sure to replace `<your_database_url>` and `<your_redis_url>` with the actual URLs for your database and Redis service.

### Run server

```
uvicorn app.main:app --reload
```

### Run test

```
pytest app/test.py
```

## Run with docker

### Run server

```
docker-compose up -d --build
```

### Run test

```
docker-compose exec app pytest test/test.py
```

## API documentation (provided by Swagger UI)

```
http://127.0.0.1:8000/docs
```

### Access PostgreSQL Server

```
docker-compose exec db psql --username=fastapi --dbname=fastapi_dev
```