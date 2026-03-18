from datetime import datetime

def log_error(data, includeTimestamp = False):
    if (includeTimestamp):
        print(f"{datetime.now()} [ERROR] {data}")
    else:
        print(f"[ERROR] {data}")

def log_info(data, includeTimestamp = False):
    if (includeTimestamp):
        print(f"{datetime.now()} [INFO] {data}")
    else:
        print(f"[INFO] {data}")

def log_warning(data, includeTimestamp = False):
    if (includeTimestamp):
        print(f"{datetime.now()} [WARNING] {data}")
    else:
        print(f"[WARNING] {data}")