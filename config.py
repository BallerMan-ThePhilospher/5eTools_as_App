import os, sys, subprocess

def app_dir():
    # Folder containing the .exe (when packaged) or these scripts
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = app_dir()
ROOT = os.path.join(APP_DIR, "5etools-src")
PORT = 8080
HOME = f"http://localhost:{PORT}"

# Verify with:  git -C <your existing folder> remote get-url origin
REPO_URL = "https://github.com/5etools-mirror-3/5etools-src.git"
IMG_REPO_URL = "https://github.com/5etools-mirror-3/5etools-img.git"

NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
