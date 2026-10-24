# Validation

Executed on Linux with CPython 3.12.15:

- Registered `scripts/research_package.py --package research/typed-quotient-path`: PASS.
- Isolated optimized `python3.12 -I -O -B research/typed-quotient-path/verify.py`: PASS.
- Exact original Git-blob/SHA256 inputs, both paid rank counts and 520-helper census: PASS.
- Both Laurent B normalizations and five sign/orientation/Q controls: PASS.
- All 2,504 complete split/support invoices through p=4: PASS.
- Rational derivative certificate stronger than 1980/7: PASS.

The all-p/all-C assertion is the written monotonicity proof, not extrapolation
from these finite cases. The supplied PR4654 typed native theorem is a premise.
Its 632-row, absolute-phase and all-width proof was not re-audited here.
No selected cold replay, changed native word, higher K or proof-kernel
acceptance is claimed. Hosted checks are separate from local replay.

A separate exact 38-file Git export of PR4654 head dca175fed8ebde8980635fd3b4508b8cba89a1b0 passed its complete portable verifier on Linux/CPython 3.12.15, including 180 warp classes, 448 wrappers, 336 block identities, backward-conjugation and drift controls. The receipt is LINUX-SOURCE-REPLAY.json. This is fresh finite source-verifier execution, not independent review of the universal argument.
