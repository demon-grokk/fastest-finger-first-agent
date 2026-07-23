import asyncio
import json
import time
from pyppeteer import connect

QUIZZES_DATA = [
    {
        "title": "Fastest Finger First - Quiz 1 (Science)",
        "questions": [
            {"q": "What is the boiling point of water in Celsius?", "a": "100"},
            {"q": "What element does 'O' stand for on the periodic table?", "a": "Oxygen"},
            {"q": "Which organ pumps blood in the human body?", "a": "Heart"}
        ]
    },
    {
        "title": "Fastest Finger First - Quiz 2 (Computer & AI)",
        "questions": [
            {"q": "What does HTTP stand for?", "a": "Hypertext Transfer Protocol"},
            {"q": "Which company created the Java programming language?", "a": "Sun Microsystems"},
            {"q": "What does CPU stand for?", "a": "Central Processing Unit"}
        ]
    },
    {
        "title": "Fastest Finger First - Quiz 3 (History)",
        "questions": [
            {"q": "In which year did India gain Independence?", "a": "1947"},
            {"q": "Who was the first President of the United States?", "a": "George Washington"},
            {"q": "Which ancient empire built the Colosseum?", "a": "Roman Empire"}
        ]
    },
    {
        "title": "Fastest Finger First - Quiz 4 (Geography)",
        "questions": [
            {"q": "What is the capital of Japan?", "a": "Tokyo"},
            {"q": "Which is the largest ocean on Earth?", "a": "Pacific Ocean"},
            {"q": "What is the capital of France?", "a": "Paris"}
        ]
    },
    {
        "title": "Fastest Finger First - Quiz 5 (Riddles)",
        "questions": [
            {"q": "What has to be broken before you can use it?", "a": "An egg"},
            {"q": "I speak without a mouth and hear without ears. What am I?", "a": "An echo"},
            {"q": "What has a head and a tail but no body?", "a": "A coin"}
        ]
    }
]

async def create_single_form(browser, quiz_info):
    page = await browser.newPage()
    print(f"\n[CREATING] {quiz_info['title']}...")
    await page.goto('https://docs.google.com/forms/u/0/create', {'waitUntil': 'domcontentloaded'})
    await page.waitForSelector('[aria-label="Form title"]')

    # 1. Set Form Title
    await page.evaluate('''(title) => {
        const titleEl = document.querySelector('[aria-label="Form title"]');
        if (titleEl) {
            titleEl.textContent = title;
            titleEl.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }''', quiz_info['title'])

    # 2. Add Questions
    for idx, q_data in enumerate(quiz_info['questions']):
        if idx > 0:
            # Click "Add question" (+) button
            await page.evaluate('''() => {
                const addBtn = document.querySelector('[aria-label="Add question"], [data-tooltip="Add question"]');
                if (addBtn) addBtn.click();
            }''')
            await asyncio.sleep(1)

        # Populate question text
        await page.evaluate('''(qText, qIdx) => {
            const questionInputs = Array.from(document.querySelectorAll('[aria-label="Question"]'));
            const targetInput = questionInputs[qIdx] || questionInputs[questionInputs.length - 1];
            if (targetInput) {
                targetInput.textContent = qText;
                targetInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }''', q_data['q'], idx)

    await asyncio.sleep(2)

    # 3. Click Send button to open sharing dialog and extract published link
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('[role="button"]'));
        const sendBtn = btns.find(b => b.textContent.trim().toLowerCase() === 'send');
        if (sendBtn) sendBtn.click();
    }''')
    await asyncio.sleep(1.5)

    # Click Link tab
    await page.evaluate('''() => {
        const tabs = Array.from(document.querySelectorAll('[role="tab"], div[aria-label*="Link"]'));
        const linkTab = tabs.find(t => (t.getAttribute('aria-label') || '').includes('Link') || t.innerHTML.includes('path'));
        if (linkTab) linkTab.click();
    }''')
    await asyncio.sleep(1)

    # Extract real published viewform link
    view_url = await page.evaluate('''() => {
        const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
        const linkInput = inputs.find(i => i.value && i.value.includes('forms/d/e/'));
        if (linkInput) return linkInput.value;
        return window.location.href.split('/edit')[0] + '/viewform';
    }''')

    await page.close()
    return {
        "title": quiz_info['title'],
        "url": view_url,
        "questions": quiz_info['questions']
    }

async def main():
    browser = await connect(browserURL='http://127.0.0.1:9222')
    created_quizzes = []

    for quiz in QUIZZES_DATA:
        quiz_res = await create_single_form(browser, quiz)
        created_quizzes.append(quiz_res)
        print(f"[CREATED] URL: {quiz_res['url']}")

    with open('/home/rajeev/Data/Personal Project/fastest-finger-first-agent/test_quizzes.json', 'w') as f:
        json.dump(created_quizzes, f, indent=2)

    print("\n[SUCCESS] 5 Test Quizzes Created Successfully!")
    print("Saved details to test_quizzes.json")
    await browser.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
