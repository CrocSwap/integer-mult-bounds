# More factor-linear terms do not beat the punctured E8 copy floor

## Statement and precise restriction

Use the real E8 root-line matrix R and the nine-dimensional binary label pairing
of PR717/PR968. Delete p <= 24 of its 120 lines. Let A,B be arbitrary complex
8-by-m matrices and let D=RA, T=RB satisfy

    D T^transpose = 2 R R^transpose

on every live row-column pair. Transpose is ordinary transpose. Remove any
zero rank-one summands, so all remaining m terms are active, and charge every
term separately by the binary pairing rank between its two nonzero supports.
Then, for any finite m,

    sum of term costs >= max(72-p, 56).

The eight-term examples of PR968 attain this lower bound over the choice of
puncture and decoder at every p. Thus allowing any number of terms **whose
columns remain in the live root code** cannot improve the best cost curve or
its minimum ratio 56/104 = 7/13. In particular the standard P112 frame puncture
retains minimum 64 in this class.

The added hypothesis D,T in col(R) is automatic for exactly eight terms; it
is not automatic for an overcomplete factorization. The countercontrol below
shows this explicitly. This theorem does not close unrestricted overcomplete
decoders, graph-only masked identities, deeper punctures, or interacting copy
programs. It is a structural copy-rank bound, not a physical supplier invoice.

## Inherited facts and their proof boundary

PR968 proves the real eight-term floor, and PR1077 extends it to arbitrary
complex coefficients with ordinary transpose. Their source-bound facts imply:

1. The live roots have rank eight. At least 96 lines remain, whereas a real
   root-spanned hyperplane contains at most 63.
2. Every nonzero complex normal has surviving support label dimension at
   least eight when p <= 24. Its dimension is therefore eight or nine.
3. When p <= 8, every support of dimension eight has a normal proportional
   over C to one of the punctured real roots. D7 reductions require 14
   punctures, and other reduced directions cannot occur in this range.
4. For two punctured root normals alpha,beta, their term cost is
   8 - 1[the true root inner product is odd]. In particular a root paired
   with itself costs eight, and a cost-seven term uses distinct root lines.

These support statements do not require A or B to have exactly eight columns.
PR1077's complex-to-real support descent is applied to each nonzero column
separately. Only its final eight-term dual-basis count requires eight terms.

The standard classification of real root-spanned E8 hyperplanes (PR968 F6)
remains an inherited cited premise. This package replays the finite A/B/C/E
facts used by the predecessors, including all eight flat types, the 1080 D7
directions and the 25-point attaining chain. It does not newly prove that
classification or equate finite replay with the universal theorem.

For support label spaces U,V, the nondegenerate nine-dimensional label form
gives cost >= dim(U)+dim(V)-9. Thus each active term costs at least seven,
and each side of dimension nine adds at least one to that lower bound.

## Rank counting for small punctures

A left inverse of R transports the all-pairs identity to A B^transpose=2I.
Consequently rank(A)=rank(B)=8 and m>=8, over C. The m=8 case is exactly the
credited predecessor theorem. Suppose m>=9.

For p<=7, let V_P be the complex span of the punctured real root normals,
of dimension r<=p. A side outside V_P is necessarily unreduced by fact 3.
At least 8-r columns of A must lie outside V_P: adjoining fewer vectors to
that r-dimensional space could not span rank eight. The same holds for B.
Summing the per-term label-rank inequality therefore gives

    cost >= 7m + 2(8-r) >= 7m + 16 - 2p.

At m=9 this exceeds or equals 72-p by 7-p, and it increases by seven for
each additional term. This handles every m>=9 and p<=7. It allows repeated
or proportional columns and does not assume that overcomplete columns form
dual bases. Reduced columns inside V_P need not be independent.

For 9<=p<=24, the simpler 7m>=63 already dominates max(72-p,56).
For p=8 and m>=10, it gives 7m>=70>64. Only p=8,m=9 remains.

## The exceptional nine-term diagonal obstruction

Suppose p=8,m=9 and total cost were below 64. Each cost is an integer at
least seven, so all nine costs must be seven. Both sides of every term must
then have label dimension eight. Fact 3 puts all eighteen normals on the
eight punctured real root lines. Since A has rank eight, those eight roots
are a real basis; write them as columns of an invertible real matrix U.

Write a_k=alpha_k U e_(r_k), b_k=beta_k U e_(s_k), with nonzero complex
alpha_k,beta_k. Fact 4 forces r_k!=s_k. Therefore

    A B^transpose = U K U^transpose,
    K = sum_k alpha_k beta_k e_(r_k) e_(s_k)^transpose

has diag(K)=0. But the required A B^transpose=2I implies

    K = 2 U^-1 U^-transpose = 2 (U^transpose U)^-1.

Every diagonal entry is twice the squared Euclidean norm of a nonzero row
of the real matrix U^-1, and is strictly positive. This contradicts zero
diagonal. Complex coefficients in K do not affect that real positive-definite
identity. No conjugate transpose or complex positivity assumption is used.
Thus cost>=64, completing all cases.

## Why unrestricted factors remain open

For the 112 live rows of the standard frame puncture, choose z outside col(R).
Let R_j denote column j. The following nine nonzero terms are an exact identity:

    (R_0+z)(2R_0)^transpose
    + sum_(j=1..7) R_j(2R_j)^transpose
    + (-z)(2R_0)^transpose = 2 R R^transpose.

The first and ninth D columns are outside col(R). A minimal-rank argument
cannot pull those overcomplete columns back into the root code. The verifier
takes z equal to the first live-coordinate unit vector, proves augmented rank
nine exactly and checks all 12544 identity entries. This is a counterexample
to extending the normal form automatically, not a cheaper decoder: no saving
is claimed for it. Any decoder beating our floor must violate at least one
stated restriction, such as allowing an outside-code column.

## Evidence, costs and limits

Four exact Gaussian-rational overcomplete factorizations use 9,10,12,16 terms.
Each is checked on all 14400 root-pair entries and all 25 inherited punctures;
every active term's pairing rank is charged. Sixteen deterministic real root
bases give 1024 root-pair classification checks and exact positive diagonals.
These examples test conventions and failure modes; they do not replace the
rank and positivity proof. The small finite p,m arithmetic table supplements
the explicit monotonic argument for unbounded m.

Five controls cover an altered coefficient, the wrong Hermitian convention,
the insufficient coarse p8/m9 bound, a dropped cancelling term, and the
outside-code rank obstruction. Separate subprocess controls exercise source,
context and complete typed receipt binding. A separate AI worker reviewed the
rank-counting and exceptional-case argument; this is not independent human
or proof-assistant review.

Only the copied-information rank sum is optimized. No scalar, center-read,
phase, restoration, helper, routing or hosting work is made free. This is a
lower bound in a favorable decoder relaxation, so those additional nonnegative
charges cannot turn a decoder below the excluded floor into a member of this
class. No completed supplier, new kappa, native execution or all-size/analytic
discharge is claimed. The selected PR1094 construction is unchanged.
