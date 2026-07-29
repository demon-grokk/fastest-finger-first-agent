import time
import subprocess
import urllib.request
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def clear_profile_locks():
    """Removes leftover Chrome singleton lock files if present."""
    lock_files = ["SingletonLock", "SingletonSocket", "SingletonCookie"]
    for lock in lock_files:
        p = os.path.join(config.DEFAULT_PROFILE_DIR, lock)
        if os.path.exists(p) or os.path.islink(p):
            try:
                os.remove(p)
            except Exception:
                pass

def stop_chrome():
    """Stops any running background Chrome processes locking our profile."""
    try:
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['pkill', '-f', config.DEFAULT_PROFILE_DIR], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['pkill', '-f', f'remote-debugging-port={config.CHROME_DEBUG_PORT}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    clear_profile_locks()
    time.sleep(1.0)

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

    if not config.CHROME_EXECUTABLE or not os.path.exists(config.CHROME_EXECUTABLE):
        print(f"[ERROR] Chrome executable not found at '{config.CHROME_EXECUTABLE}'.")
        print("[ERROR] Please make sure Google Chrome is installed, or set CHROME_PATH environment variable.")
        return False

    print(f"[CHROME] Launching optimized headless Chrome daemon on port {config.CHROME_DEBUG_PORT}...")
    cmd = [config.CHROME_EXECUTABLE] + config.CHROME_FLAGS
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Poll for port availability (up to 8 seconds for slower Windows cold starts)
    for _ in range(40):
        if is_chrome_running():
            print("[CHROME] Headless Chrome started successfully and is ready.")
            return True
        time.sleep(0.2)

    # If it failed to start, check if process died and print output
    if proc.poll() is not None:
        _, stderr_out = proc.communicate()
        print(f"[ERROR] Chrome process exited prematurely with code {proc.returncode}.")
        if stderr_out:
            print(f"[ERROR] Chrome Stderr: {stderr_out.decode('utf-8', errors='ignore')}")

    print("[ERROR] Failed to connect to Chrome remote debugging port 9222.")
    print("[HINT] Make sure no existing Chrome process is locking port 9222 or the profile folder.")
    return False

if __name__ == '__main__':
    start_chrome()
