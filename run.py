import os
import sys
from pathlib import Path
import threading
import time
import webbrowser
import uvicorn

# Locate project root
CURRENT_FILE = Path(__file__).resolve()
if CURRENT_FILE.parent.name == "app":
    ROOT_DIR = CURRENT_FILE.parent.parent
else:
    ROOT_DIR = CURRENT_FILE.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
os.chdir(ROOT_DIR)

def open_browser(port: int = 8000):
    time.sleep(1.5)
    webbrowser.open(f"http://127.0.0.1:{port}")

if __name__ == "__main__":
    is_prod = "PORT" in os.environ or os.environ.get("ENV") == "production"
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0" if is_prod else "127.0.0.1")
    reload = not is_prod

    print("\n" + "=" * 60)
    print(f"🚀 Starting PATHFORGE AI - Career Intelligence System on {host}:{port}...")
    if not is_prod:
        print(f"🌐 Opening http://127.0.0.1:{port} in your browser...")
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    print("=" * 60 + "\n")

    uvicorn.run("app.main:app", host=host, port=port, reload=reload, app_dir=str(ROOT_DIR))
