# A dyadic unit log needs two independent centre queries

The input-log construction has a representation choice with a precise
cost in information. Every dyadic log that makes its mixed source block
a unit needs sixteen independent query fields in the stated terminal
observation class. An exact division by 13 permits a log with eight.
This theorem concerns information rank. It is not a native-child bound.

## Unit separation over a residue field

Let B have r rows and n columns, and let D have n rows and r columns.
Let their coefficients lie in a commutative ring R with a homomorphism
to a field k. Assume the following conditions:

1. BD=cI, and c maps to zero in k.
2. B has row rank r over k.
3. M has r rows and n columns, and MD is a unit over R.

Then the stack [B;M] has row rank 2r over k. To prove this, suppose
that alpha B+beta M=0 over k. Multiply on the right by D. This gives
beta(MD)=0, so beta=0. Full row rank of B then gives alpha=0.
The proof also shows that n must be at least 2r.

If R is an integral domain and the map to k is a residue map, a nonzero
2r-minor over k is nonzero over the fraction field of R. Thus the stack
also has rank 2r over that fraction field. This conclusion applies to
every M with the stated unit condition, not only to a sparse minor log.

## The actual eight-centre construction

Use R=Z[1/2], k=F_13, r=8, and n=104. The pinned current core has

    BD=13I.

Its ordinary minor T=[21,37,47,76,81,87,92,110] has D_T orthogonal
over the dyadic ring. Since B=D^T in the canonical chart, B_T is a
dyadic unit too. It follows that B has rank eight modulo 13.

For every dyadic M with a dyadic inverse for MD, the theorem therefore
gives

    rank [B;M]=16.                                      (1)

The hypothesis is exactly the mixed-source unit criterion in
`../lanes/oblique-native-20261017/minor-input-log/UNIT-COMPLETION.md`.
That criterion was independently reviewed. It holds in a more general
operator ring; the present residue argument makes a distinct statement
about the dyadic representation.

The same result applies to a finite routed array with ell scalar
coordinates in each field. Use the Gaussian dyadic ring and reduce
modulo 13 with i mapped to 5. The current routing maps and their
inverses have Gaussian dyadic coefficients. The ordered identities
BD=13I and the inverse-minor identities therefore survive reduction.
If MD has an inverse in that same ring, the stack has rank 16ell.
This argument does not commute Q through B, D, M, or a route. It uses
the complete finite operator matrices and their proved inverses.

## Consequence for the controller

The source-access theorem in
`../lanes/controller-followthrough-20261017/MINOR-LOG-SOURCE-ACCESS.md`
uses a full-null family. All completed X fields and retired selected
Y fields are zero on that family. The retired ordinary Y field is an
arbitrary v. Its required original outputs include -Mv and DBv.
The full-null substitution is x_U=(I-DB)v, y_U=DBv, Qa=-Mv,
and original b=-QBv+qMv. Its proof does not use MD=I, so it applies
to every M in the present theorem. If the terminal's only further
observation is Nv, it must satisfy

    ker N is contained in ker B intersect ker M.         (2)

Over the underlying field, (2) implies that the row space of [B;M]
is contained in the row space of N. Equation (1) proves that a dyadic
unit log requires at least sixteen complete query fields in this
observation model. The result permits arbitrary postprocessing of N.
It does not restrict a different controller, more observations, a
different output partition, or operations that read ordinary Y directly.

An exact odd grid changes this limit. Set M=B/13. Then MD=I, while
[B;M] has rank eight. Thus it gives a unit mixed source code and meets
the necessary query-rank lower bound eight for this family. In contrast,
no dyadic unit log can meet that bound. The odd-grid theorem supplies
the arithmetic representation for this choice, under its exact-child,
arbitrary-borrowed-input, and outer-endpoint hypotheses.

This is a useful enabling result for the matched-log attempt. It cuts
the independent query content from sixteen fields to eight. It does
not make the remaining old-stage B query cheap. Its physical source
access, target scatter, output phases, and recursive cost remain open.

## Checks and attribution

Run from the workspace root:

    python3 -I -B work/centre-encoding-campaign-20261014/root/check_dyadic_query_separation_20261018.py

Expected status: `PASS_DYADIC_QUERY_SEPARATION`.
The checker pins the actual core, verifies both inverse-minor orders,
BD=13I, and the rank-sixteen dyadic example modulo 13. It verifies the
matched log with exact fractions. It also checks 64 dyadic
unit logs obtained by changes in the kernel of D. These finite checks
support the stated application; the argument above proves the universal
claim. Independent proof review is still required.

The oblique-native lane supplied the input-log unit construction. The
controller-followthrough lane supplied (2) and the rank-sixteen sparse
example. The native-escape lane proposed the matched log. The prior
interface-proof work and the current odd-grid review supplied the exact
division contract. The coordinating lane supplied the residue-field
argument for every dyadic unit log. This work used OpenAI Codex under
the user's direction. No independent human review is claimed.

No PR, push, or publication commit is authorized. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
