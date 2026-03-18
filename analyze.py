import os
import sys
import json
import time

# Add local path 
sys.path.insert(0, os.path.abspath('.'))
from rlm.rlm_repl import RLM_REPL

def load_repo(repo_path):
    structure = {}
    for root, _, files in os.walk(repo_path):
        if '.git' in root or 'node_modules' in root or '__pycache__' in root or 'venv' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.md', '.html', '.css', '.env_example')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        relative_path = os.path.relpath(filepath, repo_path)
                        structure[relative_path] = content
                except Exception:
                    pass
    return structure

repo_data = load_repo("./Intellidoc")
repo_context = json.dumps(repo_data)

query = """You are analyzing a GitHub repository called "Intellidoc". https://github.com/parthgenx/Intellidoc

Your task is to deeply understand the architecture of this repository and explain how the system works.
Do not give a generic explanation. Base your answer strictly on the repository's files, functions, and structure.

Tasks:

1. Explain the complete workflow when a user uploads and opens a document (PDF or DOCX).
   - Start from the user interaction in the UI
   - Trace the flow through the system
   - Explain how the document is parsed, processed, and rendered in the viewer.

2. Explain how the AI-powered features work in this repository.
   Specifically:
   - Document summarization
   - Text extraction from documents
   - Any AI or API calls used for analysis.

3. Identify the key modules/components responsible for:
   - Document loading
   - Rendering the document
   - Searching inside the document
   - Generating summaries
   - Translation (if implemented)

4. Trace the dependencies between components.
   Explain which components call or depend on others.

5. Identify potential architectural improvements or bottlenecks in the current implementation.

Important requirements:
- Mention specific files and functions when explaining.
- Do not hallucinate functionality that does not exist in the repository.
- If something is unclear, explicitly say it is unclear rather than guessing.
- Focus on architectural reasoning rather than superficial summaries.

Additionally perform the following measurement logic:

1. Record the start time before generating the response.
2. Record the end time after generating the response.
3. Compute latency using:

latency = end_time - start_time

4. Report estimated token usage including:
- input_tokens
- output_tokens
- total_tokens

Output format:

----------------------

1. System Architecture Overview
2. Document Upload & Rendering Pipeline
3. AI Feature Pipeline
4. Component Dependency Map
5. Potential Improvements

----------------------

Benchmark Metrics

Latency: <seconds>
Input Tokens: <number>
Output Tokens: <number>
Total Tokens: <number>"""

print("Initializing RLM with Gemini 2.0 Flash...")
rlm = RLM_REPL(
    provider="gemini",
    model="gemini-2.0-flash",
    recursive_model="gemini-2.0-flash",
    enable_logging=True,
    max_iterations=10,
)

print(f"Feeding the repo context (length: {len(repo_context)} chars) and query...")
start_time = time.time()
# context as a dictionary list allows the `rlm_repl` `utils.convert_context_for_repl` to write it as `context.json`
result = rlm.completion(context=[repo_data], query=query)
end_time = time.time()
print(f"Total Client Time: {end_time - start_time:.2f}s")

# Write to file for the user
with open('intellidoc_analysis.md', 'w') as f:
    f.write(result)
    
print("Saved analysis to intellidoc_analysis.md!")
