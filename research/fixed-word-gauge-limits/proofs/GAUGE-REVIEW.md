# Independent review of the wire-gauge obstruction

The boundary-paired certificate is valid for all 16 common odd centre lines.
Its exact minimum total-rank change is zero. If at least one centre edge
has different gauge bits at its two ends, the minimum is 13.

The review also proves two stronger results. Every cut of total-rank cost
zero has one common bit on all 1,971 components that meet a native edge.
Thus its native profile is unchanged. Further, no gauge in this family
reduces any increasing concave function of native rank that is zero at
rank zero. This includes the child moment `sum r^(1-b)` for `0 <= b <= 1`,
with zero-rank children omitted at `b=1`.

These statements apply to the pinned local words in both orientations.
They keep the scalar schedule and the native edge positions fixed. They
permit separate bits on every wire segment, subject only to scalar access
and the exact old endpoint. They do not exclude a different scalar program,
a larger gauge set, joint child compression, or a different controller.

## Source and independent checks

The source commit is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
The archive is `research/community-frontier1042-audit/selected-replay.tar.gz`,
with SHA-256
`22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
The reviewer reads only these archive members:

- `slots/local/CANONICAL-WORD.json.gz`, compressed SHA-256
  `16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219`.
- `slots/local/LOCAL-PROGRAMS.json.gz`, compressed SHA-256
  `241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a`.

`review_wire_gauge.py` does not import the producer's graph, geometry,
optimizer, or certificate checker. It uses exact rational scalar replay,
binary row elimination, a separate segment construction, and direct
integer flow/cut checks. The tests remain active under `python -I -O -B`.
The source scalar words have the stated endpoint on all 712 input columns,
including arbitrary helper and private inputs. Each private output is zero.

The segment construction gives 5,784 segments and 1,979 components after
the scalar and boundary equalities. There are 5,064 native events: 3,486
climbs, eight centre traversals, 1,090 adapters, and 480 residual adapters.
Thus all 1,570 old rank-zero wrappers are charged if a gauge changes across
them. There is no fixed external bit. The eight isolated components are
the final cleared private values.

The forward and backward scalar access graphs are isomorphic. The reviewer
names each persistent segment by its register and native-event count. It
names each live private segment by its centre and its high or low frame.
The two words have the same undirected scalar accesses and persistent
native edges under these names. Each centre edge has the reverse direction.
This is checked from the two complete original words. The backward common
frame is `D_U=T_U F^-1`. Since `C_a` commutes with the full frame `F`,
`D_U C_a=(T_U C_a)F^-1`. Thus both changed inverse-image labels have the
same outer `F` image, and the forward native ranks apply. Edge inversion
also preserves rank. The same cost certificate therefore applies to both
orientations for the common-line gauges.

## Boundary theorem

The theorem in `root/BOUNDARY-GAUGE.md` is correct. Give a segment the exact
frame `T_v`, including phase. Its physical value is `T_v z_v`. Replace that
frame by `T_v G_v` and each native edge by

    T_v G_v G_u^-1 T_u^-1.

For an ADD or COPY, the gauges on its live operands must be equal. The old
frames on those operands are equal at each scalar access. Therefore the
same scalar operation is legal in the new frames. A CLEAR gives a new zero
value and imposes no relation to the old gauge. Induction over the program
gives the physical endpoint

    diag(T_out) diag(G_out) P diag(G_in)^-1 diag(T_in)^-1.

Invertibility of the outer frames gives the necessary and sufficient
condition `diag(G_out) P = P diag(G_in)`. No commuting-frame assumption is
used. For a forward pair, the three nonzero blocks of `P` force the four
input/output gauges of `x_p,y_p` to be equal. The backward pair gives the
same relation. A helper forces equality of its input and output gauges.
The private rows and columns of `P` are zero, so they impose no boundary
relation. This proves the exact boundary unions used by the graph.

The identity holds at every tensor power and includes global phases. It
also preserves the full physical residual on every arbitrary helper:
`T_out G (T_in G)^-1 = T_out T_in^-1`. The review does not emit or admit a
changed native circuit. Rank bounds do not require such an emission.

## Native ranks

Write a binary Pauli label as `(x,z)` in `F_2^9 x F_2^9`. The inverse image
of the diagonal Pauli space under the canonical frame of a subspace `E` is

    L_E = {(u,u+w) : u in E, w in E^perp}.

The rank of the relative native operator between frames `E,F` is
`dim(L_E+L_F)-9`. The independent reviewer constructs these spaces by binary
row elimination. It checks each distinct native edge and its old rank.
Left monomial adapters leave this inverse-image space unchanged. Thus the
same formula also applies before and after each old rank-zero wrapper.

The symplectic action of `C_a` is `(x,z) -> (x+a(a dot z),z)`. Its inverse
has the same binary action. The reviewer applies this action to either or
both edge ends and recomputes the rank. For each of the 16 odd common lines,
all edges have the following exact price. If their old nested frames are
`E subset F`, a crossing costs minus one exactly when
`a in F intersect E^perp`; otherwise it costs plus one. Equal endpoint bits
do not change the rank. A wrapper always costs plus one when crossed:
its Lagrangian could be invariant only if `(a,0)` belongs to it, which would
require `a in E intersect E^perp`. An odd vector cannot satisfy that condition.

The lines are
`128,158,173,179,203,213,230,248,256,286,301,307,331,341,358,376`.
The reviewer derives this complete list from the original eight centre
hyperplanes. The signed energy is the sum of the prices of all crossed
native edges. Parallel edges are combined only after each is priced.

## Integer lower bounds and zero-cost rigidity

Each certificate gives a vertex cover of all negative edges. Every binary
assignment to this cover is listed. After it is fixed, all edges between
free vertices have nonnegative weight. A fixed/free edge gives a unary
cost. Subtract the smaller unary value as a constant and use its difference
as a source or sink capacity. The result is an ordinary directed cut
network with nonnegative integer capacities.

For every case, the reviewer checks integral flow, both directed capacity
bounds, flow conservation, and the source and sink values. It separately
computes the displayed cut. Its capacity equals the feasible flow value.
The resulting lower bound is therefore exact. It agrees with the direct
sum over all crossed native edges, the child profile, and the change by
event kind. All 3,384 listed cases are checked. The forced cases cover each
of eight centre edges and both assignments to its two ends. Taking their
minimum means that at least one centre traversal changes. It does not mean
that all eight change at once.

For each line, only the all-zero and all-one cover branches attain cost
zero. In the former branch, every free component incident to a native edge
is reachable from the source in the residual network. In the latter, each
such component can reach the sink. Every minimum cut must retain the first
set on the source side and the second set on the sink side. Combined with
the fixed cover bits, this forces all 1,971 live components to one common
bit. The only free components are the eight isolated cleared outputs.
This proves the claim for every optimal cut, not only the cuts saved by
the optimizer.

## All increasing concave rank costs

The separate certificate `THRESHOLD-GAUGE-COMMON.json.gz` treats
`f_k(r)=min(r,k)` for `k=1,...,8`. It has 800 integer flow/cut cases. Its
generator uses SciPy's integer maximum-flow implementation. The separate
standard-library reviewer reconstructs every changed rank from the source
Lagrangians and checks each integer witness directly. It does not rely on
the optimizer's status or on floating-point arithmetic. Every minimum is
zero. All old and changed ranks are between zero and eight.

Let `f(0)=0` and let `d_j=f(j)-f(j-1)` satisfy
`d_1 >= ... >= d_8 >= 0`. For integer `0 <= r <= 8`,

    f(r) = d_8 min(r,8) + sum_(k=1)^7 (d_k-d_(k+1)) min(r,k).

Each coefficient is nonnegative. Each threshold sum has nonnegative
change for every admissible gauge. Thus the same is true of `sum f(r)`.
The function `r^(1-b)` has these properties for `0 <= b < 1`. At `b=1`,
take `f(0)=0` and `f(r)=1` for positive ranks. This is the count of paid
children and is also `min(r,1)` on the integer ranks.

The standard local child moment is a fixed positive multiple of this sum.
Thus this gauge family cannot improve that moment with the old scalar
program and native edge positions. This conclusion is stronger than the
total-rank minimum alone. It does not claim a general lower bound for
centre information or a new value of kappa.

## Compound gauges and the four-state family

The review also checks `I,G` for `G=C_128 C_256` and for the full canonical
frame `G=T_415`. A direct binary calculation replaces the producer's
Clifford compiler. Complete the printed frame basis `u_1,...,u_r` by the
standard unit vectors, in order. Let `d_j` be the dual basis. The canonical
frame is a product of commuting symplectic transvections with vectors
`(u_j,u_j+d_j)`. This follows by conjugating each axis `C` by the canonical
coordinate map and its diagonal quadratic factor. The reviewer constructs
the dual basis by exhaustive binary inner products and applies these
transvections directly. It checks all original, crossed, and equal-bit
native ranks.

Both compound binary families have rank minimum zero. Every rank-zero cut
is again constant on all native components. The product `C_128 C_256` has
minimum zero for every capped-rank cost through cap nine, so the increasing
concave-cost theorem also applies to this family.

For `T_415`, the cap-one minimum is minus one. All other capped-rank minima
are zero. The count-saving cut changes only component 608 from a constant
gauge. Seven incoming edges keep rank four. One rank-eight centre becomes
rank zero. Seven outgoing rank-one edges become rank nine. The full rank
change is 48. Its child-moment change is

    7*9^(1-b) - 7 - 8^(1-b).

Thus the all-concave obstruction is false for this full-frame family. The
count-saving example is a shift of native work to seven later transitions.
It is not a cheap centre construction for the selected supplier.

This example gives a general cost formula. Suppose a scalar-access component
has one frame `E`, of dimension `e`, and satisfies the boundary equalities.
Assign it `G=T_E^-1` and keep the other gauges equal to the identity. The
new frame on the component is exactly zero. Count only native edges that
cross the component boundary. An edge from `A subset E` has
old rank `e-dim(A)` and new rank `dim(A)`. An edge to `B superset E` has
old rank `dim(B)-e` and new rank `dim(B)`. A centre edge to frame zero
disappears. The total rank change is therefore

    sum_entries (2*dim(A)-e) + e*number_of_exits - e*number_of_centres.

This formula includes exact phases if the new native edges use the exact
frame products. It preserves arbitrary helper values by the boundary
theorem. The inverse gauge has the same binary ranks as `T_E` for the
canonical frame, so it has the same price in the example. The formula shows
which change to the scalar program could matter: reduce the number of live
exits, or use enough entry frames of dimension less than `e/2`. The old
component has neither property. This is a conditional design criterion, not
an implemented improvement.

There is nevertheless an exact obstruction for `0 <= b <= 2/5`. Each
native rank change in this binary family is even. Every nonconstant native
cut therefore has total-rank change at least two. The threshold certificate
gives change at least minus one for `min(r,1)` and at least zero for every
other threshold. Put `a=1-b` and apply the threshold formula through rank
nine. It gives

    Delta sum r^a >= 2*(9^a-8^a) - (2-2^a).

For `a >= 3/5`, the first term has the bound
`2*(9^a-8^a) >= 2*a*9^(a-1) > 24/49`. Also `2-2^a < 97/200`.
The strict rational bounds follow from
`49^5 > 81*20^5` and `303^5 < 8*200^5`. Thus every such cut has moment
increase greater than `47/9800`. The constant cuts keep the profile.
No floating-point estimate is used in this conclusion.

For the four gauges `I,C_128,C_256,C_128 C_256`, the reviewer checks every
entry of the native four-by-four rank table. Each depends only on the XOR
of the two states. It checks the two separable lower graphs edge by edge,
then checks their integral flow/cut witnesses. Both lower minima are zero,
and both zero cuts have the same rigidity as before. Hence every zero-rank
four-state assignment is constant on the native components.

For a capped cost, write its three nonzero XOR-state changes as `d_1,d_2,d_3`.
Put `m=max(0,d_1+d_2-d_3)`. The two integer weights
`2d_1-m` and `2d_2-m` give a separable lower bound for twice the true cost.
This is checked on all four states of every original native edge. The
threshold certificate gives zero as the minimum of both lower graphs for
all caps one through nine. The constant assignment attains zero in the true
problem. Thus the four-state family has no improvement for any increasing
concave rank cost. The exploratory solver's status and bound are not used.

The product gauges commute exactly with `F`, so their conclusions hold in
both original orientations with the same gauge. The frame `T_415` does not
commute with `F`. Its forward certificate applies to the backward gauge
`F T_415 F^-1` in the backward frames `D_U=T_U F^-1`. It does not prove the
same claim for the identical `T_415` in those backward coordinates.

## Validation boundary

The source-derived checks, the flow/cut checks, and the threshold witnesses
ran locally. No selected cold replay, complete recursive repricing, changed
native lowering, or new hosting construction ran in this lane. No PR was
created. The source-domain lane produced the original gauge search and
certificates. This lane supplied an independent review and the threshold
extension. This work used OpenAI Codex assistance.
