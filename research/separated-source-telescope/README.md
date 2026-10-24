# An all-height source telescope for separated nested flows

**Scoped proof with exact source checks.** For the unchanged selected #4470
product, completion and split rule in #4436's nested divisible-width compiler,
this package proves `K/N > 3.054`. The previous lower coefficient was 2.943.
Together with Nick Petalas's [PR #5109](https://github.com/CrocSwap/integer-mult-bounds/pull/5109)
upper proof, the interval is

```text
3.054 < K/N < 3.0694,
H = 64215200000000, N = 2^H, K = ceil(log2 B_N)/H.
```

Its endpoint ratio is less than 1.0051. This is a tighter estimate of a
permitted compiler's width. It does not reduce that width or improve kappa.
The selected conditional kappa remains `60403/20000000`. Physical stock,
owned storage, routing, native realization and supplier admission remain open.

## Exact count at every height

Let positive integer target multiplicities `T_k` have minimum rank `L>=2`
and maximum rank `M`. Let positive integer paid multiplicities `P_r` have
`max r < L`. Set `W=sum T_k`, `Q=sum P_r`, `c=floor(n/M)` and
`g=max{j:L^j<=c}`, for `n>=M`. Use the unchanged default height.

Let `F_d(c)` count ordered words with `d` paid choices and `g-d` target
choices whose rank product is at most c. Count each choice with its actual
multiplicity. The paid choices form the chronological path. The target
choices give the ordered form of the source's multinomial unit weights.
Thus `0<=F_d<=Q^d W^(g-d)` and `F_g=Q^g`, since every paid rank is below L.

The exact source count is

```text
S_n = W F_0 + sum_(d=1..g) (W F_d - Q F_(d-1))
    = W Q^g + (W-Q) sum_(d=0..g-1) F_d.                 (1)
```

To prove the first equality, start with the root's `W F_0` target slots.
At depth d, eligible child units have `W F_d` target slots. An eligible
parent point contributes all its Pascal demand: replacing its last target
factor k by any paid factor r preserves eligibility because `r<k`.
The complete Pascal identity therefore matches exactly `Q F_(d-1)` of
those slots. Every other eligible slot is a distinct new top source.
There is no negative demand, omitted paid position or rank-based alias.
This is the root/nonroot census of
[PR #5067](https://github.com/CrocSwap/integer-mult-bounds/pull/5067), with the
intersection simplified under the selected rank separation. The second
equality telescopes. For `g=0`, both empty sums give `S_n=W`.

Subtract the full-layer geometric identity to obtain the nonnegative-deficit
form

```text
S_n - W^(g+1)
  = (Q-W) sum_(d=0..g-1) (Q^d W^(g-d) - F_d(c)).        (2)
```

Consequently, if `Q>=W`, then `S_n>=W^(g+1)` at every height and width.
If `Q>W`, equality holds exactly when `c>=M^g`. Sufficiency follows because
every mixed word then fits. Necessity follows from the `d=0` term: the
all-maximum target word has positive multiplicity and fails when `c<M^g`.
For a fixed g, each `F_d(c)` is nondecreasing. Thus `S_n` is nonincreasing
within a height slab when `Q>W`, constant when `Q=W`, and nondecreasing
when `Q<W`. This does not assert monotonicity across height changes.

At height one, (1) becomes `W A(c)+Q(W-A(c))`, the identity in unpaidmoon's
[PR #5273](https://github.com/CrocSwap/integer-mult-bounds/pull/5273).
The contribution here is the all-height telescope, its deficit/equality
law, and its selected lower-coefficient consequence. The height-one identity
and the underlying source census are not claimed as new.

## Selected coefficient

The pinned selected invoice and proof give

```text
W = 10928^1024, L = 21^1024, M = 145^1024.
```

Every one of the `64620^1024` positive raw paid product calls produces at
least one split call. Completion can only add paid calls, so `Q>W` without
expanding the final paid histogram. Every final paid rank is at most
`20^1024<L`. Every productive target is completed to at least L; the all-145
target remains at M. Thus the preceding theorem applies to the actual rule.

Integer bit lengths give

```text
bit_length(W)=13738, bit_length(L)=4498, bit_length(M)=7353,
hlo = floor((H-bit_length(M))/bit_length(L)) = 14276389504,
Xlo = hlo*(bit_length(W)-1) = 196114762616448.
```

They imply `M L^hlo <= N`. For every integer
`n>=M L^(hlo-1)`, the default height is at least `hlo-1`, so (2) gives
`log2 S_n>=hlo log2 W>=Xlo`. There are at least `N(1-1/L)` such indices
through N. The nested recurrence `B_n=B_(n-1) S_n`, with base width one,
therefore gives

```text
log2 B_N >= N(1-1/L) Xlo,
1000 (L-1) Xlo > 3054 L H,
K/N >= (L-1) Xlo/(L H) > 3054/1000.
```

The comparison uses only integers with thousands of bits. It never
constructs N, B_N, or the power-1024 histogram. The inherited 3.0694 upper
proof is pinned as a source premise, not independently reproved here.
This exact lower estimate does not prove a 3.055 endpoint.

## Evidence and reproduction

[RESULT.json](RESULT.json) records the arithmetic and finite checks.
[SOURCES.json](SOURCES.json) pins every consumed input at main
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. No pending branch is required.
The verifier authenticates input bytes before execution and checks them again
after it finishes. It loads the pinned flow from source bytes, without using
cached bytecode. Its independent counter uses scalar product convolutions;
the predecessor uses multivariate Pascal points and chronological matching.

From the repository root, Python 3.12 and standard library only:

```sh
python3 -I -W error -B research/separated-source-telescope/verify.py
python3 -I -O -W error -B research/separated-source-telescope/verify.py
python3 -B scripts/research_package.py --package research/separated-source-telescope
```

Expected direct marker: `PASS_SEPARATED_SOURCE_TELESCOPE K/N>3.054 no_new_kappa`.
The deterministic receipt covers 864 small merged flows, 12 complete literal
source/exit comparisons, 708 within-height monotonicity checks and 16 distinct
selected `v=1` boundary cases through height four. Six controls distinguish
omitted root/nonroot terms, omitted subtraction, `Q<W`, failed rank separation,
a changed height and a false 3.055 endpoint. All checks use explicit exceptions
and remain active under `-O`.

Registered normal and optimized checks pass on CPython 3.12.13. Optimized
CPython 3.14.7 also passes. The committed-byte check and the official 11-file
export check pass. A fresh Git-free export passes optimized verification and
rejects deliberate input-byte and receipt changes. The optional source-history
preflight refuses this shallow checkout; no full-history pass is claimed. All
source pins use the recorded base, which is the initial contribution commit's
direct parent. The portable export contains every declared live input.

The proof is uniform in height; the finite checks corroborate it. They do not
prove every native operator or the full multiplication theorem. Exact B_N,
optimal batching, the physical compiler, all-column operators, whole-job
adapters, ownership, precision/tapes, outer admission and analytic/prime/recovery
premises were not checked. No selected cold replay, Lean or Docker run is part
of this package. The new claim does not change the selected frontier.

## Coordination and credit

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5061#discussioncomment-19150437)
records this refinement of the selected-stock-envelope card, priority 7.
The final overlap snapshot covers 363 open PRs, 4,582 Discussion records
and all 7,091 base-tracked README/TASK notes, plus this package's two notes.
No omission warning was reported. Unpublished work and arbitrary diffs are
outside that check. Canonical main still matched the pinned base.
The older physical-stock question is not discharged by this mathematical result.
The task followed the source-count handoff after checking its completed
successors and current claims. No later task is reserved.

Credit JoyboyBrian for the exact source census in
[PR #5067](https://github.com/CrocSwap/integer-mult-bounds/pull/5067); Sagar Thakrar for
the coefficient bracket and handoff in
[PR #5026](https://github.com/CrocSwap/integer-mult-bounds/pull/5026); Nick
Petalas for the fractional upper bound; and unpaidmoon for the height-one
identity. Credit zxv's [PR #4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436)
flow, Jacob Alan Sussman's multinomial lockstep construction, and Cinna Davis
and zxv's [PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470)
invoice and retained native/compiler lineage. All source files and notices
remain unchanged. Ali Romman, with substantial OpenAI Codex assistance in
proof, code, verification and review. Apache-2.0. No independent human or
proof-kernel review is claimed.

## Open next questions

1. Bound one positive top-slab eligibility deficit in (2) at the actual
   product power 1024. This could raise the lower endpoint further. A uniform
   truncated-product deficit estimate is still missing; a small census alone
   does not provide it.
2. Bind the permitted width to one actual physical stock/owner caller and
   its complete routing tariff. This requires the inherited implementation
   premises and is separate from the count theorem.
