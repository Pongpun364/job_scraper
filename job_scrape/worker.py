import os
import time

from celery import Celery
from indeed import perform_scrape

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="scraper_task")
def create_task(num):
    time.sleep(int(num) * 10)
    return True


@celery.task(name="add_scrape")
def add_scrape(search_keyword: str):
    name = search_keyword.replace(" ", '_')
    table_name = f"{name}_final"
    perform_scrape(query=search_keyword)
    return table_name