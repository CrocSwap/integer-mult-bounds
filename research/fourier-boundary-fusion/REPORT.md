# Fourier fusion across a copied-center boundary

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
October 8, 2026. Bounded mechanism diagnostic; no new multiplication exponent.

## Outcome

A common partial Walsh transform can pass through a copied-center scatter.
The resulting internal map needs only one coordinate butterfly child. But
every participating target must enter and leave the common basis. In the
isolated scatter-column schedule tested here, that changes the charged
coordinate rank from 28 to 141,967 or 148,231. This candidate fails even
granting the adapted coordinate chart and coordinate packing for free.

The more general finding is a coordinate-cut obstruction. For an exact
linear implementation of an e-coordinate tensor butterfly on M original
scalar coefficient positions, suppose every uncharged operation preserves
each selected physical address-bit partition. If recursive children are
coordinate kernels on q_l selected coordinates and M_l coefficient positions,
then

    sum_l q_l M_l >= e M.

Thus arbitrary cross-gate fusion cannot produce strict rank-mass contraction
in this model. Copies, discarded scratch, and smaller child volumes obtained
by splitting spectator rows do not escape the inequality. This extends the
local mobility diagnostic in the [previous round](../direct-selected-xor/REPORT.md).
It is a written algebraic argument with exact finite regression checks,
not a Lean formalization or a lower bound for general tape algorithms.

## The actual boundary tested

The source is the [copied-center contract](../../notes/copied-centers-lemma.tex)
and its [complex construction](../../notes/copied-centers-complex.tex).
Suppress the common tensor background and past/future rank-one factors.
For a center hyperplane U in an h-dimensional active factor, the relevant
map is

    z_out = Q z,
    y_t_out = y_t + alpha_t R z,
    R = C_U^(-1), Q = C_(U-perp).

Operationally, copy the original center, apply R to the copy, scatter it
into the target bank, discard the dependent copy, and send the original
through Q. All original z and y_t inputs are arbitrary. The copy is not
another independent input role and does not divide the original volume.

We isolate one column of the actual scatter matrix. The optimized decoder
may share intermediate sums; this star is an operator-level subproblem,
not a claim that the full decoder literally consists of independent stars.
The cost comparison below is for this proposed isolated-column schedule,
not a minimum over all possible implementations of the complete scatter.

At h=28 the old R and Q calls have ranks 27 and 1. The mixed center basis
uses a set D of size 19, with D_i=T-G_i for i in D and B_i=2G_i otherwise.
Writing T=sum_i G_i gives

    T = (sum B_i - 2 sum D_i)/(-32).

For a target triple S, put k=|S intersect D|. Its scatter coefficients are

    alpha(D_i,S) = -1_(i in S)/2 + (k-1)/32,
    alpha(B_i,S) =  1_(i in S)/4 - (k-1)/64.

Enumerating all C(28,3)=3276 triples, a D center has 2628 nonzero target
dependencies and a B center has 2744. Independently, their zero counts
are 18*C(9,2) and 19*C(8,2), respectively.

## The fusion identity and its charge

Let J be all active coordinates except i, so |J|=27. Put W_J for the
unnormalized Walsh transform on J, with inverse 2^(-27) W_J. Apply W_J
to the center and every participating target at entry, and its inverse
to each at exit. Scalar scatter additions commute with this common
transform. Applying it only to the center does not implement the map.

For a D center, U is the coordinate hyperplane J. In this basis, R is
the diagonal phase i^(-wt(x_J)), and Q is the coordinate kernel C_i.

For a B center, let n be the indicator of J, so U=n-perp. Its odd norm
is 27, and Q=C_n^(27 mod 4). In the partial Walsh basis Q is the phase

    i^(27 parity(x_J)),

while R is C_i^(-1) times

    i^(-wt(x_J) + 27 parity(x_J)).

Both kinds therefore have one internal coordinate child. Each entrance
or exit transform contributes width 27, on the complete volume of its
stream. The resulting accounting is:

| Center | Targets | Old coordinate rank | Proposed coordinate rank |
|---|---:|---:|---:|
| D | 2628 | 28 | 2*27*(2628+1)+1 = 141967 |
| B | 2744 | 28 | 2*27*(2744+1)+1 = 148231 |

All streams here have the same logical coefficient volume. No padding,
work-area duplication, or zero initialization makes those entrance and
exit obligations smaller. We grant the coordinate chart and packing
for free; paying for them would not rescue this candidate.

The code checks the full arbitrary-input operator on a reduced active
factor h=4, whose odd normal has the same norm modulo four as h=28.
It checks every real basis input for the center and two targets, plus
every imaginary basis input in the test suite. Coefficients include
actual dyadic values from the retained scatter. The symbolic formulas
above establish the identities for arbitrary even h; the finite tests
are regression checks, not a simulation of the full h=28 payload space.

Keeping targets transformed through later scatters could amortize these
specific entrance/exit costs. The local numbers alone do not rule that
out. The next argument addresses a whole implementation under explicit
restrictions on its remaining operations.

## Coordinate-cut rank lemma

Work over Q(i), with exact linear operations on payload coefficients.
The root operation is C tensor e on e physical selected binary address
coordinates, on every original stream. Let M count original scalar
coefficient positions, including spectator indices and independent roles.
It does not count precision bits, dependent copies, or extra zero padding.
Use complete selected-coordinate ranges and arbitrary inputs on these
original positions. A final permutation of spectator roles is harmless.

For selected bit j, let P_j project onto positions where that address bit
is one. At each intermediate state use the corresponding projection on
its live positions, including scratch and copies. If an implementation
changes layout, the physical bit label follows the data. Encoding a bit
as a row-class label does not make subsequent cross-class mixing free.

Write its primitive linear maps as A_1,...,A_L, allowing rectangular maps.
Define the j-th defect of primitive l by

    D_(l,j) = P_(l,j) A_l - A_l P_(l-1,j).

The model makes the following assumptions:

1. Every uncharged operation has D_(l,j)=0 for every selected j. This
   includes address-diagonal phases, aligned pointwise role mixing,
   copying/deleting aligned streams, and spectator-only row splitting.
2. A charged child acts on M_l coefficient positions and q_l actual
   selected coordinates. It preserves all other selected-bit partitions.
   Coordinate C tensors, their inverses, and coordinate Walsh tensors
   satisfy this requirement. For a touched cut its defect rank is at
   most M_l, and for any untouched cut it is zero.
3. All remaining operations satisfy one of those two conditions. In
   particular, there is no uncharged noncoordinate address movement.

For T=A_L ... A_1, direct telescoping gives

    P_(L,j) T - T P_(0,j)
      = sum_l (A_L ... A_(l+1)) D_(l,j) (A_(l-1) ... A_1).

This is valid for rectangular copying/deletion maps and does not assume
that any intermediate map is invertible. Rank cannot increase under
pre/postcomposition. Therefore

    rank(P_(L,j) T - T P_(0,j))
      <= sum_l rank(D_(l,j)).

For the required target, the left side is M for every selected j. Indeed,
C=aI+bX has b nonzero, so [diag(0,1),C] is an invertible 2-by-2 matrix.
Its tensor product with the invertible C kernels on other coordinates
and identities on spectators is full rank. A cut-preserving invertible
output role permutation or diagonal phase does not change that rank.

Consequently M <= sum_(l touching j) M_l. Summing over all e cuts proves

    e M <= sum_l q_l M_l.

This proof is independent of the number of gates, where transforms
cancel, how long a basis is retained, and whether the workspace is dirty,
copied, or zero-initialized. It charges actual child volume. It can be
applied to arbitrary complete unpadded instances, so independent demands
are never inferred from padding zeros.

## Consequence for the proposed recurrence, and its limits

Set mu_l=M_l/M and r_l=q_l/e. For children no wider than the parent,
the lemma says sum mu_l*r_l >= 1. For 0<sigma<1, r_l^sigma >= r_l, so

    sum_l mu_l * r_l^sigma >= 1.

There is no strict contraction of this coefficient-volume/width moment
at exponent sigma. This rules out the proposed pure coordinate-kernel
replacement as the source of the desired saving. It is a necessary
algebraic screen; a successful tape recurrence would additionally need
precision, layout, and overhead accounting.

The existing network can beat this coordinate budget because its
noncoordinate address changes have nonzero cut defects and are handled
by other machinery. Removing them in favor of coordinate kernels plus
diagonal phases must pay their mixing cost somewhere.

This does **not** rule out a hybrid that retains cheap noncoordinate
movement, a new structured noncoordinate recursive primitive, or a
different representation of the root computation with another contract.
It does not cover nonlinear payload algorithms. A role split that allows
mixing across a selected-bit partition also falls outside the free-map
assumption; its implementation must be accounted for separately.

The actionable distinction is therefore not simply full versus smaller
volume, or local versus longer fusion. A successor needs an operation
that crosses the selected-coordinate partitions more economically than
coordinate kernels, with an actual implementation and cost. Another
Fourier-only schedule within these assumptions cannot supply that.

## Reproduction and decision

From the repository root:

```sh
python3 research/fourier-boundary-fusion/audit.py --output research/fourier-boundary-fusion/certificate.json
python3 -m unittest discover -s research/fourier-boundary-fusion -p 'test_*.py' -v
```

Seven tests cover the scatter identity, omitted-alignment counterexample,
exact dependency counts, full and child cut ranks, rectangular telescoping,
and the distinction between free spectator operations and excluded active
address movement. All computations use exact rational or Gaussian-rational
arithmetic. The [certificate](certificate.json) pins its source files;
[validation](validation.json) records reproduction and preservation checks.

**Decision:** stop the pure coordinate-Fourier replacement branch. The
bounded cross-boundary test produced a useful obstruction, not a faster
algorithm. No kappa or release certificate changes. A subsequent round
should name a concrete noncoordinate primitive or changed root contract
before launching another open-ended circuit search.
