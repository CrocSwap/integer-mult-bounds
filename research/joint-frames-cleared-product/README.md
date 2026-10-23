# Faster exact joint-frame product with identical receipts

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, the historical positive-side audit
(`scripts/audit_positive_side.py`) builds cancellation-free side DAGs and checks
every physical frame transition for small signed label families. Profiling shows
most time in `scripts/audit_joint_frames.py:product`, which previously formed
each entry as a left-associated sum of `Fraction` multiplies (each multiply and
add reducing by GCD).

This change clears denominators once per factor, multiplies with Python
integers, then rebuilds canonical `Fraction` entries. Empty left factors,
integer matrices, projector squares and every Boolean/arithmetical API besides
`product` are unchanged. Only the source pin for `scripts/audit_joint_frames.py`
changes inside the one certificate that binds that file
(`certificates/rank-product-core.json`). The positive-side certificate does not
pin `audit_joint_frames.py`; its mathematical payload is unchanged.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/joint-frames-cleared-product/verify.py
python3.12 -I -O -B research/joint-frames-cleared-product/verify.py
python3.12 -B scripts/research_package.py --package research/joint-frames-cleared-product
python3.12 -I -B research/joint-frames-cleared-product/benchmark.py --rounds 5
```

Expected:

```text
PASS_JOINT_FRAMES_CLEARED_PRODUCT positive_side_cases=12 random_cases=2500 certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/joint-frames-cleared-product outcome=completed
PASS_IDENTICAL_POSITIVE_SIDE_RECEIPTS
```

Default verify is read-only. Use `--write-certificate` only after editing the
production source. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five alternating fresh-process pairs of the full
positive-side experiment stream gave median wall time
**26.143 → 7.302 seconds (3.58×)**. Timing is host-descriptive and is not a
correctness gate; all samples and environment pins are in
[RESULT.json](RESULT.json). Every experiment receipt matches the baseline
checker fieldwise (`side_roles`, `additions`, `dag_sha256`, invocation and frame
fields). Restoring the old `audit_joint_frames.py` pin recovers the base
rank-product certificate byte-for-byte after that single substitution.

## Equivalence

Write matrices \(A=(a_{ij}/d_{ij})\) and \(B=(b_{jk}/e_{jk})\) over \(\mathbb{Q}\).
Let \(D_A=\mathrm{lcm}(d_{ij})\) and \(D_B=\mathrm{lcm}(e_{jk})\). Form integer
matrices \(A'=D_A A\) and \(B'=D_B B\). Then

\[
(AB)_{ik}=\frac{(A'B')_{ik}}{D_A D_B}.
\]

Canonical `Fraction` reduction of each right-hand entry matches the historical
entrywise `sum(x*y for ...)` result, including when \(D_A=D_B=1\) (pure integer
path). No modular or floating-point acceptance is used.

## Open next questions

1. **Question:** Can the same cleared-denominator pattern accelerate
   `inverse` / `row_basis` on the joint-frame and ternary frame streams without
   changing receipts?
   **Why it matters:** Those helpers still allocate many intermediate
   `Fraction`s on large ambient forms.
   **First step:** Profile `verify_invocation_frames` for h=9 with the ternary
   package’s baseline and time a cleared `inverse` prototype against receipt
   equality.
   **Blocked by:** Out of this session’s stop rule; `product` was the profiled
   positive-side bottleneck.

2. **Question:** Should rank-product and positive-side certificates both pin
   `audit_joint_frames.py` going forward?
   **Why it matters:** Only rank-product currently records that digest, so a
   silent product drift would not bump the positive-side pin list.
   **First step:** Add the pin in a dedicated provenance follow-up if maintainers
   want symmetric coverage.
   **Blocked by:** Provenance expansion is outside this tooling change.

## Overlap and credit

Closest priors (different objects):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
packed balanced-Fano replay;
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793)
inplace-side prefix scan;
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861)
parity-side basis/contains memoization;
[CrocSwap/integer-mult-bounds#1217](https://github.com/CrocSwap/integer-mult-bounds/pull/1217)
ternary frame-pair memoization;
local `research/joint-frame-modular-screen/` (modular *rank* screen for the
joint-frame certificate, not matrix product).
No competing open PR on cleared-denominator `product` at refresh.

Douglas R. Colkitt authored the joint-frame helpers and positive/rank-product
side compilers. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
