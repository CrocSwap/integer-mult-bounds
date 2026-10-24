# Actual paid-site sensitivity

This component proves the scoped result in [PROOF.md](PROOF.md). Its scientific
receipt records all 6,596 actual paid sites, the independent fault witnesses,
four rejecting controls, direct finite-fault checks and the exact conditional
all-concave-moments cost comparison. It does not claim a new bound or exclude
coherent correlated implementations.

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -I -O -B research/two-full-border-paid-precision/paid-sensitivity/check_paid_sensitivity.py --expected research/two-full-border-paid-precision/paid-sensitivity/PAID-SENSITIVITY.json.gz --out /tmp/paid-sensitivity-replay.json.gz
```

The output path must be fresh. Replay compares the decoded JSON payload, not
gzip container bytes. The checker uses only the Python standard library and
reads the exact current round-three input declared in SOURCES.json. An exported
input can be supplied through `--source /path/to/ACTUAL-WORD.json.gz`.

Prepared by Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0. Predecessor and source credit is retained
in SOURCES.json and PROOF.md.
