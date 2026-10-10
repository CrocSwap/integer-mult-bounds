# Five-stage stage-private completed banks

This is a finite bank-allocation extension of the PR197/PR200 completed-bank construction to PR234's five-stage
bit geometry. It is retained from eumemic's source527 package (via #285) and applied here to the independent
helper census of the p = 10 word: h = 20, m = 5h = 100. It does not claim a new all-size compiler theorem or
replace the scalar admission.

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
classes. Distinctness is literal. Choose a coordinate j outside Hᵢ. The embedded inverse fixes e_j, and
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
| 3 | rank-17 entrances | 70 |
| 4 | rank-16 entrances | 1,200 |
| 20 | ungauged roles | 6,960 |

A bank holds blocks of total width exactly 100. With 60 replicas the total residual width must therefore
satisfy 60·width ≡ 0 (mod 100), i.e. width ≡ 0 (mod 5). Banks are never padded. A padded bank would not sum to
I₁₀₀; its unused coordinates would count as stock without children and break the telescoping identity
m·W − mass = 60·(4v − 5h(h−2)) that `bank_check.py` and `math_check.py` assert.

The physical-layer producer enforces divisibility with `make_physical.py --bank-parity`. This generalizes gen5's
parity rule (60·width ≡ 0 mod 120). It drops the fewest trailing reuse pairs that make 60·width divisible by m.
Dropping a pair returns its rank-17 recipient to the entrances as a width-3 family, and its donor stays a plain
helper, so each drop adds 3 to the width.

For this word the maximum matching has 892 pairs and width 144,204 ≡ 4 (mod 5). Two drops are therefore minimal
(3k ≡ 1 mod 5 gives k = 2). The dropped pairs are [3454, 9119] and [3409, 9118], and the width goes 144,204 →
144,207 → 144,210. In the unbanked price the two drops cost about 1.5·10⁻⁸.

`bank_template.tile()` then finds an exact tiling, with no padding:

| Blocks | Banks per stage |
| --- | ---: |
| 20 of dimension 3 and 2 of dimension 20 | 210 |
| 25 of dimension 4 | 2,880 |
| 5 of dimension 20 | 83,436 |

The tiler mixes a width that does not divide m (here 3) with a filler width that does (here 20). It backtracks
until every remaining pure width divides out, and asserts:

- every pattern sums to m;
- every block is used exactly once.

The patterns are pinned in `word-pins.json`.

## Counts and selector bill

There are 86,526 banks per stage, 432,630 banks in total and 230,400 data families. Literal stock is 663,030,
and its per-replica normalized value is 132,606/12. The checker enumerates each of the 2,469,000 actual
role/replica/stage assignments exactly once, verifies each actual role's chart rank, and hashes the complete
allocation.

Every actual chart (163 distinct entrance bases) uses at most 150 factors. At most 99 coordinate transpositions
and 100 scalar-coordinate factors give 349 normalizer factors. A conservative added out-and-back selector bill,
in addition to all retained PR234 route and scalar bills, is

    2·5·60·((663030 − 1) + 8230·100·349) = 172,734,017,400 < 2⁴⁰.

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
divisibility rule and the exact tiler were added with Claude assistance. Apache-2.0; inherited source
attribution remains unchanged.
