from datetime import datetime
import os

def debug(s: str) -> None:
    env = os.environ.get('APP_ENV') or "DEBUG"
    if env == "DEBUG":
        now = datetime.now()
        print(f"{now.strftime("%H:%M:%S.%f")[:-2]}: {s}")