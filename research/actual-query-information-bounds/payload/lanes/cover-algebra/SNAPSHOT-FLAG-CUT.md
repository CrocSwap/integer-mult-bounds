# A shared cache-network cut bound

The retained snapshot model needs at least 42 units of native rank to
produce all eight FULL centre queries. This bound permits scalar sharing
between outputs. It does not prove the desired bound of 64, and it does
not give a construction below 64.

The model is the same-content monotone frame network in
`CHRONOLOGICAL-CACHE-PATHS.md`. It grants every recorded snapshot time,
scalar COPY and ADD operations, arbitrary owned cache storage, and final
X and helper cleanup. The core is unchanged. A transition from frame
`U` to a containing frame `V` costs at least `dim(V)-dim(U)` per field.
The proof does not cover logical address re-gauging between frames.

## The flag cuts

Choose an ordered binary basis `v_0,...,v_8` of the nine-dimensional
address space. Express each frame in this basis, and use row echelon
form with the lowest nonzero coordinate as leading coordinate. Let
`P(U)` be the set of leading positions of `U`.

Every nonzero vector in `U` has a leading position in `P(U)`, and every
position in `P(U)` occurs. Therefore

\[
U\subseteq V\quad\Longrightarrow\quad P(U)\subseteq P(V),
\qquad |P(U)|=\dim U. \tag{1}
\]

For each position `i`, form the cut `Omega_i` of all network nodes whose
frame has `i` in its pivot set. A transition `U -> V` enters exactly
`dim(V)-dim(U)` such cuts. An ADD or COPY at one frame enters no cut.

Give each port `q_p` its dual coordinates

\[
b_j(p)=q_p\cdot v_j.
\]

Let `E_i` contain the ports whose largest nonzero dual-coordinate index
is `i`. These nine sets partition all 112 ports.

If `i` is a pivot of `U`, choose a vector of `U` whose leading coordinate
is `i`. For `p` in `E_i`, its dot product with that vector is one. The
exact snapshot support law therefore makes every observation in
`Omega_i` zero on the valid input family

\[
x=Jy,\qquad h=c=0,\qquad \operatorname{supp}y\subseteq E_i. \tag{2}
\]

The completed X and restored helper rows are also zero. The eight
required FULL queries on (2) have rank

\[
r_i=\operatorname{rank}R_{E_i}. \tag{3}
\]

Every dependence on (2) that reaches a FULL output must enter
`Omega_i` across a native cache edge. A field on such an edge can carry
at most one full field dimension of linear information. Thus the sum
of incoming field capacities is at least `r_i`. This is the cut
inequality from the general row-flow model. It is valid with arbitrary
fanout, scalar combinations, cancellations, and reuse inside the cut.

Sum the nine inequalities. By (1), every edge is charged at most its
native-rank cost. Hence

\[
\boxed{\text{native rank}\ \geq\sum_{i=0}^8\operatorname{rank}R_{E_i}.} \tag{4}
\]

The argument holds for full native payload arrays. If one field has
dimension `d`, the demand in (3) is `r_i d` and an entering field has
capacity at most `d`. The factor cancels. No constant-array restriction
or independent-output-tree assumption is used.

## The exact witness

The basis used in the certificate is

```text
[243, 249, 311, 132, 131, 489, 442, 405, 178]
```

The exact rational shell ranks are

```text
[0, 1, 1, 2, 8, 6, 8, 8, 8]
```

Their sum is 42. `check_snapshot_flag_cut.py` checks the binary basis,
all nine rational ranks, all 23,279 frame/shell separation cases, and
the cut charge on all 2,880 distinct retained native edges. It pins the
independent exact snapshot support review. It imports no source
producer.

Run:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/cover-algebra/check_snapshot_flag_cut.py
```

The result is `PASS_SHARED_MONOTONE_CACHE_DAG_LOWER_BOUND_42`, saved in
`SNAPSHOT-FLAG-CUT.json`. A bounded search of 20,000 binary bases found
this witness. The search is not an optimality proof. The exact checker
does not rely on the search result beyond the displayed basis.

The single-tree bound of eight still does not add across shared output
trees. Equation (4) is a separate valid shared-network bound. A stronger
cut family or a positive network is required to resolve the interval
from 42 through 63.
