from datetime import datetime

class Log:
    def __init__(self):
        pass

    def log_error(self, data, includeTimestamp = False):
        if (includeTimestamp):
            print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} [ERROR] {data}")
        else:
            print(f"[ERROR] {data}")

    def log_info(self, data, includeTimestamp = False):
        if (includeTimestamp):
            print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} [INFO] {data}")
        else:
            print(f"[INFO] {data}")

    def log_warning(self, data, includeTimestamp = False):
        if (includeTimestamp):
            print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} [WARNING] {data}")
        else:
            print(f"[WARNING] {data}")

    def log_divider(self):
        print("-------------------------------------------------------------------------------------------------")