# Fastest Finger First - AI Quiz Agent ⚡🏆

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![OS Compatibility](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Benchmark](https://img.shields.io/badge/benchmark-%3C2.5s--execution-orange.svg)]()
[![Powered By](https://img.shields.io/badge/powered%20by-Groq%20%2B%20Llama%203.3-purple.svg)](https://console.groq.com)

An ultra-high-speed, **100% autonomous, zero-dependency** Google Forms quiz solver designed for live quiz competitions (like *"Fastest Finger First"*). 

The agent monitors Gmail natively in headless Chrome, detects incoming HR quiz emails, opens them, extracts Google Form links (including image links), solves questions using **Groq's free Llama 3.3 70B API**, and submits the form — all in **under 2.5 seconds** with **zero human intervention**.

---

## 💻 OS Independence (Windows, macOS, Linux)

This project is **100% OS-Independent** and works identically on **Windows (PowerShell / CMD)**, **macOS**, and **Linux**:
* **Chrome Path Auto-Detection**: Automatically locates installed Google Chrome binaries across Windows (`C:\Program Files\Google\Chrome`), macOS, and Linux.
* **Persistent Session Profile**: Saves your logged-in Google session cross-platform in `~/.fff-agent-profile` (`C:\Users\<User>\.fff-agent-profile` on Windows).
* **Zero Browser Extensions Required**: Pure Python + Chrome DevTools Protocol implementation.

---

## 🏆 Performance & Competition Results

* **Global Competition Benchmark**: **< 2.5 seconds** total turnaround (from email arrival in Gmail to submitted form confirmation).
* **Zero Mid-Quiz Approvals**: Fully autonomous AI reasoning with Groq Llama 3.3 70B.
* **Top-5 Email Safeguard**: Only inspects the top 5 most recent emails to prevent re-submitting stale or old quizzes and conserve API quota.

---

## 📦 Installation & Setup

### 1. Clone & Install Dependencies

**Linux / macOS:**
```bash
git clone https://github.com/your-username/fastest-finger-first-agent.git
cd fastest-finger-first-agent

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/your-username/fastest-finger-first-agent.git
cd fastest-finger-first-agent

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🔑 Step 2: Set Up Your Free Groq API Key

The agent uses **Groq's free API** (no credit card required) to solve quiz questions using **Llama 3.3 70B**.

1. Sign up for free at **[console.groq.com](https://console.groq.com)**.
2. Go to **API Keys** → Click **"Create API Key"** (starts with `gsk_...`).
3. Create a `.env` file in the project root directory:

**Linux / macOS:**
```bash
echo 'GROQ_API_KEY=gsk_your_actual_key_here' > .env
```

**Windows (PowerShell):**
```powershell
"GROQ_API_KEY=gsk_your_actual_key_here" | Out-File -FilePath .env -Encoding utf8
```

---

## 🔐 Step 3: One-Time Google Account Login (`python cli.py login`)

Some Google Forms require users to be logged into a Google Account (*"Limit to 1 response"*).

To save your Google session permanently, **run this command ONCE before quiz day**:

```bash
python cli.py login
```

1. A visible Chrome window will open pointing to Google Account Sign-In.
2. Log into your Google Account.
3. Return to the terminal and press **ENTER**.

> 💡 **Saved Permanently**: Session cookies are saved in `~/.fff-agent-profile`. All future `watch-gmail` and `listen` runs will automatically run signed in!

---

## 🚀 How to Run

### 🌟 Mode 1: Native Gmail Watcher (RECOMMENDED for Competitions)

Monitors Gmail natively in headless Chrome using your saved profile. Includes a **Top-5 Email Safeguard** and **High-Precision Timing Logs**.

Run at ~10:55 AM before the competition:
```bash
python cli.py watch-gmail
```

**Timestamped Execution Logs:**
```text
===========================================================================
⚡ FASTEST FINGER FIRST - NATIVE GMAIL INBOX WATCHER ⚡
Profile Directory: /home/user/.fff-agent-profile
Top-Email Safeguard Limit: Top 5 Inbox Mails
===========================================================================

[12:41:00.123] [GMAIL WATCHER] Connecting to Chrome session...
[12:41:01.450] [GMAIL WATCHER] Gmail Inbox loaded in 1.327s!
[12:41:01.455] [GMAIL WATCHER] 🟢 Active monitoring enabled! Polling top 5 emails every 500ms...

[12:41:05.100] [GMAIL WATCHER] ⚡ Fresh Google Form Link Discovered: https://docs.google.com/forms/d/e/.../viewform
[12:41:05.102] [SOLVER] Opening dedicated tab for form...
[12:41:05.650] [TIMING] Navigation completed in 0.548s
[12:41:05.900] [TIMING] Form questions loaded in 0.250s
[12:41:06.120] [TIMING] Extracted 3 questions in 0.220s
[12:41:06.900] [TIMING] LLM reasoning completed in 0.780s
[12:41:07.350] [TIMING] Form filled & submitted in 0.450s
[12:41:07.351] [BENCHMARK] ⚡ TOTAL TURNAROUND BENCHMARK: 2.249 seconds!
```

---

### ⚡ Mode 2: Direct Form URL Solver (Manual Link Input)

If you already have the Google Form URL and want to solve it immediately:

```bash
python cli.py listen --url "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform"
```

---

### 🎯 Mode 3: Direct One-Shot Command (Pre-Known Answers)

If you already know the answers beforehand and want to bypass AI:

```bash
python cli.py submit \
  --url "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform" \
  --answers '{"question keyword": "answer", "another keyword": "another answer"}'
```

---

## 📈 Benchmark Comparison

| Execution Strategy | Time Taken | User Approvals | Result |
| :--- | :--- | :--- | :--- |
| **Interactive Browser Subagent** | 60 - 90s | 3+ approvals | ❌ Lost |
| **Manual Shell Command Execution** | 70 - 75s | 4 approvals | ❌ Lost |
| **Native Gmail Watcher + Groq AI (Our Agent)** | **< 2.5s** | **0 approvals** | **🏆 Sub-2.5s Winner** |

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
