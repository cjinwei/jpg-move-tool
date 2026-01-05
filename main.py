import threading
import uvicorn
from app_backend import app
import webview

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=3000, log_level="warning")

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    webview.create_window(
        "JPG Move Tool",
        "http://127.0.0.1:3000",
        width=1200,
        height=900,
    )
    webview.start()