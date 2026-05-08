import logging
import os
import random
import time
import schedule
from prometheus_client import Counter, Gauge, Histogram, start_http_server

LOG_FILE = os.getenv("LOG_FILE", "/app/logs/heartbeat.log")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ],
)

job_runs_total = Counter("job_runs_total", "Total number of job runs", ["job_name"])
job_failures_total = Counter("job_failures_total", "Total number of failed job runs", ["job_name"])
job_duration_seconds = Histogram("job_duration_seconds", "Job duration in seconds", ["job_name"])
job_last_success = Gauge("job_last_success_timestamp", "Unix timestamp of last successful run", ["job_name"])

JOB_NAME = "heartbeat"

def run_job():
    start = time.time()
    try:
        logging.info("heartbeat job started")
        time.sleep(random.uniform(0.2, 1.0))
        job_runs_total.labels(job_name=JOB_NAME).inc()
        job_last_success.labels(job_name=JOB_NAME).set_to_current_time()
        logging.info("heartbeat job completed successfully")
    except Exception:
        job_failures_total.labels(job_name=JOB_NAME).inc()
        logging.exception("heartbeat job failed")
    finally:
        elapsed = time.time() - start
        job_duration_seconds.labels(job_name=JOB_NAME).observe(elapsed)

if __name__ == "__main__":
    start_http_server(METRICS_PORT)
    logging.info("metrics server started on port %s", METRICS_PORT)
    schedule.every(1).minutes.do(run_job)
    run_job()

    while True:
        schedule.run_pending()
        time.sleep(1)