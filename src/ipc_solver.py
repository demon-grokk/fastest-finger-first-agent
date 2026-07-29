import asyncio
import os
import sys
import json
import time
from pyppeteer.page import Page

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.chrome_manager import start_chrome
from src.form_engine import connect_to_browser, extract_questions, fill_and_submit_form

def cleanup_ipc_files():
    """Removes leftover IPC signal files before running."""
    for filepath in [config.URL_FILE, config.QUESTIONS_FILE, config.ANSWERS_FILE]:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass

async def listen_and_solve(url_override: str = None):
    """Main IPC listening daemon loop."""
    cleanup_ipc_files()

    if not start_chrome():
        print("[DAEMON] Pre-warm daemon skipped. Proceeding with inline browser launch fallback...")

    url = url_override

    if not url:
        print("[DAEMON] Waiting for Google Form URL in url.txt...")
        for _ in range(config.URL_POLL_TIMEOUT * 10):
            if os.path.exists(config.URL_FILE):
                try:
                    with open(config.URL_FILE, 'r') as f:
                        url = f.read().strip()
                    if url:
                        break
                except Exception:
                    pass
            await asyncio.sleep(0.1)

    if not url:
        print("[TIMEOUT] Timed out waiting for url.txt.")
        sys.exit(1)

    start_time = time.time()
    print(f"\n[DAEMON] Received Form URL: {url}")
    print("[DAEMON] Connecting to browser & navigating...")

    browser, page = await connect_to_browser()
    await page.goto(url, {'waitUntil': 'domcontentloaded'})

    # Check if Google Sign-in redirect occurred
    curr_url = page.url
    page_title = await page.title()
    if 'accounts.google.com' in curr_url or 'sign-in' in page_title.lower() or 'signin' in curr_url.lower():
        print("\n[ERROR] GOOGLE SIGN-IN REQUIRED!")
        print("[ERROR] This Google Form requires you to be logged into a Google account.")
        print("[ACTION REQUIRED] Please run 'python cli.py login' once in your terminal to sign into Google.")
        await page.screenshot({'path': config.SCREENSHOT_PATH})
        await browser.disconnect()
        sys.exit(1)

    try:
        await page.waitForSelector('div[role="listitem"]', {'timeout': 10000})
    except Exception:
        print("\n[ERROR] Question elements ('div[role=\"listitem\"]') not found on the page.")
        print(f"[ERROR] Current Page Title: '{await page.title()}' | Page URL: '{page.url}'")
        await page.screenshot({'path': config.SCREENSHOT_PATH})
        await browser.disconnect()
        sys.exit(1)

    # Extract questions
    questions = await extract_questions(page)
    print(f"\n[DOM] Extracted {len(questions)} Questions:")
    print("EXTRACTED_QUESTIONS:" + json.dumps(questions))

    with open(config.QUESTIONS_FILE, 'w') as f:
        json.dump(questions, f, indent=2)

    print("\n[DAEMON] Waiting for answers.json payload...")

    answers = None
    # Optional Auto-Solve via API Key if configured
    from src.llm_client import solve_questions_with_llm
    auto_answers = solve_questions_with_llm(questions)
    if auto_answers:
        print("[LLM] Automatically solved questions using API key!")
        answers = auto_answers
        with open(config.ANSWERS_FILE, 'w') as f:
            json.dump(answers, f, indent=2)

    # Poll for answers.json if auto_answers was not used
    if not answers:
        for _ in range(config.ANSWERS_POLL_TIMEOUT * 10):
            if os.path.exists(config.ANSWERS_FILE):
                try:
                    with open(config.ANSWERS_FILE, 'r') as f:
                        answers = json.load(f)
                    if answers:
                        break
                except Exception:
                    pass
            await asyncio.sleep(0.1)

    if not answers:
        print("[TIMEOUT] Timed out waiting for answers.json payload.")
        await browser.disconnect()
        sys.exit(1)

    print(f"\n[SOLVER] Injecting answers: {answers}")
    submission_result = await fill_and_submit_form(page, answers, submit=True)
    print(f"[RESULT] Submission Details: {submission_result}")

    # Wait briefly for post-submission landing page & capture proof screenshot
    await asyncio.sleep(1.5)
    await page.screenshot({'path': config.SCREENSHOT_PATH})

    total_duration = time.time() - start_time
    print(f"\n[BENCHMARK] Total execution benchmark: {total_duration:.2f} seconds!")
    print(f"[SCREENSHOT] Confirmation saved to {config.SCREENSHOT_PATH}")

    await browser.disconnect()

if __name__ == '__main__':
    url_arg = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(listen_and_solve(url_arg))
