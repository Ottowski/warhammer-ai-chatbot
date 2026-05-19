import threading
import time

import requests
import uvicorn
import webview

from api import app

APP_URL = "http://127.0.0.1:8000"


def wait_for_api(url: str, timeout: int = 120) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=2)
            if response.ok:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def run_api() -> None:
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    server.run()


def main() -> None:
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    if not wait_for_api(APP_URL):
        raise RuntimeError("Backend API did not start in time.")

    webview.create_window("WH AI Chatbot", APP_URL, width=1280, height=800)
    webview.start()


if __name__ == '__main__':
    main()
