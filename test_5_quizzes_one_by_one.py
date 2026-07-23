import asyncio
import json
import time
from pyppeteer import connect
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
from src.form_engine import fill_and_submit_form

async def test_quiz_one_by_one(quiz_item, idx):
    title = quiz_item['title']
    view_url = quiz_item['url']
    questions_data = quiz_item['questions']
    answers = {q['q']: q['a'] for q in questions_data}

    print(f"\n==================================================")
    print(f"▶️ RUNNING TEST {idx}/5: {title}")
    print(f"🔗 Form URL: {view_url}")
    print(f"📝 Target Answers: {answers}")

    start_time = time.time()
    browser = await connect(browserURL=config.CHROME_DEBUG_URL)
    page = await browser.newPage()

    try:
        # Navigate to Form
        await page.goto(view_url, {'waitUntil': 'domcontentloaded'})
        await page.waitForSelector('div[role="listitem"], form', {'timeout': 6000})

        # Fill and submit form
        res = await fill_and_submit_form(page, answers, submit=True)
        elapsed = round(time.time() - start_time, 2)

        print(f"⚡ Execution Time: {elapsed} seconds")
        print(f"✅ Submission Result: {res}")
        
        # Save screenshot artifact for verification
        ss_path = f"/home/rajeev/Data/Personal Project/fastest-finger-first-agent/quiz_{idx}_result.png"
        await page.screenshot({'path': ss_path})
        print(f"📸 Screenshot Saved: {ss_path}")
        
        return {"quiz": title, "status": "SUCCESS", "time": elapsed}

    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        print(f"❌ Error during test execution: {e}")
        return {"quiz": title, "status": "FAILED", "time": elapsed, "error": str(e)}

    finally:
        await page.close()
        await browser.disconnect()

async def main():
    json_path = "/home/rajeev/Data/Personal Project/fastest-finger-first-agent/test_quizzes.json"
    with open(json_path, 'r') as f:
        quizzes = json.load(f)

    results = []
    print("🚀 STARTING FASTEST FINGER FIRST - 5 QUIZZES TEST SUITE\n")
    for idx, quiz in enumerate(quizzes, 1):
        res = await test_quiz_one_by_one(quiz, idx)
        results.append(res)
        await asyncio.sleep(1)

    print("\n==================================================")
    print("📊 5 QUIZZES TEST RESULTS SUMMARY")
    print("==================================================")
    for r in results:
        status_icon = "⚡ PASSED" if r["status"] == "SUCCESS" else "❌ FAILED"
        print(f"- {r['quiz']}: {status_icon} in {r['time']}s")
    print("==================================================")

if __name__ == '__main__':
    asyncio.run(main())
