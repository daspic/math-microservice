from fastapi import APIRouter, Depends, Header, HTTPException
# BackgroundTasks
from sqlalchemy.orm import Session
from app.models.schemas import (FactorialRequest, FibonacciRequest, PowerRequest,
                                OperationRecord)
from app.models.db_models import MathOperation
from app.db.session import SessionLocal
from typing import List

from app.services.math_service import factorial, fibonacci, power
from app.workers.queue_worker import (enqueue_math_operation,
                                      task_queue, worker_threads, log_queue)
from app.utils.cache import factorial_cache, fibonacci_cache, power_cache
from app.utils.monitoring import APP_START_TIME
import json
import time

API_KEY = "secretKey"
API_KEY_NAME = "ApiKeyName"

router = APIRouter()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


@router.post("/factorial")
async def calc_factorial(
        data: FactorialRequest,
):
    source = ""
    start = time.time()
    if data.number in factorial_cache:
        result = factorial_cache[data.number]
        source = "cache"
    else:
        result = factorial(data.number)
        factorial_cache[data.number] = result
        enqueue_math_operation("factorial",
                               json.dumps(data.model_dump()), result)
        source = "fresh"
    duration = time.time() - start
    log_queue.put(
        f"[/factorial] {source} → n={data.number},"
        f" result={result}, time={duration:.6f}s"
    )
    log_queue.join()
    return {"result": result}


@router.post("/fibonacci")
async def calc_fibonacci(
        data: FibonacciRequest,
):
    source = ""
    start = time.time()
    if data.n in fibonacci_cache:
        result = fibonacci_cache[data.n]
        source = "cache"
    else:
        result = fibonacci(data.n)
        fibonacci_cache[data.n] = result
        enqueue_math_operation("fibonacci", json.dumps(data.model_dump()), result)
        source = "fresh"
    duration = time.time() - start
    log_queue.put(
        f"[/fibonacci] {source} → n={data.n}, result={result}, time={duration:.6f}s"
    )
    log_queue.join()
    return {"result": result}


@router.post("/power")
async def calc_power(
        data: PowerRequest,
):
    source = ""
    start = time.time()
    key = (data.base, data.exponent)
    if key in power_cache:
        result = power_cache[key]
        source = "cache"
    else:
        result = power(data.base, data.exponent)
        power_cache[key] = result
        enqueue_math_operation("power",
                               json.dumps(data.model_dump()), result)
        source = "fresh"
    duration = time.time() - start
    log_queue.put(
        f"[/power] {source} → n={data.base, data.exponent}, "
        f"result={result}, time={duration:.6f}s"
    )
    log_queue.join()
    return {"result": result}


@router.get("/history", response_model=List[OperationRecord],
            dependencies=[Depends(verify_api_key)])
def get_history(db: Session = Depends(get_db)):
    records = db.query(MathOperation).all()
    return records


@router.get("/status", dependencies=[Depends(verify_api_key)])
def get_status():
    uptime_seconds = time.time() - APP_START_TIME
    return {
        "uptime_seconds": round(uptime_seconds, 2),
        "queue_size": task_queue.qsize(),
        "active_workers": sum(1 for t in worker_threads if t.is_alive()),
        "cache_sizes": {
            "factorial": len(factorial_cache),
            "fibonacci": len(fibonacci_cache),
            "power": len(power_cache)
        }
    }


def save_operation_to_db(
        db: Session,
        operation: str,
        input_data: str,
        result: float
):
    record = MathOperation(
        operation=operation,
        input_data=input_data,
        result=result
    )
    db.add(record)
    db.commit()
