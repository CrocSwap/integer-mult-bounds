# Five-stage stage-private completed banks

This is a finite bank-allocation extension of the PR197/PR200 completed-bank construction to PR234's five-stage
bit geometry. It is retained from eumemic's source527 package (via #285 and #315) and applied here to the
independent helper census of this package's p = 10 word: h = 20, m = 5h = 100. It does not claim a new all-size
compiler theorem or replace the scalar admission.

## Endpoint of one local invocation

For one complete local invocation, the source-bound physical telescope has no data/helper cross blocks. On an
independent helper with genuine entrance projector σ, its endpoint is the exact partial swap D_(I₂₀−σ),
supported in the active local window. This holds on arbitrary correlated dirty contents. The complemented
inverse invocation has the same residual: its reversed endpoints are 0 and I₂₀ − σ. Source-owned gauges are
visible-data paths and are excluded from the independent helper census.

## Bank normalizers

In stage i, PR234 routes the helper at local class d to physical class g = d·τᵢ. Relative to g, the residual is
Pᵢ = τᵢ·diag(I₂₀ − σ, 0, …, 0)·τᵢ, supported only in Hᵢ. Each stage gets a disjoint collection of banks, and
every bank is filled by disjoint coordinate blocks of total dimension 100. For the actual gauge chart B, whose
columns are residual columns followed by gauge columns, set

    N_b = (b+1)·Π_b·embed_i(B⁻¹).

For an ungauged role, B = I₂₀. Π_b is the explicit coordinate permutation sending the first residual
coordinates in Hᵢ to the assigned bank interval. Thus N_b·Pᵢ·N_b⁻¹ is exactly that coordinate projector. The
scalar leaves conjugation unchanged.

The residual columns of B are G⁻¹ applied to the frame's annihilator rows, for G = I − J/9. Up to the positive
scalar h − 9 = 11, these are the integer rows 11a − Σa (15a − Σa at h = 24).

The checker reconstructs every actual chart and checks:

- both inverse identities;
- the G-orthogonality of its two summands;
- its residual action;
- its elementary factorization.

This is therefore a projector identity for the actual bases, not a rank substitution.

## Bank routes and distinctness

The bank route is g → g·N_b⁻¹, which is d·τᵢ·N_b⁻¹ in the original local invocation. If the bank class is h,
its residual is h·N_b·Pᵢ·N_b⁻¹·h⁻¹. Every occurrence visits every bank class once, because right multiplication
is a bijection on the complete GL cover.

If two roles in one local invocation are assigned the same bank family, their distinct N_b give distinct bank
classes. (In this word no two roles of one invocation share a bank family: the pinned collision count is 0. The
argument is kept because the checker supports the general case.) Distinctness is literal. Choose a coordinate j outside Hᵢ. The embedded inverse fixes e_j, and
N_b·e_j = (b+1)·e_(Π_b(j)). The resulting columns differ for all b, at every eligible prime q > 2⁸⁰ and every
local ring Z/q^w. All scalars are between 1 and 25 (the largest bank has 25 blocks), so they remain distinct
units. The proof uses the full GL cover, not a projective quotient.

## Completed endpoint

Complete the entire cover sweep for each stage and replica, in fixed order, before its boundary phase. The
complete local source endpoint separates every bank from the data and the other banks, so each subsequent
invocation may receive arbitrary dirty bank contents.

For each bank, its block projectors are disjoint and sum to I₁₀₀, so the literal partial swaps compose to
D_I₁₀₀ on every address column. The common inherited ancestor chart is the same for each block and cancels
between blocks. The checker verifies:

- all 200 address columns;
- the reverse schedule;
- failures when a block is omitted or repeated.

No new independence assumption on dirt is used.

The five bank collections remain separate, and each is touched only in its own stage. This gives every physical
bank its full required endpoint once. The data stage routes, bridge maps, idle children and final exchanges
remain PR234's. Consequently there are no independent exterior rank-5a children. Their removal follows from the
completed bank endpoint. No internal, data, compensation or copied-centre child is removed.

## Families and the exact tiling

The actual residual families are:

| width | source | roles |
| ---: | --- | ---: |
| 4 | rank-16 entrances | 1,200 |
| 20 | ungauged roles | 6,900 |

There are no rank-17 entrances: all 960 rank-17 gauges are reuse recipients.

A bank holds blocks of total width exactly 100. With 60 replicas the total residual width must therefore
satisfy 60·width ≡ 0 (mod 100), i.e. width ≡ 0 (mod 5). Banks are never padded. A padded bank would not sum to
I₁₀₀; its unused coordinates would count as stock without children and break the telescoping identity
m·W − mass = 60·(4v − 5h(h−2)) that `bank_check.py` and `math_check.py` assert.

The physical-layer producer enforces divisibility with `make_physical.py --bank-parity`. This generalizes gen5's
parity rule (60·width ≡ 0 mod 120). It drops the fewest trailing reuse pairs that make 60·width divisible by m.
Dropping a pair returns its rank-17 recipient to the entrances as a width-3 family, and its donor stays a plain
helper, so each drop adds 3 to the width.

For this word the maximum matching has all 960 pairs. The residual width is 4·1,200 + 20·6,900 = 142,800 ≡ 0
(mod 5), so 60·142,800 = 85,680·100 and no pair is dropped. (In #315 the matching had 892 pairs, the width was
144,204 ≡ 4 (mod 5), and two pairs were dropped.)

`bank_template.tile()` then finds an exact tiling, with no padding:

| Blocks | Banks per stage |
| --- | ---: |
| 25 of dimension 4 | 2,880 |
| 5 of dimension 20 | 82,800 |

Both widths divide m = 100, so every bank is pure: 60·1,200 = 72,000 blocks of width 4 fill 2,880 banks, and
60·6,900 = 414,000 blocks of width 20 fill 82,800 banks. The tiler can also mix a width that does not divide m with
a filler width that does, backtracking until every remaining pure width divides out. That path is not used here.
In every case it asserts:

- every pattern sums to m;
- every block is used exactly once.

The patterns are pinned in `word-pins.json`.

## Counts and selector bill

There are 85,680 banks per stage, 428,400 banks in total and 230,400 data families. Literal stock is 658,800,
and its per-replica normalized value is 131,760/12. The checker enumerates each of the 2,430,000 actual
role/replica/stage assignments exactly once, verifies each actual role's chart rank, and hashes the complete
allocation.

Every actual chart (120 distinct entrance bases) uses at most 150 factors. At most 99 coordinate transpositions
and 100 scalar-coordinate factors give 349 normalizer factors. A conservative added out-and-back selector bill,
in addition to all retained PR234 route and scalar bills, is

    2·5·60·((658800 − 1) + 8100·100·349) = 170,009,279,400 < 2⁴⁰.

## Literal realization

The literal stock, not the rational per-replica stock, must be used for physical role routing and finite
storage. All 60 scalar replicas execute, and all recursive child counts are multiplied by 60 in a literal
realization. Any smaller integer normalization used only in the moment arithmetic must be distinguished from
the literal replica count.

Serial execution may share an external copied-centre work stream only after erasure. The fixed bank selector
bill is explicitly charged before the inherited positive ordinary-leaf gap absorbs it. After completion removal
the largest child is 42 of 100, so a single level halves, and the histogram remains a one-level profile.

## Scope

This witness leaves the following to the integrator (verify.py):

- the full scalar, integer and sign audits;
- the frame ledgers and the exact global lowering;
- the prime guard and the complete fallback profile;
- the 47 outer inequalities.

Its input charts and census are the independently admitted p = 10 helper. The existing compiler, common weighted
chart, restored selectors, complete-stream routing and all-size analytic hypotheses remain conditional, as in the
cited sources.

Prepared with OpenAI Codex assistance (source527 package, eumemic). The gen5 and p = 10 numbers, the bank
divisibility rule and the exact tiler were added with Claude assistance (#285, #315 and this package). Apache-2.0; inherited source
attribution remains unchanged.

## Transcript stages: residual widths and the economy tiling

With the transcript stages (`STAGES-PROOF.md`) the banks hold more residual widths. The kernel pivots of rank e
have residual 20 − e (widths 19, 18, 16, 15, 13, 12 here), the 240 early-restored helpers have residual
P_E − P_σ of rank 19 − 16 = 3, and the ten terminal sinks remove ten full-width helpers. The residual census
(`residual_families` in `word-pins.json`) is {20: 5,551, 19: 1,296, 18: 26, 16: 7, 15: 3, 13: 2, 12: 5, 4: 960,
3: 240}.

#315's filler search fails on such a census: it mixes every width that does not divide 100 with the most numerous
filler first and needs six rank-4 blocks per four 19-wide pivots, and the rank-4 blocks run out (the p = 12
analogue was PR #299's change from (r⁴, 4^(30−r)) to (r⁴, 24, 4^(24−r))). `tile()` falls back to
`economy_tile()` (our #320), which uses both fillers (F = 20, f = 4) and, for each other width w in decreasing
order, picks the bank w^a F^c f^b with the fewest f blocks per w block (then the largest a): here (19⁴, 20, 4),
(18⁴, 20, 4²), (16⁵, 20), (15⁴, 20²), (13⁴, 20², 4²), (12⁵, 20²), (3²⁰, 20²), with at most one remainder bank per
width; the leftover fillers fill (20⁵), (4²⁵) and one residue bank (20, 4²⁰). The same post-conditions are asserted
as before: every bank sums to m = 100 and every block is used exactly once, so there is no padding and the stock
is the same as for any exact tiling: banks per stage = 60 · Σ residual / 100 = 84,549, literal stock
230,400 + 5 · 84,549 = 653,145. The ten patterns and their counts are pinned (`bank_patterns`). The total entrance
rank plus the restoration saving is 1,445 + 240 = 1,685, a multiple of 5.

Restored helpers are charted by the pair (σ, E): the chart basis is (residual rows of P_E − P_σ, the basis of σ,
the E-perp rows), checked to be G-orthogonal blocks and exactly inverted like the plain charts (`residual_rows` in
`bank_check.py`). 726 charts are built (`final_charts`); the completion rows carry the endpoint frame E and the
completion rank 5(a + h − dim E). With the kernel entrances, roles of one invocation can share a bank family
(`family_collisions` pinned at 110,405), which is the general case the injectivity argument above covers; the
largest chart uses 400 factors (`max_chart_factors`), and the finite coefficient bound is re-pinned
(`finite_coefficient`).
