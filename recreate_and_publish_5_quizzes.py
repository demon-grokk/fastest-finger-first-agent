import asyncio
import json
import time
from pyppeteer import connect

# Spec containing exactly ONE quiz for simplicity and verification
QUIZZES_SPEC = [
    {
        "title": "Fastest Finger First - Verified Quiz",
        "questions": [
            {"q": "What is the boiling point of water in Celsius?", "a": "100"},
            {"q": "What element does 'O' stand for on the periodic table?", "a": "Oxygen"},
            {"q": "Which organ pumps blood in the human body?", "a": "Heart"}
        ]
    }
]

async def create_single_form(browser, spec):
    page = await browser.newPage()
    # Set viewport to 1280x800 to ensure elements are visible
    await page.setViewport({'width': 1280, 'height': 800})
    print(f"\n[BUILDING QUIZ] {spec['title']}...")
    
    # Open form editor
    await page.goto('https://docs.google.com/forms/u/0/create', {'waitUntil': 'networkidle2'})
    await asyncio.sleep(5)

    # Dismiss "Got it" dialog if present
    await page.evaluate('''() => {
        const gotItBtn = Array.from(document.querySelectorAll('[role="button"]')).find(b => b.textContent.includes('Got it'));
        if (gotItBtn) gotItBtn.click();
    }''')
    await asyncio.sleep(1)

    # 1. Focus and Type Title
    title_selector = 'div[aria-label="Form title"]'
    await page.waitForSelector(title_selector)
    await page.click(title_selector)
    await asyncio.sleep(0.5)
    
    await page.keyboard.down('Control')
    await page.keyboard.press('KeyA')
    await page.keyboard.up('Control')
    await page.keyboard.press('Backspace')
    await asyncio.sleep(0.3)
    await page.keyboard.type(spec['title'])
    await asyncio.sleep(1)

    # 2. Add and Configure Each Question
    for idx, q_info in enumerate(spec['questions']):
        print(f"   Adding question {idx+1}: {q_info['q']}")
        
        if idx == 0:
            # First question card is already present by default. Just click to focus.
            first_q = 'div[aria-label="Question"]'
            await page.waitForSelector(first_q)
            await page.click(first_q)
            await asyncio.sleep(1.5)
        else:
            # Click the "+" (Add question) button on the side panel
            add_btn_selector = '[aria-label="Add question"]'
            await page.waitForSelector(add_btn_selector)
            await page.click(add_btn_selector)
            await asyncio.sleep(2)

        # Change the active question's type to "Short answer"
        print("     - Changing question type to Short answer...")
        dropdown = await page.evaluateHandle('''() => {
            const listboxes = Array.from(document.querySelectorAll('[role="listbox"]'));
            const visible = listboxes.filter(l => l.getBoundingClientRect().height > 0);
            return visible[visible.length - 1]; // Return the last visible dropdown (active card)
        }''')
        
        if dropdown:
            box = await dropdown.boundingBox()
            if box:
                # Click center of dropdown to open menu
                await page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                await asyncio.sleep(1.5)
                
                # Click the visible "Short answer" option (data-value="0") inside JS
                click_success = await page.evaluate('''() => {
                    const opts = Array.from(document.querySelectorAll('div[role="option"][data-value="0"]'));
                    const visibleOpt = opts.find(el => el.getBoundingClientRect().height > 0);
                    if (visibleOpt) {
                        visibleOpt.click();
                        return true;
                    }
                    return false;
                }''')
                print(f"     - Option click status: {click_success}")
                await asyncio.sleep(1.5)
            else:
                print("     [WARNING] Could not find dropdown bounding box.")
        else:
            print("     [WARNING] Could not find active dropdown listbox.")

        # Focus the active question input field and type the text
        print("     - Typing question text...")
        await page.evaluate('''() => {
            const textareas = Array.from(document.querySelectorAll('textarea[aria-label="Question"], div[aria-label="Question"]'));
            const visible = textareas.filter(el => el.getBoundingClientRect().height > 0);
            const activeTextarea = visible[visible.length - 1]; // Focus the last visible textarea (active card)
            if (activeTextarea) activeTextarea.focus();
        }''')
        await asyncio.sleep(0.5)
        
        await page.keyboard.down('Control')
        await page.keyboard.press('KeyA')
        await page.keyboard.up('Control')
        await page.keyboard.press('Backspace')
        await asyncio.sleep(0.3)
        await page.keyboard.type(q_info['q'])
        await asyncio.sleep(1)

    # 3. Wait for changes to auto-save to Google Drive
    print("   Waiting for changes to save to Google Drive...")
    await asyncio.sleep(6)

    # 4. Open Publish Dialog
    print("   Opening Publish Dialog...")
    publish_btn_selector = '[data-action-id="freebird-publish-dialog"]'
    await page.waitForSelector(publish_btn_selector)
    await page.click(publish_btn_selector)
    await asyncio.sleep(3.5)

    # 5. Click Publish button inside the dialog
    print("   Clicking Publish in dialog...")
    dialog_pub_selector = 'div[jsshadow][role="button"].QvWxOd'
    await page.waitForSelector(dialog_pub_selector)
    await page.click(dialog_pub_selector)
    await asyncio.sleep(4)

    # 6. Extract the published responder link from the popup input
    print("   Extracting published responder URL...")
    preview_url = await page.evaluate('''() => {
        const inputs = Array.from(document.querySelectorAll('input'));
        const linkInput = inputs.find(i => i.value && i.value.includes('forms/d/e/'));
        if (linkInput) return linkInput.value;
        return null;
    }''')

    if not preview_url:
        print("   [WARNING] Could not locate link in popup. Scanning all inputs...")
        preview_url = await page.evaluate('''() => {
            const inputs = Array.from(document.querySelectorAll('input'));
            for (let i of inputs) {
                if (i.value && i.value.includes('viewform')) return i.value;
            }
            return null;
        }''')

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
    
    # Close old viewform/edit/create tabs to start clean
    pages = await browser.pages()
    for p in pages:
        if 'docs.google.com/forms' in p.url or 'viewform' in p.url:
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

    print(f"\n✅ Single Active Fillable Quiz Created & Saved to {out_file}!")
    await browser.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
