# Composable edge-helper compensation contract

This gives a complete local compensation construction **conditional on an
admitted K-word interface**. It does not admit a new all-size supplier or
assert favorable cost. Its predecessor interfaces are Dominik Scholz's
PR606, DreamingOfClouds' H6 package, and the common-frame and same-order
inverse-transpose rules of `research/e8-complex-gauge-kernel/PROOF.md`
sections 2.1--2.4. Prepared with OpenAI Codex assistance; Apache-2.0.

## Hypotheses on the supplied K-word

Let H=17, N=30,960, and let every port have the actual odd-norm binary
address p_s from PR606. Let P_s=span(p_s) and Q_t=p_t^perp. Let A=I-K,
using the pinned scalar factor K. The K-word is required to have:

1. Initial frames x_s at P_s, y_t at zero, with its independent auxiliary
   dirt z at their admitted entrances. Final frames are x_s at FULL,
   y_t at Q_t, with each auxiliary at its admitted endpoint. The source
   and target register sets may have the same port-index set but are
   distinct physical registers.
2. Exact *logical* scalar map `(x,z,y) -> (x,z,y+Kx)` for all x,z,y.
   In particular the target self-block and source self-block are identity,
   and auxiliary-to-data blocks vanish. Merely fitting K on clean target
   or auxiliary inputs is insufficient.
3. A valid common-frame stream, charged monotone paths, legal copy lifetimes
   and its own restoration/accounting certificate. Its second orientation
   dualizes each scalar gate in the same order and with the same frame
   chronology, giving `(x,z,y) -> (x-K^T y,z,y)`.

All comp-helper registers below are disjoint from that word's registers and
private streams, including its physical bank slots. K can internally mutate
sources and targets: only the stated endpoint map matters.

## Construction

For each ordered nonzero entry e=(t,s) of A, allocate one independent
ordinary dirty register h_e. It begins at frame zero. Its initial logical
value d_e is arbitrary, including arbitrary correlations with all other
inputs. Perform the following phases in the listed order:

1. At zero, for every e, `y_t += -A_ts h_e`.
2. For every e, climb h_e from zero to P_s; at P_s perform `h_e += x_s`.
   Sources have not entered the K-word and are still at P_s.
3. Run the complete K-word on its original data and auxiliary registers.
   No comp-helper is touched by it.
4. For every e, climb h_e from P_s to Q_t and, at Q_t,
   perform `y_t += A_ts h_e`. The K-word has already placed every target
   at its final Q_t.
5. For every e, climb h_e from Q_t to FULL and, at FULL,
   perform `h_e += -x_s`. Every source is already at FULL.

All phase-1 gates must precede every comp-helper's departure from zero.
All phase-2 gathers must precede the K-word. Phase 4 begins only after
the complete K-word, including its private-copy erasures. No comp-helper
is a private copy and there is no additional copy episode in this extension.

## Frame proof

For distinct ports t,s, A_ts is nonzero only at odd integral inner products
t_real=±1 or±3. PR606's address identity is

`p_t dot p_s = 1 + t_real (mod 2)`.

Hence p_t dot p_s=0 for every nonzero A_ts. The diagonal of A is zero.
Therefore P_s is contained in Q_t. Every address has odd norm and is
nonzero, so dim P_s=1 and dim Q_t=16. The comp-helper chain is

`0 < P_s < Q_t < FULL`,

with ranks **[1,15,1]**. Every addition has both operands at exactly the
same current frame. The K-word's own operands and frame histories are
unchanged, and comp-helper operations introduce no transition on any data
register. The same frame proof holds after scalar dualization, because a
dual addition keeps its operand pair and the stream order.

Use identical exact representatives T_Ps and T_Qt on the helper and data
registers at these gates. If the chosen endpoint representatives differ
by rank-zero adapters, those adapters must be emitted and counted. The
binary inclusion proves transition rank; it does not license ignoring
representative phases or adapters.

## Exact forward map

Let E be the edge set. After phases 1 and 2,

`y'_t = y_t - sum_(e=(t,s)) A_ts d_e`,
`h'_e = d_e + x_s`.

The K-word accepts this arbitrary target input and restores logical x,z,
so its target output is `y' + Kx`. Phase 4 adds
`sum_(e=(t,s)) A_ts(d_e+x_s)`, canceling every independent d_e.
Phase 5 restores each h_e to d_e. Therefore the complete scalar map is

`(x,z,d,y) -> (x,z,d,y+(K+A)x) = (x,z,d,y+x)`.

This calculation is columnwise exact for all helper dirt, source, target,
and K-auxiliary inputs, so correlated dirty banks require no probabilistic
independence assumption. By common-frame conjugation the physical output
on each register is its final T-frame times this logical output, with the
initial frame inverse applied to its input. The comp-helper block is
exactly `T_FULL T_0^-1`, the ordinary width-17 residual. There is no virtual
entrance and no borrowed entering-helper spectator in this construction.

## Exact second orientation

Dualize `a += c b` as `b += -c a` in the same event order. The five phases
become, suppressing climbs:

1. `h_e += A_ts y_t`.
2. `x_s += -h_e`.
3. K-word dual: `x += -K^T y` (z and y restored).
4. `h_e += -A_ts y_t`.
5. `x_s += h_e`.

After phase 1 h_e=d_e+A_ts y_t. Phase 2 subtracts d_e+A_ts y_t from x_s.
The dual K-word accepts these arbitrary source inputs, preserves logical y,
and subtracts K^T y. Phase 4 restores h_e=d_e, and phase 5 cancels the
subtracted d_e. Thus

`(x,z,d,y) -> (x-(K+A)^T y,z,d,y) = (x-y,z,d,y)`.

The scalar source mutation before the dual K-word is legal under the
arbitrary-source hypothesis. A K-word valid only on fixed source values
would not satisfy this compositional interface. This is the same-order
inverse-transpose orientation, not time reversal of the frame stream.

## Complete paid local extension

Let R=nnz(A). The pinned H6 domain has R=480,337,920. The extension has:

- R ordinary restored dirty roles, each path [1,15,1].
- Per local invocation: R rank-1 initial climbs, R rank-15 middle climbs,
  R rank-1 final climbs, and 4R weighted scalar additions.
- No new private center descent, new data climb, virtual entrance, or
  entering-helper spectator. K-word private descents remain charged by K.
- At odd stage count L and m=1+16L, q=floor(m/17) pure width-17 slots per
  physical comp-helper bank, with pad p=m-17q. Replicate by a multiple of
  q and price the full helper-bank stock LR/q and paid pad work LpR/q.
  The total extension rank mass is `17LR+LpR/q=LmR/q`. It leaves deficit
  unchanged but increases pressure. For each invocation use separate
  ordinary slots; never assign speculative sharing or hosting credit.

The huge R is a legal local fallback target, not a favorable helper count.
An emitted K-word and full compiler/outer invoice are still required before
calling the result a supplier. The frozen H6 break-even allowance is far
smaller than this R; exact pricing of the composite word is a separate gate.

## Weighted additions, precision and inherited compiler boundary

On A's support the weights are ±1/16 at |t_real|=1 and ∓5/16 at
|t_real|=3. They are dyadic. The inherited emitter
`research/e8-complex-gauge-kernel/code/emit_gk.py::primitive_bound`
counts a weighted addition q=a/b by

`3+(bit_length(a)-1)+popcount(a)+(bit_length(b)-1)`.

This is cleared coefficient work using binary Horner multiplication,
halving, signed accumulation and erasure. In that convention weights
±1/16 cost at most 8 scalar primitives, ±5/16 cost at most 11, and ±1
cost at most 4. Hence each |t_real|=1 edge costs at most 24 scalar
primitives and each |t_real|=3 edge at most 30; the latter has 3,363,840
ordered edges in the pinned domain. These are finite scalar primitive
bounds, **not additional Fourier children**. They must enter the actual
compiler, router/literal/tape and precision receipts; no previous small
supplier's fixed constants may be reused without reconstruction.

The composition also amplifies intermediate coefficient norms. A safe
local prefix bound uses the maximum edge degree Δ=15,872 and |A_ts|≤5/16.
Forward target precompensation gives row l1 at most `1+5Δ/16=4,961`.
Dual source gathers give at most `1+21Δ/16=20,833`. If B_K is the K-word's
certified maximum scalar row-l1 amplification on unit input rows, its
internal prefix must be bounded using these enlarged inputs, at most
20,833 B_K. The additional cleanup accumulations and Horner private
streams must also be recounted. Exact dirt cancellation at the endpoint
does not erase this precision cost.

The remaining supplier obligations are the inherited all-size compiler,
exact endpoint/operator representatives, finite adapter primitive counts,
mutable-source/common-frame interface, correlated dirty bank realization,
template integration, precision/tape/common grid, and analytic transfer.
This theorem proves the new local schedule and transparent scalar map;
it does not independently prove those global interfaces or the K-word.

## First independent replay

`replay.py` checks all exact rational input columns in both orientations
for a nonconstant small K fixture, including independent comp-helper dirt
and arbitrary target inputs. K is treated as an abstract certified block
with the interface above; its internal compiler is not modeled. The
replay rejects omission of precompensation, gather, scatter and cleanup and a
nonorthogonal helper incidence. This finite replay supplements the symbolic
proof; it is not an exhaustive replay of the 480-million-edge word.

## Open next questions

- Supply an exact emitted K-word satisfying the stated arbitrary-input
  interface; combine its certificate with this extension and recount the
  full stage, bank, primitive, precision and outer inequalities.
- Compress the edge-helper network while retaining its exact dirty map and
  low-frame source/target incidences. A useful first step is one restored
  shared helper servicing a geometrically compatible orthogonal block.
