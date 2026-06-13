import os
import sys
import threading
import time
import webview

APP_URL = "http://127.0.0.1:8000"

LOADING_HTML = """<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #1a1a2e;
    display: flex; align-items: center; justify-content: center;
    height: 100vh; font-family: 'Segoe UI', sans-serif;
  }
  .container { text-align: center; color: #c8a84b; }
  h1 { font-size: 2.2rem; margin-bottom: 0.5rem; letter-spacing: 2px; }
  p { color: #888; font-size: 0.95rem; margin-top: 1.2rem; }
  .dots span {
    display: inline-block; width: 10px; height: 10px; margin: 0 4px;
    background: #c8a84b; border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
  }
  .dots span:nth-child(2) { animation-delay: 0.2s; }
  .dots span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce {
    0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
    40% { transform: scale(1); opacity: 1; }
  }
</style>
</head>
<body>
  <div class="container">
    <h1>&#9876; WH AI Chatbot</h1>
    <div class="dots"><span></span><span></span><span></span></div>
    <p>Loading AI model and knowledge base...</p>
  </div>
</body>
</html>"""


def _apply_window_icon() -> None:
    """Set the title bar icon to match the exe icon (Windows only)."""
    if sys.platform != 'win32':
        return
    import ctypes
    import ctypes.wintypes as wintypes

    hwnd = ctypes.windll.user32.FindWindowW(None, "WH AI Chatbot")
    if not hwnd:
        return

    WM_SETICON = 0x0080
    ICON_SMALL = 0
    ICON_BIG = 1

    h_large = wintypes.HICON()
    h_small = wintypes.HICON()

    if getattr(sys, 'frozen', False):
        src = sys.executable
    else:
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'frontend', 'public', 'app_icon.ico')

    if not os.path.exists(src):
        return

    count = ctypes.windll.shell32.ExtractIconExW(
        src, 0, ctypes.byref(h_large), ctypes.byref(h_small), 1
    )
    if count > 0:
        if h_large.value:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_large.value)
        if h_small.value:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_small.value)


def _run_api() -> None:
    import uvicorn
    from api import app as fastapi_app
    config = uvicorn.Config(app=fastapi_app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    server.run()


def _wait_and_navigate(window) -> None:
    import requests
    while True:
        try:
            r = requests.get(f"{APP_URL}/health", timeout=2)
            if r.ok:
                break
        except Exception:
            pass
        time.sleep(1)
    window.load_url(APP_URL)


def main() -> None:
    window = webview.create_window(
        "WH AI Chatbot",
        html=LOADING_HTML,
        width=700,
        height=750,
    )

    threading.Thread(target=_run_api, daemon=True).start()
    threading.Thread(target=_wait_and_navigate, args=(window,), daemon=True).start()

    webview.start(func=_apply_window_icon)


if __name__ == '__main__':
    main()
