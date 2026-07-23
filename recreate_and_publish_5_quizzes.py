import asyncio
import json
from pyppeteer import connect

QUIZZES_SPEC = [
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
            {"q": "Which company created Java programming language?", "a": "Sun Microsystems"},
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

async def create_active_quiz(browser, spec):
    page = await browser.newPage()
    print(f"\n[BUILDING QUIZ] {spec['title']}...")
    await page.goto('https://docs.google.com/forms/u/0/create', {'waitUntil': 'domcontentloaded'})
    await asyncio.sleep(2)

    # 1. Title
    await page.evaluate('''(title) => {
        const titleEl = document.querySelector('[aria-label="Form title"]');
        if (titleEl) {
            titleEl.focus();
            document.execCommand('selectAll', false, null);
            document.execCommand('insertText', false, title);
        }
    }''', spec['title'])
    await asyncio.sleep(1)

    # 2. Add Questions
    for idx, q_info in enumerate(spec['questions']):
        if idx > 0:
            await page.evaluate('''() => {
                const addBtn = document.querySelector('[aria-label="Add question"], [data-tooltip="Add question"]');
                if (addBtn) addBtn.click();
            }''')
            await asyncio.sleep(1)

        await page.evaluate('''(qText, idx) => {
            const qInputs = Array.from(document.querySelectorAll('[aria-label="Question"]'));
            const target = qInputs[idx] || qInputs[qInputs.length - 1];
            if (target) {
                target.focus();
                document.execCommand('selectAll', false, null);
                document.execCommand('insertText', false, qText);
            }
        }''', q_info['q'], idx)
        await asyncio.sleep(0.5)

    await asyncio.sleep(2)

    # 3. Click Preview button to open fillable form
    preview_url = None
    def on_target_created(target):
        nonlocal preview_url
        if 'viewform' in target.url:
            preview_url = target.url

    browser.on('targetcreated', on_target_created)

    await page.evaluate('''() => {
        const prevBtn = Array.from(document.querySelectorAll('[role="button"], a')).find(b => b.getAttribute('aria-label') === 'Preview' || b.getAttribute('data-tooltip') === 'Preview');
        if (prevBtn) prevBtn.click();
    }''')
    await asyncio.sleep(2.5)

    if not preview_url:
        pages = await browser.pages()
        for p in pages:
            if 'viewform' in p.url:
                preview_url = p.url
                break

    await page.close()
    print(f"✨ Published Fillable Form URL: {preview_url}")
    return {
        "title": spec['title'],
        "url": preview_url,
        "questions": spec['questions']
    }

async def main():
    browser = await connect(browserURL='http://127.0.0.1:9222')
    quizzes = []
    for spec in QUIZZES_SPEC:
        q_item = await create_active_quiz(browser, spec)
        quizzes.append(q_item)

    out_file = '/home/rajeev/Data/Personal Project/fastest-finger-first-agent/test_quizzes.json'
    with open(out_file, 'w') as f:
        json.dump(quizzes, f, indent=2)

    print(f"\n✅ All 5 Active Fillable Quizzes Created & Saved to {out_file}!")
    await browser.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
