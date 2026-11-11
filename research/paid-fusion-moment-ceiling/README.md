# Paid-fusion moment ceiling

How much can a paid-side rewrite buy at a crossing exponent `c` with
`0 < c < 1`? This package answers the fusion case exactly.

## Scope

A *paid fusion* replaces paid ranks `b_1,...,b_m` by their sum `b_1+...+b_m`
and leaves the productive multiset `T` fixed. Write `M_H(c) = sum_{h in H} h^c`
for a finite multiset of positive integer ranks. No word, caller, compiler,
precision tape or outer row is claimed; this is a statement about the moment
model that the signed invoice evaluates.

## Result

Claim type: scoped written proof with exact finite corroboration. No κ change.

1. `(a+b)^c < a^c + b^c` strictly for all integers `a,b >= 1` and every
   `c` in `(0,1)`; equality at `c = 1`; the inequality reverses for `c > 1`.
   Every paid fusion therefore strictly lowers `M_P(c)` and every productive
   split strictly raises `M_T(c)` on the whole sub-unit exponent range.
2. The single-fusion saving `D(a,b) = a^c + b^c - (a+b)^c` obeys
   `0 < D(a,b) < min(a,b)^c`. The constant one is sharp
   (`D(a,b)/a^c -> 1` as `b/a -> infinity` for fixed `a`) and never attained.
3. At a fixed total paid rank `r = a+b`, `D(a,r-a)` is maximized by the
   balanced split and minimized by the unbalanced ones.
4. Let any partition of a paid multiset `P` be replaced by its block sums. The
   paid moment falls, and for every partition

   `M_{P'}(c) >= (sum_{p in P} p)^c`, hence
   `M_P(c) - M_{P'}(c) <= G(c) = sum_{p in P} p^c - (sum_{p in P} p)^c`,

   with equality only for the one-block collapse. `G(c)` is the total budget
   that all paid-only fusion schemes share.
5. Consequently the crossing exponent after any paid-only fusion is at most the
   root of `M_T(c) = (sum_{p in P} p)^c`. No set of fusions, and no choice of
   which jobs to fuse, can pass that root.

Point 5 is the usable form: it converts a fusion family into one scalar test
that needs no word replay.

## Evidence

`verify.py` encloses each `a^c` in an exact rational interval and then compares
exactly. It certifies, with zero inconclusive cases:

- points 1 and 2 for all `1 <= a <= b <= 40` at five exponents: `1/1000`,
  `1/279`, `363005817/100000000000` (the selected record's exponent), `1/2`
  and `3/4`;
- the `m`-block form for `m = 2,3,4` on five block shapes per exponent;
- the sharpness approach `0.99 < D(1,b) < 1` for `b = 10^4..10^12` at
  `c = 1/2`, with exact Newton enclosures of both square roots;
- point 3 against every other split of the same total for `3 <= r <= 60`;
- point 4 on five explicit multisets and every partition shape, with the full
  collapse attaining the bound, plus a non-fusion control where a paid split
  strictly raises the moment;
- rejection controls at `c = 1, 2, 3/2` and for non-positive ranks or `c = 0`.

The transcendental step is CPython `decimal` at 90 digits (correctly rounded per
its documentation), widened by one unit in the last place; all later arithmetic
is exact rational, so a certified inequality is a proof of that finite case.
`RESULT.json` stores the SHA-256 of the canonical summary and of `PROOF.md`;
`verify.py` recomputes both and fails on any mismatch.

## Reproduction

From the repository root with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/paid-fusion-moment-ceiling
python3.12 -B scripts/check_research_commit.py --package research/paid-fusion-moment-ceiling --check-source-history
```

The registered command is `{python} -B {package}/verify.py`. It runs in a few
seconds.

## Limitations

- The ceiling is a moment-model statement. A legal realization, native delivery,
  dirty restoration, the compiler, the precision tape and the nine outer rows
  remain separate obligations.
- Only the paid side is bounded here. The productive side already has a
  balanced-split optimum and halving test for a concave rank tariff in #6651;
  that result is cited, not re-derived or replayed.
- The package does not evaluate any invoice. Points 4 and 5 are a template: an
  application needs the exact `T` and `P` the gate consumes.

## Open next questions

1. **Apply the ceiling to one live fusion family.** Take the exact invoice
   histogram the interval gate consumes, collapse `P` to one job of rank
   `sum p`, and compute the root of `M_T(c) = (sum p)^c`. Report whether the
   family's target lies above that root. First step: read the gate's own audit
   input rather than the `invoice` summary block of
   `research/shared-wire-split-composition/FULL-RESULT.json`, because the
   summary histograms are not interchangeable with the gate's argument. Why it
   matters: one scalar decides whether more fusion exclusions are worth
   running. Blocked by: pinning the rank convention of that audit input.
2. **Fusion plus productive credit.** Extend to rewrites that fuse paid jobs and
   also add productive targets. Does the budget stay separable, or does the
   joint movement of both sides need a two-parameter bound? First step: state
   the joint model and look for a counterexample to separability. Blocked by:
   no joint model is fixed in the current packages.

## Credit

The quantitative cap, the global fusion budget and the crossing consequence,
with the verifier and certificate, were produced by Nick Petalas. Credit
thakrarsagar's #718 for the scoped `(5,1)`-versus-`(4,2)` paid-read comparison
that exhibits the same subadditivity on specific ranks, and Nick Petalas's #6651
for the balanced-split optimum and halving test on the productive side; both are
cited background, not replayed. Concavity of `x^c` is classical. Apache-2.0.
Independent human review and formal proof-kernel acceptance are unclaimed.
