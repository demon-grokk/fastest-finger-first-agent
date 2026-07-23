import time
import subprocess
import urllib.request
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def is_chrome_running() -> bool:
    """Checks if headless Chrome is active and responding on the debugging port."""
    try:
        with urllib.request.urlopen(f"{config.CHROME_DEBUG_URL}/json", timeout=1) as response:
            return True
    except Exception:
        return False

def start_chrome() -> bool:
    """Launches headless Chrome daemon with performance-tuned flags if not already running."""
    if is_chrome_running():
        print(f"[CHROME] Chrome is already active on port {config.CHROME_DEBUG_PORT}.")
        return True

    print(f"[CHROME] Launching optimized headless Chrome daemon on port {config.CHROME_DEBUG_PORT}...")
    cmd = [config.CHROME_EXECUTABLE] + config.CHROME_FLAGS
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for _ in range(15):
        if is_chrome_running():
            print("[CHROME] Headless Chrome started successfully and is ready.")
            return True
        time.sleep(0.2)

    print("[ERROR] Failed to connect to Chrome remote debugging port.")
    return False

if __name__ == '__main__':
    start_chrome()
