# Exact bounded joint-schedule argument

## Fixed input

Fix one orientation of the PR1263 static word. Let its chronological scalar
ADD events be the reference stream. All static gauges, original SCALEs, frame
events, recursive calls, copies, centers, and cleanup remain fixed. The only
variables are the additional integer dyadic offsets `u_j` for L253 and `v_j`
for L254 immediately before each ADD in the union of their supports. Each
offset lies in `[-4,4]`, and both offsets start and finish at zero.

There are 96 L253 incident ADDs, 120 L254 incident ADDs, and one common ADD,
event 19427. The ordered union therefore has 215 stages.

## Map preservation and complete cost

At a stage with offsets `(u,v)`, interpret the two helpers as
`L253 = 2^u x253` and `L254 = 2^v x254`, where `x253` and `x254` are the values
in the frozen static word. If an affected ADD has target/source signs
`(s253,s254)` in `{−1,0,1}²`, replace its exact dyadic coefficient `q` by

```text
q' = q · 2^(s253*u + s254*v).
```

Before each changed offset, insert the corresponding SCALE at that event's
frame. At the end, scale each helper back by its final offset. These updates
preserve each ADD equation exactly. The offsets begin and end at zero, so
arbitrary incoming helper values are restored. Every nonscalar event remains
unchanged; the full replay checks all 704 data/helper columns and eight private
center columns in both directions.

For an exact dyadic coefficient `q = ±p·2^e` with odd positive `p`, the
retained PR696 lowerer charges

```text
c(q) = 1 + bit_length(p) + popcount(p) + |e| − [p = 1 and e = 0].
```

The real-component cost difference at stage `j` is therefore

```text
c(q_j · 2^(s253*u_j + s254*v_j)) − c(q_j)
  + |u_j-u_(j-1)| + |v_j-v_(j-1)|.
```

The terminal cost adds `|u_last| + |v_last|`. This counts coefficient work at
every incident ADD and all entry, intermediate, and restoration scales. The
static word already includes all original scalar work; subtracting its local
coefficient prices leaves exactly the invoice delta above. At a shared ADD the
coefficient is charged once using the sum of both offsets.

## Dynamic program

For each union ADD, the verifier enumerates every state in `[-4,4]^2` and
applies the recurrence

```text
node_j(u,v) = c(q_j · 2^(s253*u + s254*v)) − c(q_j)
D_j(u,v) = node_j(u,v) +
           min_(u',v') [D_(j-1)(u',v') + |u-u'| + |v-v'|],
```

starting from `D_0(0,0)=0`, then adds terminal restoration and minimizes over
all last states. Every transition and node charge is an integer derived from
the exact rational coefficient. This proves the minimum over the stated finite
box.

If a helper is absent from a union ADD, its offset is held fixed at that stage.
Any change there can be postponed to its next incident ADD with the same
coefficient sequence and no greater transition cost. This normal form retains
an optimum and removes irrelevant gauge changes between that helper's own ADDs.

The recurrence does not establish an optimum outside `[-4,4]^2`. The complete
replay separately certifies the emitted improving word, which is sufficient
for the finite construction result.
