# Math Microservice – FastAPI Project

This project provides a small web service (microservice) used to calculate math operations like: factorial, fibonacci and power.

Requests to this app can be made in the browser using Swagger UI, and it will give back the results in JSON format.

## The service supports the following operations:  
- `POST /factorial` – calculates the factorial of a number (like 5! = 120)  
- `POST /fibonacci` – returns the n-th number in the Fibonacci sequence  
- `POST /power` – raises one number to the power of another (like 2^3 = 8)
- `GET /history` - returns all saved operations (requires API key)
- `GET /status` - returns uptime, queue size, active workers, and cache sizes (requires API key)

## How the app woks:
- every request is validated using **Pydantic**
- every result is checked in a **cache** first (to avoid repeating the same calculations)
- if the result is not in the cache, it is calculated
- if it is new, the request is saved in **PostgreSQL** database via a background worker (queue.Queue)
- all the logs are handled by a **background thread**, so that the user doesn't have to wait
- graceful worker shutdown and task flushing

## Authorisation  
Protected endpoints (/status, /history) require an API key:
- use the "ApiKeyName" HTTP header
- key is "secretKey"

## Monitoring
The /status endpoint returns real-time metrics:
- Uptime (seconds)
- Background queue size
- Number of active worker threads
- Cache size per operation

## Containerization
The app runs as a **Docker** container alongside a **PostgreSQL** container via docker-compose.  
Start the stack using: **docker compose up --build**

## Used Technologies
- **FastAPI** — Python web framework
- **Pydantic** — input validation and schema generation
- **SQLAlchemy ORM** — database interaction
- **PostgreSQL** — relational DB (in Docker)
- **Docker + Docker Compose** — containerized deployment
- **Threading + queue.Queue** — worker and log queues
- **Swagger UI** — auto API docs at `/docs`
- **flake8** - used for linting

## Requirements
- Docker or Rancher Desktop installed

## Run the project
cd MathMicroservice  
docker compose up --build

After a calculation is done for the first time, it is stored in the DB. You can check it using DBeaver IDE or  
you can use **docker exec -it math_postgres psql -U mathuser -d mathdb** form the terminal.  
Once inside, run **SELECT * FROM math_operations;**  
To quit: **\q**

**Ctrl + C** - to stop the app  
**docker compose down** - shut down your app and database and free up ports

## Access the API
- Swagger UI: http://localhost:8000/docs
- use ApiKeyName: secretKey for protected routes (/history, /status)
