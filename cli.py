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
from src.webhook_server import start_webhook_server

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

def main():
    parser = argparse.ArgumentParser(
        description="Fastest Finger First AI Quiz Agent - High Speed Google Forms Solver (<5s Benchmark)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: watch
    watch_parser = subparsers.add_parser("watch", help="Starts the live HTTP Webhook Server for Tampermonkey")
    watch_parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")

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

    if args.command == "watch":
        start_webhook_server(args.port)
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
