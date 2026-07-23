import asyncio
import json
import time
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

async def create_single_form(browser, spec):
    page = await browser.newPage()
    print(f"\n[BUILDING QUIZ] {spec['title']}...")
    
    # Open form editor and wait until page is fully loaded
    await page.goto('https://docs.google.com/forms/u/0/create', {'waitUntil': 'networkidle2'})
    await asyncio.sleep(4)

    # 1. Focus and Type Title
    title_selector = 'div[aria-label="Form title"]'
    await page.waitForSelector(title_selector)
    await page.click(title_selector)
    await asyncio.sleep(0.5)
    
    # Clear and Type
    await page.keyboard.down('Control')
    await page.keyboard.press('KeyA')
    await page.keyboard.up('Control')
    await page.keyboard.press('Backspace')
    await asyncio.sleep(0.3)
    await page.keyboard.type(spec['title'])
    await asyncio.sleep(1)

    # 2. Focus and Type First Question
    q_selector = 'div[aria-label="Question"]'
    await page.waitForSelector(q_selector)
    await page.click(q_selector)
    await asyncio.sleep(0.5)
    
    await page.keyboard.down('Control')
    await page.keyboard.press('KeyA')
    await page.keyboard.up('Control')
    await page.keyboard.press('Backspace')
    await asyncio.sleep(0.3)
    await page.keyboard.type(spec['questions'][0]['q'])
    await asyncio.sleep(1)

    # 3. Add subsequent questions via Keyboard Shortcuts
    for q_info in spec['questions'][1:]:
        print(f"   Adding question: {q_info['q']}")
        # Ctrl + Shift + Enter
        await page.keyboard.down('Control')
        await page.keyboard.down('Shift')
        await page.keyboard.press('Enter')
        await page.keyboard.up('Shift')
        await page.keyboard.up('Control')
        await asyncio.sleep(2) # wait for new question input to mount and focus
        
        # Type question text directly into the focused field
        await page.keyboard.type(q_info['q'])
        await asyncio.sleep(1)

    # 4. Turn OFF MagicBricks Domain Restriction (Make Form Public)
    print("   Making form public (removing domain restriction)...")
    await page.evaluate('''() => {
        // Switch to Settings Tab
        const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
        const settingsTab = tabs.find(t => t.textContent.includes('Settings'));
        if (settingsTab) settingsTab.click();
    }''')
    await asyncio.sleep(2)

    # Expand Responses dropdown and disable restriction
    await page.evaluate('''() => {
        // Find and click the Responses expand header if it's not already open
        const headers = Array.from(document.querySelectorAll('div'));
        const respHeader = headers.find(h => h.textContent.trim().startsWith('Responses'));
        if (respHeader) respHeader.click();
    }''')
    await asyncio.sleep(1.5)

    await page.evaluate('''() => {
        // Find the Restrict toggle and switch it OFF
        const toggles = Array.from(document.querySelectorAll('[role="checkbox"], [role="switch"]'));
        const restrictToggle = toggles.find(t => {
            const container = t.closest('div');
            // Try to find if parent container text mentions Restrict to MagicBricks
            let current = container;
            for (let i = 0; i < 5 && current; i++) {
                if (current.textContent.includes('Restrict to users in') || current.textContent.includes('MagicBricks')) {
                    return true;
                }
                current = current.parentElement;
            }
            return false;
        });
        if (restrictToggle && restrictToggle.getAttribute('aria-checked') === 'true') {
            restrictToggle.click();
        }
    }''')
    await asyncio.sleep(2)

    # Switch back to Questions tab before saving/sending
    await page.evaluate('''() => {
        const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
        const qTab = tabs.find(t => t.textContent.includes('Questions'));
        if (qTab) qTab.click();
    }''')
    await asyncio.sleep(1.5)

    # Wait for Auto-Save to synchronize with Google Drive
    await asyncio.sleep(4)

    # 5. Open Send Dialog & Get URL
    preview_url = None
    
    # Click Send button
    await page.evaluate('''() => {
        const btns = Array.from(document.querySelectorAll('[role="button"]'));
        const sendBtn = btns.find(b => b.textContent.trim().toLowerCase() === 'send');
        if (sendBtn) sendBtn.click();
    }''')
    await asyncio.sleep(3)

    # Click Link tab in dialog
    await page.evaluate('''() => {
        const tabs = Array.from(document.querySelectorAll('[role="tab"], div[aria-label*="Link"]'));
        const linkTab = tabs.find(t => (t.getAttribute('aria-label') || '').includes('Link') || t.innerHTML.includes('path') || t.textContent.includes('link') || t.outerHTML.includes('link'));
        if (linkTab) linkTab.click();
        
        const icons = Array.from(document.querySelectorAll('.quantumWizDialogPapercanvasEl, div'));
        const linkIcon = icons.find(i => i.getAttribute('aria-label') === 'Link');
        if (linkIcon) linkIcon.click();
    }''')
    await asyncio.sleep(3)

    # Extract real published viewform link
    preview_url = await page.evaluate('''() => {
        const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
        const linkInput = inputs.find(i => i.value && i.value.includes('forms/d/e/'));
        if (linkInput) return linkInput.value;
        return null;
    }''')

    if not preview_url:
        print("[WARNING] Link tab failed. Falling back to preview tab...")
        # Fallback to preview button
        await page.evaluate('''() => {
            const prevBtn = Array.from(document.querySelectorAll('[role="button"], a')).find(b => b.getAttribute('aria-label') === 'Preview' || b.getAttribute('data-tooltip') === 'Preview');
            if (prevBtn) prevBtn.click();
        }''')
        await asyncio.sleep(3)
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
    
    # Close any old viewform/edit tabs first to start fresh
    pages = await browser.pages()
    for p in pages:
        if 'viewform' in p.url or 'edit' in p.url:
            if len(await browser.pages()) > 1:
                try:
                    await p.close()
                except Exception:
                    pass

    for spec in QUIZZES_SPEC:
        q_item = await create_single_form(browser, spec)
        quizzes.append(q_item)

    out_file = '/home/rajeev/Data/Personal Project/fastest-finger-first-agent/test_quizzes.json'
    with open(out_file, 'w') as f:
        json.dump(quizzes, f, indent=2)

    print(f"\n✅ All 5 Active Fillable Quizzes Created & Saved to {out_file}!")
    await browser.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
