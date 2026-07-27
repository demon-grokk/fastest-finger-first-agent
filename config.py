import os
import sys

# Project Root Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Auto-load .env file if present (cross-platform, handles Windows UTF-16/BOM encoding)
_env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(_env_path):
    try:
        # Try utf-8-sig first (handles BOM from Windows Notepad/PowerShell)
        with open(_env_path, encoding='utf-8-sig') as _f:
            _content = _f.read()
    except Exception:
        with open(_env_path, encoding='utf-8', errors='ignore') as _f:
            _content = _f.read()
    for _line in _content.splitlines():
        _line = _line.replace('\x00', '').strip()  # Strip null bytes (UTF-16 artifact)
        if _line and not _line.startswith('#') and '=' in _line:
            _key, _val = _line.split('=', 1)
            os.environ.setdefault(_key.strip(), _val.strip())

# Data & Scratch File Paths for IPC
URL_FILE = os.path.join(BASE_DIR, "url.txt")
QUESTIONS_FILE = os.path.join(BASE_DIR, "questions.json")
ANSWERS_FILE = os.path.join(BASE_DIR, "answers.json")
SCREENSHOT_PATH = os.path.join(BASE_DIR, "submission_confirmation.png")

# Chrome Executable Finder (Cross-Platform: Windows, macOS, Linux)
def get_chrome_executable() -> str:
    env_path = os.environ.get("CHROME_PATH") or os.environ.get("CHROME_EXECUTABLE")
    if env_path and os.path.exists(env_path):
        return env_path

    import shutil
    for name in ["google-chrome", "google-chrome-stable", "chrome", "chromium", "chromium-browser"]:
        found = shutil.which(name)
        if found:
            return found

    if os.name == 'nt':  # Windows
        candidates = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles%\Chromium\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Chromium\Application\chrome.exe"),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
    elif sys.platform == 'darwin':  # macOS
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
    else:  # Linux
        candidates = [
            "/opt/google/chrome/chrome",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

    return "chrome" if os.name == 'nt' else "/opt/google/chrome/chrome"

CHROME_DEBUG_PORT = 9222
CHROME_DEBUG_URL = f"http://127.0.0.1:{CHROME_DEBUG_PORT}"
DEFAULT_PROFILE_DIR = os.path.abspath(os.path.expanduser("~/.fff-agent-profile"))
CHROME_EXECUTABLE = get_chrome_executable()

# Performance Optimization Flags for Headless Chrome (Cross-Platform)
CHROME_FLAGS = [
    f"--remote-debugging-port={CHROME_DEBUG_PORT}",
    f"--user-data-dir={DEFAULT_PROFILE_DIR}",
    "--headless",
    "--disable-gpu",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-sync",
    "--blink-settings=imagesEnabled=false"
]

if os.name != 'nt':
    CHROME_FLAGS.append("--no-sandbox")

# Timeouts (in seconds)
URL_POLL_TIMEOUT = 600       # Time to wait for url.txt when listening
ANSWERS_POLL_TIMEOUT = 300   # Time to wait for answers.json after questions extracted
PAGE_LOAD_TIMEOUT = 15       # Maximum page navigation timeout
