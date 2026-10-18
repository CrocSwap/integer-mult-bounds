#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Compare all four complete replays; timings belong to fresh benchmark workers."""

import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import worker


def main():
    expected = json.loads((HERE / "RESULT.json").read_bytes())
    for mode in worker.MODES:
        result = worker.run(mode)
        worker.require(result.pop("mode") == mode, "requested census mode")
        worker.require(result == expected, "complete cross-mode census mismatch: " + mode)
        print("PASS_COMPLETE_CENSUS", mode, result["census_sha256"], flush=True)
    print("PASS_FANO_COMPACT_STORAGE full_receipts=4 no_new_mathematical_claim")


if __name__ == "__main__":
    main()
