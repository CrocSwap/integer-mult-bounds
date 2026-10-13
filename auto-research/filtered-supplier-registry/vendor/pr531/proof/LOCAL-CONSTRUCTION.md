# The same-partition 504-helper scalar construction

Prepared for icekylinx with GPT-6 Astra assistance. Apache-2.0.

This note describes the changed local scalar construction, its exact response
selection, and the accounting boundary. The finite word, rather than a rank
estimate, is the object to be admitted. The selected final word is
`evidence/local/FULL-WORD.json.gz`.

## 1. The identity to implement

Keep the 112 non-coordinate E8 root lines of the existing Hamming model. Write
their representatives as `r_t` in eight coordinates, with squared norm four, and
put `G[t,s] = <r_t,r_s>/2`. The representatives have four-coordinate supports in
the existing fourteen Hamming blocks, with eight lines per block. Define

$$
T_i=\sum_s r_s[i]x_s,\qquad
C_t=\frac14\sum_i r_t[i]T_i.
$$

Then `C_t = x_t + sum_{s != t} G[t,s] x_s/2`. It suffices to deliver the side
term `-sum_{s != t} G[t,s] x_s/2`, while restoring every source and helper.
The eight coordinate centers retain their actual rank-eight frames. The eight
isolated coordinate ports of the old 120-port construction are removed by the
same explicit restriction used in Round19; they do not contribute additional
centers or hidden scalar calls.

For a coordinate pair `p=(i,j)` in a block `D`, normalize its face packet as

$$
F_{D,p,\epsilon}
=\sum_{s\in D:\ r_s[i]r_s[j]=\epsilon}r_s[i]x_s.
$$

The module's recorded output scale is part of this normalization. Exactly three
Hamming blocks contain a fixed coordinate pair. If `B` is the target block and
`A,C` are the other two, put `M_{B,p,epsilon}=F_A+F_C`. The usual face-packet
decomposition supplies all cross-block Gram terms; within a block, the only
nonzero off-diagonal Gram terms join its opposite-parity tetrahedra.

## 2. Put the own-block term directly in an output basis

For every block `(i,j,k,l)`, select the partition `(i,j)|(k,l)` in **both**
tetrahedra. For a selected target pair `(t,u)`, let

$$
a=r_t[i],\quad b=r_t[k],\quad c=r_u[i],\quad d=r_u[k],
\qquad d=-bc/a,
$$

and use the invertible output change

$$
K=\begin{pmatrix}1&1\\c/a&-c/a\end{pmatrix},
\qquad
K^{-1}=\begin{pmatrix}1/2&a/(2c)\\1/2&-a/(2c)\end{pmatrix}.
$$

Loading `-a M_p/2` and `-b M_q/2` into the two coordinates before applying `K`
gives the required two cross-block outputs. Applying `K^{-1}` to the two
own-block Gram rows gives

$$
-G[t,s]/4-aG[u,s]/(4c),\qquad
-G[t,s]/4+aG[u,s]/(4c).
$$

Each row has exactly two nonzero source coefficients and equals a scaled
rank-two partial already present after the module's first forty operations.
The constructor matches the full exact coefficient vector, including its
scale, to the unique existing register. This replaces the eight separate
own-output helpers per block with the eight existing output registers.

Arbitrary initial outputs are handled by applying `K^{-1}` at frame zero.
The center scatter is also expressed in that basis. The later explicit `K`
restores the original target coordinates. All other pair deliveries are added
after that restoration. Thus the construction preserves arbitrary initial
outputs, as well as giving the correct clean source columns.

## 3. Complete centers before those output loads

The center cut must precede the rank-two own-output loads. At the first-forty
operation frontier, selecting the same partition in both tetrahedra protects
eight pair-partial registers and leaves **eight** face assemblies whose two
operands avoid those registers. Execute those eight assemblies early.

Their eight retired donors have clean source rank eight. At the containing
rank-four block frame, an explicitly emitted invertible elementary program
changes their basis so that four coordinates are the block totals
`sum_{s in B} r_s[i] x_s`; four complementary coordinates retain the remaining
information. No donor is overwritten or assumed initially clean. The emitted
operations, including their actual scale factors, are subject to the scalar
primitive audit; invertibility or rank alone does not admit an operation.

The existing rank-eight center paths combine these block totals into the eight
`T_i`. At this cut the raw word has not touched any output. After the cut, load
the eight protected partials directly into the preconditioned outputs at their
rank-two frames, and execute the remaining four face assemblies.

## 4. Deliver selected sums in two halves

Each face packet has its existing carrier and one explicitly allocated copy,
one for each other block containing its coordinate pair. This costs twelve
helpers per block.

Because both tetrahedra use the same partition, a selected key
`(B,p,epsilon)` has two selected output consumers and no ordinary consumer.
Write its packet sum as `A+C`, and call the two output coordinates `y_0,y_1`.
Before any cross-block packet summation, perform all first-half reads:

* Load `A` into `y_0` using the copy of `A` assigned to the other block `C`.
* Load `C` into `y_1` using the copy of `C` assigned to the other block `A`.

Only after every first-half read, form the ordinary packet sums. For the
selected key, keep its two assigned raw copies instead of summing them.
Complete `y_0` from its `C` copy and `y_1` from its `A` copy. The actual module
scales and selected-output coefficients multiply each read.

The first loads join the own partial and their donor at rank four, and the
second loads join at rank six. Every join lies inside the relevant target
hyperplane, and all donor chains remain monotone. The constructor checks these
literal subspaces for all 112 first and 112 second loads. Performing all first
reads before packet summation is essential: the other copy may subsequently
change value and frame. Selected packet sums need no clone. The unselected
keys retain the previously explicit two-output pair transform and its copies.

The per-block helper count is therefore

| Purpose | Same partition | Different partitions, default504 |
|---|---:|---:|
| Original packet factory | 16 | 16 |
| Second copy of each face packet | 12 | 12 |
| Extra early center carriers | 0 | 4 |
| Ordinary two-consumer packet copies | 8 | 4 |
| Separate own-output or selected-sum clones | 0 | 0 |
| Total per block | 36 | 36 |

Both variants have 504 helpers. The same-partition variant changes the
arbitrary-dirt response geometry; its advantage is not a further raw helper
reduction. In particular, this construction does **not** have 448 helpers.

## 5. Exact arbitrary-dirt cancellation and restoration

Let `D_h` be the raw target response to arbitrary initial helper `h`, and let
`C_h=K^{-1}D_h`, using the block-diagonal collection of selected output bases.
The response engine propagates exact rational columns through the entire
`A + cut + B` program and applies the recorded target preconditioner. A
correction `y -= C_h h` before the raw program cancels its helper response.

For a kernel pivot `p`, an exact dyadic relation
`C_p = sum_d q_d C_d` permits the explicit prefix
`d -= q_d p` at a common entrance frame `E`. Pivot and donors must all contain
`E` in their first-use frames. The kernel prefix is an invertible source/helper
program. Globally disjoint pivot and donor sets prevent interacting pivots;
shared donors must follow comparable entrance frames.

A gauge executes the correction `y -= C_h h` at its nonzero entrance frame.
That frame must be contained in the helper's first frame, in every affected
target's first frame, and in every center frame serving those targets. Target
levels and each center's served levels must form actual nested chains. Gauged
helpers are disjoint from both pivots and donors in this construction.

Source/helper mutations never read an output. Reversing all source/helper
mutations at the full frame, including the kernel prefix, restores their entire
arbitrary initial state. The frame-zero preconditioner and the remaining
frame-zero dirty corrections then make the whole word exactly
`(x,y,h) -> (x,y+x,h)`. The independent final auditor checks this equality on
every live column in both forward and inverse-transpose orientations; clean
factory matching alone is not used as the arbitrary-dirt guarantee.

## 6. Frozen entrance choice and paid profile

`gauge_same.py` enumerates every admissible line for a helper in the fixed raw
word, using the actual response, first target frames and center incidences. An
exact dynamic program over partitions of the eight center labels finds 72
compatible line gauges. The selected solution uses the single binary line
spanned by `6` in the raw Hamming labels, before canonical transport. This is a maximum only within this fixed-word, line-gauge
subclass and its retained first-use frames.

With those 72 helpers reserved, `kernel_screen_same.py` searches first frames
and pairwise intersections. Modular rank is only a discovery filter. Every
accepted relation is solved and checked over `Fraction`, and its coefficients
are checked to be dyadic. The frozen choice has six rank-one classes (the
generators below also use raw Hamming labels):

| Binary generator | Donors in class | Pivots |
|---|---:|---:|
| 486 | 36 | 32 |
| 480 | 36 | 32 |
| 414 | 20 | 4 |
| 408 | 20 | 4 |
| 390 | 8 | 4 |
| 384 | 8 | 4 |

There are 128 distinct donors and 80 distinct pivots. This kernel search is
greedy and makes no optimality claim. The frozen `SELECTION.json`, not the
modular screening result, specifies the proof object. There are 152 helpers
of residual width eight and 352 of width nine.

Backward frame coalescing subsequently changes 248 gate-frame annotations,
all in body `B` (none in the entrance prefix);
it preserves every scalar operation, coefficient, order, cut level, and helper
entrance/exit. Each promoted frame is permitted by both operands' actual
future frames. The literal profile, including donor prefix splits, is:

| Rank | Raw same504 | 72 gauges + 80 pivots | Final coalesced word |
|---|---:|---:|---:|
| 1 | 1880 | 2060 | 2028 |
| 2 | 832 | 912 | 752 |
| 3 | 312 | 188 | 156 |
| 4 | 168 | 280 | 392 |
| 5 | 168 | 56 | 56 |
| 6 | 56 | 56 | 56 |
| 7 | 0 | 8 | 8 |
| 8 | 8 | 0 | 0 |

The final rank mass is exactly

$$
6240=2\cdot112\cdot8+152\cdot8+352\cdot9+64.
$$

Coalescing preserves that mass and reduces the natural-log local fee
`sum_r r H_r log(73/r)` by exactly `96 log(64/3)`, approximately
293.785996290393. This is a local accounting statement. The global exponent
requires actual whole owners, spectator/entrance wrappers, all idle and bank
terms, finite compilation charges, and the exact global moment and outer
checks. Those are separate receipts; no local-only estimate is substituted
for them.

## 7. Sources, credits and verification scope

The pinned PR514 package supplies the Hamming geometry, packet modules and
`construct_partial.py`; it in turn credits PR507's partial-own factory and
the PR425/433 scalar ancestry. The scalar elementary-operation routines here
retain those notices. The exact response and word rewriter are the pinned
`e8-complex-gauge-kernel/code/gk_word.py` from DreamingOfClouds, whose original
notice credits Claude Opus 5.5 assistance and whose method credits
PR417/435/434/440 for kernels and PR401/408–416 for gauges. Their substantive
contributions remain part of the construction.

This round's changes are the early own-output schedule, the early retired-row
center basis, the two-half selected packet delivery, the same-partition
variant, the joint frozen entrance selection, and its compatible frame
coalescing, prepared for icekylinx with GPT-6 Astra assistance. The contemporaneous
PR522 by contributor (handle omitted), pinned at
`e9f8075b5212e9bddf361097dbb022dcd052e0bb`, supplies a related rank-sector
coordinate-total principle used for inspiration and comparison. This round
does not import its `56 H_1 + 56 H_5 -> 56 H_6` patch: the early eight retired
rows, earlier center cut and output delivery form a newly emitted scalar
architecture. Its standalone numerical gain is not added to this word. The final package should
retain its broader inherited source/phase/whole-owner notices as well.

The discovery scripts check exact clean identities, selected response
relations and literal local frames. The final independent auditor rebuilds
all dirty compensation and checks all columns, the inverse-transpose action,
dyadic primitives and canonical transport. Phase lowering, physical owners,
wrappers, finite invoices and global assembly are separate explicit checks.
No new universal compiler theorem, Lean certification, or unrestricted
optimality result is asserted by this note.
