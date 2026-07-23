import os
import json
import urllib.request
import urllib.error

def solve_questions_with_llm(questions: list[str]) -> dict[str, str]:
    """
    Optional standalone solver using Gemini API or OpenAI API.
    If GEMINI_API_KEY or OPENAI_API_KEY is present in environment,
    solves questions autonomously without requiring pair programming.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    prompt = (
        "You are an ultra-fast quiz solver. Answer the following quiz questions concisely.\n"
        "Return ONLY a raw JSON object mapping each question to its answer.\n"
        f"Questions:\n{json.dumps(questions, indent=2)}"
    )

    if gemini_key:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                text = data['candidates'][0]['content']['parts'][0]['text']
                return json.loads(text)
        except Exception as e:
            print(f"[LLM] Gemini API call failed: {e}")

    elif openai_key:
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {openai_key}'
        })
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                text = data['choices'][0]['message']['content']
                return json.loads(text)
        except Exception as e:
            print(f"[LLM] OpenAI API call failed: {e}")

    return {}
