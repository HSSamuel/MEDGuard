import multiprocessing

# Number of workers (e.g., 2 * CPU cores + 1)
workers = multiprocessing.cpu_count() * 2 + 1

# Set the worker class to eventlet for WebSocket support
worker_class = 'eventlet'

# Bind to the port Render expects
bind = "0.0.0.0:10000"

# Optional: Increase the timeout to give workers more time
timeout = 120


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %d)", worker.pid)


def when_ready(server):
    server.log.info("Gunicorn is ready and listening at http://%s", bind)