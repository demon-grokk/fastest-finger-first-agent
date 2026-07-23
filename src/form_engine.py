import asyncio
from typing import Dict, List, Any
from pyppeteer import connect, launch
from pyppeteer.page import Page
from pyppeteer.browser import Browser

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
async def connect_to_browser() -> tuple[Browser, Page]:
    """Connects to the active remote debugging Chrome instance."""
    browser = await connect(
        browserURL=config.CHROME_DEBUG_URL,
        defaultViewport={'width': 1050, 'height': 850}
    )
    pages = await browser.pages()
    page = pages[0] if len(pages) > 0 else await browser.newPage()
    return browser, page

async def extract_questions(page: Page) -> List[str]:
    """Navigates and extracts Google Form questions from the DOM."""
    questions = await page.evaluate('''() => {
        const divs = document.querySelectorAll('div[role="listitem"]');
        return Array.from(divs).map(div => {
            const heading = div.querySelector('div[role="heading"]');
            return heading ? heading.textContent.trim() : null;
        }).filter(Boolean);
    }''')
    return questions

async def fill_and_submit_form(page: Page, answers: Dict[str, str], submit: bool = True) -> Dict[str, Any]:
    """Injects answers into text inputs, radio options, and checkboxes, then clicks Submit."""
    result = await page.evaluate('''(answers, clickSubmit) => {
        // 1. Tick the email record consent checkbox if present
        const checkboxes = document.querySelectorAll('[role="checkbox"]');
        let emailChecked = false;
        checkboxes.forEach(cb => {
            const text = (cb.getAttribute('aria-label') || cb.textContent || '').trim().toLowerCase();
            if (text.includes('record') && text.includes('email')) {
                if (cb.getAttribute('aria-checked') !== 'true') {
                    cb.click();
                    emailChecked = true;
                } else {
                    emailChecked = true;
                }
            }
        });

        // 2. Process form questions
        const divs = document.querySelectorAll('div[role="listitem"]');
        let filledCount = 0;

        divs.forEach(div => {
            const headingEl = div.querySelector('div[role="heading"]');
            if (!headingEl) return;
            const questionText = headingEl.textContent.trim().toLowerCase();

            let matchedAnswer = null;
            for (const [qKey, aVal] of Object.entries(answers)) {
                if (questionText.includes(qKey.toLowerCase()) || qKey.toLowerCase().includes(questionText)) {
                    matchedAnswer = aVal;
                    break;
                }
            }

            if (matchedAnswer !== null) {
                // Text input or textarea
                const textInput = div.querySelector('input[type="text"], textarea');
                if (textInput) {
                    textInput.value = matchedAnswer;
                    textInput.dispatchEvent(new Event('input', { bubbles: true }));
                    textInput.dispatchEvent(new Event('change', { bubbles: true }));
                    filledCount++;
                    return;
                }

                // Radio buttons
                const radios = div.querySelectorAll('[role="radio"]');
                if (radios.length > 0) {
                    radios.forEach(radio => {
                        const labelText = radio.getAttribute('aria-label') || radio.textContent.trim();
                        if (labelText.toLowerCase().includes(matchedAnswer.toLowerCase()) || matchedAnswer.toLowerCase().includes(labelText.toLowerCase())) {
                            radio.click();
                            filledCount++;
                        }
                    });
                    return;
                }

                // Multiple-choice checkboxes
                const itemCheckboxes = div.querySelectorAll('[role="checkbox"]');
                if (itemCheckboxes.length > 0) {
                    itemCheckboxes.forEach(checkbox => {
                        const labelText = checkbox.getAttribute('aria-label') || checkbox.textContent.trim();
                        if (labelText.toLowerCase().includes(matchedAnswer.toLowerCase()) || matchedAnswer.toLowerCase().includes(labelText.toLowerCase())) {
                            checkbox.click();
                            filledCount++;
                        }
                    });
                    return;
                }
            }
        });

        // 3. Trigger submit action
        if (clickSubmit) {
            const submitBtn = Array.from(document.querySelectorAll('[role="button"]')).find(btn => {
                const text = btn.textContent.trim().toLowerCase();
                return text === 'submit' || text === 'next';
            });
            if (submitBtn) {
                submitBtn.click();
                return { success: true, filled: filledCount, emailChecked: emailChecked, clickedSubmit: true };
            }
        }

        return { success: false, filled: filledCount, emailChecked: emailChecked, clickedSubmit: false };
    }''', answers, submit)

    return result
