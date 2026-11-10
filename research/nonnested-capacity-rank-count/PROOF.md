# Exact joint completion with arbitrary target capacities

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

Nick Petalas's PR6489 gives the exact nested-target criterion and count.
This package handles arbitrary simultaneous target subspaces over a finite
field. It is an exponential reference method, not a replacement for that
fast nested criterion. Kernel-subspace inversion, Gaussian coefficients
and projective cross-ratio obstructions are classical. The contribution
is their exact application to this repository's shared-map contract, with
full rank counts, constructive witnesses and joint rejection controls.

## Contract and linear equations

Let V and W have dimension n over F_q. Specify any finite list of fixed
images g(u)=v and any finite list of inclusions g(A_i)<=C_i. The spaces
A_i and C_i may overlap or repeat, and the C_i need not be nested.
A fixed partial injection is one permitted list of fixed images. More
general or inconsistent fixed lists are allowed; an inconsistent list
has count zero. No generic-position hypothesis is used.

Choose bases of V,W and write g as an n-by-n matrix X. A fixed image
supplies n scalar affine equations. For every basis vector a of A_i and
every basis vector lambda of the annihilator C_i^perp, add

    lambda X a = 0.

Nondegeneracy of the coordinate dual pairing shows these equations are
necessary and sufficient for the full inclusion. Dependent input lists
are harmless. Let L be the resulting affine solution set of matrices.
This construction preserves all joint dependencies; it does not replace
them with separate dimension inequalities.

## Count by exact rank

For every subspace K of V, let F(K) be the number of matrices in L that
vanish on K. Add Xk=0 for a basis of K to the affine system. If the
augmented system is inconsistent, F(K)=0. Otherwise

    F(K)=q^(n^2-rho_K),

where rho_K is its coefficient rank. For 0<=j<=n put

    A_j=sum_(dim K=j) F(K).

Let N_t count matrices in L with kernel dimension t. Double-count pairs
(X,K), where X is in L and K is a j-subspace of ker X. This gives

    A_j=sum_(t=j..n) [t choose j]_q N_t.                  (1)

The Gaussian coefficient is the number of j-subspaces of F_q^t. It is
obtained by dividing the number of independent ordered j-tuples by the
number of ordered bases of a j-space. In particular [j choose j]_q=1.
Thus the following descending recurrence gives every exact count:

    N_j=A_j-sum_(t=j+1..n) [t choose j]_q N_t.            (2)

The number of rank-r completions is N_(n-r). Invertible completion exists
if and only if N_0>0. If N_0=0 but L is not empty, the largest r with
N_(n-r)>0 is the exact maximum feasible rank. This measures an algebraic
rank deficit, not the physical cost of a repair.

The familiar equivalent formula for the invertible count is

    N_0=sum_(K<=V) (-1)^dim K q^(dim K (dim K-1)/2) F(K).

It is the classical subspace-lattice Mobius formula. The executable uses
(2), which also provides the entire rank histogram. The double-counting
argument above proves the formula used here without an external theorem.
For historical background, see Richard Stanley's author-hosted
[Enumerative Combinatorics, volume 1](https://math.mit.edu/~rstan/ec/ec1.pdf),
which treats the subspace lattice and its Mobius function. No novelty is
claimed for this inversion machinery.

## Compress the fixed partial injection

Suppose the fixed images specify an injection on an independent basis of
a u-dimensional U. Extend this basis and its image to ambient bases P,Q.
In these coordinates every extension has the form

    X = Q [ I_u  A ] P^-1.
          [  0   B ]

Here m=n-u, A is u-by-m, and B is m-by-m. Thus rank X=u+rank B.
There are n*m free scalar entries, not n^2. Substitute this exact affine
form into every capacity equation. For a source with P-coordinates x
and a covector with Q-coordinates y, the resulting equation is

    sum_(i,j) y_i x_(u+j) Y_ij = -sum_(i<u) y_i x_i,

where Y consists of A above B. No constraint is lost. Enumerate kernels
K of B in F_q^m, impose Bk=0, and count all n*m-variable affine solutions,
including A. The same double count (1)-(2), with m in place of n, gives
the rank histogram of B and hence of X. It keeps every coupling between
A and B; treating A as a free factor without checking the equations would
be invalid. This reduces the subspace lattice from dimension n to n-u.

The compressed executable permits ambient n<=12 with n-u<=4, over the
same three prime fields. It requires the fixed generators and images to
be independent. The uncompressed API still accepts arbitrary affine data.
The proof has no size limit. This gives a larger useful ambient contract
without enumerating its full subspace lattice or dropping fixed images.

## Construct a witness at any feasible rank

Suppose the count at rank r is positive. Process the n^2 matrix entries
in a fixed order. For the next entry, partition the current solution set
by its q possible values and recompute the rank-r count in each fiber.
The fiber counts add to the positive current count, so at least one is
positive. Fix the first such value and continue. At the end one matrix
remains. It has rank r and satisfies the original full affine system.
This constructs an isomorphism when r=n, or an exact maximum-rank witness
when no isomorphism exists. A requested rank with zero count returns no
witness; it is never silently replaced with another rank. For the compressed
system, assign the n*m entries of Y and reconstruct X with P,Q. The same
positive-fiber argument applies to the required rank of B.

The reference uses reduced-row-echelon bases to list every K exactly
once. For a chosen pivot set, each nonpivot entry to the right of its
row pivot is free; all other entries are forced. This describes exactly
all RREF matrices and hence all subspaces. The number of subspaces grows
exponentially with n. One count uses that many finite linear solves;
the entry constructor uses at most q*n^2 count calls. The uncompressed Python API is
explicitly bounded to n<=4 and q in {2,3,5}. The written result holds for
all finite fields and all finite dimensions. No efficient general
optimizer, extension-field implementation or infinite-field count is claimed.

## A joint obstruction missed by every three contacts

Over F5, use four source lines generated by

    (1,0), (0,1), (1,1), (1,2)

and four target lines generated by

    (1,0), (0,1), (1,1), (1,3),

with the displayed correspondence. The first two inclusions force X to
be diagonal. The third forces its diagonal entries to agree. The fourth
then forces 2a=3a, so a=0. The full joint system has exactly the zero
matrix. It has no invertible or rank-one completion.

Every three contacts do admit invertible maps. The exact rank histograms
for subsets, in increasing matrix-rank order, are

| Number of contacts | Counts at ranks 0,1,2 |
|---|---|
| 0 | 1,144,480 |
| 1 | 1,44,80 |
| 2 | 1,8,16 |
| 3 | 1,0,4 |
| 4 | 1,0,0 |

The row for a given size holds for EVERY subset of that size. The
verifier derives each count with (2), checks it by literal enumeration
of all 625 matrices, and constructs a full-rank witness for each triple.
This is the classical four-line projective obstruction in the exact
late-capacity contract, not a claim of new cross-ratio geometry.

All dimensions of sums and intersections of corresponding line subsets
agree: each singleton has dimension one; any two distinct lines span the
whole plane and have zero intersection. Even this complete subset
sum/intersection dimension data cannot replace the joint equations.
The example also has no fixed partial map that could explain the failure.

## Verification and connection to the source contract

The verifier compares all rank counts with literal vector-action and
matrix enumeration in small fields. It includes every ordered pair of
binary two-dimensional source/capacity subspaces, with every one-vector
injective prescribed image or no fixed image. It also tests nonnested
and inconsistent affine systems, random three-dimensional contracts,
zero dimension, diagonal/block constraints with independent exact count
formulas, and the retained nested source's 4/12/0 compatibility example.
Returned matrices are checked against the original vector inclusions,
not only the compiled equations. RREF subspace enumeration is checked
against a separate closure-of-vector-sets construction.

The exact maximum-rank and impossible-joint certificates can prevent a
search from synthesizing incompatible separately feasible frame maps.
This is a GL interface only. It does not impose symplectic pairings,
signs, absolute phase, physical native movement, a chronological word,
dirty restoration or a profitable full caller. Those are separate costs
and constraints. All five selected assumptions remain. No new kappa,
selected-frontier change, independent human review or proof-kernel
acceptance is claimed. Finite replay corroborates the written theorem.

Credit Nick Petalas / PR6489 for nested capacities and PR4919 for the
separate three-subspace correspondence; Brian / JoyboyBrian / PR5020
for the shared-map question; Cao Yifan / intqwq / PR4610 and codyw912 /
PR4735 for the native context; Cinna Davis, Dugongue, zxv, Jacob Alan
Sussman and the retained native/compiler lineage. The source proof is
retained byte for byte. No predecessor scientific verifier is imported.
