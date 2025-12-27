import os

    # Define the base broker path
    broker_dir = os.path.join(os.getcwd(), 'celery_broker')
    
    # Define the required subdirectories for Kombu filesystem transport
    # It needs a folder for the specific queue (usually 'celery' or 'data_in')
    folders = [
        broker_dir,
        os.path.join(broker_dir, 'out'),
        os.path.join(broker_dir, 'processed')
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created: {folder}")

    # Crucial Step: Define the 'data_in' path specifically for the default queue
    # Celery's default queue is named 'celery'.
    # The filesystem transport often looks for a file or folder matching the queue name.
    # For simplicity, let's update the config to point to these specific paths.
    ```