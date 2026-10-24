# Sharp-window bad density for the compact switch

**Scoped comparison. No new κ.** The selected conditional exponent is
unchanged. This does not accept PR #4100.

## Result

CRT.md §4 bounds the bad density of one batch by

```text
r [2/B + 8B/2^K] ≤ C p 2^{-G}
```

and then uses the separate room

```text
2^{-G} E(p, ell) ≤ C 2^{-60 ell} (p+2)^{-48}.
```

The window summand `8B/2^K` is the fraction of `K−1`-bit windows outside
the published margin `2B ≤ W < 2^m − 2B`. The isolated post-increment
step admits the larger range `0 ≤ W ≤ 2^m − B + 1`. On that predicate the
bad-window count is exactly `B − 2`, so the summand is

```text
β = 2(B − 2) / 2^K = ((B − 2) / (4B)) · (8B / 2^K).
```

For every `B > 2` this is strictly less than one quarter of the published
window term. It is zero when `B = 2`.

Under CRT.md's parameters `G = 64(ell + ceil(log2(p+2)))`, `B = 2^G`,
`K = 64G`, with `ell ≥ 1`, `p ≥ 2`, `L ≤ p` and `r ≤ floor(L/(100G))`,

```text
r (2/B + β) < p 2^{-G} / 6400.
```

The same ceiling holds for the published window term. The displayed
`2^{-G} E` line does not contain `8B/2^K`, so it is unchanged. Replacing
the window term therefore does not shrink the scalar room CRT.md uses to
put bad-key work in `O(V)`.

The argument is in [PROOF.md](PROOF.md). The executable checks the window
count by running the isolated step, the integer form of the ratio, the
room identity, and the `C = 1/6400` comparison on a finite parameter grid.

## Scope

Card `formal-interface-lemma`, scope **refined**. The catalogue's first
experiment for #4100 is to audit the compact-switch contract before a
formalization campaign. That audit is PR #4321. Its open question 2 asks
whether the section-4 density still fits `O(V)` if the window hypothesis
is the sharp range. This package answers that question.

The simultaneous carry argument in CRT.md still assumes the stricter `2B`
margin. This count does not extend that argument to the extra windows.
No tape repair, Lean proof, or multiplication theorem is claimed.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/compact-switch-sharp-density/verify.py
python3.12 -B scripts/research_package.py --package research/compact-switch-sharp-density
```

The direct command prints `PASS_COMPACT_SWITCH_SHARP_DENSITY`.

## Open next questions

1. Does one two-target macro with disjoint guards still restore both
   controls on a window that is sharp-good but outside the published `2B`
   margin? The density line can use `β` for the isolated predicate only.
   First step: run the live two-target macro at `W = 0` and at
   `W = 2^m − B + 1` with `K`-separated positions. Blocker: the twelve
   paid `H`-bit exchanges are not replayed here.
2. Is `L ≤ p` true for a real #4174 placement, or only a sufficient
   hypothesis inherited from #4328? The constant `1/6400` uses that
   hypothesis. First step: read one production plan's address length
   against its `p`. Blocker: reservoir placement is not an input here.

## Credit

Cinna Davis, PR #4100, for CRT.md and `check_batched_crt.py`. The
live-digit lemma and the sharp window are the compact-switch contract
audit, PR #4321. The published density identity and the `L ≤ p`
absorption hypothesis are PR #4328. The uniform evaluator constant is
PR #4377 and is not reused. The guard-coloring decision is PR #4329.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0. No independent human review and no formal-kernel acceptance
are claimed.
