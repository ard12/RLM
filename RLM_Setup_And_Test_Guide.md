# RLM Setup And Test Guide

## Purpose

This guide explains:

1. how to set up the `RLM-FULL` repo locally
2. how to run the plain `LLM` and `RLM` benchmark scripts
3. how the imported `llm-test/` and `rlm-test/` folders are organized
4. which tests are cheapest to run first
5. where the recorded rerun notes live

This guide is written for the current local benchmark workflow used in this repo.

## Repo Location

Current workspace:

`/Users/abhigyanshekhar/Desktop/RLM-FULL`

## If You Already Cloned The Repo

You do not need to clone again.

Use:

```bash
cd /path/to/rlm
git fetch origin
git checkout codex-tsp-rlm-benchmark
git pull origin codex-tsp-rlm-benchmark
```

If you do not have the repo yet:

```bash
git clone https://github.com/Abhigyan-Shekhar/rlm.git
cd rlm
git checkout codex-tsp-rlm-benchmark
```

## Environment Setup

### Option 1: Use The Existing Virtualenv

If the repo already has `.venv` and dependencies installed:

```bash
cd /Users/abhigyanshekhar/Desktop/RLM-FULL
source .venv/bin/activate
```

### Option 2: Fresh Setup With `uv`

```bash
cd /Users/abhigyanshekhar/Desktop/RLM-FULL
uv venv --python 3.11
source .venv/bin/activate
uv pip install -e .
```

### API Key

Set your Gemini API key before running the benchmarks:

```bash
export GEMINI_API_KEY="your_key_here"
```

Or put it in `.env` at the repo root:

```env
GEMINI_API_KEY=your_key_here
```

## Benchmark Layout

There are two benchmark styles in this repo.

### Root Scripts

These live in the repo root and are the main local benchmark scripts used in the recent runs.

- `*_llm_only.py`: plain baseline `LLM`
- paired non-`llm_only` script: usually baseline `LLM` plus `RLM`

Examples:

- `test_tsp_llm_only.py`
- `test_tsp_branch_bound.py`
- `test_stochastic_tsp_adaptive_llm_only.py`
- `test_stochastic_tsp_adaptive.py`
- `test_long_context_authproxy.py`

### Imported Benchmark Folders

This repo now also contains the imported benchmark folders from the external `rlm-testing` repo:

- `/Users/abhigyanshekhar/Desktop/RLM-FULL/llm-test`
- `/Users/abhigyanshekhar/Desktop/RLM-FULL/rlm-test`

Use these when you want the preserved original benchmark scripts and saved markdown logs.

#### `llm-test/`

This folder preserves the external baseline-only scripts that were copied in for comparison:

`/Users/abhigyanshekhar/Desktop/RLM-FULL/llm-test`

Typical files:

- `test_llm.py`
- `test2_llm.py`
- `clinical-llm.py`
- `test_tsp_llm_only.py`
- `test_stochastic_tsp_adaptive_llm_only.py`
- `test_pdf_cersei_warning.py`
- `test_launch_note_app.py`

#### `rlm-test/`

This folder preserves the external `RLM` benchmark scripts and their saved logs:

`/Users/abhigyanshekhar/Desktop/RLM-FULL/rlm-test`

Typical files:

- `test_got.py`
- `test_long_context_authproxy.py`
- `test_long_context_clinical_trial.py`
- `test_tsp_branch_bound.py`
- `test_stochastic_tsp_adaptive.py`
- `test_pdf_cersei_warning.py`
- `test_launch_note_app.py`

## Which Scripts Should You Use?

Use the root scripts if:

- you want the latest local benchmark harnesses
- you want the rerun notes in this repo to line up with the scripts you run

Use `llm-test/` and `rlm-test/` if:

- you want the imported original benchmark layout from `rlm-testing`
- you want to compare against the saved historical markdown logs in those folders

## Cheapest Tests To Run First

If you want to spend the fewest credits, start with the under-specified TSP pair.

### Cheapest Matched Pair

```bash
cd /Users/abhigyanshekhar/Desktop/RLM-FULL
source .venv/bin/activate

python3 test_tsp_llm_only.py
python3 test_tsp_branch_bound.py
```

Why this pair is cheap:

- short prompt
- short correct answer when grounded
- lower token usage than the long-context and stochastic benchmarks

## Core Tests And Commands

### 1. Under-Specified TSP

Purpose:

- tests hallucination resistance
- the prompt is intentionally unsolvable because the distance matrix is missing

Commands:

```bash
python3 test_tsp_llm_only.py
python3 test_tsp_branch_bound.py
```

Imported equivalents:

```bash
python3 llm-test/test_tsp_llm_only.py
python3 rlm-test/test_tsp_branch_bound.py
```

Expected correct behavior:

- say the task is under-specified
- do not invent a distance matrix

Rerun note:

- [`benchmark_rerun_tsp.md`](/Users/abhigyanshekhar/Desktop/RLM-FULL/benchmark_rerun_tsp.md)

### 2. Stochastic Adaptive TSP

Purpose:

- tests exact dynamic reasoning on a fully specified stochastic optimization problem

Commands:

```bash
python3 test_stochastic_tsp_adaptive_llm_only.py
python3 test_stochastic_tsp_adaptive.py
```

Imported equivalents:

```bash
python3 llm-test/test_stochastic_tsp_adaptive_llm_only.py
python3 rlm-test/test_stochastic_tsp_adaptive.py
```

Rerun note:

- [`benchmark_rerun_stochastic_tsp.md`](/Users/abhigyanshekhar/Desktop/RLM-FULL/benchmark_rerun_stochastic_tsp.md)

### 3. AuthProxy Long-Context Retrieval

Purpose:

- tests retrieval under noise, distractors, and misleading facts

Root `RLM` command:

```bash
python3 test_long_context_authproxy.py
```

Imported `RLM` command:

```bash
python3 rlm-test/test_long_context_authproxy.py
```

Important baseline note:

- the imported LLM-only auth proxy script depends on `google.generativeai`
- in the current local environment, that file may not run unless that package is installed
- the latest baseline comparison was run with an equivalent one-off Gemini client command using the exact prompt from `test_long_context_authproxy.py`

Imported baseline file path:

- `llm-test/llm-test for long context problem - same as rlm , just modified for llm`

Rerun note:

- [`benchmark_rerun_authproxy.md`](/Users/abhigyanshekhar/Desktop/RLM-FULL/benchmark_rerun_authproxy.md)

### 4. Other Long-Context And Planning Tests

Commands:

```bash
python3 test_pdf_cersei_warning.py
python3 test_long_context_clinical_trial.py
python3 test_launch_note_app.py
```

These are more expensive than the cheap TSP pair.

Imported equivalents:

```bash
python3 llm-test/clinical-llm.py
python3 llm-test/test_launch_note_app.py
python3 llm-test/test_pdf_cersei_warning.py

python3 rlm-test/test_long_context_clinical_trial.py
python3 rlm-test/test_launch_note_app.py
python3 rlm-test/test_pdf_cersei_warning.py
python3 rlm-test/test_got.py
```

## Recommended Run Order

Use this order when you want a practical sequence from cheapest to more expensive:

1. `python3 test_tsp_llm_only.py`
2. `python3 test_tsp_branch_bound.py`
3. `python3 test_stochastic_tsp_adaptive_llm_only.py`
4. `python3 test_stochastic_tsp_adaptive.py`
5. `python3 test_long_context_authproxy.py`
6. `python3 test_long_context_clinical_trial.py`
7. `python3 test_pdf_cersei_warning.py`
8. `python3 test_launch_note_app.py`

If you want to stay entirely inside the imported benchmark layout, use:

1. `python3 llm-test/test_tsp_llm_only.py`
2. `python3 rlm-test/test_tsp_branch_bound.py`
3. `python3 llm-test/test_stochastic_tsp_adaptive_llm_only.py`
4. `python3 rlm-test/test_stochastic_tsp_adaptive.py`
5. `python3 rlm-test/test_long_context_authproxy.py`
6. `python3 rlm-test/test_long_context_clinical_trial.py`
7. `python3 llm-test/test_pdf_cersei_warning.py`
8. `python3 rlm-test/test_pdf_cersei_warning.py`
9. `python3 llm-test/test_launch_note_app.py`
10. `python3 rlm-test/test_launch_note_app.py`

## How To Interpret Outputs

Most scripts print:

- the prompt
- the answer
- wall time
- token usage

For `RLM` runs, also expect:

- iteration-by-iteration trace
- code blocks executed in the local REPL
- sub-calls via `llm_query`
- final answer section
- latency breakdown

## Current Local Findings Snapshot

### Under-Specified TSP

- useful for grounding and hallucination checks
- `RLM` has shown grounded refusals on missing-matrix runs
- baseline `LLM` has been inconsistent across runs

### Stochastic Adaptive TSP

- stronger computation benchmark than the missing-matrix TSP
- latest recorded `RLM` metrics:
  - total wall time: `73.576s`
  - execution time: `73.378s`
  - input tokens: `14,740`
  - output tokens: `3,328`
  - total tokens: `18,068`

### AuthProxy

- latest baseline `LLM` run was clean and efficient
- latest `RLM` run did not cleanly answer Q1-Q5, even though it indirectly recovered the key facts

## Files Worth Checking

- [`README.md`](/Users/abhigyanshekhar/Desktop/RLM-FULL/README.md)
- [`benchmark_rerun_tsp.md`](/Users/abhigyanshekhar/Desktop/RLM-FULL/benchmark_rerun_tsp.md)
- [`benchmark_rerun_stochastic_tsp.md`](/Users/abhigyanshekhar/Desktop/RLM-FULL/benchmark_rerun_stochastic_tsp.md)
- [`benchmark_rerun_authproxy.md`](/Users/abhigyanshekhar/Desktop/RLM-FULL/benchmark_rerun_authproxy.md)
- [`llm-test`](/Users/abhigyanshekhar/Desktop/RLM-FULL/llm-test)
- [`rlm-test`](/Users/abhigyanshekhar/Desktop/RLM-FULL/rlm-test)

## Minimal Setup Checklist

```bash
cd /Users/abhigyanshekhar/Desktop/RLM-FULL
source .venv/bin/activate
export GEMINI_API_KEY="your_key_here"
python3 test_tsp_llm_only.py
python3 test_tsp_branch_bound.py
```

That is the fastest path to confirm the repo is set up and the benchmark harness works.
