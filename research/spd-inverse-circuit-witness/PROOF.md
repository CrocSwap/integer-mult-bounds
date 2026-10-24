# Conditioned witnesses with true inverse calls

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This is an author-checked written proof. It has no proof-kernel or independent
human review claim.

## Contract and result

Use the complete rational register grammar in the retained
[predecessor proof](vendor/UPSTREAM-PROOF.md). Each of the r initial roles is
independent. Each program returns all r roles. Instructions are scalar linear
assignments, named-generator applications, and scalar queries of a named
generator applied to a role. An application or query can use the **true
inverse of that same generator**. All sources refer to their values before
the instruction, including when a source is also the destination. Only
inverses of named generators are allowed. An inverse of an operator sum is
outside this grammar.

Let q+ and q- count the forward and inverse occurrences in both programs.
Queries with coefficient zero count. Put q=q++q- and N=r+q. Suppose the two
complete endpoints differ for some tuple of invertible matrices over Q.
For every rational e0 in (0,1/4], there is a constructive rational witness
of dimension d<=N with the following properties:

- Each generator A_a is real symmetric positive definite, with spectrum in
  [1-2e,1] for a common rational e in (0,e0].
- Each inverse call uses the actual A_a^(-1). Its spectrum is in
  [1,1/(1-2e)]. Both A_a and A_a^(-1) have spectral condition number at most 2.
- The operator norm of A_a-I is at most 2e. Thus the generators can be as
  close to identity as requested. The inverse distance is at most
  2e/(1-2e).
- The witness search needs at most L+1 literal endpoint evaluations, where
  L=q+ + d q-. It tests a fixed rational grid; no random choice is needed.
- One declared input role contains e_(d-1), and all other input roles contain
  zero. A declared output differs in its coordinate zero. This is one legal
  input, not a clean-helper assumption in the universal statement.

The inverse matrices need not be contractions: their operator norms can be
as large as 2. Requiring a positive-definite matrix and its inverse both to
be contractions would force that matrix to be identity.

## Nonzero coefficient and symmetric path

The retained inverse frontend constructs a finite realization of the full
endpoint series at G_a=I+Y_a. If the universal identity is false, it returns
an output o, input i, word w=a1...aD with D<N, and nonzero rational coefficient
c at that word. Its producer finds a shortest word. The proof below needs
only a nonzero coefficient and D<N; it does not need shortestness.

Set d=D+1. On coordinates 0,...,D define the symmetric labelled path

    S_a = sum_(j: a_(j+1)=a) (E_(j,j+1) + E_(j+1,j)),
    R_a = -I + S_a/2,
    A_a(e) = I + e R_a = (1-e)I + (e/2)S_a.

Each row of S_a has absolute sum at most 2. Symmetry and the row bounds put
its spectrum in [-2,2]. Therefore A_a(e) has spectrum in [1-2e,1]. For
0<e<=1/4 it is invertible and has the stated conditioning and norm bounds.
All entries are rational at rational e. The D=0 case gives S_a=0 and the
scalar matrix A_a=1-e.

Consider entry (0,D) of endpoint block (o,i) as a function f(e). It is a
rational function regular at zero. Substitution of Y_a=e R_a in the
predecessor series gives its formal expansion at zero. Terms with fewer
than D letters have zero entry (0,D), since each factor can move at most
one edge. A product of D factors can move from D to zero only by using
all D forward path edges, in their matrix-product order. Its labels must
be w; neither a diagonal step nor a backward step can reach the endpoint
in D factors. Thus

    f(e) = (c / 2^D) e^D + terms of degree greater than D.

For D=0 the leading term is c. In all cases f is a nonzero rational
function. This argument does not truncate an inverse series. Formal
substitution is valid degree by degree, since each degree contains only
finitely many words. The actual finite program uses inverses of matrices
with determinant constant term 1, so its rational expansion is the same
formal series.

This is the step which differs from the earlier polynomial construction.
There is no highest degree for an inverse series. Higher terms can cancel
the value at a particular nonzero e, so a single fixed parameter does not
suffice for this construction.

## A bounded rational grid

For a fixed word and d, every A_a(e) has entries of degree at most 1.
Its determinant has degree at most d, and its adjugate has degree at most
d-1. Track a common denominator for every role in one program. Initially
it is 1, and the numerator degree is zero.

A scalar linear assignment does not increase the degree. A forward
application or query increases the maximum numerator degree by at most 1.
At an inverse application or query, multiply the common denominator by
one copy of det(A_a). For a changed term, multiply its old numerator by
adj(A_a); for unchanged roles or an old query destination, multiply by
det(A_a). Thus the maximum numerator degree increases by at most d. This
bound also holds for a self-source query, because it reads the old value.
A zero query can retain an unused determinant factor without harm.

For one program with counts p+,p-, the common denominator has degree at
most d p- and all numerators have degree at most p+ + d p-. To subtract
the two endpoints, use the product of their denominators. Every resulting
numerator has degree at most

    L = q+ + d q-.

For 0<e<=e0, all these determinant factors are positive. Let P be the
numerator for f in this representation. The nonzero leading series term
shows that P is not the zero polynomial. A nonzero rational polynomial
of degree at most L has at most L distinct roots. Therefore at least one
of the L+1 points

    e_j = e0 (L+2-j)/(L+1),  j=1,...,L+1

has f(e_j)!=0. Literal exact evaluation at the grid points finds one.
The search starts at the cap, which avoids a small grid denominator when
the cap already gives a witness. This order does not change the root bound.
There is no finite-field version of this root-grid claim here; the adapter
requires Q. There is also no bound here on rational intermediate bit
lengths or on the numerical magnitude of the final nonzero discrepancy.

The grid bound can be attained. For d=1 and m inverse occurrences, set
alpha_j=1/(1-(m+2-j)/(4(m+1))) and take the scalar endpoint

    product_(j=1 to m) (G^(-1)-alpha_j I).

It has a nonzero constant coefficient at G=I. With G=1-e, its first m
points on the grid vanish and its (m+1)-st point does not. The verifier
checks m=1,2,4,7. At m=1 the first point e=1/4 gives zero; the second point
e=1/8 gives -4/21. This tests actual cancellation, not just a stored bound.

## Implementation and independent checks

The byte-exact predecessor `algebra.py` returns the coefficient word. This
package does not replace its equality certificate or its proof. The new
producer then executes the original program at the grid points. The path
matrices are tridiagonal, so the literal interpreter applies them directly
and solves each inverse call by exact tridiagonal elimination. Positive
definiteness gives positive pivots. This solve is the true matrix inverse
applied to a vector, not a new independent inverse label.

The public checker does not import the coefficient producer. It checks
the program hash, word labels, dimension bound, parameter range and grid
index. It recomputes every final role by literal exact execution and
requires the claimed output coordinate to differ. It certifies this
concrete negative witness; it does not certify a shortest word, the
coefficient value, or the universal positive case.

The verifier separately constructs dense matrices, inverts them with
pivoted Gauss-Jordan elimination and executes both programs with snapshots
of all old roles. A separate reduced-group-word expansion decides only
the small differential tests. These checks corroborate the proof. They
do not turn a finite sample into a universal theorem.

## Credit and limits

[PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262) by
@krzysztofwojt supplies the inverse-aware realization, its dimension bound,
and the nonzero coefficient word. Its source at
`6f92ccf1e61c4668c8ee687bd1df8b42932b8759` is retained unchanged, with proof
and attribution. It credits @zxv's
[PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235), the
classical rational-series, Magnus and weighted-automata methods, and the
prior dirty-echo/tensor/phase work. Those credits remain in
[the retained source README](vendor/UPSTREAM-README.md).

Ali Romman's earlier
[PR #5268](https://github.com/CrocSwap/integer-mult-bounds/pull/5268) proves
the highest-degree polynomial SPD construction. This result replaces that
finite-degree step with a leading path coefficient and a rational root
grid, and preserves actual inverse calls. Path matrices, root counting,
Gershgorin bounds and exact elimination are classical. No new general PIT
algorithm or global literature priority is claimed.

Extra commutation, involution, Clifford, adjoint or native-family relations
are not imposed. The result covers this grammar only. It provides no
floating-point detection threshold, least-dimensional witness, native
adapter, physical cost, bit-complexity bound, supplier admission, kappa
improvement or selected-frontier change.
