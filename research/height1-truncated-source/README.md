# Exact height-1 source count for the selected nested widths

**Author-checked identity and two negative endpoint implications. No new κ.**
JoyboyBrian's `research/selected-truncated-source-envelope`, already on this
base, proves a uniform root and missing-demand census and the accumulated
bound `K/N < 3070/1000`. Sagar Thakrar's #5026 proves the inherited lower
bound `K/N > 2943/1000`. This package does not replace either bound. It
proves the census collapses on the default height-1 slab, and that
substituting that exact count cannot move either published thousandth.

The selected conditional exponent remains `60403/20000000`. No enormous word
and no selected-frontier change is proposed.

## Height-1 count

Let target multiplicities `W_k` be supported on ranks in `[L, m]`, with
`W = sum W_k` and `A(c) = sum_{k <= c} W_k`. Let paid multiplicities have
total `P` and maximum rank `rmax < L`. For `n >= m`, write `cap = n//m`.
The default-height flow has height 1 precisely when `L <= cap < L^2`.
Its merged source count is

```text
S = W*A(cap) + P*(W - A(cap)).
```

In particular `S - W^2 = (W - A(cap))*(P - W)`. Once `cap >= m`, every
target fits, `A(cap) = W` and `S = W^2`.

The count follows the authenticated `direct-mixed-flow/flow.py` rules.
At height 1 the root units are the degree-1 points `e_k` with `k <= cap`,
each of weight `W_k`. Extending by one target records `W*A(cap)` root
sources. Every paid rank is strictly below `L`, hence strictly below `cap`,
so every paid copy is explored. The child is the empty word, whose demand
is one full set of targets. For `k <= cap` that demand equals the parent
supply, so Pascal matching creates no source and no exit. For `k > cap`
the parent supply is absent and the `P` paid copies contribute
`P*(W-A(cap))` truncated sources. The leaf records exits only.

The equality of supply and demand uses degree 1, where the unit weight of
`e_k` is exactly `W_k`. The same sentence is not claimed at height 2 or
above. The identity also needs `rmax < L`: a paid rank above `cap` is not
explored and does not contribute the truncated term.

## Selected completion

The #4470 product at power `v`, completion to `L = 21^v` and splitting at
`20^v` leaves every paid rank at most `20^v`, so `rmax < L`. The ambient
rank is `M = 145^v`. Because `145 < 21^2`, the cap interval `[M, L^2)` lies
inside height 1, and `S = W^2` there with `W = 10928^v`.

At `v = 1` the completed invoice is `W = 10928`, `A(21) = 7792`,
`P = 77564`, `L = 21` and `m = 145`. The identity gives

```text
S(cap=21) = 328391680,    S(cap>=145) = 119421184 = 10928^2.
```

The drop is `(P-W)*(W-A(21))`. Since `P > W`, `S` is constant between
target ranks and falls when `cap` crosses a target rank. These are the
published ranks 3045 and 63944, both at height 1. The verifier compares
the formula with the merged flow at every cap from 21 through 440, and
with four smaller profiles. It also replays one literal chronological word
on each small profile.

## Neither published endpoint moves

Put `H = 64215200000000` and `N = 2^H`. The product `B_N` runs over ranks
`n` from `M` through `N`. Every height-1 rank satisfies `n < M*L^2`, so
there are fewer than `63945^v` such ranks. The top slab used by the #5026
lower estimate starts at height at least `hlo - 1`, and the recomputed
`hlo = 14276389504` is at least 4, so that slab is disjoint from height 1.

On height 1 the paid-count bound of #5026 gives `S <= Qbar*W`. Thus the
sum of `log2(S_n)` over the slab is strictly less than
`63945^v * bit_length(Qbar*W)`. Adding that sum to the inherited lower
estimate still leaves

```text
1000 * (lower estimate) < 2944 * H * N.
```

The same cardinality cuts the other way for JoyboyBrian's uniform charge
`X = 197115103572543`, recomputed here from the same rank-mass formula.
Even if each height-1 factor dropped out of the sum entirely, the removed
mass would be smaller than `63945^v * X`. The resulting optimistic upper
estimate would remain strictly above `(3069/1000)*H*N`. Both comparisons
are integer bit-length checks. They instantiate neither `N` nor a product
histogram at `v = 1024`.

So this exact count does not prove `K/N >= 2944/1000` and does not prove
`K/N < 3069/1000`. The certified bracket remains
`(2943/1000)*N < K < (3070/1000)*N`.

## Reproduction

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -W error -B research/height1-truncated-source/verify.py
python3 -I -O -W error -B research/height1-truncated-source/verify.py
python3 -B scripts/research_package.py --package research/height1-truncated-source
```

The verifier authenticates `flow.py`, the selected invoice, the #5026
receipt and the uniform-moment receipt by SHA-256 and Git blob before and
after the run. Finite checks cover 40 small caps, 4 literal replays, all
420 selected height-1 caps, the six published calibration rows, and four
rejection controls: a paid rank at least `L`, the truncated term omitted,
the formula extended to `n = 63945`, and a square lower bound where `P < W`.
The endpoint arithmetic is exact. Allow about a minute. Evidence is
author-checked. No independent reviewer or proof kernel is claimed.

Not checked: an all-height base reduction, exact `B_N`, alternative
batching, a physical word, owned storage, routes, precision, tapes, or
supplier admission. No selected record or predecessor package is edited.

## Open next questions

1. **Reduce the exponential base on the tall ranks.** A thousandth below
   `3070/1000` needs about three bits off `log2(T1/L)` uniformly through
   `N`. The height-1 window cannot supply them. First keep the missing-parent
   indicator and the full completion mass, and test any proposed uniform
   factor against the `v = 1` source count at `n = 63944` before using it
   at `v = 1024`. The blocker is a bound that remains valid when a source
   rank sits just above `n/M`.

## Attribution

Card `selected-stock-envelope`, priority revision 7, refined to the
height-1 case of handoff comment 19140126 after the uniform estimate had
already landed. Seed `c4e8a17b90d26f3518ab64e0c77d1295`.

Credit Sagar Thakrar / thakrarsagar (#5026 and the handoff);
JoyboyBrian (`research/selected-truncated-source-envelope`, the uniform
census and `K/N < 3070/1000`); James Reed / jwr404 (#4972); zxv (#4436
flow); Jacob Alan Sussman (Theorem 1G); Cinna Davis / 1337isnot1337 and
zxv (#4440/#4470); Mark / Matarener (#4612); Ryanson Jonathan (#4476);
and mihir-s-05 (#4507). Retained source notices stay intact.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
