# A barrier to diagonal-tensor restriction of the original PR117 word

Jose Manuel (@jmbarrancoml), with substantial OpenAI Codex assistance.

I prove that no nonzero binary row isometry supported on the 24 diagonal
tensor axes gives positive coverage for the original PR117 carrier schedule.
The proof retains the original scalar incidences and commuting projector
frames. It allows constant source gauges, bank concatenation, and catalytic
helpers. I grant free centres and omit further helper work in the lower bound.

For each nonzero column of the isometry, the first-stage helper paths force
at least **317,823,660 extra rank units**. The data can save at most
**32,388,554 units** per odd-norm column. Thus the complete rank mass exceeds
the Fourier-role baseline by at least **285,435,106 units per nonzero column**.
Even the zero-saving moment fails in this model.

I do not improve the multiplication exponent. A new carrier assignment,
internal gate order, frame choice, or projection outside the diagonal tensor
span changes the theorem's premises. The selected PR1094 word has unrestricted
Clifford frames and is not the source of this experiment.

## Frozen source and proposed restriction

Use eumemic's [PR117](https://github.com/CrocSwap/integer-mult-bounds/pull/117),
head `cbb05ce504d571546d9b7794c186a613c659c3bf`, as retained under
`references/three-stage-cover/pr117`. Apply icekylinx's original
`scripts/partial_gauge/match.cpp` and physical assignment from `word.py`.
Do not apply the later lift/select passes. The replay reconstructs 91,770
addition nodes, 8,120 roots, 71,185 matched arcs, 28,705 physical roles,
and 118,451 middle-mixer additions. It checks the exact original matching
receipt; matching optimality is unnecessary for this fixed-word theorem.

Let H=F2^24, with the standard dot product. In H tensor H tensor H, let
Delta span the 24 vectors e_i tensor e_i tensor e_i. Choose a matrix
B in F2^(k by 24) with BB^t=I_k, where 1<=k<=24. Restrict each commuting
quadratic phase by substituting x=B^t y on Delta and setting the other
ambient coordinates to zero. This is an algebra homomorphism on the
commuting phases, so it preserves the completed scalar word. It can change
the native Fourier ranks.

The old full phase restricts to i^wt(B^t y). Its polar matrix is I_k.
Consequently it differs from i^wt(y) by a known Pauli character, which the
endpoint normalization can absorb. The argument concerns all tensor-column
counts because the same substitution applies in each column.

## Proof

### 1. Internal path defects survive completion

For a sequence of binary polar matrices P_0,...,P_l on one physical carrier,
define its defect by

```
d(P) = sum_j rank(P_j + P_(j-1)) - rank(P_l + P_0).
```

Rank subadditivity gives d(P)>=0. Replace disjoint retained segments of a
complete carrier path by their net edges. This removes exactly the sum of
their defects from the rank bill. A Fourier-normalized carrier still has
net polar change I_k, so its original bill is at least k plus those defects.
An identity-restored catalytic carrier has bill at least the defects.

A constant gauge shift preserves the differences inside a segment. Bank
joins concatenate complete segments. A carrier with a constant retained
path has zero defect and may leave the Fourier-normalizing inventory.
These operations therefore cannot erase the lower bound. An interpretation
reset inside an unfinished scalar word would change the premise; a reset
between completed units must still pay the accumulated endpoint correction.

I use one ordered segment per physical helper role in each first-stage
invocation. I keep its source-copy incidence, its middle-M incidences and
its ordinary output-cap incidences. I omit early readouts, cleanup and
centre excursions. If omitted gates lie between two retained incidences,
rank subadditivity bounds their total cost by the direct retained edge.
Different first-stage invocations and roles give disjoint segments. Multiple
uses of one role belong to its one ordered list, so no transition receives
two charges.

### 2. A 24-coordinate exact census

For a local node frame U, write P_U for its orthogonal projector. A type-2
coordinate frame has diagonal equal to its coordinate cover. A type-1
common-pair frame has an orthonormal triple basis, so its diagonal is the
XOR of those triple vectors. The verifier reconstructs both from the pinned
positive DAG, without reading a stored frame census.

At coordinate i, each retained path becomes a bit sequence. Its defect is
the number of bit changes minus the XOR of its first and last bits. Summing
over the 28,705 roles gives, in coordinate order 0 through 23:

```
6048 5982 6046 6176 6046 6084 6026 6048
6004 6082 6048 6152 6112 6134 6114 6046
6112 6046 6114 6042 6116 6046 6114 6046
```

In particular, D_i>=5982. The replay distinguishes the matcher's node-order
use lists from the physical compiler's rank-order use lists. Substituting
one order for the other changes the physical paths.

### 3. First-stage helper cost after an arbitrary diagonal-span isometry

Write c_i for column i of B, and S={i:c_i!=0}. A first-stage invocation has
two external triples A,C. If A intersect C={i}, its restricted node polar
matrix is

```
(P_U)_(i,i) * c_i c_i^t.
```

For i in S, the outer product has rank one, including when c_i has even
norm. The entire local singleton defect is therefore D_i. There are

```
binom(23,2) binom(21,2) = 53,130
```

ordered external pairs with intersection exactly {i}. These classes are
disjoint across i. The first stage alone contributes helper defect at least

```
53,130 sum_(i in S) D_i >= 317,823,660 |S|.
```

This calculation uses no inverse-stage frame assumption.

### 4. Upper bound on the entire data gain

For a data position indexed by three triples, let s be the indicator of
their common intersection and let w=Bs. Its original norm-one tensor line
has weight 27. Its restricted source phase is therefore
3 parity(w dot y) modulo four, whose square is the Pauli translation X_w.
Apply the retained source/target Pauli corrections and swap/sign
normalization. The X path has endpoint phases T_s to T_full; the Y path
has endpoints I to T_full T_s^(-1). Both endpoint polar differences are
I_k+ww^t. These are the retained data boundaries in
`notes/complex-compression.tex` and its original tensor composition.

Their combined paid rank is at least 2 rank(I_k+ww^t). Over F2,
rank(I_k+ww^t)=k-(w dot w), where the last quantity is a bit interpreted as
an integer. Thus the pair saves at most two units, and it saves zero unless
w has odd norm. This endpoint bound allows any refinement of the paid
data paths.

Let O={i:c_i dot c_i=1}. If w has odd norm, the common intersection contains
at least one i in O. Each point belongs to binom(23,2)^3 ordered data
positions. A union bound gives

```
data gain <= 2 |O| binom(23,2)^3
          = 32,388,554 |O|
          <= 32,388,554 |S|.
```

### 5. Complete comparison

Let W count the Fourier-normalized roles, including the data; identity
catalysts do not increase W. Combining the endpoint bound with the helper
defects gives total paid rank at least

```
k W + (317,823,660 - 32,388,554) |S|
= k W + 285,435,106 |S| > k W.
```

The isometry has positive row rank, so S is nonempty. For a>=0 and children
of rank 0<r<=k, (r/k)^(1-a)>=r/k. The normalized moment cannot fall below
one. Proper-child lowering, adapters, precision and the inherited
denominator-21 arithmetic can only add obligations; the lower bound has
already granted their favorable omission.

## Reproduce and evidence limits

From the repository root:

```sh
python3 scripts/research_package.py --package research/diagonal-tensor-projection-barrier --check-only
python3.12 scripts/research_package.py --package research/diagonal-tensor-projection-barrier
```

The standard-library verifier regenerates the matching and physical paths;
it requires neither a C++ compiler nor a bundled matching artifact. It uses
explicit exceptions under Python optimization. Seven corruptions must fail:
wrong denominator, overlapping summands, a wrong disjoint root, a missing
match, a repeated donor, a repeated use, and an omitted internal incidence.
Small exhaustive controls check data endpoint ranks and the isometry's
Pauli correction. The universal quantification over B follows from the
written proof, rather than an enumeration of all isometries.

I cross-checked the coordinate census with a separate full-projector replay
and a separate read-only agent reconstruction. These checks involved Codex;
I claim no independent human review or formal proof verification.

## Open next questions

- A projection outside Delta could avoid these singleton defects. First
  derive its endpoint and helper bill on a small off-diagonal support. No
  favorable complete candidate came from this investigation.
- A new internal schedule or producer could reduce the coordinate defects.
  First replay its actual carrier incidences and price all boundary changes.
  The present theorem supplies no lower bound for those changed paths.

See [TASK.json](TASK.json) for the scope change and structured next steps.

## Credit

Eumemic supplied the PR117 DAG and producer replay, with Claude assistance.
Icekylinx supplied the retained compatible matcher and physical compiler,
with GPT-6 Astra/Codex assistance. Rohan Arun supplied prior weighted carrier
matching. I retain the PR104/deferred-word ancestry and the original notices;
see [NOTICE.md](NOTICE.md) and [SOURCES.json](SOURCES.json).

I contribute the scoped diagonal-span obstruction and this replay. New work
uses Apache-2.0. I leave frozen sources and the selected frontier unchanged.
