# Quadratic five-cube recoding: exact copy floor and rank-cap tradeoff

**Status: scoped structural negative result. No new kappa.**

Adding one quadratic Boolean mask to the five-cube parity code does not
reduce its minimum copy-rank sum below **32**. The certificate covers all
**16,383** augmented codes and every finite binary factorization within
each code, including redundant and zero-cost terms. For the **16,368**
genuinely quadratic codes, limiting each term's rank to 15 raises the
minimum total to at least **34**; a **13,13,8** witness is exact. Separate
integer and rational implementations verify the coverage and certificates.
Under the inherited additive stage ledger, the optimistic deficit remains
negative. This is a scoped structural result, with no new kappa or physical
supplier.

Both factor spaces must lie in the same `span_F2{1,parity,h}`, with
`degree(h)<=2`. This changes PR1046's affine restriction and differs from
PR1177's at-most-three-term arbitrary-mask result. See [PROOF.md](PROOF.md)
for the complete domain, graph certificate argument, exact capped-cost
table, accounting premises and exclusions.

## Reproduce

Python 3.10+; standard library only; from the repository root:

```sh
python3 -I -O -B research/five-cube-quadratic-code-seed44/test_package.py
```

Expected: **six test groups pass**, ending in `Ran 6 tests` and `OK`.
This regenerates the certificate, runs the separate mathematical checker,
tests corrupted inputs, and repeats both CLIs from a standalone copy.
The scripts themselves can also be run separately:

```sh
python3 -I -O -B research/five-cube-quadratic-code-seed44/verify.py
python3 -I -O -B research/five-cube-quadratic-code-seed44/independent.py
```

Expected markers: `PASS_FIVE_CUBE_QUADRATIC_CODES` and
`PASS_INDEPENDENT_QUADRATIC_CODES`.

`verify.py --write /new/path.json` writes a fresh certificate and refuses
an occupied output. `CERTIFICATE.json` contains 64 exact rank tables,
all 16,383 symmetry transports, two potential certificates per orbit,
and attaining words. The separate checker imports no generator code and
does not run its shortest-path algorithm.

## Pins and attribution

- Base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.
- Track: structural decoder research; first OS-random seed **44**.
- [SOURCES.json](SOURCES.json): exact source hashes, Git blobs and heads.
- [CLAIM.json](CLAIM.json): candidates, overlap, domain and stopping rule.
- [VALIDATION.json](VALIDATION.json): executed checks and their limits.
- [NOTICE.md](NOTICE.md): predecessor credit and AI-assistance disclosure.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex**
assistance. Apache-2.0. PR1046's attaining value, PR958's geometry and
accounting, and PR1177's adjacent three-total family retain their credit.
The selected construction and `upstream/` are unchanged.
