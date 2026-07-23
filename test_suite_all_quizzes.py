import json
import time
import subprocess
import os
import sys

def run_test_suite():
    json_path = "/home/rajeev/Data/Personal Project/fastest-finger-first-agent/test_quizzes.json"
    if not os.path.exists(json_path):
        print("[ERROR] test_quizzes.json not found!")
        sys.exit(1)

    with open(json_path, 'r') as f:
        quizzes = json.load(f)

    results = []
    print("================================================================")
    print("🏆 FASTEST FINGER FIRST - BENCHMARK SUITE FOR 5 QUIZZES")
    print("================================================================")

    for idx, quiz in enumerate(quizzes, 1):
        title = quiz['title']
        url = quiz['url']
        stop_words = {'what', 'which', 'where', 'when', 'how', 'does', 'this', 'that', 'have', 'from', 'with', 'your'}
        answers_dict = {}
        for q in quiz['questions']:
            words = [w.lower() for w in q['q'].replace('?', '').split() if len(w) > 3 and w.lower() not in stop_words]
            key = words[0] if words else q['q']
            answers_dict[key] = q['a']

        print(f"\n[TEST {idx}/5] {title}")
        print(f"URL: {url}")
        print(f"Answers: {answers_dict}")

        start_t = time.time()
        cmd = [
            "/home/rajeev/.gemini/antigravity/brain/7339498b-d1da-4965-85b6-89ff7c9c20b5/scratch/venv/bin/python",
            "/home/rajeev/Data/Personal Project/fastest-finger-first-agent/cli.py",
            "submit",
            "--url", url,
            "--answers", json.dumps(answers_dict)
        ]

        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        duration = time.time() - start_t

        print(f"[STDOUT]\n{proc.stdout}")
        if proc.stderr:
            print(f"[STDERR]\n{proc.stderr}")

        success = "success': True" in proc.stdout or "'success': True" in proc.stdout
        status = "PASSED ⚡" if success else "FAILED ❌"

        results.append({
            "quiz": title,
            "duration": round(duration, 2),
            "status": status,
            "stdout": proc.stdout
        })

        print(f"[STATUS] {status} in {duration:.2f} seconds")

    print("\n================================================================")
    print("📊 FINAL BENCHMARK SUMMARY REPORT")
    print("================================================================")
    total_time = 0
    passed_count = 0
    for r in results:
        total_time += r['duration']
        if "PASSED" in r['status']:
            passed_count += 1
        print(f"- {r['quiz']}: {r['duration']}s ({r['status']})")

    avg_time = total_time / len(results) if results else 0
    print("----------------------------------------------------------------")
    print(f"Total Quizzes Tested : {len(results)}")
    print(f"Success Rate         : {passed_count}/{len(results)} ({passed_count/len(results)*100:.0f}%)")
    print(f"Average Speed        : {avg_time:.2f} seconds per quiz!")
    print("================================================================")

if __name__ == '__main__':
    run_test_suite()
