# Production signed modular determinants for the P112 free-sink audit

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`,
`research/p112-free-sink-audit97/independent.py` still computed every signed
minor with rational `Fraction` elimination. woklerx’s opt-in adapter
`research/p112-signed-modular86/` (incorporated
[#1144](https://github.com/CrocSwap/integer-mult-bounds/pull/1144)) already
proved a modulo-521 kernel that recovers each full signed determinant inside a
checked Hadamard envelope, with identical complete audit receipts. This package
wires that equivalent rewrite into the **production** independent checker.

The original rational elimination is retained as `rational_determinant` and as
the fallback for rows outside the envelope. Pairwise Fraction-only bytes are
vendored in `baseline.py`. The opt-in package vendors the same baseline for its
reference engine.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/p112-signed-modular-production/verify.py
python3.12 -I -O -B research/p112-signed-modular-production/verify.py
python3.12 -B scripts/research_package.py --package research/p112-signed-modular-production
taskset -c 0 python3.12 -I -B research/p112-signed-modular-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_P112_SIGNED_MODULAR_PRODUCTION cases=28560 minors=4030 signed_matrices=19767 controls=… no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/p112-signed-modular-production outcome=completed
PASS_IDENTICAL_P112_SIGNED_MODULAR_PRODUCTION_RECEIPTS
```

Default verify is read-only. Temp-copy certificate determinant-flip foil rejects
via audit failure. Package gates under `-O` still load checkers with
`compile(..., optimize=0)`. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating in-process pairs
over the complete 28,560-case / 4,030-minor audit gave median wall time
**0.681 → 0.143 s (4.754×)** with per-round ratios **4.618–4.880×**. Details are
in [`RESULT.json`](RESULT.json). Timing is host-descriptive and is not a
correctness gate. Every audit receipt matches the pairwise baseline.

## Why the modular path is equivalent

Every frozen square minor has dimension at most eight and integer rows of
squared Euclidean norm at most four. Hadamard’s inequality gives
`|det A| ≤ 2^n ≤ 256`. Modulus 521 is prime and greater than twice 256, so
balanced modular recovery uniquely determines the signed integer determinant.
Inputs outside the envelope retain the original rational routine. See
`research/p112-signed-modular86/PROOF.md`.

## Open next questions

1. **Question:** Should other historical Fraction-only minor auditors that share
   the same E8 root-line envelope adopt the same modulo-521 recovery?
   **Why it matters:** Related sink / joint-frame auditors still pay rational
   elimination on bounded integer minors.
   **First step:** List auditors that already check `n≤8` and row-norm `≤4` on
   every fast-path call.
   **Blocked by:** One-object stop rule.

2. **Question:** Should `research/p112-signed-modular86` be marked superseded as
   an opt-in monkey-patch now that production ships the modular path?
   **Why it matters:** The opt-in still usefully vendors the Fraction baseline
   and engine controls.
   **First step:** Decide whether maintainers prefer a provenance note or a
   soft-deprecation banner.
   **Blocked by:** Maintainer preference.

## Overlap and credit

Closest priors (different delivery):

- `research/p112-signed-modular86/` / [#1144](https://github.com/CrocSwap/integer-mult-bounds/pull/1144)
  — opt-in modulo-521 signed recovery; this is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Leave-alone tooling through [#2412](https://github.com/CrocSwap/integer-mult-bounds/pull/2412)
  and pending `cursor/omission-lanes-production-60b9` / deferred
  `ck-dyadic-replay-production` / `scalar-fused-dyadic-production` were not
  reopened. Related mod-101 rank work (#976) does not recover these signed
  determinants.

Credit Joel Pulikkan / DreamingOfClouds (geometry), woklerx (exact free-sink
audit and opt-in modular kernel), and martinxxx9 (related modular rank tooling).
Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0.
