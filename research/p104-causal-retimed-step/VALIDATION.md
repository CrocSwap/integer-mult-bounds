# Validation and limits

Local environment: CPython 3.14.7, macOS arm64; exact details in ENVIRONMENT.json. Scientific baseline is #7004 head2ee11a4460f23abf06d16b12f18c8ef9aca889f1. Canonical main refreshed at entry, pivot and submission:17469fff78c22941280f04d39dc5a1faee09c840, priorities revision8, selected record unchanged.

Final stdout is retained in REPLAY.txt; its SHA256 is recorded in ENVIRONMENT.json.

Executed:

- Direct complete verifier with a new receipt output: passed source rebuild, rational cut and all-input endpoint/adjoint, exact forward common-grid, formal caller, full invoice and ordinary bill, BIT binding, two rational price engines, compiler and 54+4 outer gates, precision envelopes, four exact512-column chart/phase checks, five construction mutations, relaxed native replay and full512-component physical replay. The initial status spelling was corrected without changing scientific data.
- Final direct command against frozen RESULT.json: passed, ending PASS_P104_RETIMED_HELPER_STEP. Command: `python3 -I -B research/p104-causal-retimed-step/verify.py`.
- `python3 -B scripts/research_package.py --package research/p104-causal-retimed-step --check-only`: passed metadata and exact provenance pins; not a mathematical acceptance check.

The local interpreter has no Python 3.12, so the repository's registered 3.12 execution is unrun locally. The registered manifest supplies the complete command for hosted replay. Optimized mode is rejected deliberately because borrowed source engines use assertions. No Lean, Docker, whole selected multiplier or all-history replay was run.

Exact endpoint replay and finite physical replay are distinct evidence. The original source engines retain their attribution and assumptions; these checks do not constitute independent human/kernel review or full supplier admission. In particular, all five framework assumptions plus #7004's exact odd-return, owned-ascent, caller, paired BIT and physical-tariff contracts remain.
