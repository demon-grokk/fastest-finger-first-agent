import os

# Project Root Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Auto-load .env file if present (no external packages needed)
_env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _val = _line.split('=', 1)
                os.environ.setdefault(_key.strip(), _val.strip())

# Data & Scratch File Paths for IPC
URL_FILE = os.path.join(BASE_DIR, "url.txt")
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.json")
ANSWERS_FILE = os.path.join(BASE_DIR, "answers.json")
SCREENSHOT_PATH = os.path.join(BASE_DIR, "submission_confirmation.png")

# Chrome Configuration
CHROME_DEBUG_PORT = 9222
CHROME_DEBUG_URL = f"http://127.0.0.1:{CHROME_DEBUG_PORT}"
DEFAULT_PROFILE_DIR = os.path.expanduser("~/.gemini/antigravity-browser-profile")
CHROME_EXECUTABLE = "/opt/google/chrome/chrome"

# Performance Optimization Flags for Headless Chrome
CHROME_FLAGS = [
    f"--remote-debugging-port={CHROME_DEBUG_PORT}",
    f"--user-data-dir={DEFAULT_PROFILE_DIR}",
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-sync",
    "--blink-settings=imagesEnabled=false"
]

# Timeouts (in seconds)
URL_POLL_TIMEOUT = 600       # Time to wait for url.txt when listening
ANSWERS_POLL_TIMEOUT = 300   # Time to wait for answers.json after questions extracted
PAGE_LOAD_TIMEOUT = 15       # Maximum page navigation timeout
