import asyncio
import json
from pyppeteer import connect

async def enable_responses_for_form(browser, edit_url):
    page = await browser.newPage()
    print(f"[ENABLING RESPONSES] Navigating to editor: {edit_url}")
    await page.goto(edit_url, {'waitUntil': 'domcontentloaded'})
    await asyncio.sleep(2)

    # Click "Responses" tab
    await page.evaluate('''() => {
        const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
        const respTab = tabs.find(t => t.textContent.toLowerCase().includes('responses'));
        if (respTab) respTab.click();
    }''')
    await asyncio.sleep(1.5)

    # Check toggle "Accepting responses"
    status = await page.evaluate('''() => {
        const toggle = document.querySelector('[role="switch"][aria-label*="Accepting responses"], [role="checkbox"][aria-label*="Accepting responses"]');
        if (toggle) {
            const isChecked = toggle.getAttribute('aria-checked') === 'true' || toggle.getAttribute('aria-selected') === 'true';
            if (!isChecked) {
                toggle.click();
                return "TOGGLED_ON";
            }
            return "ALREADY_ON";
        }
        return "TOGGLE_NOT_FOUND";
    }''')
    print(f"[STATUS] {status}")
    await page.close()

async def main():
    browser = await connect(browserURL='http://127.0.0.1:9222')
    with open('/home/rajeev/Data/Personal Project/fastest-finger-first-agent/test_quizzes.json', 'r') as f:
        quizzes = json.load(f)

    for q in quizzes:
        # Get edit URL from public viewform URL
        view_url = q['url']
        # The form ID is in view_url or we can extract form edit URL
        print(f"\nProcessing {q['title']}...")

    await browser.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
