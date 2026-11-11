# The fixed-line permutation theorem

## Contract

Let `V` be a finite-dimensional binary vector space and let `L_1,...,L_n`
be distinct one-dimensional subspaces. The scalar payload space is over an
arbitrary field `K`; the frame field and payload field need not agree.
Register `X_i` has frame `L_i` and arbitrary independent initial payload `x_i`.
All public register frames stay fixed. Other public registers have arbitrary
independent initial payloads. There are no preloaded copies of any `x_i`.

The circuit is finite, fixed and linear. A local operation can combine or
scale registers only when their current frames agree. Owned registers can be
initialized to zero at any frame and cleared at any time. Every owned MOVE
changes a register's frame between strictly nested subspaces; its rank is the
positive dimension difference. MOVEs carry the payload unchanged in the
common-chart convention. Arbitrarily many carriers, feedback, intermediate
frames, repeated visits and interleaved reads and writes are permitted.
No control flow or scalar side channel communicates payload between frames.

For a permutation `pi` and nonzero scalars `a_i`, require the checkpoint
endpoint `X_{pi(i)} = a_i x_i`. All other public registers are restored and
all owned registers are cleared. Let `s` be the number of indices with
`pi(i) != i`. The checkpoint is before releasing the fixed public frames.

## Theorem

Every such circuit has at least `2s` owned MOVEs. A circuit with exactly `2s`
rank-one MOVEs exists. Consequently its minimum owned MOVE tariff is `2s`
for every tariff `c(r)` with `c(1)=1` and `c(r)>=1` for positive integer `r`.

### Lower bound

For a designated line `L_i`, call the set of registers whose current frame
equals `L_i` its region. An INIT contributes zero, a CLEAR discards data,
and local operations cannot communicate across its boundary. The only ways
data enter or leave this region are MOVEs whose arrival or departure frame
equals `L_i`. This statement includes every owned carrier currently there.

If no MOVE ever leaves `L_i`, the coefficient of the independent input `x_i`
remains zero in every register outside the region. This follows by induction
on events. Local operations outside see zero coefficients; INIT is zero;
CLEAR cannot introduce one; and every MOVE not leaving the region carries
a zero coefficient from an outside register or remains within it. But for
`pi(i) != i`, the endpoint outside the region contains `a_i x_i` with
`a_i != 0`. Therefore a departure from `L_i` is required.

Likewise, if no MOVE ever enters `L_i`, every register there stays independent
of all initial `x_j` with `j != i`. The same event induction proves this,
even if outside registers have previously received `x_i`. For a moved line,
its final register requires `x_{pi^{-1}(i)}` from a different line, with a
nonzero coefficient. Therefore an arrival at `L_i` is required.

There are `s` departure requirements and `s` arrival requirements. A single
MOVE can serve at most one of them. Its departure frame and arrival frame
cannot be two different designated lines, since distinct lines are
incomparable and every MOVE is strictly nested. Nor can both endpoints be
the same designated line, since the inclusion is strict. Each MOVE thus
contributes at most one item to these `2s` requirements. This proves the
lower bound without a read-once, two-phase or independent-carrier premise.

### Attainment

For each moved index `i`, initialize a zero owned register `C_i` at `L_i`,
copy `X_i` into it, and set `X_i := X_i - C_i`. These are local operations;
now `C_i=x_i` and all moved public registers are zero. Scale any fixed-point
register `X_i` by `a_i` locally.

For each moved source `i`, put `j=pi(i)` and `H=L_i+L_j`. The two distinct
binary lines span a plane. MOVE `C_i` from `L_i` UP to `H` and DOWN to `L_j`,
then perform `X_j := X_j + a_i C_i` and CLEAR `C_i`. Both MOVEs have rank one.
Every moved destination receives exactly one source. Therefore the endpoint
is the required scaled permutation and all owned registers are cleared.
Other public registers are untouched. There are exactly `2s` MOVEs.

All scalar copying, subtraction, scaling and owned erasure are part of this
local circuit, but only its MOVEs are counted in the stated tariff. The
construction uses `s` owned registers; it does not claim minimum peak storage.

## Application and limits

PR #6939 section 1.3 specifies a perfect-matching exchange on the 104 distinct
P104 lines before its Y bounce. Each of its X registers exchanges its x payload
with its partner while both public frames stay fixed. Taking `s=104` proves
an owned-MOVE floor of `208` for that preprocessing contract. The predecessor's
two rank-one transfers per port attain it. This is an application of the new
all-circuit lower bound, not a new construction of the predecessor's native.

In particular, sharing runs, allowing more intermediate frames or tolerating
temporary junk cannot save an owned MOVE while preserving this contract.
Merely checking the endpoint's shadow matrix would not establish this floor;
the separation of line regions is the additional invariant.

The application does not assert that every proposed shared-landing native
contains this checkpoint. Allowing a public register to leave its line, using
a different endpoint, or interleaving with the later changing Y frames removes
a hypothesis. The full common-chart versus physical phase interface, the
complete signed invoice and every all-size framework assumption remain open.
The checker's changed-frame control permits public descent as well as ascent.
It demonstrates the necessity of the fixed-frame premise in this abstract
model; it does not supply a native under monotone public-frame rules.
For `0 <= C <= 1`, `r^(1-C)>=1` at every positive integer rank, so the tariff
corollary applies on its stated range. Nothing is asserted for cheaper
positive-rank tariffs.
