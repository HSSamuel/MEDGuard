from celery import Celery

# We configure Celery to use a non-network-dependent broker 
# (filesystem) to bypass the Redis dependency when running locally 
# without the Redis server.
celery_app = Celery(
    __name__, 
    broker='filesystem://', 
    backend=None # Disable backend completely
)

# You may need to create a temporary directory for the filesystem broker:
# import os
# os.makedirs('./celery_broker', exist_ok=True)