import os
import sys
import time
import subprocess
import re
from dotenv import load_dotenv

load_dotenv()


scripts = [
    r"llm-test/llm-test for long context problem - same as rlm , just modified for llm",
    r"rlm-test/test_long_context_authproxy.py",
    r"llm-test/clinical-llm.py",
    r"rlm-test/test_long_context_clinical_trial.py",
    r"llm-test/test_launch_note_app.py",
    r"rlm-test/test_launch_note_app.py",
    r"llm-test/test_pdf_cersei_warning.py",
    r"rlm-test/test_pdf_cersei_warning.py",
    r"llm-test/test_llm.py",
    r"rlm-test/test_got.py"
]
keys = [v for k, v in os.environ.items() if k.startswith("GEMINI_API_KEY") and v.strip()]
if "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"].strip() not in keys:
    keys.insert(0, os.environ["GEMINI_API_KEY"].strip())

if not keys:
    print("Warning: No GEMINI_API_KEY or GEMINI_API_KEY_n environment variables found.")
    keys = [""] # dummy key to avoid IndexError, will fail on use


os.makedirs("benchmark-outputs", exist_ok=True)

env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"

key_idx = 0

for s in scripts:
    print(f"Running {s}...")
    name = os.path.basename(s).replace('.py', '')
    if 'long context problem' in name:
        name = 'authproxy-llm'

    max_retries = len(keys)
    
    for retry in range(max_retries):
        env["GEMINI_API_KEY"] = keys[key_idx]
        print(f"  Using key index {key_idx}")
        start_t = time.perf_counter()
        try:
            cp = subprocess.run([sys.executable, s], capture_output=True, text=True, timeout=600, env=env, encoding="utf-8", errors="replace")
            stdout = cp.stdout
            stderr = cp.stderr
            status = "success" if cp.returncode == 0 else "failed (non-zero)"
        except subprocess.TimeoutExpired as e:
            stdout = str(e.stdout)
            stderr = str(e.stderr)
            status = "failed (timeout 600s)"
        except Exception as e:
            stdout = str(e)
            stderr = ""
            status = "failed"
        end_t = time.perf_counter()
        duration = end_t - start_t

        full_output = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
        
        # Check for 429 ResourceExhausted
        if "429" in str(stderr) and "quota" in str(stderr).lower():
            print(f"  Hit 429 ResourceExhausted for {name}. Switching key and retrying.")
            key_idx = (key_idx + 1) % len(keys)
            time.sleep(5)  # slight cooldown before retry
            continue
        else:
            break

    # Extract metrics if they exist
    tokens = ""
    wall = ""
    if "input=" in full_output:
        match = re.search(r"input=([\d,]+),\s*output=([\d,]+)", full_output)
        if match:
            tokens = f"- Input tokens: {match.group(1)}\n- Output tokens: {match.group(2)}"
    if "wall time:" in full_output.lower():
        match = re.search(r"wall time:\s*([\d\.]+)s", full_output.lower())
        if match:
            wall = f"- Computed/Reported Wall time: {match.group(1)}s"

    # Handle duplicate script names by prepending llm/rlm directory name
    if s.startswith("llm-test/"):
        final_name = name + "_llm-anshul.md"
    else:
        final_name = name + "_rlm-anshul.md"
        
    md = f"""# Run Metadata
- Repo: https://github.com/ard12/rlm
- Branch: anshul-benchmark-findings
- Script: {s}
- Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}
- Command: python "{s}"
- Status: {status}

# Environment Snapshot
- Python version: {sys.version.split(' ')[0]}
- Active virtualenv: {sys.prefix}
- Provider/model: gemini-2.5-flash

# Raw Output
```text
{full_output[:40000]}
```

# Metrics
- Actual Wall time (Python run): {duration:.3f}s
{wall}
{tokens}

# Notes
{'(Script failed or timed out)' if status != 'success' else 'Execution finished successfully.'}
"""
    with open(f"benchmark-outputs/{final_name}", "w", encoding="utf-8", errors="ignore") as f:
        f.write(md)
    print(f"  -> Saved to {final_name} in {duration:.2f}s")
