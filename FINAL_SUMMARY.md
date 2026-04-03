# Unattended Benchmark Final Summary

### Hard Stop Condition Reached
Execution was aborted because **all available API keys have been exhausted / reported as leaked**. Consecutive runs yielded `403 PERMISSION_DENIED` errors across all configured key slots (`key_1` through `key_5`).

### Execution Overview

- **What completed**: 
  - `0` pairs completed.
  - Successfully initialized safety checkpoints (tags and branches) in both the `rlm` and `rlm-testing` repositories.
  
- **What failed**: 
  - Pair 1 execution (`python3 llm-test/test_tsp_llm_only.py`) failed due to immediate API key revocation / 403 errors across all key indices dynamically assigned.

- **What was skipped**: 
  - All remaining 7 pairwise runs (13 scripts total in the sequence) were aborted to honor the hard stop rule.

- **Keys Used**: 
  - `key_1`, `key_2`, `key_3`, `key_4`, `key_5` were attempted. None are functional.

- **Branches Updated**: 
  - `anshul-benchmark-findings` (in `rlm` repo): *No commits were made since no pairs completed.*
  - `anshul-benchmark-outputs` (in `rlm-testing` repo): *No commits were made since no pairs completed.*

- **Rollback Checkpoint/Tags**:
  If needed, you can rollback to the exact state before the unattended session using:
  - **`rlm`**: tag `pre-unattended-benchmark-20260402-1110` or branch `checkpoint/pre-unattended-benchmark-20260402-1110`
  - **`rlm-testing`**: tag `pre-unattended-benchmark-20260402-1110` or branch `checkpoint/pre-unattended-benchmark-20260402-1110`
