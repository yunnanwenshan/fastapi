# fastapi-example [![CircleCI](https://circleci.com/gh/marciovrl/fastapi-example.svg?style=svg)](https://circleci.com/gh/marciovrl/fastapi-example)

A simple example of using Fast API in Python.

## Preconditions:
- Python 3

## Clone the project

Make sure to replace `<your_database_url>` and `<your_redis_url>` with the actual URLs for your database and Redis service.

```
```
pytest app/test.py
```
## Run with docker

### Run server
### Run test

docker-compose exec app pytest test/test.py
```

### Access PostgreSQL Server

```
docker-compose exec db psql --username=fastapi --dbname=fastapi_dev
```