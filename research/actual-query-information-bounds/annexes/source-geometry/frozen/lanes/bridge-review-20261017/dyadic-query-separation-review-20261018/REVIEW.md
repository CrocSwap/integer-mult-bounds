# Independent review of dyadic query separation

The universal query-separation theorem passes this review. The actual
eight-centre B matrix has full row rank modulo 13. Every dyadic M for
which MD has a dyadic two-sided inverse therefore gives a stack `[B;M]`
of rank sixteen. The full-null family applies to general M; it does not
require MD=I. The matched choice M=B/13 has rank eight and MD=I.

This is a theorem about the rank of fixed linear observations in the
stated output partition. Postprocessing may be nonlinear. The theorem
does not bound native children, concurrent scratch fields, arbitrary
nonlinear encodings, or packing on one bounded finite input domain. It
does not prove that the old-stage B query is cheap or physically available.

## Sources and independent method

The producer source is
[DYADIC-QUERY-SEPARATION-20261018.md](../../../root/DYADIC-QUERY-SEPARATION-20261018.md),
SHA256 `664f430efd099f35cbc7c2abc8025968c03020707027857d2882daa51a065a1a`.
The source criterion is
[UNIT-COMPLETION.md](../../oblique-native-20261017/minor-input-log/UNIT-COMPLETION.md),
and the terminal class is
[MINOR-LOG-SOURCE-ACCESS.md](../../controller-followthrough-20261017/MINOR-LOG-SOURCE-ACCESS.md).
All proof and checker pins are in [REVIEW.json](REVIEW.json).

The independent checker reads the actual R entries from the pinned
decompressed `CLEAN-J-PROGRAMS.json.gz` payload, SHA256
`a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa`.
It derives the selected inverse by exact elimination. It then derives B
and D and checks the actual minor inverses. It imports no producer module.
Its modular rank check builds a column basis instead of using the
producer's row reduction.

The exact actual sparse stack has a nonzero 16-by-16 minor with columns

```text
[1,2,3,4,5,6,8,12,21,37,47,76,81,87,92,110]
```

and determinant 1/8. The checker also checks 24 different logs for which
MD is a nonidentity dyadic unit. Thus the independent examples are not
limited to sections with MD=I. A Gaussian two-coordinate route fixture
uses noncommuting unit routes and has stack rank 32 after reduction.
The finite fixture is not a replay of the complete global native schedule.

## Residue proof and rank lift

Let R be a commutative ring with a unital map phi to a field k. Suppose
B is r by n, D is n by r, and M is r by n, all over R. Assume

```text
BD=cI,       phi(c)=0,
rank_k phi(B)=r,
MD is a unit in Mat_r(R).
```

Apply phi entrywise. Since a matrix inverse over R maps to its inverse
over k, `phi(MD)` is invertible. If

```text
alpha phi(B)+beta phi(M)=0,
```

right multiplication by `phi(D)` gives `beta phi(MD)=0`. Hence beta
is zero. The full row rank of `phi(B)` then makes alpha zero. This
proves row rank 2r over k and also implies `n>=2r`. It does not assume
MD is identity, that B and M commute, or that R is a field.

For the fraction-field conclusion, assume R is an integral domain.
Some 2r-by-2r determinant has nonzero image under phi. Its determinant
over R is therefore nonzero. The same determinant remains nonzero in
the fraction field. Thus the stack has rank 2r there. In fact this
step needs no extra property of a residue map beyond the stated ring
homomorphism and integral-domain hypothesis.

Both hypotheses have a role. If MD is only invertible over Q, choose
M=B in the actual example. Then MD=13I, but `[B;M]` has rank eight.
If full residue rank of B is dropped, the scalar example B=13, D=M=1
has a unit MD and a rank-one stack. If the condition phi(c)=0 is
dropped, B=D=M=1 gives the same failure. These are failures of the
weakened hypotheses, not exceptions to the theorem.

## Binding to the actual canonical and routed matrices

Use the actual selected minor
`A=[0,7,20,27,36,46,57,111]` and ordinary minor
`T=[21,37,47,76,81,87,92,110]`. Direct calculation gives

```text
B=R_A^-1 R_U,
D=R_U^T (R_A^-1)^T,
BD=13I.
```

The inverse of B restricted to T and the inverse of D restricted to T
are both dyadic. The checker verifies both orders of each inverse.
Reducing the B minor modulo 13 preserves its inverse. Thus B has full
row rank eight over F_13. This proves the actual application for every
dyadic M with a dyadic unit MD, without an enumeration of all M.

For finite routed arrays, let each field have ell complex coordinates.
Flatten every ordered operator to its complete finite matrix over
`Z[i,1/2]`. The map

```text
i -> 5,      1/2 -> 7,      integers -> F_13
```

is well defined, because `5^2=-1` and `2*7=1` in F_13. Every proved
Gaussian-dyadic inverse maps to an inverse. The complete identities
`BD=13I` and the inverse-minor identities therefore give the hypotheses
with r replaced by 8ell and n by 104ell. The stack has rank 16ell.

This argument uses the full finite matrices. A ring of ell-by-ell
operators is not itself being called a field. Flattening puts the rank
argument over the commutative scalar residue field. No Q, frame change,
or port route moves through B, D, or M. If an intended physical map
does not have the stated ordered identities and Gaussian-dyadic
inverses, it has not met the theorem's hypotheses.

## The source unit condition for general MD

The mixed-source part of the local map, in source variables beta=qb
and v, is

```text
w=-D beta-v+DMv,
d=Mv.
```

The invertible output changes `f0=-w+Dd` and `g=d-Mf0` give

```text
f0=v+D beta,
g=-MD beta.
```

The input change from `(beta,v)` to `(beta,v+D beta)` is invertible.
After component reordering, the source map is therefore equivalent
to `diag(I,-MD)`. That map is a unit exactly when MD is a two-sided
unit. This proves the criterion over the ordered operator ring as
well as over a field. A zero-kernel test alone would not prove this
ring-level statement.

## Full-null family for arbitrary M

Let q=Q^-1, and choose an arbitrary ordinary vector v. Put all later
pair inputs to zero. For pair zero, set

```text
original x_U=(I-DB)v,
original y_U=DBv,
Qa=-Mv,
original b=-QBv+qMv.
```

The first full shear gives incoming ordinary Y equal to v. Since
`a=-qMv`, its selected source value becomes `-QBv`. Thus the backward
call gives

```text
d=Qa+Mv=0,
h=q(-QBv)+Bv=0,
w=(I-DB)v-v+D(0-q(-QBv))=0.
```

These cancellations use only qQ=I and Qq=I. They do not use MD=I,
MD invertibility, or BD=13I. The independent checker verifies this
in free operator words with only those two inverse relations. It
also rejects removal of the original-b term qMv.

Every selected exchange acts on zeros. The raw or corrected forward
call leaves retired ordinary Y equal to v. The bridge to the next
ordinary bank is `-v+v=0`. Every later pair and the final completed-X
triangle therefore remain zero, for every pair count.

The required original selected data and ordinary source values include
`-Mv` and `DBv`. Their destination fields are zero on this family.
The terminal obtains all other information about v only through the
fixed linear observation Nv. If Nv=0, these destination outputs must
match the zero-input outputs. Hence Mv=0 and DBv=0. Over Q or Q(i),
BD=13I makes D injective, so DBv=0 is equivalent to Bv=0. Therefore

```text
ker N is contained in ker B intersect ker M.
```

For finite vector spaces, this condition is equivalent to a linear
factorization `[B;M]=LN`. Define L on the image of N by `L(Nv)=[B;M]v`;
the kernel condition makes it well defined. Extend L to the observation
space. It follows that `rank N>=rank[B;M]`. This proof permits arbitrary
nonlinear postprocessing of N: postprocessing cannot distinguish two
inputs with the same N value.

If N returns q complete fields of ell coordinates, its rank is at most
qell. Thus q must be at least sixteen for a dyadic-unit log. Cross-pair
queries do not help this family: restrict N to the first ordinary bank.
The count is total independent observation rank. It is not a claim
that sixteen scratch fields must be live at the same time.

The argument does not require recovery of every coordinate of v from N.
The retained ordinary Y can keep its unobserved contents and receive
known corrections. The displayed kernel condition is a necessary source
condition; it does not prove a full decoder. If the underlying inputs
are Gaussian dyadic, a finite rational kernel witness can be cleared
of denominators and scaled by a power of two. It then gives admissible
dyadic witnesses in a uniform all-precision model. The argument is not
a lower bound for precision-dependent packing of one bounded finite set.

## Exact odd division and a sharper consequence

For M=B/13, the equation MD=I holds and the stack has rank eight over
the fraction field. Its rank is exactly eight because B has an invertible
minor. This M lies outside the dyadic ring, and its entries cannot be
reduced modulo 13. The independent checker verifies both facts. The
existing common-grid theorem supplies exact division by 13 only under
its exact-child, all-numeric-stream root conversion, arbitrary-borrowed
input, binary-guard, and final dyadic-endpoint conditions.

The argument has a stronger coefficient-ring consequence. Suppose B
has an invertible r-column minor over an integral domain R, BD=cI
with nonzero c, and `[B;M]` has fraction-field rank r. Then

```text
M=T B,
T=M_minor (B_minor)^-1 lies in Mat_r(R),
MD=cT.
```

If MD is a unit over R, then `T(MD)^-1` is in Mat_r(R), and c times
this matrix is identity. A diagonal entry therefore gives an inverse
of c in R. Conversely, if c is a unit, M=B/c has MD=I and stack rank r.
Thus a unit log with only r independent query rows exists exactly when
c is a unit in the coefficient ring.

For the actual construction, an eight-query unit log consequently
requires inversion of 13. Rational divisions with denominators coprime
to 13 leave the residue map intact and still force sixteen queries.
In particular, division by three alone does not resolve this query
obstruction. Under the normalization MD=I, the rank-eight choice is
uniquely M=B/13. More generally it is `M=K B/13` for a unit K=MD.

This also gives a scheduling alternative. In the ring with 13 inverted,
one may take the dyadic initial log M=B, leave K=13I, and use
`K^-1=I/13` in the general source-code formulas. This moves the odd
normalization from the initial log to the decoder. It does not remove
the required B query or establish a cheaper physical implementation.

## Reproduction and status

Run from the workspace root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/dyadic-query-separation-review-20261018/check_review.py
```

Expected status:

```text
PASS_INDEPENDENT_DYADIC_QUERY_SEPARATION
```

The independent checker passed. The producing checker and receipt were
pinned and read; this review did not rerun its entry point because that
entry point writes the frozen producer receipt. No material defect was
found in the stated theorem. The coefficient-ring characterization above
is a direct consequence proved in this review.

The cheap implementation of the remaining old-stage query, target
scatter, phases, recursive admission, complete decoder, and supplier
moment remain open. No native-child lower bound or kappa result follows.
This review used substantial OpenAI Codex assistance.

No PR, push, or publication commit is authorized. Before a future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
