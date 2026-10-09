# Served controls with cascade frames and compatible butterflies

This package composes PR223's 373 served controls, PR211's 6,191 frame
refinements and **67 of PR217's 440 butterflies**. The other 373 frozen
butterflies each require one of the deleted control roles.

The conditional arithmetic gives

    kappa = 693078488574615 / 10^18 = 0.000693078488574615

This is approximately **0.134926% above PR223**, under its inherited interfaces.
It is not a record claim: newer five-stage candidates already exist. The
overlap audit is useful independently of the numerical result.

## Reproduce

Python 3.11+ and Git are sufficient; no third-party Python package is required.
From a checkout of CrocSwap/integer-mult-bounds containing this package:

```sh
git fetch origin \
  a1175449f34d39ff933d9d8ab23ced1f32b290ec \
  187e1010ac8b259af8e9b5166f68b64bc27b4b47 \
  8786fec0148a41409874cad133123da227d93751 \
  b739fc226a54a4a507989aa1bef092d491287451
git worktree add --detach ../composition-bit a1175449f34d39ff933d9d8ab23ced1f32b290ec
git worktree add --detach ../composition-complex 187e1010ac8b259af8e9b5166f68b64bc27b4b47
git worktree add --detach ../composition-served 8786fec0148a41409874cad133123da227d93751
git worktree add --detach ../composition-frames b739fc226a54a4a507989aa1bef092d491287451
python3 -B research/served-frame-composition/verify.py \
  --bit-root ../composition-bit \
  --complex-root ../composition-complex \
  --served-root ../composition-served \
  --frames-root ../composition-frames \
  --output ../served-frame-replay
```

Use a new output directory on each run. Source checkouts must be at the pinned
commits with no changes to tracked files. The verifier does not download or
modify dependencies. It compares the newly computed result with certificate.json.
`--write-certificate` explicitly regenerates that committed certificate.

The output includes the complete graph/word/frame/schedule payloads, exact prime
witnesses, mathematical certificate and execution receipt. Compressed container
bytes are not treated as semantic identities; emitted input and prime-payload
hashes refer to canonical uncompressed JSON.

## Validation scope

- Exact frame geometry, complete role and target chronology, and rank ledger.
- All 20,261 terminal columns in F2 and both integer decoder directions.
- Seven adverse word/chronology controls and three terminal controls.
- Fresh prime witnesses with a missing-record rejection control.
- Exact charts, bank incidence colouring, two paid moment engines, finite
  ordinary leaves, 47 assembly constraints and seven strict margins.

The repository's `make entrance-bank-verify` target also passed on the
unchanged reviewed checkpoint, including its bank-scheduling diagnostic.
The new verifier passed both certificate generation and a separate fresh
replay against the saved certificate on Python 3.12.14. The replay took about
134 seconds in the development environment; this measures verification cost,
not integer-multiplication performance.

The inherited complex supplier proof is not freshly rerun. The retained
all-size compiler and multiplication-transfer interfaces remain conditional;
finite replay is not full theorem verification or a runtime benchmark.

See PROOF.md for the mathematical scope, NOTICE.md for named predecessors,
and PR.md for a proposed review description.
