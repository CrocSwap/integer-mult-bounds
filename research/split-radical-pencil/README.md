# Exact reachability of square-zero radical pencils

This package was produced by Nick Petalas. Apache-2.0.

**Scoped algebraic proof, with finite corroboration.** For every field K,
every n >= 1 and A in M_n(K), put R = K[x,y]/(x,y)^2. Allow paid factors
I + u v^T with u in R^n and v in K^n, including singular factors, and free
GL_n(K) maps anywhere. Then

```text
xI_n + yA is reachable
    if and only if the characteristic polynomial of A splits over K.
When reachable, its exact paid cost is n.
```

A scalar eigenvalue alone is insufficient. For example, over F2,

```text
    [0 0 0]
A = [0 0 1]       has characteristic polynomial t(t^2+t+1).
    [0 1 1]
```

Its pencil is unreachable at every finite length, although A has eigenvalue
zero. This settles Open next question 1 of
[PR #4773](https://github.com/CrocSwap/integer-mult-bounds/pull/4773), whose
necessary condition only excludes matrices without a base-field eigenvalue.
The new proof uses determinants of polynomial lifts, followed by a sharp
column-replacement construction. It does not audit the predecessor theorem.
No new kappa, supplier admission or complete multiplication theorem is claimed.

## Proof

### Necessity by polynomial lifting

Take any alleged finite word, including its free maps. Every paid left vector
has a unique expression a + xb + yc with a,b,c in K^n. Lift that factor to

```text
F_hat = I + (a + Xb + Yc) v^T  over K[X,Y],
```

and lift each free map to the same constant matrix. Let Q be the literal
polynomial product in the same order. Reduction modulo (X,Y)^2 is the alleged
endpoint, so every entry of Q has zero constant term and

```text
Q = XI + YA + terms of total degree at least two.
```

The homogeneous degree-n part of det(Q) is therefore det(XI+YA). There are
no terms of degree below n, and the coefficient of X^n is one. In particular,
det(Q) is not the zero polynomial and has exact order n at the origin.

The rank-one determinant identity over the commutative polynomial ring gives

```text
det(F_hat) = 1 + v^T a + X v^T b + Y v^T c.
```

Determinant multiplicativity expresses det(Q) as a nonzero constant from
the free maps times a product of these affine linear polynomials. None can
be identically zero. Let s be the number whose constant term is zero.
The lowest homogeneous part of their product has degree s, because a product
of nonzero polynomials over a field is nonzero. Since det(Q) has order n,
s=n. Its homogeneous degree-n part is a nonzero scalar times the product
of those n homogeneous linear factors. Hence

```text
det(XI+YA) = c product_(i=1)^n (alpha_i X + beta_i Y),  c != 0.
```

The coefficient of X^n forces every alpha_i to be nonzero. Substituting
X=t,Y=-1 shows that det(tI-A) splits over K. This excludes every finite
word for a nonsplit A, even with arbitrary free maps and extra paid factors.
It also proves that any realizing word has at least n paid factors.

Lifting is essential. The determinant of the endpoint in R itself is zero
when n>=2 and would give no such condition. No equality of higher-degree
matrix entries in K[X,Y] has been assumed.

### Sufficiency and exact cost

A matrix over K has split characteristic polynomial exactly when it is
triangularizable over K. For completeness, choose an eigenvector, pass to
the quotient by its invariant line, and repeat. The quotient characteristic
polynomial is the original one divided by that linear factor, so induction
constructs a full invariant flag. Conversely an upper triangular matrix has
split characteristic polynomial by its diagonal.

Choose S in GL_n(K) with T=S^-1 A S upper triangular. Let M= xI+yT and
m_j its j-th column. Define the paid factors

```text
C_j = I + (m_j-e_j)e_j^T,   j=1,...,n.
```

They are legal because e_j is over K. In execution order C_1,...,C_n, the
first j-1 factors leave coordinate j unchanged: their modified columns have
support only in rows at most j-1. Consequently e_j^T C_(j-1)...C_1=e_j^T.
Multiplication by C_j replaces column j of the partial product with m_j
without changing its other columns. Induction gives

```text
C_n ... C_1 = xI+yT,
S C_n ... C_1 S^-1 = xI+yA.
```

This word uses exactly n paid factors. The lower bound above proves its
optimality. It is a literal matrix identity on arbitrary dirty inputs;
there are no assumed zero registers or erased inputs.

## Executed evidence

The standalone verifier uses only the Python standard library and imports
no predecessor executable. It compares two different criteria on every A in
its declared finite domains: a permutation expansion and root division of
the characteristic polynomial, and a constructive invariant-flag search
that never reads that polynomial. Every successful flag yields an explicit
legal paid word, checked by direct square-zero matrix multiplication and
free conjugation.

The domains are all matrices at (q,n)=(2,2),(2,3),(3,2),(3,3),(4,2),(5,2),(7,2).
F4 uses t^2+t+1. These domains contain 23,574 matrices in total. The binary
three-role classification is exactly

```text
352 split, reachable at cost 3;
112 nonsplit with a scalar eigenvalue, unreachable;
 48 without a scalar eigenvalue, unreachable.
```

The 112 rootful exclusions are additional to the predecessor's eigenvalue
obstruction. The familiar 48 count agrees with #4773; the new result is the
classification, not an independent audit of that count. All 512 binary dirty
inputs pass one nontrivial three-role upper-triangular word. Nine evaluations
of an odd-field polynomial lift check its determinant against the product
of the individual affine determinants without truncating degree-two terms.

The nine control cases are the rootful nonsplit witness, reversed word,
three separate dropped factors, an odd-characteristic determinant sign,
the F4 multiplication law, an irreducible polynomial and a singular A with
nonsplit characteristic polynomial. These exercise different hypotheses or
failure modes. Checks use explicit exceptions and remain active under -O.
Each run emits a generated receipt binding all five package files by SHA256;
no receipt is stored or hand-written.

## Reproduction

From the repository root, with CPython 3.12 and no third-party dependencies:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/split-radical-pencil/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/split-radical-pencil/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/split-radical-pencil
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/split-radical-pencil --check-source-history
```

Any CPython 3.12 installation may replace the local interpreter path. Expected
marker: `PASS_SPLIT_RADICAL_PENCIL binary_three_role=352/512 rootful_excluded=112 no_new_kappa`.
Both registered commands have a 120-second timeout. The current selected
source-binding orientation also passed; it is metadata orientation only.

## Scope and implementation limits

This classifies the particular two-generator pencils with invertible first
coefficient normalized to I. It does not classify all radical matrices,
more radical generators, higher nilpotency, restored auxiliary roles or
ring-valued right vectors/free maps. The universal claim is the written
proof; the finite checks corroborate it and do not exhaust finite words.
Independent human and formal proof-kernel review are unclaimed. Native
coefficient preparation, physical routing, restoration, precision, stock and
complete supplier costs remain unknown. Lean, Docker and the selected operator
replay were outside scope and were not run. All registered checks ran locally.

The verifier has no recursion or subprocesses and accepts no search-size
arguments. The largest matrix has nine entries and the largest streamed
census has 19,683 matrices. Flag vectors and spans have at most 49 elements;
loops are bounded by the fixed domain, n<=3 and q<=7. Functions stay below
60 physical lines. Package receipt reads have a 128 KiB limit per file.
Managed Python allocation is a bounded deviation from fixed steady-state
allocation, including tuples and generator temporaries during arithmetic.
There is no persistent service or resource. Warning-strict normal and
optimized execution provide the available diagnostics. No repository-wide
static-analysis configuration was changed.

## Open next questions

1. Which pencils xB+yC with singular B are reachable? Start with a fixed
   Kronecker singular block and compare its minimal indices with column
   replacement words. The invertible-coefficient determinant argument no
   longer gives a nonzero degree-n determinant.
2. With three or more independent square-zero generators, when is splitting
   of the homogeneous determinant sufficient? Start with an invertible first
   coefficient and two other coefficient matrices. Simultaneous invariant
   flags can fail even if a determinant factors; an attaining word or a new
   obstruction is needed.

Structured first steps, relevance and blockers are in [TASK.json](TASK.json).
These follow-ups are not investigated here.

## Credit, provenance and coordination

Produced by Nick Petalas. Nick Petalas's #4773 supplies the open question,
the earlier arbitrary-role eigenvalue obstruction and its explicit first
working example. #4745 supplies the two-role square-zero classification;
#4243 supplies the common free-map convention. Wentao Li's #4099 following
#2513 supplies the right-vector alphabet, and ToikY's #4334 supplies the
shared-chart algebra context. Determinant multiplicativity, the rank-one
determinant identity and triangularization are classical. The new contribution
is their polynomial-lift application giving the exact all-role pencil
classification and exact cost. No predecessor credit line is changed.

The formal-interface-lemma card is changed to a formal-alphabet algebraic
side result. The selected source-bound baseline replaces the card's historical
baseline as directed by current priorities. Initial baseline attempts exposed
omitted sparse files; all selected source directories were materialized before
the successful run. No scientific replay was inferred from that control.
SOURCES.json pins the original card, selected record and conceptual predecessor
README as provenance at canonical main 624de9dc66858af0945e5f8a0942488d62280d43,
priority revision 7. There are no live predecessor executable dependencies.

Before claiming, open PRs, this account's recent PRs and claims, active
Discussions, the local reservation directory, merged PR terms and main README
terms were checked. The overlap helper reported complete remote pagination
at 19:44 UTC and incomplete sparse local-note coverage. This is search
coverage, not proof of novelty. The relevant merged package is #4773;
no currently open PR in the inspected list studies this pencil classification.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19131512).
