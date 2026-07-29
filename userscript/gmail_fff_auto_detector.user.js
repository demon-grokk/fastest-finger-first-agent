// ==UserScript==
// @name         Fastest Finger First - Gmail Auto Form Detector & Clicker
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  Monitors Gmail inbox, auto-opens HR email, extracts image links, and submits Google Form!
// @author       Antigravity Deepmind Team
// @match        https://mail.google.com/*
// @match        *://mail.google.com/*
// @include      https://mail.google.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_notification
// @run-at       document-idle
// ==UserScript==

(function() {
    'use strict';

    const WEBHOOK_URL = 'http://localhost:5000/solve';
    const PROCESSED_URLS = new Set();
    let AUTO_OPENED = false;

    console.log('[FFF AGENT v2.0] Gmail Auto-Detector & Clicker active!');

    function createToast(message, isSuccess = true) {
        let toast = document.getElementById('fff-agent-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'fff-agent-toast';
            toast.style.position = 'fixed';
            toast.style.top = '20px';
            toast.style.right = '20px';
            toast.style.zIndex = '999999';
            toast.style.padding = '12px 20px';
            toast.style.borderRadius = '8px';
            toast.style.fontFamily = 'Google Sans, Roboto, sans-serif';
            toast.style.fontSize = '14px';
            toast.style.fontWeight = 'bold';
            toast.style.color = '#ffffff';
            toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
            toast.style.transition = 'all 0.3s ease';
            document.body.appendChild(toast);
        }
        toast.style.backgroundColor = isSuccess ? '#0f9d58' : '#d93025';
        toast.innerText = message;
        toast.style.display = 'block';

        setTimeout(() => {
            if (toast) toast.style.display = 'none';
        }, 5000);
    }

    function extractActualFormUrl(rawUrl) {
        if (!rawUrl) return null;

        // If wrapped in Gmail redirect google.com/url?q=...
        if (rawUrl.includes('google.com/url?q=')) {
            try {
                const urlParams = new URLSearchParams(new URL(rawUrl).search);
                rawUrl = urlParams.get('q') || rawUrl;
            } catch(e) {}
        }

        // Clean query parameters
        let clean = rawUrl.split('?')[0].split('&')[0].split('"')[0].split("'")[0].trim();
        if (clean.includes('docs.google.com/forms') || clean.includes('forms.gle')) {
            if (!clean.endsWith('/viewform') && clean.includes('/viewform')) {
                clean = clean.split('/viewform')[0] + '/viewform';
            }
            return clean;
        }
        return null;
    }

    function scanForQuizUrls() {
        let foundUrls = [];

        // 1. Scan all anchor tags (including links wrapped around images & data-saferedirecturl)
        try {
            const links = document.querySelectorAll('a[href], a[data-saferedirecturl]');
            links.forEach(link => {
                const hrefUrl = extractActualFormUrl(link.href);
                if (hrefUrl) foundUrls.push(hrefUrl);

                const redirectUrl = extractActualFormUrl(link.getAttribute('data-saferedirecturl'));
                if (redirectUrl) foundUrls.push(redirectUrl);
            });
        } catch(e) {}

        // 2. Scan visible page text via regex
        try {
            const regex = /https:\/\/(docs\.google\.com\/forms\/d\/e\/[a-zA-Z0-9_-]+\/viewform|forms\.gle\/[a-zA-Z0-9_-]+)/g;
            const bodyText = document.body.innerText || '';
            const matches = bodyText.match(regex);
            if (matches) foundUrls.push(...matches);
        } catch(e) {}

        if (foundUrls.length === 0) return;

        foundUrls.forEach(url => {
            if (!PROCESSED_URLS.has(url)) {
                PROCESSED_URLS.add(url);
                console.log('[FFF AGENT] ⚡ Extracted Google Form URL:', url);
                createToast('⚡ FFF Agent: Image/Text Form link detected! Solving...', true);
                sendToAgent(url);
            }
        });
    }

    function autoOpenHREmail() {
        if (AUTO_OPENED) return;

        // Look for unread email rows with "Fastest Finger First" in inbox
        const emailRows = document.querySelectorAll('tr[role="row"]');
        emailRows.forEach(row => {
            const rowText = row.innerText || '';
            if (rowText.includes('Fastest Finger First') || rowText.includes('Team HR')) {
                console.log('[FFF AGENT] ⚡ HR Quiz Email Row Found! Auto-clicking...');
                createToast('⚡ FFF Agent: HR Quiz Email arrived! Auto-opening...', true);
                AUTO_OPENED = true;
                row.click();
            }
        });
    }

    function sendToAgent(formUrl) {
        GM_xmlhttpRequest({
            method: 'POST',
            url: WEBHOOK_URL,
            headers: {
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({ url: formUrl }),
            onload: function(response) {
                if (response.status === 200) {
                    console.log('[FFF AGENT] Successfully sent URL to local solver agent!');
                    createToast('🚀 FFF Agent: Sent to local solver! Submitting...', true);
                }
            },
            onerror: function(err) {
                console.error('[FFF AGENT] Server error:', err);
                createToast('❌ FFF Agent: Run "python cli.py watch" in terminal!', false);
            }
        });
    }

    // High-frequency DOM watcher
    const observer = new MutationObserver(() => {
        autoOpenHREmail();
        scanForQuizUrls();
    });

    observer.observe(document.body, { childList: true, subtree: true });
    setInterval(() => {
        autoOpenHREmail();
        scanForQuizUrls();
    }, 500);

    createToast('⚡ FFF Agent v2.0 Ready & Active!', true);
})();
