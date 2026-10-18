# Asynchronous delivery of the P104 frame-pair decoder

This is a finite geometric result and a written scheduling proof. It is not
an implementation of a supplier or a formal proof of the multiplication
theorem.

## 1. Decoder family and exact finite facts

Use PR717's label space `V=F2^9`. A root line `r` has label `u_r`, with

```text
B(u_r,u_s) = (<r,s> + 1) mod 2.
```

PR968 gives 896 admissible frames `F1` disjoint from a fixed coordinate
frame `F0`. Each pair has eight mixed dual bases. A term has row normal
`a_k` and column normal `b_k`. Both are punctured roots. Their inner
product is odd, and `<a_k,b_j>=0` for `k!=j`. There are 104 live targets.
Define

```text
S_t = {k : <r_t,a_k> != 0},    E_k = span(u_a_k),
H_t = u_t^perp,                Q_k = u_b_k^perp.
```

The source support spans `Q_k`. The reader support spans `u_a_k^perp`.
The rank-seven COPY has endpoint `E_k`, since `E_k` is contained in `Q_k`.
The eight labels `u_a_k` are independent. A survivor line is in a target
sink exactly when that target reads the term:

```text
E_k subset H_t  iff  k in S_t.                                  (1)
```

`verify.py` checks these facts for all 7168 decoders. It also checks the
2025-frame orbit under eight root reflections. Thus the result applies
to every choice of the first frame, after a root isometry. Reflections
can change representative signs. They preserve zero products and the
binary pairing; no invariance of signed representatives is assumed.
The pairing matrix has rank nine. A reflection permutes its rows and
columns together. The column permutation is a linear isomorphism on
the row span, which is the label space. Thus the reflection also
preserves label ranks, subspace inclusion, and frame distances.

The new finite fact is the full target-support family. Make a graph on
the eight terms, with an edge for each two-term target support. This
graph is a cube. The 104 supports are exactly:

- its 12 edges;
- its 24 induced trees on three vertices;
- its 32 induced trees on four vertices;
- its 24 induced trees on five vertices, which are paths;
- the 12 complements of edges.

Every support occurs once. This statement is checked for all 7168
members. `independent.py` constructs the roots again and enumerates all
partitions of each frame pair, without importing the PR968 enumerator.
It checks the same result by graph isomorphisms.

Let `F_K={S_t intersect K : t live}`, with the empty set removed. Its
order is set inclusion. The exact widths needed here are

```text
width(F_all) = 32,
width(F_all_minus_k) = 26  for every k.                          (2)
```

`CERTIFICATE.json` contains an antichain and a chain cover of equal size
for each of these nine posets. Both checkers validate all memberships,
all comparisons, and complete cover of each poset. The four-term supports
already give the first lower bound. A chain cover proves that this bound
cannot be increased by the terminal-support argument alone. A chain cover
is not a legal decoder schedule.

## 2. Admitted delivery interface

The theorem below concerns this interface.

1. Each term first has its rank-seven COPY at `E_k`. A delivery carrier
   is a continuous register path assigned to one term. Its data are that
   term, possibly scaled, plus dirty input that the full word must remove.
   The term assignment stays fixed on the path. Carriers do not hold
   linear combinations of different decoder terms.
2. A carrier receives the term at a frame containing `E_k`. Transfers and
   target reads use the same frame on both registers. Each nonzero term
   is delivered to each required target. Target orders can differ.
3. A target starts at zero and ends at `H_t`. A dirty carrier starts at
   zero and ends at `V`. A clean carrier starts at `E_k`; its path can
   end after its last use with no endpoint constraint. Extra frame
   directions and arbitrary frame moves are allowed. The complete
   frame path is charged. Termination supplies no later read or reset.
4. A change from frame `U` to frame `W` costs
   `d(U,W)=dim U+dim W-2 dim(U intersect W)`. Each carrier path has its
   own charge. Renaming a register does not start a new free path.
5. `P` counts all continuous delivery paths, including the original
   center copies. A new allocation or reconstruction starts another
   path. It does not count as reuse of a previous path at a free frame.
   Forked copies count as different paths. The bound can give their
   allocation and restoration other than frame moves a zero price.

This interface permits asynchronous target orders, frame padding,
repeated downward moves on both carriers and targets, and loss of a
survivor line. It is larger than PR1071's fixed-decoder, monotone-carrier,
single-cut or common-order classes. It does not permit arbitrary changes
of linear basis between terms, a direct different-endpoint query COPY,
or a register reset with no charge. The path count is not a bound on peak
simultaneous memory when paths can be allocated in sequence.

Define `L` as follows. For each dirty carrier, subtract nine from its
complete frame-move rank. For each target, subtract eight. For each clean
carrier, count all frame moves after its rank-seven seed. Sum the results.
This is the excess rank over the monotone endpoint costs, together with
all clean-carrier moves. It does not include the original eight seeds.

Call a term *erased* if some carrier for it loses `E_k` in a frame move
after receiving its seed and before its path ends. Mere termination
does not erase a survivor for this definition. Let `q` be the number
of erased terms, `K` the remaining terms,
and `P_K` the number of paths assigned to `K`.

## 3. Dimension accounting

For a frame step put

```text
down(U,W) = dim U - dim(U intersect W).
```

Then

```text
d(U,W) = dim W - dim U + 2 down(U,W).                       (3)
```

On a dirty carrier or target, the dimension differences cancel across
the complete path. Its excess rank is therefore exactly twice the sum
of its downward dimensions. In particular, every nonmonotone target
costs at least two excess ranks.

If two frames are incomparable by inclusion, any path from the first
to the second has distance at least two. It must lose a vector of the
first frame and gain a vector of the second. A dirty path that visits
`j` pairwise incomparable frames has at least `j-1` downward dimensions.
A clean path that visits them pays at least `2(j-1)` moves between visits.
These bounds allow intermediate frames of any dimension.

Every erased term costs at least one unit of `L`. For a clean carrier,
the first loss of `E_k` is a positive-rank move. For a dirty carrier it
is a downward move and costs at least two excess ranks. Different terms
use different paths, so these charges do not coincide. This is one
reason the fixed-term condition in the interface is necessary.

## 4. Terminal-read theorem

**Theorem.** Under the interface in section 2,

```text
L >= q + 2 max(0, width(F_K) - P_K).                         (4)
```

For `q>=2`, the weaker statement `L>=q` is enough for the price screen.
For `q=0,1`, equation (2) supplies the exact width in (4).

*Proof.* Select target witnesses for an antichain of size `w=width(F_K)`.
Let `z` of these targets have a nonmonotone path. They contribute at
least `2z` to `L` by (3). Remove these witnesses from the argument.

For each remaining target `t`, take its last read of a term in `K`.
The target path is monotone. Its frame `U_t` contains each survivor it
has already read, and all of `S_t intersect K` has now been read. Thus

```text
span{u_a_k : k in S_t intersect K} subset U_t subset H_t.     (5)
```

For two different antichain supports, choose a term in each set
but not the other. Equation (1) and (5) give a vector in each of the two
frames that is absent from the other. Therefore the frames are
incomparable. Extra directions in the frames do not change this fact.

Assign each last read to its physical carrier path. A path assigned `j`
of the remaining witnesses pays at least `2(j-1)` excess ranks, by
section 3. Summing over at most `P_K` paths gives
`2 max(0,w-z-P_K)`. These paths belong to `K`. Their charges are separate
from the erased-term charges and from target charges. Consequently

```text
L >= q + 2z + 2 max(0,w-z-P_K)
  >= q + 2 max(0,w-P_K).
```

This proves (4). No global order of centers or targets is used.

**Consequences.** Every term has at least one path, so `P_K<=P-q`.

- With no erased term, `L>=2 max(0,32-P)`. A monotone delivery needs at
  least 32 paths, or 24 paths beyond the eight seeds.
- With one erased term, `L>=1+2 max(0,27-P)`. A delivery with `L<=1`
  needs at least 27 paths, of which at least 26 carry retained terms.
- With two or more erased terms, `L>=2` at any path count.
- Hence every admitted delivery with `P<=26` has `L>=2`. With no erased
  term, the same conclusion holds through `P=31`.

The theorem gives necessary conditions. It does not produce a schedule
at 27 or 32 paths. It also does not prove that these path counts are the
optima for all reads, source access, or cleanup.

## 5. Pinned and refreshed price screens

The experiment base selects PR942/T37. Main changed to PR1042/T16 during
this run. Both input records are retained as exact bytes. The refreshed
record is from `ba82555c64e1879e4b7decce28186f208fcb8262`.

| Selected record | Complex b | Integer kappa |
|---|---|---|
| PR942 at the experiment base | 0.001664727258740678855772 | 0.001661960547713947 |
| PR1042 at the refresh commit | 0.001674989015937672328468 | 0.001672188119205421 |

Both retain bit `c=0.001733427039589844234749`.

Use PR968's stated P104 knob model. In each call it replaces eight
rank-eight COPY children by rank-seven children. It removes eight modal
source and target paths and the associated idle children. The same
formula applies to both recorded geometries. The two pinned moment
engines check the following prices.

| Geometry | Calls | P104 W | Base deficit | P104 deficit |
|---|---:|---:|---:|---:|
| PR942/T37, m=73 | 333 | 30784 | 11840 | 12136 |
| PR1042/T16, m=73 | 144 | 13312 | 5120 | 5248 |

At each record's selected `b`, the favorable P104 moment is below one.
One extra rank per call, at the lower price of one per rank unit, leaves
it below one. Two extra ranks per call give a positive residual:

```text
T37: Phi_P104(b) + 2*333/(73*30784) - 1 > 0.0000134226900304,
T16: Phi_P104(b) + 2*144/(73*13312) - 1 > 0.0000124883855037.  (6)
```

The certificate gives rational outward intervals from both engines.
This relaxation is favorable: a real child of rank `r<73` costs
`r*(73/r)^b > r`. Helper provision, copies, scans, phase repair, and
restoration other than the specified rank are all given zero price in
(6). Literal additions of two rank-one children give these roots:

| Geometry | P104 knobs | P104 knobs plus two H1 children per call |
|---|---|---|
| PR942/T37 | 0.001756471346539970492513 | 0.001659687316130507441362 |
| PR1042/T16 | 0.001767619679132010864348 | 0.001670217638307139184594 |

Both last-column values are below their selected comparators.

**Cost contract.** Equation (6) rules out a gain only if the remaining
paid moment is at least the corresponding P104 knob profile at the
selected `b`, and the excess rank in (4) is additional to that profile.
In particular, it applies when that profile is retained and the extra
moves are added. The geometric theorem alone does not prove this cost
contract for every new word. A changed target path, source schedule,
helper bank, host, phase frame, or child grouping can change other
prices. Such a proposed saving needs its own complete invoice.

Thus the result closes the stated small-path delivery class under this
explicit price contract, on both recorded frontiers. It does not close
all P104 suppliers. Larger path banks, term mixing, different query
endpoints, and savings in other parts of a complete word remain open.
The bit cap remains a separate constraint. No new kappa or practical
speedup is claimed.
