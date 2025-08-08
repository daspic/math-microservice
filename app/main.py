from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router as math_router
from app.workers.queue_worker import worker_threads, shutdown_event, task_queue


@asynccontextmanager
async def lifespan(application: FastAPI):
    # App startup
    yield
    # App shutdown
    print("Shutting down worker threads...")
    shutdown_event.set()
    for _ in worker_threads:
        task_queue.put(None)
    for thread in worker_threads:
        thread.join()
    print("All workers shut down cleanly.")

app = FastAPI(title="Math Microservice", lifespan=lifespan)
app.include_router(math_router)
print("[main.py] Router loaded:", math_router)
