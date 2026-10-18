# A compressed full compensation network with one dirty helper per edge

This directory gives an exact scalar/common-frame construction for the complete
H6 `C = I-K` matrix. It assigns one independent ordinary dirty helper to every
nonzero entry. The construction is a deliberately expensive baseline, useful
for isolating the problem of compression from the problem of legality.

The complete stream has over three billion events and is defined by deterministic
iterators instead of materializing it. Bounded 8-port and 32-port fixtures emit
every compensation event and replay every arbitrary input column exactly. The
composition fixtures additionally exercise an explicit restored K **interface
macro**; they do not compile the K implementation. No supplier admission,
physical Clifford compiler replay, improved helper bound, or new kappa is claimed.

Geometry and the ordinary-helper/controller interface are attributed to Dominik
Scholz's PR606. The H6 compensation/Walsh proposal is attributed to DreamingOfClouds.
This extension retains the earlier independent audit and all frozen inputs
unchanged. Prepared with OpenAI Codex assistance; Apache-2.0.

## Definition and actual address legality

Let the actual 30,960 E8-squared ports be indexed in the pinned PR606 enumeration.
Put `t_st = (u_s dot u_t)/4`, `K_ts = (t_st^3-4*t_st)/48`, and
`c_ts = delta_ts-K_ts`. The reconstructed addresses are odd 17-bit words and
satisfy `p_s dot p_t = 1+t_st mod 2`.

The diagonal has `t=4`, so `c_ss=0`. Every off-diagonal pairing belongs to
`{-3,-2,-1,0,1,2,3}`. Its compensation coefficient is nonzero precisely when
t is odd, with respective values `5/16,-1/16,1/16,-5/16` at
`t=-3,-1,1,3`. Therefore every required edge satisfies `p_s dot p_t=0`.
Consequently its source line `E_s=span(p_s)` lies in its target cap
`L_t=p_t^perp`. Oddness makes the line dimension 1 and the cap dimension 16.

`edge_records(ports,packed,range(30960),range(30960))` is the canonical edge
iterator: target index first, then source index, retaining exactly the nonzero
coefficient. It computes each rational coefficient from the actual port vectors
and checks orthogonality. Its working edge memory is constant; producing every
edge still requires a huge traversal. The complete count **480,337,920** is
retained from the pinned prior exhaustive matrix audit, whose receipt hash is
recorded in `SCHEMA.json`; this extension does not silently rerun that full audit.

`event_records(...)` defines the complete phase stream without allocating the
edge set or scalar matrix. The fixtures use this identical iterator. Register
names `h{target_position}_{source_position}` are unique for every edge.

## Complete compensation lifecycle

Sources begin at E_s, targets at zero, and each helper h_ts at zero with
independent arbitrary logical dirt d_ts. The following are *emitted operations*,
including every compensation, gather, scatter and cleanup:

1. While all targets/helpers are at zero, add `y_t -= c_ts*h_ts` for every edge.
2. Climb each helper `0 -> E_s`, then add `h_ts += x_s` at E_s. Complete every
   such gather before any source leaves its initial line.
3. Climb every source `E_s -> FULL`, rank 16. A composed K implementation may
   run at this cut, while compensation helpers are dormant at E_s and targets
   are still at zero.
4. Climb every target `0 -> L_t`, rank 16. For each edge climb its helper
   `E_s -> L_t`, rank 15, and add `y_t += c_ts*h_ts` at L_t.
5. Climb every helper `L_t -> FULL`, rank 1, and add `h_ts -= x_s` at FULL.

Every addition has both operands at its current frame. Every ordinary transition
is ascending and nested, by `E_s subset L_t`. All sources/helpers end FULL and
each target ends at its actual cap. There are no private copies or descents in
the compensation network. Registers are never identified or reused between
different edges, so no independence or dirty-reuse shortcut is assumed.

## Scalar proof on every independent dirt column

Let G be the `R by N` matrix whose edge row selects its source, and B the
`N by R` matrix whose edge column is `c_ts*e_t`. Then `BG=C`, entry by entry.
For arbitrary source x, target y, and independent helper dirt d, the phases give:

```text
prefix:       y <- y-Bd
gather:       d <- d+Gx
optional K:   y <- y+Kx
scatter:      y <- y+B(d+Gx)
cleanup:      d <- d-Gx
```

The optional K phase has no helper effect. With it included, the endpoint is
`x'=x`, `y'=y+(K+BG)x=y+x`, `d'=d`. Without it, `y'=y+Cx` instead. This proves
all source, target and helper columns simultaneously and preserves arbitrary
initial targets; checking only clean targets or zero helper inputs would omit
essential parts of this identity.

Every elementary scalar event is invertible. Taking the inverse transpose of
each event in the **same event order** gives the inverse transpose of the whole
scalar map. An addition `dst += q*src` becomes `src -= q*dst`; the two registers
still have the same current frame. The chronology and transition ranks are
unchanged. The exact fixture interpreter independently verifies this orientation.

Under the common-frame conjugation lemma retained in
`research/e8-complex-gauge-kernel/PROOF.md` section 2.2, the scalar word therefore
lifts to the corresponding endpoint-conjugated linear operators for any chosen
invertible frame operators. Supplying and replaying the concrete physical
Clifford/child recipes and controller admission remains a separate obligation.

## Precise composition obligation for K

The composed fixtures invoke the matrix K as a serialized interface macro at
the cut. They verify the algebra and the source-FULL/target-zero boundary;
**the macro's internal gates are not emitted or checked here**. To replace it
with an actual implementation, require a complete restored invocation:

- In the forward orientation it leaves source logical values x unchanged and
  maps arbitrary target inputs by `y -> y+Kx`, with target-to-target block I.
- It restores every independent K-helper dirt column and does not touch the
  compensation helper registers. It starts/ends its source boundary at FULL
  and target boundary at zero for the direct `[16]` data profiles above.
- Its inverse-transpose implementation uses the admitted same frame chronology;
  its own private copies, helpers, cleanup, pads and stock are separately charged.

The full-center proposal can be considered for this boundary by postponing
target climbs until after its frame-zero scatter. Its scalar/frame/compiler
admission is not inferred from that proposal's invoice.

More generally, an already emitted K word with nested source and target paths
can use the same prefix/suffix: put every edge gather before the first source
climb and every edge dirt precompensation before the first target climb; append
the edge scatter when targets reach their caps and the cleanup when sources
are FULL. The K word must restore its source logical values at that cut and
have target-to-target block I. Retain all of its actual split data paths in the
invoice, instead of substituting `[16]`. A K program that mixes/scales target
inputs or leaves source/non-target effects needs a new block-composition proof;
the simple prefix above does not automatically apply.

## Counted profile

| Role | Count | Transition ranks per register |
| --- | ---: | --- |
| Sources | 30,960 | `[16]` |
| Targets | 30,960 | `[16]` |
| Ordinary restored edge helpers | 480,337,920 | `[1,15,1]` |

Compensation has `7R+2N = 3,362,427,360` events: `4R` scalar additions and
`3R+2N` transitions. Its local transition rank mass is
`32N+17R = 8,166,735,360`. These counts exclude K. They also exclude stages,
bank stock, pads, replication, adapters and compiler work. The separate invoice
must include all of those; local rank mass alone is not a pressure bound.
This enormous helper count is not a competitive H6 mechanism. It supplies a
full legal scalar/frame baseline against which a compression proposal can be
tested without assuming away arbitrary dirt or chronology.

## Emitted fixtures, checks and controls

`fixture-8-*` uses 8 distinct actual labels and 36 edges; its exact sparse linear
replay covers all 52 arbitrary input columns. `fixture-32-*` uses 32 distinct
actual labels and 522 edges, covering all 586 columns. Both compensation-only
and K-composed variants pass forward and inverse-transpose replay. The interpreter
checks current operand frames, nesting, initial/end frames, and exact path ranks.

Five controls run on each 8-port variant:

- Remove one dirt-prefix addition: target helper-dirt response remains.
- Remove one compensation scatter: the intended source-to-target matrix changes.
- Remove one FULL cleanup: a helper retains source information.
- Substitute the source's own target cap: the odd label makes the edge
  nonorthogonal, so the source line is not contained in that cap.
- Remove one helper's source-line climb: the gather's current operand frames differ.

These controls isolate substantive mathematical and lifecycle failures. Fixtures
contain the complete emitted compensation stream; receipts identify the interface
macro wherever used. Neither a finite replay nor a macro assertion is described
as a compiler proof for all ports.

## Reproduction

With a NumPy-capable Python, from the repository root:

```sh
python3 -B research/h6-compensation-network/construction/network.py
python3 -O -B research/h6-compensation-network/construction/network.py
```

Checks remain active under `-O`. The script imports predecessor geometry only;
its sparse rational and GF(2) frame interpreters are independent of previous
circuit audits. It writes only adjacent fixtures, `SCHEMA.json` and `RESULT.json`.
The full stream is intentionally not generated during this bounded replay.

## Open next questions

- Replace independent edges with actual shared rectangles contained in one
  common frame. Begin with repeated source labels, then require exact dirt
  precompensation and cleanup for every shared helper; report the resulting
  target/source paths rather than retaining the baseline invoice by assumption.
- Supply and replay a complete K implementation at the stated cut, including
  its arbitrary-dirt restoration and physical transitions. This is the remaining
  composition/compiler gate before claiming an admitted whole invocation.
- Price this baseline and each successful compression using actual helper-bank
  stock, pads and stages. A helper reduction alone is insufficient if it creates
  private descents or fragments the data paths.
