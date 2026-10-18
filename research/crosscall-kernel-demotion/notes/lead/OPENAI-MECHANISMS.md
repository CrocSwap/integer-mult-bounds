# Two distinct OpenAI mechanisms: root assembly worker

These sources were inspected in the registered OpenAI math tree. The exact
repository paths, source hashes and declaration lines are in OPENAI-SOURCES.json.
This round does not compile Lean or assert a new kernel certificate. The source
collection is https://github.com/openai/math .

## 1. CapacityScan: prefix checks have an exact complete-load meaning

Source: OAI.Computability.BinPackingGap.CapacityScan.scan_eq_true_iff and
scan_initial_eq_true_iff_load, in
`lean/OAI/Computability/BinPacking/Packing/CapacityScan.lean`.
For valid nonnegative item widths, the early-rejecting scan accepts exactly when
the completed load of the labelled container does not exceed one.

Adaptation: scale each physical child's capacity to its integer axis rank. For a
fixed literal final owner table, group role widths by actual physical identity
(owner replica, child, port). Scan those widths in execution order with pointer
s_0=0 and s_{j+1}=s_j+w_j. Accept iff all w_j are positive integers, each role's
saved offset is s_j, and s_k <= C. Positivity gives s_j <= s_k, so this is exactly
a sufficient nonoverlap/capacity certificate: the blocks [s_j,s_{j+1}) are
disjoint and contained in [0,C), and [s_k,C) is the one complete paid remainder.
The per-call family-uniqueness and inactivity-window checks remain separate and
mandatory. No scalar rank count licenses borrowing an active owner.

This prevents a candidate's aggregate spare-rank count from being mistaken for a
physical construction. It also explains why end shrinkage must precede a fresh
scan of the final assignment rather than being added as a free gain. The literal
owner audit applies this sufficient scan, computes every remainder, and exposes
negative controls for wrong offsets and over-capacity loads.

## 2. Arithmetic program composition preserves semantics and exact charged cost

Source: Program.eval_mapInput / cost_mapInput, Program.eval_mapSource /
cost_mapSource, and Program.Substituted.correct / cost_eq, in
`lean/OAI/LinearAlgebra/MatrixMultiplication/Arithmetic/ProgramComposition.lean`.
Relabelling source inputs leaves a program's gate cost unchanged. Composing two
explicit programs through fixed wires has the stated composed semantics and
cost equal to the sum of the actual two gate costs.

Adaptation: let P_{k,o} be the actual emitted local program of provider k in
orientation o. At call c, dispatch selects one k(c), and the whole-owner chart
supplies a fixed embedding of its input labels into physical coordinates. This
relabel does not erase any scalar gate of P_{k(c),o(c)}. For arbitrary initial
dirty data, the freshly checked provider contract gives its transformation and
restoration; composing through the exact embeddings is therefore sufficient for
the literal sequence of local calls. Its local primitive cost is

    sum_c primitive_count(P_{k(c),o(c)}).

Wrappers, chart construction, dispatch, movement, parent work, recursive child
calls, precision and recovery are additional costs, not covered by a source
relabel. The fresh finite invoice charges these explicitly and adds the complete
new bill to the retained old allowance. All prefix, tape and row inequalities
must hold on this charged bill before the price can be delivered.

This is the reason a call-dependent portfolio is legal without declaring all
providers to execute at every call. It supplies an exact sufficient composition,
not a weighted average of separately claimed kappa values. The complete positive
paid histogram, including every residual block, is then independently priced by
two exact rational engines and the retained strict outer recipe.

## Frozen routes and early falsifiers

The frontier was read through PR1153; PR1148 has the highest explicit construction
claim in that snapshot. PR1152's new T37 flow is a useful compatible stock source,
but the simple attempt to install PR1148 while preserving its rank-48 tails
fails the improvement test. Exact arithmetic screening gives
0.001672752546014868, below both PR1152 and PR1148. This says nothing about a
different actual T37 packing; it stops that one representation early.

The selected route instead retains PR1148's concrete T16 table and admits extra
local demotions only at calls for which actual legal donor axes can be assigned.
The local worker enumerates codimension-one frames rather than assuming the last
basis vector is the only removable direction. Each selected provider must pass
fresh full-column, emitted-program and phase checks. The final owner witness,
complete profile and fresh invoice remain the sufficient assembly obligations.
No unchecked candidate receives a numerical gain.
