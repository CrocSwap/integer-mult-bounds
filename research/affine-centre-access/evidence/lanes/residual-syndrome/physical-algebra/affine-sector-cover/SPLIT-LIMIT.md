# A scan bound for affine Haar projector trees

The single-piece stream has geometric total volume because it refines
only one active half. That bound does not extend to a positive-density
union merely by sharing the common parts of many affine encodings.
This note gives an exact limit for that proposed implementation class.
It permits arbitrary binary linear tests, unequal leaf codimensions,
and invertible affine changes of the current address coordinates.
It is not a lower bound for every circuit or every projector method.

## 1. The implementation class and its charge

The initial Fourier address set is `F_2^m`, of size `N=2^m`.
Unselected address, row, spectator, compact, and polynomial indices
are carried as unchanged external indices. They multiply every volume
below by the same factor.

An affine Haar projector tree has the following properties.

- Each current branch represents an affine set `A` of Fourier
  addresses. Its coefficient stream has `|A|` records per external
  index.
- A split tests a nonconstant affine binary functional on `A`.
  A two-point Haar code gives its two halves. Both halves are retained;
  either can be refined. The split processes `|A|` coefficient records.
- An invertible affine change of the current spectral coordinates can
  occur before any split. Its address map and its inverse must be paid.
  It preserves affine sets and their dimensions. Such maps can depend
  on the branch, but not on arbitrary input coefficient values.
- At a terminal branch, the whole branch is accepted or rejected.
  A projector shear changes the target leaf exactly at accepted
  branches, then reverses the codes. Thus the accepted leaves form a
  disjoint affine partition of the desired spectral set `S`.

A block operation is included if it is a literal group of these Haar
splits. It can expose many branches at once or keep one active branch
and a sequence of detail branches. Expand the block into its actual
binary splits when its processed volume is counted. This includes
unequal child codimensions. It does not count a rank-`r` native child,
an unproved direct block algorithm, or a full rank-`r` Fourier transform
as one free scan.

Let `w` be a common charged coefficient-record width, or a uniform
lower bound on that width at each split. Put `V=Nw`. A fixed-format
implementation with reserved guard bits, as in `STREAM.md`, has exactly
this form. Reading and writing a full record in a split costs at least
a fixed positive multiple of `w`. Address-map work is additional.
The theorem first bounds the number of processed records, so it does
not require a claim about a narrower adaptive coefficient format.

## 2. The exact volume identity

Let `d_l` be the number of binary splits on the path to terminal leaf
`A_l`. Each test has rank one on the current affine set, and every
intermediate coordinate map is invertible. Thus

    dim A_l=m-d_l.

The total processed record count in the forward code is exactly

    T = sum_(internal v) |A_v|
      = sum_(all leaves l) |A_l| d_l.                   (1)

The second identity counts each spectral address once for each split
on its path. It does not depend on bit order, on a common choice of
linear basis across branches, or on the number of accepted leaves.

Equation (1) also gives a direct block form. If a block partitions its
input `A` into terminal parts `B_j`, of relative codimension `c_j`, its
literal split work is

    sum_j |B_j| c_j.

The parts include the stored detail branches. Keeping only the chosen
active descendant in this count would omit work or arbitrary input
data. Combining blocks and canceling their internal boundaries recovers
(1). Work to reverse the code, align records, or change coordinates is
nonnegative and is not needed for the lower bound.

Suppose every affine subset of `S` has dimension at most `m-k`.
Every accepted leaf then has `d_l>=k`. Hence

    T >= k |S|,                                        (2)
    split bit work = Omega(k delta V),
    delta=|S|/N.

For a fixed disjoint affine partition with no tree given, (2) is a
necessary lower bound for any realization by this class of Haar trees.
It does not assert that each such partition has a cheap tree.

## 3. Application to the correlated native sector

For the all-odd correlated sector `S_n` in an `n`-by-`lambda` Fourier
address, `m=n lambda`. The reviewed affine bound gives, for `n>=2`,

    k=n ceil(lambda/2)-(lambda mod 2).

The exact density theorem in the separately reviewed correlated-sector
packet gives, for fixed `n`,

    delta_(n,lambda) -> 2^-((n-1)(n+2)/2) > 0.

Consequently any exact projector for the full `S_n` in the class above
has forward split work `Omega(lambda V)` as `lambda` tends to infinity.
At `n=73`, the limit density is `2^-2700`; the checked density is within
one percent of that limit from `lambda=152`. The constant is very
small. The theorem is an asymptotic statement, not a useful large
numerical lower bound for the current finite local budget.

For a fixed phase residue `d`, use the stronger sharp bound

    k_d=n(lambda-kappa_lambda(d)).

Then the exact bound is `T>=k_d |S_(n,d)|`. This includes the smaller
optimal product pieces at nonpreferred residues. It also shows why
unequal piece dimensions do not avoid the depth charge.

For any fixed `0<tau<1`, the positive-density bound cannot fit into an
all-size overhead `O(V (n lambda)^tau)` in this class. The compact
address-map procedure does not remove this issue: the lower bound
already excludes its additional cost.

## 4. What the result does and does not rule out

Shared Haar prefixes can replace an exponential list of separate
piece computations by a tree. A full binary Fourier tree, followed by
the exact sector test on its leaves, is a finite example with at most
`mN` forward processed records. Thus sharing does change which direct
implementations are possible. It still cannot keep the one-piece
geometric `O(V)` scan bound for the complete positive-density sector.

The theorem leaves several concrete possibilities open: non-affine
leaf blocks, interference between overlapping codes, a circuit that
does not compute the full projector, or productive native children
that perform a block transformation under their own recursive bill.
An address-dependent quadratic-code certificate from `COVERAGE.md`
does not by itself realize any of these possibilities. A finite-state
signature description also does not by itself price physical access.

The theorem does not forbid arbitrary nonlinear changes of Fourier
labels as an abstract permutation. Such a change is outside affine
splitting and still needs a physical implementation. Nor does it
give a lower bound for a general bounded-coefficient linear circuit,
for cancellation across multiple encodings, or for the actual centre
query without a complete sector projector.

## 5. Exact checks and provenance

`check_split_limit.py` builds finite affine decision trees in independent
noncoordinate bases. It checks every leaf against direct odd-phase
membership, verifies the rank and codimension of every node, computes
both sides of (1), and checks (2) for the full sector and each residue.
It groups unequal-depth subtrees as block operations and checks the
same weighted identity. These checks support the combinatorial proof;
they are not a general circuit lower bound.

The affine bound is pinned by `RIGIDITY.md` and the correlated-access
review. The density constant is pinned by the independent
`correlated-sector-review/REVIEW.json`. Exact hashes are in the receipt.
The stream construction and its independent review supply the stated
literal split implementation. No producer file was changed.

Proof and exact checks: OpenAI Codex under the user's direction.
The parent requested the general block and coordinate-change scope.
No PR, push, or commit was made. Before any future PR description,
read `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
