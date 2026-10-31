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

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Starting PATHFORGE AI - Career Intelligence System...")
    print("🌐 Opening http://127.0.0.1:8000 in your browser...")
    print("=" * 60 + "\n")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, app_dir=str(ROOT_DIR))
