#!/usr/bin/env python3
"""
Fastest Finger First AI Quiz Agent CLI
Command-line interface to pre-warm headless Chrome, start the IPC listener, or execute one-shot solver.
"""

import argparse
import asyncio
import sys
import json
import os

import config
from src.chrome_manager import start_chrome
from src.ipc_solver import listen_and_solve
from src.form_engine import connect_to_browser, fill_and_submit_form

async def execute_oneshot(url: str, answers_json: str, submit: bool):
    """Executes a direct one-shot quiz submission."""
    answers = json.loads(answers_json)
    if not start_chrome():
        print("[CLI] Pre-warm daemon skipped. Proceeding with inline browser launch fallback...")

    print(f"[CLI] Connecting to Chrome & navigating to {url}...")
    browser, page = await connect_to_browser()
    await page.goto(url, {'waitUntil': 'domcontentloaded'})
    await page.waitForSelector('div[role="listitem"]', {'timeout': 10000})

    print(f"[CLI] Filling form with answers: {answers}")
    result = await fill_and_submit_form(page, answers, submit=submit)
    print(f"[CLI] Execution Result: {result}")

    if submit:
        await asyncio.sleep(1.5)

    await page.screenshot({'path': config.SCREENSHOT_PATH})
    print(f"[CLI] Confirmation screenshot saved to {config.SCREENSHOT_PATH}")
    await browser.disconnect()

async def login_google():
    """Launches visible Chrome using the project profile so the user can log into their Google Account once."""
    from pyppeteer import launch
    from src.chrome_manager import stop_chrome, clear_profile_locks

    print("[LOGIN] Closing any background Chrome daemon processes...")
    stop_chrome()
    clear_profile_locks()

    print("[LOGIN] Launching Chrome browser for Google Sign-in...")
    print(f"[LOGIN] Profile path: {config.DEFAULT_PROFILE_DIR}")

    args_list = [
        f"--user-data-dir={config.DEFAULT_PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    if os.name != 'nt':
        args_list.append("--no-sandbox")

    launch_kwargs = {
        'headless': False,
        'args': args_list,
        'defaultViewport': None
    }
    if config.CHROME_EXECUTABLE and os.path.exists(config.CHROME_EXECUTABLE):
        launch_kwargs['executablePath'] = config.CHROME_EXECUTABLE

    browser = await launch(**launch_kwargs)
    pages = await browser.pages()
    page = pages[0] if pages else await browser.newPage()
    await page.goto("https://accounts.google.com/ServiceLogin?service=wise", {'waitUntil': 'domcontentloaded'})

    print("\n" + "="*70)
    print("👉 INSTRUCTIONS:")
    print("1. Log into your Google Account in the opened Chrome window.")
    print("2. Once logged in, come back to this terminal and press ENTER.")
    print("="*70 + "\n")

    input("Press ENTER after completing Google login in the browser...")
    try:
        await browser.close()
    except Exception:
        pass

    stop_chrome()
    print("[LOGIN] Success! Your Google session is saved in your profile.")
    print("[LOGIN] All future 'python cli.py listen' runs will now use this signed-in account automatically!\n")

def main():
    parser = argparse.ArgumentParser(
        description="Fastest Finger First AI Quiz Agent - High Speed Google Forms Solver (<5s Benchmark)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: login
    subparsers.add_parser("login", help="Opens headful Chrome once to sign into your Google Account")

    # Command: start-chrome
    subparsers.add_parser("start-chrome", help="Pre-warms headless Chrome on port 9222")

    # Command: listen
    listen_parser = subparsers.add_parser("listen", help="Starts the zero-approval IPC polling daemon")
    listen_parser.add_argument("--url", help="Optional initial URL to start immediately")

    # Command: submit
    submit_parser = subparsers.add_parser("submit", help="Executes a direct one-shot solver run")
    submit_parser.add_argument("--url", required=True, help="Google Form URL")
    submit_parser.add_argument("--answers", required=True, help="JSON mapping question keywords to answers")
    submit_parser.add_argument("--no-submit", action="store_true", help="Fill form without clicking submit")

    args = parser.parse_args()

    if args.command == "login":
        asyncio.run(login_google())
    elif args.command == "start-chrome":
        start_chrome()
    elif args.command == "listen":
        asyncio.run(listen_and_solve(args.url))
    elif args.command == "submit":
        asyncio.run(execute_oneshot(args.url, args.answers, not args.no_submit))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
