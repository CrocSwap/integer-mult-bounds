# Faster exact ternary invocation frames with identical receipts

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, the historical ternary-side small
controls (`scripts/audit_ternary_side.py` on `h=8,9`) spend almost all wall time
in `scripts/experiments/ternary_side.py:verify_invocation_frames`. Profiling
shows repeated `Fraction` matrix products/inverses while building Gram
projections, and repeated `rank(sub(F, old))` work on recurring physical edges.

This change keeps the default checker path and:

1. clears denominators once per Gram factor for products and clears the pivot
   row before Gauss–Jordan scaling for inverses (same rational values as the
   historical entrywise `Fraction` arithmetic);
2. memos exact ordered frame transitions for one `verify_invocation_frames`
   call by identity-then-value interning;
3. caches projections on immutable row tuples within the call.

Every support/topology `require`, both orientations, and every orientation
evidence field stay identical. Only the `scripts/experiments/ternary_side.py`
source pin changes inside `certificates/ternary-side.json`. The h=29 DAG
construction and assembly invoice are not replayed.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/ternary-frame-cleared-cache/verify.py
python3.12 -I -O -B research/ternary-frame-cleared-cache/verify.py
python3.12 -B scripts/research_package.py --package research/ternary-frame-cleared-cache
python3.12 -I -B research/ternary-frame-cleared-cache/benchmark.py --rounds 5
```

Expected:

```text
PASS_TERNARY_FRAME_CLEARED_CACHE frame_cases=2 product_cases=160 certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/ternary-frame-cleared-cache outcome=completed
PASS_IDENTICAL_TERNARY_FRAME_RECEIPTS
```

Default verify is read-only. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing `build(..., retain_graph=True)` plus
`verify_invocation_frames` for `h=8` and `h=9` gave median wall time
**13.578 → 4.733 seconds (2.87×)**. Timing is host-descriptive and is not a
correctness gate; all samples and environment pins are in
[RESULT.json](RESULT.json). Every orientation receipt matches the baseline
checker fieldwise. Restoring the old `ternary_side.py` pin recovers the base
ternary-side certificate byte-for-byte after that single substitution.

## Equivalence

Cleared product: for matrices over \(\mathbb{Q}\), with
\(D_A=\mathrm{lcm}\) of \(A\)'s denominators and \(D_B\) likewise for \(B\),

\[
(AB)_{ik}=\frac{(D_A A\cdot D_B B)_{ik}}{D_A D_B}.
\]

Canonical `Fraction` reduction matches entrywise `sum(x*y for ...)`. Cleared
inverse scales each pivot row to integers before dividing by the pivot, then
performs the same elimination; the resulting right block equals the historical
Gauss–Jordan inverse. The transition memo keys exact rational frames (tuple
equality), so equal frames share one cached `(rank(new-old), rank(new)-rank(old))`
pair and unequal frames do not collide.

## Open next questions

1. **Question:** Can the same cleared-denominator inverse land in
   `scripts/audit_joint_frames.py` for the positive-side / rank-product streams
   once open [CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922)
   merges?
   **Why it matters:** Those certificates still call the historical `Fraction`
   inverse; a shared helper would avoid duplicating the cleared path.
   **First step:** Rebase onto the merged product helper and remeasure
   positive-side `verify_frames` with receipt equality.
   **Blocked by:** Leave #1922's `audit_joint_frames.py` edit independent until
   that PR lands.

2. **Question:** Should the opt-in `research/ternary-frame-cache` adapter be
   marked superseded by this default-path rewrite?
   **Why it matters:** Maintainers may want one recommended replay path for the
   historical ternary frame controls.
   **First step:** Add a one-line pointer in that package README after this
   change merges.
   **Blocked by:** Documentation-only follow-up outside this tooling change.

## Overlap and credit

Closest priors (different objects or delivery):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1217](https://github.com/CrocSwap/integer-mult-bounds/pull/1217)
(opt-in ternary frame-pair memo; credited, not re-opened),
[CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922)
(cleared product + open ternary inverse question; `audit_joint_frames.py` left
independent),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984),
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994).
No competing open PR on the default `verify_invocation_frames` path at refresh.

Douglas R. Colkitt authored the ternary checker; Zhihao Chen’s #7 supplied the
five-subset motif. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Detailed predecessor attribution is in [NOTICE.md](NOTICE.md).
This changes no inherited mathematical assumptions and is not a formal proof of
the full multiplication theorem.

### Maintainer integration note (PR2100 + PR2117)

Both optimizations are incorporated together. The shared ternary certificate
therefore changes two source pins. The check permits exactly the reviewed
companion hash, authenticates its live source, and preserves every other
certificate field. Independent baseline equivalence checks remain required for
each optimization. This adds no new mathematical claim or performance result.
