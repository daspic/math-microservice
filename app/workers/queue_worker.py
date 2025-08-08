import threading
import queue
# import time
from app.models.db_models import MathOperation
from app.db.session import SessionLocal


#  Task queue
#  this holds the tasks for multithreading
task_queue = queue.Queue()

shutdown_event = threading.Event()

log_queue = queue.Queue()


# Worker function that runs in a separate thread
def worker():
    while not shutdown_event.is_set():
        task = None
        try:
            task = task_queue.get(timeout=1)
            if task is None:
                break
            # time.sleep(5)
            db = SessionLocal()
            record = MathOperation(**task)
            db.add(record)
            db.commit()
            db.close()
            print(f"[{threading.current_thread().name}] Processed task: {task}")
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Worker error: {e}")
        finally:
            if task is not None:
                task_queue.task_done()


def log_worker():
    while not shutdown_event.is_set():
        log_message = None
        try:
            log_message = log_queue.get(timeout=0.1)
            if log_message is None:
                break
            # Process log
            print(f"[log] {log_message}")
        except queue.Empty:
            continue
        finally:
            if log_message is not None:
                log_queue.task_done()


# Start multiple worker threads
NUM_WORKERS = 4
worker_threads = []

for i in range(NUM_WORKERS):
    thread = threading.Thread(target=worker, daemon=True, name=f"Worker-{i+1}")
    thread.start()
    worker_threads.append(thread)


# Log processing worker
log_thread = threading.Thread(target=log_worker, daemon=True, name="Logger")
log_thread.start()
worker_threads.append(log_thread)  # Add to the list for shutdown tracking


# Function to enqueue a new task
def enqueue_math_operation(operation: str, input_data: str, result: float):
    task = {
        "operation": operation,
        "input_data": input_data,
        "result": result,
    }
    task_queue.put(task)
