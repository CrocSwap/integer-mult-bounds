# Executed validation

Executed on 2026-11-12T03:25:26.410664+00:00 with Python 3.12.14.
The following four invocations exited successfully:

```sh
python check.py
python -O check.py
python -I -W error -B check.py
python -I -W error -O -B check.py
```

All four structured outputs were byte-identical to RESULT.json. Its SHA256 is
`8a550b3a5537bb47bedef8d419b6bd0f19a2a12b90db2e626448835617b03f58`. Optimized mode does not remove critical checks;
`require` raises explicitly instead of using `assert`. Isolated mode works
from a supplied package location without the repository root on sys.path.

- Scientific program SHA256: `4b516d85baf3303db809bc1174394009b1fc71a8f7d17fb6c729ec8bb6aba245`.
- Emitted table SHA256: `2fc06c64f3ed63d84e130f4c71b721e2ad967f8ca3f424a310424d1597123f8e`.
- 524 locations, 13 tapes, four symbols; no host arithmetic/callback opcode.
- Nine source files authenticated by exact byte length, SHA256 and Git blob.
- 3,814 accepting packets and 31,833 payload bits; 4,053,639 accepting transitions.
- All positive P,R,B with V<=8 (38 shapes), every payload; 64 larger random packets.
- Random seed 20261112; no unbounded search was conducted.
- Every accepting packet satisfied the exact full cost formula and current visit caps.
- Twelve finite invalid packets rejected before DATA writes (2,697 transitions).
- Six actual graph mutations and two wrong-permutation alternatives were detected.
- Six identical-owner grow/shrink/regrow calls; retained private spans
  26,500,500,500,500,500; 26,147 additional transitions.
- Twenty-one exact retained-source flip_digit comparisons; 134,400 transitions.
- Five fixed-vector cases, fifteen literal calls; 553,041 transitions.
- The stride-2 scope control distinguishes XOR 1010 from full four-bit reversal.

The source-map and fixed-vector checks are finite interface tests. They do
not lower the old host caller, supply a general affine routine, certify
strided packing, or prove any new complete multiplication exponent.
The proof of all valid shapes is in PROOF.md. Independent review status
and separate receipts are recorded in REVIEW.md.

The relocated independent commands also passed and reproduced their saved
receipts exactly (structured JSON comparison):

```sh
python -I -W error -B independent/dense_check.py reverse.py
python -I -W error -B independent/peer/check.py .
```

Their original normal/optimized runs agree, as recorded by their authors.
No independent scientific file was edited during packaging. The source-domain
clarification changed only PROOF.md and corresponding metadata; the literal
program and author RESULT receipt remain unchanged.

A scoped whitespace check passes with `core.whitespace=-blank-at-eof`.
The two frozen scientific files retain their reviewed terminal blank line;
the default whitespace checker reports only those two end-of-file blanks.
Their hashes are intentionally preserved. No tracked predecessor deletion
or unrelated staged change is present.
