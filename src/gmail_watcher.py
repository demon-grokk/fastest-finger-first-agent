"""
Fastest Finger First AI Quiz Agent - Native Gmail Watcher Service
Monitors Gmail inbox directly in headless Chrome using saved profile session.
Includes Top-5 email limit safeguard to prevent stale/duplicate quiz submissions.
"""

import asyncio
import datetime
import json
import os
import re
import sys
import time

import config
from src.chrome_manager import start_chrome
from src.form_engine import connect_to_browser, extract_questions, fill_and_submit_form
from src.llm_client import solve_questions_with_llm

PROCESSED_URLS = set()

def get_timestamp():
    """Returns formatted current timestamp with milliseconds."""
    return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]

def log(tag: str, message: str):
    """Prints timestamped log output."""
    print(f"[{get_timestamp()}] [{tag}] {message}")

async def solve_form_in_new_tab(browser, url: str):
    """Opens a separate browser tab to solve the form without destroying the Gmail tab context."""
    t0 = time.time()
    log("SOLVER", f"Opening dedicated tab for form: {url}")
    form_page = await browser.newPage()
    
    t_nav_start = time.time()
    try:
        log("SOLVER", "Navigating to Google Form URL...")
        await form_page.goto(url, {'waitUntil': 'domcontentloaded'})
        log("TIMING", f"Navigation completed in {time.time() - t_nav_start:.3f}s")

        curr_url = form_page.url
        page_title = await form_page.title()
        if 'accounts.google.com' in curr_url or 'sign-in' in page_title.lower():
            log("ERROR", "GOOGLE SIGN-IN REQUIRED! Please run 'python cli.py login'.")
            await form_page.close()
            return

        t_wait_start = time.time()
        await form_page.waitForSelector('div[role="listitem"]', {'timeout': 10000})
        log("TIMING", f"Form questions loaded in {time.time() - t_wait_start:.3f}s")

        t_extract_start = time.time()
        questions = await extract_questions(form_page)
        log("TIMING", f"Extracted {len(questions)} questions in {time.time() - t_extract_start:.3f}s")
        log("DOM", f"Questions: {json.dumps(questions)}")

        t_llm_start = time.time()
        log("LLM", "Solving questions via Groq Llama 3.3 AI...")
        answers = solve_questions_with_llm(questions)
        log("TIMING", f"LLM reasoning completed in {time.time() - t_llm_start:.3f}s")
        log("SOLVER", f"Answers generated: {answers}")

        if answers:
            t_fill_start = time.time()
            log("SOLVER", "Injecting answers into form & clicking Submit...")
            result = await fill_and_submit_form(form_page, answers, submit=True)
            log("TIMING", f"Form filled & submitted in {time.time() - t_fill_start:.3f}s")
            log("RESULT", f"Submission result: {result}")

            await asyncio.sleep(1.5)
            await form_page.screenshot({'path': config.SCREENSHOT_PATH})
            log("SCREENSHOT", f"Confirmation saved to {config.SCREENSHOT_PATH}")

            total_time = time.time() - t0
            log("BENCHMARK", f"⚡ TOTAL TURNAROUND BENCHMARK: {total_time:.3f} seconds!\n")
    except Exception as e:
        log("SOLVER ERROR", f"Execution exception: {e}")
    finally:
        try:
            await form_page.close()
        except Exception:
            pass

async def watch_gmail_inbox(top_limit: int = 5):
    """Main watcher loop that monitors Gmail and solves incoming quizzes."""
    print("=" * 75)
    print("⚡ FASTEST FINGER FIRST - NATIVE GMAIL INBOX WATCHER ⚡")
    print(f"Profile Directory: {config.DEFAULT_PROFILE_DIR}")
    print(f"Top-Email Safeguard Limit: Top {top_limit} Inbox Mails")
    print("=" * 75 + "\n")

    t_start = time.time()
    log("GMAIL WATCHER", "Starting Chrome daemon...")
    if not start_chrome():
        log("GMAIL WATCHER", "Failed to pre-warm Chrome.")
        return

    log("GMAIL WATCHER", "Connecting to Chrome session...")
    browser, page = await connect_to_browser()

    log("GMAIL WATCHER", "Navigating to Gmail Inbox...")
    t_nav_gmail = time.time()
    await page.goto("https://mail.google.com/mail/u/0/#inbox", {"waitUntil": "domcontentloaded"})

    try:
        await page.waitForSelector('div[role="main"]', {"timeout": 15000})
        log("GMAIL WATCHER", f"Gmail Inbox loaded in {time.time() - t_nav_gmail:.3f}s!")
    except Exception:
        log("GMAIL WATCHER", "⚠️ Warning: Inbox selector timeout. Ensure you ran 'python cli.py login'.")

    log("GMAIL WATCHER", f"🟢 Active monitoring enabled! Polling top {top_limit} emails every 500ms...\n")

    while True:
        try:
            # High-speed DOM evaluation: returns extracted form URLs directly to Python
            t_poll_start = time.time()
            found_urls = await page.evaluate(f"""
                (maxRows) => {{
                    let urls = [];

                    // 1. Check & auto-open HR email row in top N emails
                    const rows = document.querySelectorAll('tr[role="row"]');
                    let count = 0;
                    for (let row of rows) {{
                        if (count >= maxRows) break;
                        const text = row.innerText || '';
                        if (text.includes('Fastest Finger First') || text.includes('Team HR')) {{
                            row.click();
                            break;
                        }}
                        count++;
                    }}

                    // 2. Extract Google Form URLs from anchor tags & saferedirecturl
                    const links = document.querySelectorAll('a[href], a[data-saferedirecturl]');
                    links.forEach(link => {{
                        let raw = link.href || link.getAttribute('data-saferedirecturl');
                        if (raw) {{
                            if (raw.includes('google.com/url?q=')) {{
                                try {{
                                    const params = new URLSearchParams(raw.split('?')[1]);
                                    raw = params.get('q') || raw;
                                }} catch(e) {{}}
                            }}
                            if (raw.includes('docs.google.com/forms') || raw.includes('forms.gle')) {{
                                let clean = raw.split('?')[0].split('&')[0].trim();
                                if (!clean.endsWith('/viewform') && clean.includes('/viewform')) {{
                                    clean = clean.split('/viewform')[0] + '/viewform';
                                }}
                                urls.push(clean);
                            }}
                        }}
                    }});

                    // 3. Extract via regex from visible text
                    const regex = /https:\\/\\/(docs\\.google\\.com\\/forms\\/d\\/e\\/[a-zA-Z0-9_-]+\\/viewform|forms\\.gle\\/[a-zA-Z0-9_-]+)/g;
                    const bodyText = document.body.innerText || '';
                    const matches = bodyText.match(regex);
                    if (matches) urls.push(...matches);

                    return [...new Set(urls)];
                }}
            """, top_limit)

            if found_urls:
                for url in found_urls:
                    if url and url not in PROCESSED_URLS:
                        PROCESSED_URLS.add(url)
                        log("GMAIL WATCHER", f"⚡ Fresh Google Form Link Discovered: {url}")
                        log("GMAIL WATCHER", "Launching solver in dedicated tab...")
                        await solve_form_in_new_tab(browser, url)
                        log("GMAIL WATCHER", "Resuming inbox monitoring...\n")

            await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            break
        except Exception as e:
            log("GMAIL WATCHER", f"Polling exception: {e}")
            await asyncio.sleep(1)
