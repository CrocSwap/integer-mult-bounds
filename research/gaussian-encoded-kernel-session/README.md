# Encoded Gaussian kernel preparation session

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

A persistent fixed-bank owner keeps one actual PR3851 Axis and one encoded
old-kernel inverse across a stream of protected Gaussian pages. Each page
retains the original Window Schur/LU/factor layout and is consumed by actual
Core.run. The cache stores serialized source Matrix tapes, not host rational
matrices. A hit returns an independently owned encoded copy; a changed length
evicts the resident entry. Kernel values and bandwidth remain private and
immutable for the session lifetime.

The complete paid profile in [PROOF.md](PROOF.md) retains initial Axis setup,
every non-inverse Window operation, all miss inversions, every hit/miss copy,
lookup, eviction, page emission/consumption, Core/halo calls and final disposal.
The inverse allowance changes from all requests to misses, with an explicit
O((k+1)^8(P+log(k+1))^3) copy allowance on every request. Original inversions
retain the source O((k+1)^10(P+log(k+1))^3) allowance. Persistent high-water
backing is charged. No unconditional short-stream speedup or complete supplier
budget improvement is inferred.

`guard_verify.py` separately checks all five encoded parameter roles against
both resident pool and output aliases, using the actual Count/Signed/Tape/run
classes. Its deliberately incomplete owner never passes the guard and is not
production admission evidence. Normal and optimized modes both use explicit
checks; this cheap calibration was added after independent peer review.

The source-bound verifier executes axis(13,14,1,1), work precision24 and target16.
It checks identical protected-page and nonzero actual Core bytes across a real
miss and hit, a changed-length eviction, an actual encoded resident numerical
corruption, pending-output protection, negative signed resident-alias rejection
before any tape traffic, borrowed frames, and complete session disposal. The
third window exercises page production/eviction only; its Core call is not
repeated. Owner meter counters include the validation controls and are finite
observations, not a fitted general cost theorem.

Reproduce serially with Python3.12; each actual source replay takes several
minutes and should not run concurrently with other scientific regeneration:

```sh
python3.12 -I -B research/gaussian-encoded-kernel-session/verify.py
python3.12 -I -O -B research/gaussian-encoded-kernel-session/verify.py
python3.12 scripts/research_package.py --package research/gaussian-encoded-kernel-session --check-only
```

Only explicit `--write-result` generates a receipt. Normal replay requires
SOURCES.json and RESULT.json, validates frozen input hashes before importing
source, and compares complete typed canonical JSON. Source gaussian_sources
also authenticates both nested word/reference archives. The source files and
archives are unchanged and exported as declared live inputs.

Credit Jose Manuel's PR3851 physical Gaussian core and its inherited word,
interval and Chafik Boukhalfa factorization sources; Dugongue's PR3872 sliding
inverse cache is mathematical precedent, not the page ABI implemented here.
Nick Petalas's PR5119 residual barrier is not silently substituted or used to
lower precision. Canonical claim:
[discussion4202 comment19144826](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202#discussioncomment-19144826).

## Open next questions

Bind the actual catalogue's window sequence, miss pattern, persistent bank and
halo transport to compare complete budgets. A multi-entry encoded directory
requires a separate priced storage policy. Production-sized Gaussian grids,
the full tensor/CRT caller and a new finite-instruction compilation are not
executed or claimed. The selected frontier remains unchanged; source production
approximation and word arithmetic premises remain inherited.
