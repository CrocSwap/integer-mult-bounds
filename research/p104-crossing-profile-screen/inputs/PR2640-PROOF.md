# A dimension cut for the monotone correction network

## 1. Exact model

Let V be the nine-dimensional binary frame space. The 104 immutable original
sources have initial lines L_s and the frozen increasing X_s frame paths.
Original targets have the frozen increasing Y_t paths, beginning at ZERO and
ending at distinct hyperplanes H_t. Only their additive correction writes are
part of the new network. There are no reads from targets, writes to sources,
or reads/writes of original helper/private roles by the correction network.
The inherited channel may run in parallel, but is not a correction dependency
edge. Its known G/2 contribution is subtracted at the logical boundary.

A new helper lifetime begins at ZERO with an arbitrary source-independent dirty
logical value, follows a finite strictly increasing frame path, and ends at
FULL. It may make arbitrarily many common-frame rational ADDs. It is restored
at the end. Physical helpers may be reused, but each reset starts another
counted lifetime. Source-dependent initialization, descents and cross-frame
ADDs are not operations of this model. All scalar coefficients are fixed,
independent of input values. No bound on the number of ADDs is required.

The intended added source-to-target matrix is C=I-G/2. Reconstructing the E8
roots and the puncture gives 4,992 nonzero entries, all +/-1/2. Each such pair
(s,t) obeys L_s subset H_t. The literal source word also verifies that original
sources have no ADD writes and original targets have no ADD reads.

All frame statements are invariant under binary basis changes. To count target
hyperplanes, let h_t be the unique nonzero ordinary dual covector annihilating
H_t. This definition does not identify the compressed source labels' pairing
with the ordinary dot product. The verifier reconstructs linear functionals
alpha on V and gamma on V* for which alpha(l_s)=1 and gamma(h_t)=1 for every
source line's nonzero l_s and every target normal. In the frozen coordinates,
alpha=13 and gamma=511.

## 2. Remove possible original crossings

Fix an integer k between 1 and 7. Remove a nonzero correction pair (s,t) if
at least one of the following holds, without imposing timing constraints:

1. Some original X_s frame of dimension greater than k is contained in H_t.
2. Some original Y_t frame of dimension at most k contains L_s.

Let E_k be the remaining set. The first condition allows any source read after
its dimension cut. The second allows delivery before the target's dimension
cut. Both are favorable relaxations. Their absence is a necessary condition
for attributing every path to a new helper crossing.

The exact census is:

| k | Source bypass | Target bypass | Their union | size of E_k |
|---|---:|---:|---:|---:|
| 1 | 336 | 0 | 336 | 4656 |
| 2 | 336 | 0 | 336 | 4656 |
| 3 | 252 | 92 | 320 | 4672 |
| 4 | 168 | 168 | 312 | 4680 |
| 5 | 92 | 252 | 320 | 4672 |
| 6 | 0 | 336 | 336 | 4656 |
| 7 | 0 | 336 | 336 | 4656 |

PR2614 and the preceding screen already identify the 336 later-readable
entries. The symmetric cut-dependent removal and its 4,680 residual are the
finite premises added here. The primary checker hashes each complete E_k;
the independent implementation reconstructs every count from the two JSON
inputs without importing candidate code.

## 3. Every surviving dependency crosses on a new helper

First restrict all logical rows to their X-source coefficients. Restoration
makes these rows zero at every helper lifetime boundary. A reused physical
helper can therefore be represented by separate virtual lifetimes, each
initialized with the zero X row: omit the physical reset edge between them.
This preserves every source-to-target coefficient and removes any FULL-to-ZERO
edge from the dependency argument. Successive lifetimes may reuse the same
original dirt; it need not be mutually independent across lifetimes.

Expand this finite correction program into its chronological scalar linear
dependency graph. A nonzero C_ts coefficient implies at least one
nonzero path from X_s's input to Y_t's final value. This remains true with
negative coefficients, arbitrary dirty values, cancellations and helper
mixing. A nonzero sum of path weights has at least one nonzero summand.

Follow such a path. ADD edges have equal frames; transport edges increase
frames. It starts at L_s and ends at H_t, so every intermediate frame contains
L_s and is contained in H_t. The path can enter another original source only
by a write, which is forbidden. It can leave a target only by a read, also
forbidden. Initial dirty-helper inputs are source-independent, so they cannot originate
this source dependency.

The frame dimensions must cross from at most k to greater than k. A crossing
on X_s would give an original source frame of dimension greater than k
contained in H_t, which was removed. A crossing on Y_t would give an original
target frame of dimension at most k containing L_s, also removed. Therefore
for every pair in E_k there is a crossing A subset B on a new helper with

```text
1 <= a=dim A <= k < b=dim B <= 8,
L_s subset A, B subset H_t.
```

The endpoints a=0 and b=9 cannot carry such a path. A strictly increasing
helper lifetime crosses a given dimension cut at most once. Assign each
surviving pair to one of its paths and one such crossing. No assumption of
independence between the assigned entries is needed for this support count.

## 4. Rectangle capacity and rank invoice

For a fixed crossing A subset B, all its assigned source labels lie in A.
Since alpha is one on each of them, there are at most 2^(a-1) such distinct
labels. All assigned h_t lie in the annihilator B^0, of dimension 9-b. Since
gamma is one on each, there are at most 2^(8-b) distinct target normals.
Thus its assigned pairs are contained in a rectangle of size at most

```text
2^(a-1) * 2^(8-b) = 2^(7-r), where r=b-a.
```

If alpha or gamma restricts to zero, the corresponding set is empty and the
same bound holds. The affine-odd hypotheses matter: arbitrary nonzero vectors
in a four-dimensional A and the annihilator of a five-dimensional B can give
15*15=225 pairs. Under affine-odd restrictions the corresponding bound 8*8=64
is attained by a generic binary alphabet. No claim of attainment by the P104
root subset is made.

Writing n_(k,r) for the useful rank-r helper crossings at cut k proves

```text
sum over r=1..7 of n_(k,r) * 2^(7-r) >= size of E_k.
```

In particular the cut-4 inequality has right side 4,680. This is an inequality
on actual crossing occurrences. Counting a positive transport at a different
cut as this crossing is not justified.

For any proposed saving with p=1-a in (0,1], a crossing of dimensions a0,b0
also has a complete lifetime transport bill at least

```text
a0^p + (b0-a0)^p + (9-b0)^p.
```

The preceding and following segments have total ranks a0 and 9-b0;
subadditivity of x^p makes splitting either segment at least as expensive.
All other costs remain payable. This symbolic lower bound is compatible with
the support inequality, but this package does not solve or certify a global
moment optimization. At p=1 it is just nine units per complete lifetime.

## 5. Shape consequences and limits

At cut 4, the three possible chronological orders of multiset {1,1,7} cross
as follows:

| Order | Cut crossing | Capacity for E_4 |
|---|---|---:|
| 1,1,7 | dimension 2 to 9 | 0 |
| 1,7,1 | dimension 1 to 8 | at most 1 |
| 7,1,1 | dimension 0 to 7 | 0 |

Consequently a network containing only that multiset requires at least 4,680
lifetimes. This does not forbid an individual legal {1,7,1} carrier. The
executable positive control follows actual frozen X/Y paths and implements
y<-y+x with an arbitrary helper restored, using initial dirty compensation,
a line capture, a hyperplane delivery and full-frame cleanup. Removing either
compensation or cleanup rejects, as do a wrong capture and a wrong frame.

Every other lifetime still has at most one useful cut-4 crossing, of capacity
at most 64. If a network has L lifetimes, M of other multisets, then

```text
4680 <= (L-M) + 64M = L + 63M.
```

For L<=482 this requires M>=ceil(4198/63)=67. The number 482 is a hypothetical
budget boundary from the preceding screen; its validity and attainability do
not follow from this proof. Without a shape restriction the present bound is
only 74 lifetimes and is weaker than the existing 208 floor.

Original-helper/private reads, target feedback, changed data paths or new
helper descents can invalidate the monotone-path or bypass arguments. They
must be priced and analyzed separately. The claim is a written scoped proof
with exact finite premises, not a universal multiplication lower bound,
attaining correction circuit, proof-assistant theorem or supplier admission.
