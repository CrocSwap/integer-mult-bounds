# An exact spectral criterion for deficiency-two symplectic spread completion

This contribution was produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed.

## Result and scope

**Claim type: scoped written mathematical proof, with exact finite controls.**
Let q >= 3 be a prime power, n >= 1, and let S consist of q^n - 1 pairwise
trivially intersecting Lagrangians in a nondegenerate alternating 2n-dimensional
F_q-space. A full symplectic spread has q^n + 1 members, so S has deficiency two.

Form the graph Gamma on the uncovered projective points. Join two distinct
points exactly when their symplectic pairing is nonzero. Let A be its ordinary
0/1 adjacency matrix and put

$$
N=\frac{2(q^n-1)}{q-1},\qquad k=q^{n-1},\qquad Q=kI_N+A.
$$

Then S extends to a full symplectic spread **if and only if det(Q) = 0 over the rationals**.
Here Q is the integer signless Laplacian, regardless of the characteristic of
F_q. More precisely:

- If det(Q) = 0, Gamma is connected and bipartite, Q has nullity one, and every
  nonzero rational kernel vector is a nonzero constant times a vector with
  entries +1 and -1. The two sign classes are exactly the projective points of
  the two missing Lagrangians. The unordered completion pair is unique.
- If det(Q) != 0, Q is positive definite over R and S has no completion.

Thus no search over candidate missing Lagrangians is required after the hole
graph is constructed. This is an exact algebraic decision and recovery
criterion, not an assertion that every deficiency-two partial spread completes.
The explicit F3 negative fixture below has no completion.

The new step is the combination of the deficiency-two hole degree with a sharp
component-size lemma. David Ganz's [atlas, PR #2849](https://github.com/CrocSwap/integer-mult-bounds/pull/2849)
proves deficiency-one completion at B098 and explicitly leaves the stronger
deficiency-two proposal unresolved. Its result is cited, not rechecked here.
The signless-Laplacian kernel identity and elementary symplectic dimension
facts are classical. This package supplies the completion criterion and its
proof; it makes no claim of global literature priority.

This is an algebraic side result. It changes the `formal-interface-lemma` card
from a selected-supplier proof obligation to a precise completion interface in
the atlas. It is not a new supplier, COPY invoice, kappa improvement, selected
frontier change, or complete multiplication theorem.

## Proof

### 1. The hole graph has N vertices and degree k

Write omega for the alternating form. Each L in S contains
(q^n - 1)/(q - 1) projective points. Distinct members of S have disjoint point
sets. Subtract their total from the (q^(2n) - 1)/(q - 1) ambient points to obtain

$$
|V(\Gamma)|=
\frac{q^{2n}-1-(q^n-1)^2}{q-1}
=\frac{2(q^n-1)}{q-1}=N.
$$

Fix a hole represented by h. For each old L, h does not belong to L = L-perp.
The functional omega(h,-) on L is therefore nonzero. Exactly q^n - q^(n-1)
nonzero vectors of L pair nontrivially with h, or q^(n-1) projective points.
There are q^(2n-1) projective points in the ambient space that pair nontrivially
with h. Consequently the number of nonorthogonal holes is

$$
q^{2n-1}-(q^n-1)q^{n-1}=q^{n-1}=k.
$$

Alternation gives no loops. Thus Gamma is a simple k-regular graph. Moreover

$$
3k-N=\frac{(q-3)q^{n-1}+2}{q-1}>0
$$

for q >= 3. In particular N <= 3k.

### 2. A singular signless Laplacian forces one bipartite component

For any simple k-regular graph and real vector z,

$$
z^T(kI+A)z=\sum_{\{u,v\}\in E}(z_u+z_v)^2.
$$

Hence Q is positive semidefinite and z lies in its kernel exactly when
z_u = -z_v on every edge. A connected component supports a nonzero such vector
exactly when it is bipartite. On a bipartite connected component the vector is
constant on each part, with opposite constants. An odd cycle forces the
constant to be zero. This proves the usual signless-kernel characterization
without assuming that the whole graph is connected.

Now let a simple k-regular graph with k > 0 have at most 3k vertices. A
bipartite component has at least k vertices in each part, hence at least 2k
vertices. Any further component has at least k + 1 vertices, since every
vertex has k distinct neighbors. Both components would require at least
3k + 1 vertices. Therefore a bipartite component, if present, is the whole
graph. It is connected, and its signless kernel is one-dimensional.

The size gate is sharp for general regular graphs. The disjoint union C4 and
K3 has k = 2 and N = 3k + 1. Its signless Laplacian is singular, although the
whole graph is not bipartite. This is an abstract graph example, not a claim
that this graph occurs as a symplectic hole graph.

Applying this lemma to Step 1, singularity of Q forces Gamma to be connected
and bipartite. Its rational kernel is nonzero because Q has integer entries.
Each nonzero kernel vector has equal nonzero magnitudes and opposite signs
on the two parts.

### 3. The two parts are precisely two missing Lagrangians

Let X,Y be the two parts. Since Gamma is regular with positive degree,
counting edges from each side gives k|X| = k|Y|. Thus

$$
|X|=|Y|=\frac{q^n-1}{q-1}.
$$

Representatives of points in X pair to zero, since there are no edges within X.
Their span is isotropic, and so has dimension at most n. But a subspace of
dimension at most n - 1 contains at most (q^(n-1) - 1)/(q - 1) projective points,
fewer than |X|. Its span therefore has dimension n, and X is its entire
projective point set. The same argument applies to Y.

Call these spans L_X and L_Y. They meet each other trivially because X and Y
are disjoint full point sets. They meet every old member of S trivially
because all their points are holes. Adding them fills every hole and gives
a full symplectic spread.

Conversely, a completion partitions the holes into the two missing
Lagrangians. There are no nonorthogonality edges within either point set,
so Gamma is bipartite and Q is singular. Step 2 then shows that Gamma is
connected. Its bipartition is unique up to swapping the parts, which proves
uniqueness of the unordered completion pair. If Q is nonsingular, its
positive semidefiniteness makes it positive definite. This proves every
assertion of the result.

## Relation to the nonzero-vector formulation

The advance claim used uncovered nonzero vectors as graph vertices. The
projective graph here compresses each scalar class of q - 1 vectors. Within
one class the nonorthogonality adjacency rows are identical. Subtracting the
two signless-kernel equations shows that a kernel vector is constant on every
class, since its degree is (q - 1)k > 0 over Q. On class-constant vectors the
uncompressed signless Laplacian acts as (q - 1)Q. The kernels therefore
correspond exactly, so this compression preserves the claimed decision and
recovery criterion.

## Exact finite evidence

The standalone verifier enumerates projective points and every Lagrangian in
each named four-dimensional model, constructs the hole graph from the literal
old subspaces, computes exact rational kernels and integer determinants, and
independently enumerates possible completion pairs. It recovers both missing
subspaces from the kernel signs in each positive case.

For q = 3 and q = 5, take the standard form
omega((x,y),(x',y')) = x dot y' - y dot x', with two-coordinate x,y.
Choose the least nonsquare d. The q^2 - 1 old subspaces are the graphs of

$$
M(a,b)=\begin{pmatrix}a&b\\ b&da\end{pmatrix},\qquad (a,b)\ne(0,0).
$$

Their matrices are symmetric, and each nonzero difference has determinant
d a^2 - b^2 != 0. The two missing subspaces are the graphs of zero and the
vertical plane.

For the negative F3 fixture, use the form
omega((x,y),(x',y')) = det(x,x') - det(y,y'). Take graphs of the eight matrices
+/-I, +/-J, +/-K, +/-JK, where

$$
J=\begin{pmatrix}0&1\\2&0\end{pmatrix},\qquad
K=\begin{pmatrix}1&1\\1&2\end{pmatrix}.
$$

These are the elementary quaternion subgroup matrices in SL2(F3). No novelty
is claimed for the group or this fixture. Every matrix has determinant one;
the verifier directly checks isotropy and disjointness of the eight graphs.

| Fixture | Enumerated Lagrangians | Hole points | Degree | Rank Q | det Q | Completion pairs |
|---|---:|---:|---:|---:|---:|---:|
| F3 field puncture | 40 | 8 | 3 | 7 | 0 | 1 |
| F3 quaternion graphs | 40 | 8 | 3 | 8 | 2304 | 0 |
| F5 field puncture | 156 | 12 | 5 | 11 | 0 | 1 |

The verifier also checks rejection of a duplicated old line in every fixture
and the C4 disjoint K3 size-bound control. The finite controls corroborate the
new criterion; the universal theorem rests on the written argument above.

## Reproduction

From the repository root, use CPython 3.12. No third-party packages or network
are needed for the verifier.

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/symplectic-deficiency-two-spectral/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/symplectic-deficiency-two-spectral
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/symplectic-deficiency-two-spectral --check-source-history
```

The direct check prints `PASS_SYMPLECTIC_DEFICIENCY_TWO_SPECTRAL` and the table
values above. `--receipt /absolute/path/outside-checkout/receipt.json` optionally
writes a generated receipt binding the output to every package file's SHA256
and the interpreter version. No receipt is handwritten or retained here.
`SOURCES.json` pins the atlas text, original card and selected-record provenance.
The atlas is a provenance reference; the mathematical checker does not import
or rerun its validator or predecessor proof.

Local validation used CPython 3.12.15. The direct verifier, registered replay
and committed-byte/source-history preflight are the required local checks;
hosted CI status is recorded in the PR body.

## Limits and implementation bounds

The theorem covers every prime power q >= 3 and every n >= 1. The executable
controls use only q = 3,5 and n = 2; they are not an exhaustive finite proof of
the all-dimension statement. There is no proof-assistant build or independent
human proof review. General projective partial spreads without isotropy,
higher deficiencies and the binary case in higher dimension are outside scope.

The matrix is indexed by N hole points, so this is a polynomial algorithm in
the explicit point inventory, not a polynomial algorithm in log(q) and n.
It uses rational linear algebra even when the geometry is over a finite field.
Taking the determinant modulo the geometry's characteristic is not the test.

The verifier has no recursion, subprocesses, dynamic code evaluation or imported
project code. Every loop ranges over explicit finite inputs: at most 5^4
vectors, 156 projective points, 156 Lagrangians and a 12-by-12 geometric matrix.
The exact-linear-algebra helper enforces a 16-by-16 ceiling. Python and Fraction
allocate dynamically; this is the bounded managed-runtime deviation from the
Power of Ten fixed-memory rule. Assertions enforce isotropy, disjointness,
degree, kernel equations, recovery and exhaustive-completion agreement. The
registered invocation enables warnings as errors and keeps assertions enabled.

## Open next questions

1. Does the singular-Q criterion hold for binary symplectic deficiency-two
   partial spreads when n >= 3? The component-size proof no longer suffices.
   Start by classifying whether a binary hole graph can have both a bipartite
   component and another component. This matters because such a graph would
   be a false positive for the proposed extension. No such example or
   impossibility proof is supplied here.
2. For deficiency t >= 3, can additional exact algebraic constraints recover
   the t missing Lagrangians without solving unrestricted graph coloring?
   The first step is to derive the corresponding hole degree and test a
   concrete t = 3 fixture. The present two-part kernel argument does not
   provide a criterion in that setting.

## Sources and overlap

The exact atlas source at base ff3cc58e370d0f678e529246f8c73e8094e18fcf is pinned
in `SOURCES.json`; PR #2849's retained head is
00576c07434c1196f49823dac83d57211ef731f1. Credit David Ganz for the atlas and
its deficiency-one theorem and deficiency-two question. The elementary graph
kernel identity is classical and is proved explicitly here.

Live open PRs, recent account submissions and claims, active Discussions,
targeted merged-PR searches and main-tree README searches were checked before
claiming this question. The broad cached card scan reported complete remote
pagination but incomplete sparse local-note coverage. Those checks do not
establish global mathematical novelty or exclude unpublished work.
