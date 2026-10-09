# Extended carrier matching: argument and scope

**Setting.** #161's complex word at p = 11: its signed DAG (searched triple module, annealed pair module, merged
face-2/edge-02 outputs), compiled by #144's `compile_graph`, gauged by #144's `select`, then given a physical
layer by `scripts/paired_cube_physical.py`. A carrier arc `x -> u` lets the control register of addition `x`, which
still holds one operand `y` of `x` after the gate, serve another use `u` of `y` instead of dying. Each arc removes
one role.

**The pre-test.** `compile_graph` first gives every node the frame

    initial[x] = (intersection of the root frames reachable from x in the DAG) with unused coordinates removed

and accepts `x -> u` only if `initial[x]` lies inside the receiving frame `initial[t]` (or the root frame), with
`t` later than `x` in the order `(dim initial, node)`. It then discards these frames and recomputes every frame as
the full backward intersection over DAG successors, arc successors and roots, and asserts that each value span
lies in its frame. The pre-test guarantees that this final assertion holds. It is not what the construction uses.

**What the construction uses.** A physical frame must contain the span of the addresses in the value's support and
must lie inside every frame the register visits later. For an arc set A this is exactly:

1. the graph with DAG edges and arc edges `x -> t` is acyclic, so the operations can be ordered with every arc
   forward;
2. with `ann[x]` the span of the root annihilators reachable from `x` through DAG or arc edges,
   `span(x)` is orthogonal to `ann[x]` for every node.

`cxlinks.compile_closure` computes these frames, checks 1 and 2, orders the operations by (frame rank,
topological index), and then uses the repository's ledger formulas unchanged. Nothing else differs from
`compile_graph`: with #161's arcs and the repository's order it returns #161's certified record exactly, which
`verify.py` checks.

**Why the added arcs are sound.** They satisfy 1 and 2 by construction, and this is checked independently, not by
the code that chose them. The repository's `scripts/paired_cube/verify.py` receives the graph, the frames, the
order, the arcs and the compiled word, and re-derives:

- every DAG edge and every arc goes forward in the order;
- every frame equals the full backward intersection of its successors' frames (`Incomplete intersection`);
- every value span lies in its frame;
- the signed scalar word produces the exact matrix H, and K is its own inverse;
- the physical replay of all operations moves every role only upward, and its rank recount equals the ledger;
- the gauges are the forced intersections, on roles untouched by phase one, and the target chains ascend.

That checker has no pre-test. It passes unchanged on the extended word.

**Physical layer.** The layer follows #161's rules and is checked by #161's own
`scripts/paired_cube_physical.py`, unchanged: each moved operation frame contains its value span, every role chain
is nested with each hand-off spliced, each donor is ungauged, is not a root and dies before its recipient's read,
its last frame lies in the recipient's gauge, the target chains ascend in actual read order, the deficit
telescopes, and an exact aliased replay with arbitrary dirty scratch restores every slot and adds x to y. The
three negative controls are rejected.

**Accounting.** #161's shared-core ledger is unchanged: three copies of the local, source and target children,
`2v` endpoint children, `W = 2v + R - pairs`, deficit `2v - 3 loss = 1320`. Each added arc lowers R by one. The
largest child stays 20. The role count enters #161's finite bridge and row reserve only through quantities that
decrease, and `verify.py` evaluates both with #161's functions.

**Scope.** This is a finite conditional construction. Every interface #161 retains stays an assumption: the
paired source scheduling and completed-core sharing, the Clifford frame compiler, the uniform recursion and the
analytic and tape contracts.

Not established here:

- No optimality. The arcs are a greedy extension of #161's matching in node order, and the pairing is greedy by
  first-order saving. The certified value does not depend on how either was found.
- The repository's operation order is replaced by another linear extension. The two orders give different
  phase-one closures (11,302 operations here, 10,150 in #161). The gauges are selected by the repository's rule
  on the new order and are checked by the repository's checker; there are 2,970 rank-18 gauges in both.
- #161's bit supplier is used as certified there and is not re-run by this package.
- #161 was closed in favour of #168 and is not on main. Its files are pinned at `d14e291` in `baseline-pr161.tar.gz`, so
  this package stays valid for that commit.
