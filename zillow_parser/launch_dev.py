"""Start Django and the parser worker together for local IDE development."""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

def main():
    server = subprocess.Popen(
        [PYTHON, "manage.py", "runserver", "127.0.0.1:8000"],
        cwd=ROOT,
    )
    worker = subprocess.Popen(
        [PYTHON, "manage.py", "run_zillow_parser"],
        cwd=ROOT,
    )
    processes = [server, worker]
    try:
        while True:
            for process in processes:
                code = process.poll()
                if code is not None:
                    raise SystemExit(code)
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    main()
