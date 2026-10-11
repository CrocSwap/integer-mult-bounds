# Ceilings on κ for the paired-cube constructions

This note proves upper bounds on the κ that a paired-cube construction can certify, and applies them to #168's word. It
makes no κ claim and changes no existing file. `ceiling.py` evaluates every bound on #168's pinned files and checks its
own model against #168's certified ledger.

## Setting

A shared-core supplier is described per group vertex by `W` roles, `m = 3h`, and a multiset of children: `n_r`
children of width `r`, with `0 < r < m` (`notes/paired-cube-sharing.tex`). Its rank mass telescopes:

    Σ_r r·n_r = W·m − D,     D = 2v − 3ℓ,

where `v` is the number of ports and `ℓ` the copied-centre loss. Write `f(r) = r·ln(m/r)` and

    C = Σ_r n_r·f(r).

The repository certifies a saving `a` when an exact rational upper bound on the moment `Σ n_r·(r/(W·m))·(m/r)^a` is
below 1 (`exact_moment` in `scripts/paired_cube_network.py`). The bit side also adds a positive bad-class term
before testing. `exp_upper` and `log_upper` bound `exp` and `ln` from above, so a certified `a` always satisfies

    Σ_r n_r·r·(m/r)^a < W·m.                                                     (∗)

## Fact 1: the moment root

**Lemma 1.** If (∗) holds then `a < D / C`.

*Proof.* For `0 < r < m` we have `ln(m/r) > 0`. Since `e^x ≥ 1 + x`, each term satisfies
`(m/r)^a ≥ 1 + a·ln(m/r)`. Summing gives `W·m > Σ n_r·r + a·Σ n_r·r·ln(m/r) = W·m − D + a·C`. ∎

The bound is nearly tight. Let `a*` be the root of the moment. Using `e^x ≤ 1 + x + (x²/2)·e^x` for `x ≥ 0`,
`a* ≥ D / (C + (a*/2)·Σ n_r·r·ln²(m/r)·(m/r)^{a*})`. The relative gap is at most about `a*·ln(m)/2`, which is
below 0.2% here. On #168 the certified complex and bit savings lie within 0.09% of `D/C` (`ceiling.py`, fact 1).

## Fact 2: the assembly

PR #183 (romainhedouin) gives the assembly's acceptance region in closed form. From a supplier saving `a`, with
`q = a(1 − 2η)`, the assembly accepts κ exactly below

    G(a) = q(1 − η) / (1 + q)              (balanced prefix, scripts/paired_cube_assembly.py),
    G(a) = q(1 − η) / (1 + q(2 + η))       (original prefix, scripts/structured_bulk_assembly.py).

Both assemblies pass `a = min(AB, (1 − β)·AC − 10⁻¹⁰)`. Here `AB = (1 − ATOM)·COARSE + ATOM·OLD` is at most
`COARSE` (since `OLD < COARSE`), and `(1 − β)·AC − 10⁻¹⁰ < AC`. `G` is increasing in `a`, and `G(a) < a`. Hence

    κ < G(min(COARSE, AC)) < G(D_c / C_c),

where `D_c`, `C_c` belong to the complex supplier. The bit supplier gives the same bound with its own `D`, `C`.

## Fact 3: chains

`f` is strictly concave on `(0, m)` and tends to 0 at 0, so it is strictly subadditive: `f(x) + f(y) > f(x + y)`.

**Lemma 3.** A chain of positive steps `r_1, …, r_k` with total `t` costs at least `f(t)`. If `k ≥ 2`, it costs at least
`f(1) + f(t − 1)`.

*Proof.* Merging steps lowers the cost, so `Σ f(r_i) ≥ f(r_1) + f(t − r_1)`. The function `x ↦ f(x) + f(t − x)` is
concave and symmetric about `t/2`, so its minimum over `[1, t − 1]` is at the endpoints. ∎

## Fact 4: the frame floor of a fixed word

The complex child multiset consists of:

- three times the steps of every physical slot's frame chain;
- three times the source and target data steps;
- three copy children per copied centre, each of width equal to the centre's frame dimension;
- one child of width `3·dim σ` per gauged first occupant;
- `2v` children of width 2.

`ceiling.py` rebuilds this multiset from the tree's own word and frames, and checks that it equals the certified
complex ledger child for child.

Fix the word: its DAG, the operations and their order, the carrier arcs, the gauges, the reuse pairs and the
terminal sinks. The free choice is the frame `F_i` of each operation. A layout is admissible when the conditions
checked by `scripts/paired_cube/verify.py` and `scripts/paired_cube_physical.py` hold:

- `span(x_i) ⊆ F_i`;
- both registers of operation `i` are at `F_i` while it runs;
- every slot's frames nest along its chain: entrance (0, the source line, or the gauge), its operations' frames,
  its root frame, then the full space;
- a recipient is read exactly at its gauge `σ`, after its donor's last operation.

**Lemma 4a (joint bounds).** Every admissible layout has `L_i ⊆ F_i ⊆ U_i`, where:

- `L_i = span(x_i) + L_{prev(a)} + L_{prev(b)}`, computed forward in operation order from the registers' entrance
  frames;
- `U_i = up(x_i) ∩ U_{next(a)} ∩ U_{next(b)}`, computed backward from root frames, recipients' gauges (for
  donors) and the full space;
- `up(x)` is the full backward intersection of `x`, i.e. the intersection of the root frames reachable from `x`
  through DAG and carrier edges.

Registers of terminal sinks are skipped in both passes, since the certified word deletes them.

*Proof.* By induction along the operation order. Both registers sit at `F_i`, so `F_i` contains everything below
either register's previous frame and lies inside everything above either register's next frame. `F_i ⊆ up(x_i)`
because every root reachable from `x_i` is read from a nested register chain that passes through `F_i`. For a DAG
edge, the register holding the operand, or the copy that carries it, takes part in the consuming operation. For a
carrier arc, the control register continues to the use. A root is read at its root frame. ∎

`ceiling.py` checks that the tree's own layout satisfies every `L_i ⊆ F_i ⊆ U_i`.

**Lemma 4b (slot floor).** For each slot, take the minimum of `Σ f(steps)` over nondecreasing dimension sequences
with `d_i ∈ [dim(cumulative L), dim(cumulative U)]` at each event. Exact events (source line, recipient gauge, root
read) are fixed. The sequence starts at the entrance dimension and ends at `h`. The sum of these minima over the
slots is at most the slots' actual cost in every admissible layout.

*Proof.* An admissible layout gives each slot such a sequence. The only constraints dropped are that the two
registers of an operation share one dimension, and that the frames are subspaces rather than dimensions. ∎

**Lemma 4c (coupling).** For any prices `λ_i`, add `+λ_i·d` to the dest register's cost at operation `i` and
`−λ_i·d` to the control register's cost. The sum of the per-slot minima is still a lower bound.

*Proof.* In an admissible layout both registers have `d = dim F_i`, so the price terms cancel. Weak duality. ∎

`ceiling.py` runs 400 rounds of integer subgradient steps on the prices. It keeps the best round, and asserts that
every round's total lies below the tree layout's own cost.

The data banks climb a total rank of `h − 1` per bank and stage, so they cost at least `6v·f(h − 1)` (Lemma 3). The
copy, gauge and endpoint children are fixed. Write `C_floor` for the sum of all these floors. Then
`C ≥ C_floor` for every admissible layout of the word, and

    κ < G(D / C_floor).

For terminal sinks, the certified record removes exactly one child of width `r` and one of width `h − r` per sink and
stage (`research/terminal-sinks`, re-checked by `ceiling.py`). The other slots' chains are unchanged: an operation
that writes a sink keeps its control register at `F_i`. The target registers still climb `h − 1`.

**Arithmetic.** Every logarithm is replaced by a rational lower bound: partial sums of `2·atanh`, whose terms are all
nonnegative. Every `f(r)` is rounded down to the grid `2^-64`, and all sums and the dynamic programme use exact
integers. So `C_floor` is a true lower bound, and the printed ceiling is rounded up.

## Fact 5: design ceilings

These keep the tree's `h`, `v`, `ℓ` and decoder, but allow any word.

- **No auxiliary registers:** `κ < G(D / (6v·f(h−1) + 2v·f(2) + copies))`.
- **No centre loss either:** take `D = 2v` and drop the copies.
- **One register per source:** in every construction in this repository, each source is injected into its own
  register before the first addition (the transparent word `z ← z + Vx`, then `z ← Mz`). Those `v` slots are
  simultaneously live, so they are distinct. Each needs at least two steps (its source line, then the full space),
  so it costs at least `3·(f(1) + f(h − 1))` (Lemma 3).

These are far from tight. They show where the room is: either in the numerator `D`, or in the auxiliary registers,
which carry about 85% of the cost in every certified word.

## Scope

- **Facts 1–3** are proved here and are elementary.
- **Fact 4** is a statement about one fixed word, varying only its operation frames. It does not bound constructions
  that change the circuit, the gauges, the reuse pairs or the sinks.
- **Fact 5** bounds whole designs under the stated hypotheses.
- Nothing here is machine-checked beyond `ceiling.py`'s exact arithmetic and self-tests.
