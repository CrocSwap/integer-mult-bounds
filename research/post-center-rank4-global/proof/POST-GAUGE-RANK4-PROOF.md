# Post-center gauges followed by rank-four response kernels

Prepared for **icekylinx with GPT-6 Astra assistance**. This note proves the
new composition used in `code/build_rank4_portable.py`. The SAME504 scalar word is retained
from icekylinx's PR #531. The response-kernel and gauge primitives retain
DreamingOfClouds's attributed PR #484 implementation and its cited predecessors.
The new contribution is the ordered composition below: a helper may first
serve its own post-center gauge and subsequently donate to a larger-frame
kernel. The former disjoint-role restriction is unnecessary with this order.

## Algebra and required order

Let (B) denote the unchanged delivery suffix. Write its target map as

$$
y_{\rm out}=K y_{\rm in}+D h+u,
$$

where (h) consists of the ordinary-M helpers that have not been touched in
the source prefix or center cut; (u) collects all other inputs. The existing
target preconditioner is (K^{-1}). A gauge of helper (d), performed at the
beginning of (B), adds (-K^{-1}D_d h_d) to the targets. Its later contribution
is therefore (-D_dh_d), cancelling the ordinary response of its initial dirt.

Suppose an ungauged pivot (p) satisfies the exact relation

$$
D_p=\sum_{d\in\mathcal D}q_{dp}D_d.
$$

**After all gauge compensations**, apply

$$
h_d\leftarrow h_d-q_{dp}h_p
\qquad(d\in\mathcal D),
$$

then execute the original (B). The pivot's target coefficient becomes

$$
D_p-\sum_dq_{dp}D_d=0.
$$

The coefficient of each donor's own initial scalar remains its original unit
coefficient: adding pivot dirt to a donor does not change the donor's initial
column. Thus its earlier gauge compensation remains exact. The gauge has not
read the newly injected pivot dirt. This is why the same helper can legally
be both a gauged helper and a kernel donor. Reversing these two operations
would generally require a different compensation formula.

The 14 groups use disjoint registers, and pivots never serve as donors. All
relations can therefore be applied simultaneously without substitution terms.
Relations for (K^{-1}D), used by the builder, and for (D), used by the
independent audit, are equivalent because (K) is invertible.

## Actual frames and cleanup

The 112 helpers numbered 392 through 503 form 14 groups of eight. Each group
has a common four-dimensional frame (E), four independent donor columns,
and four pivot relations. Every member's first native frame has rank five
and contains (E). Each donor's retained gauge line (L_d) satisfies

$$
L_d\subset E\subset F_d^{\rm first}.
$$

A donor therefore serves its compensation at (L_d), climbs to (E) for the
kernel shears, and continues into its native frame. A pivot starts at (E)
and has no gauge compensation. These helpers are absent from every source
prefix and center-cut operand, so all hold exactly their initial scalars at
the insertion point. Removing the pivot gauges leaves 112 post-center gauges
and 320 target additions. Their frames are nested at each target and contained
in that target's first own-Y frame. Targets still have frame zero at the
unchanged center cut.

All new helper shears are invertible with dyadic coefficients. Their pivots
are zero on clean source inputs, so the source scalar map is unchanged.
Sources and helpers never read targets. Reversing all source/helper operations,
including the new shears, therefore restores arbitrary source/helper inputs;
this cleanup takes place at the paid full frame. Every physical helper keeps
its original whole-call owner interval.

## Inventory and audit scope

The word retains 40 rank-one face-kernel pivots, 112 rank-one post-center
gauges, and 56 rank-four pivots. Its entrance-rank sum is

$$
40+112+4\cdot56=376,
$$

and its residual widths are **56 of width 5, 152 of width 8, and 296 of width
9**. There are 168 new donor shears. The coalesced local profile is

$$
H=\{1:2208,\;2:728,\;3:184,\;4:280,\;5:56,\;6:56,\;8:8\},
\qquad \sum_r rH_r=6016.
$$

`audit_post_rank4.py` independently accumulates the raw (B) adjoint with exact
fractions; it imports neither the response builder nor the kernel solver.
`POST-GAUGE-RANK4-AUDIT.json` records all 56 exact relations, all group and
gauge frame containments, the untouched-before-(B) condition, and all remaining
target compensation chains. Its measured runtime was about 0.055 seconds.
That targeted audit proves the new local composition. Full endpoint identity,
literal Clifford phases, and physical global hosting are separate certificates;
no global exponent follows from the inventory alone.
