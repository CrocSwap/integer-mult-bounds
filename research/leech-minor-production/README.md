# Production byte-lane Leech-minor rows

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`scripts/experiments/affine_vector_screens.py:leech_minor` still built each
binary row with the historical pairwise sparse-dot genexpr. Jerry Chen's
opt-in adapter `research/leech-minor-byte-lanes/` (incorporated
[CrocSwap/integer-mult-bounds#898](https://github.com/CrocSwap/integer-mult-bounds/pull/898))
already proved an exact base-256 byte-lane algorithm with identical receipts.
This package wires that equivalent check into the **production** source used by
`scripts/audit_affine_vectors.py` / `make verify-certificates`.

Only the source pin for `scripts/experiments/affine_vector_screens.py` changes
inside `certificates/affine-vector-screens.json`. Every matrix entry is still
materialised; Golay inventory, norms, rational span witnesses, binary
elimination, polynomial-code screens and the retained historical `2^-31`
language are unchanged. Selected frontier untouched.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/leech-minor-production/verify.py
python3.12 -I -O -B research/leech-minor-production/verify.py
python3.12 -B scripts/research_package.py --package research/leech-minor-production
python3.12 -I -B research/leech-minor-production/benchmark.py --rounds 5
```

Expected:

```text
PASS_LEECH_MINOR_PRODUCTION leech_cases=5 code_cases=4 certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/leech-minor-production outcome=completed
PASS_IDENTICAL_LEECH_MINOR_PRODUCTION_RECEIPTS
```

Default verify is read-only. Use `--write-certificate` only after editing the
production source. Timing is host-descriptive and is not a correctness gate.

On Linux / CPython 3.12.3, five alternating fresh-process pairs gave median
**leech-only 5.579 → 1.043 s (5.35×)** and **complete audit 9.465 → 4.213 s
(2.25×)**. Samples are in [`RESULT.json`](RESULT.json).

## Why the byte lanes are equivalent

Coordinates of every Leech sample vector lie in `[-4,4]`. For each coordinate
`k`, pack nonnegative base-256 integers

```text
P_k = sum_j (v_j[k] + 4) 256^j
M_k = sum_j (4 - v_j[k]) 256^j
```

For a row vector `u` with `||u||_1 <= 31` (true of every historical Leech row:
l1 norms 8, 16 or 26),

```text
S_u = sum_{u[k]>0} u[k] P_k + sum_{u[k]<0} (-u[k]) M_k
```

has byte `j` equal to `dot(u,v_j) + 4 ||u||_1`, with every digit at most
`8*31 < 256` and no inter-column carries. Decoding bytes and comparing to
`shift + 4 ||u||_1`, while forcing the diagonal, returns exactly
`C[i,j] = (i == j or dot(v_i,v_j) == shift)` in the original column order.
This is the same argument as `research/leech-minor-byte-lanes/README.md`.

## Overlap and credit

Closest priors:

- [Jerry Chen / leech-minor-byte-lanes](../leech-minor-byte-lanes/) — opt-in
  byte-lane adapter (#898 incorporated); this package is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2054/#2150
  shared/mixed-point, #2100 ternary, #2117 DisjointTensor.frame_data, #2194
  production verify_factor, #1861 parity-side) was not reopened.

Douglas R. Colkitt authored the affine/vector screens and original checker.
Jerry Chen authored the byte-lane algorithm. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should the four polynomial-code screens in the same audit
   receive a similar production packing pass?
   **Why it matters:** After Leech minors shrink, the unchanged cubic-code path
   is a larger share of the complete audit.
   **First step:** Profile `audit_affine_vectors.certificate` with production
   lanes already merged.
   **Blocked by:** No open identical-receipt adapter yet for
   `polynomial_code_witness`.

2. **Question:** Should `research/leech-minor-byte-lanes/` note that production
   now ships the same algorithm?
   **Why it matters:** That package's source-admission string match expects the
   historical pairwise block.
   **First step:** Add a one-line status note without editing pinned evidence.
   **Blocked by:** Maintainer preference on touching incorporated historical
   packages.
