# Independent review of the actual row-involution completion

Status: PASS within the stated scope.

The frozen construction gives a dyadic involution A on the actual 112
ports. It preserves all 96 ordinary rows of the old response E. Its
transpose, the two scalar implementations, and both late queries pass
independent exact checks. No native word or complete caller is
established by this review.

The producer freeze is
`538ec208e510af7ee29aff4783d304e393c967697a6612e5c42e38fbc0ab9be2`.
The proof hash is
`c8470cc2280a057cbebf4a31ee679495990b200a6d6c033cc39e459eb2cf139f`.
The payload hash is
`a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b`.
This review also binds the separate limits freeze
`775c1b565ec0aa969f2dbecebb04f4b9a82a561e7e7d842c2b1abae7a75509a6`,
with proof
`91bd564b31766300cc89b87cf808439135d89c27bde655a2fc1842646c304607`
and payload
`25b15d03837fa2b3544bb2189208bacb06fcfc7dc6d4c8aee6d98174c8a512aa`.

## General construction and its uniqueness scope

Work over a commutative ring in which 2 is a unit. Let
`E=I+UV`, with `U` of size `n by r` and `V` of size `r by n`.
Let `P` have r indices and let `R` be its complement. Assume that
`V_P` has an inverse over the ring. Set

```text
U'_R = U_R,
U'_P = V_P^-1 (-2I-V_R U_R).
```

Then `VU'=-2I` and

```text
A^2 = (I+U'V)^2 = I+U'(2I+VU')V = I.
```

Every row in R is unchanged. The identity `VU'=-2I` supplies a left
inverse for `U'` and a right inverse for V. Over a field of
characteristic other than two, both factors have rank r, so
`rank(A-I)=r`. Also

```text
det(A) = det(I+VU') = (-1)^r.
```

The decomposition into `im(U')` and `ker(V)` is direct. A acts as
minus identity on the first summand and identity on the second.
This proves the eigenspace statements.

The frozen proof's phrase "the change has rank r" refers to `A-I`.
It must not be read as a general statement about `A-E`. For example,
E can already equal A. The producer accepted this wording
clarification without changing the frozen proof.

The stated uniqueness claim is valid. Within the fixed factor family,
V, `U_R`, and the desired value of `VU'` determine `U'_P` through
the invertible minor. The source does not assert uniqueness among
all possible row completions.

The general K extension is also valid. Replace `-2I` by `K-I`.
Then `VA=KV` and `det(A)=det(K)`. If K is a unit, direct
multiplication on both sides gives

```text
A^-1 = I-U' K^-1 V.
```

No commutation between K and `U'` or V is used. This algebra does
not supply a scalar tariff for an arbitrary K.

## Independent construction from the actual signed blocks

The reviewer reads the pinned old native response and the pinned
physical pair flags. It does not import the producer's code. One
matrix helper from a prior independent review is pinned and used
for exact elimination and reverse output propagation.

In the mode chart, the old response consists of eight signed blocks
of size six and eight signed blocks of size eight:

```text
E_k = I-dd^T.
```

For the actual selected pivot p, the source signs satisfy `d_p=1`.
The reviewer constructs

```text
u'_k = (k-2)e_p-d,
A_k = I+u'_k d^T.
```

The contraction `d^T u'_k=-2` proves each block involutive. Its
nonpivot rows equal the old rows. Its selected row is

```text
(k-2) x_p + (k-3) d_R^T x_R.
```

The checker constructs the physical matrices from these blocks and
the actual pair code H. It also reconstructs the old factor matrices
U and V. They agree with the source factors, in the source's exact
centre-coordinate order.

The actual pivot order is

```text
0,27,36,111,20,7,57,46,1,3,6,8,17,18,24,23.
```

The selected minor obeys

```text
V_P V_P^T = diag(2 I8,I8).
```

Thus its inverse can be formed from its transpose and these sixteen
diagonal units. The reviewer checks both inverse orders, then
reconstructs the general completion formula above. It agrees with
the independent signed-block construction on every entry.

The final exact facts are

```text
A^2 = (A^T)^2 = I,
rank(A-I) = 16,
rank(A-E) = 16,
det(A) = 1,
trace(A) = 80.
```

The equality `rank(A-E)=16` is an additional fact of this actual
source. It is not a consequence claimed for every input to the
general theorem.

## The physical transpose uses the pair metric

For a general pair matrix H, transposition does not pass through
similarity unchanged. If `A=H^-1 A_mode H`, then

```text
H A^T H^-1 = G A_mode^T G^-1,
G = H H^T.
```

For the actual H,

```text
G = diag(2 I48,I64).
```

The actual mode response does not mix these two components. Thus G
commutes with `A_mode^T`, and the right side is exactly
`A_mode^T`. The checker verifies the metric, the commutation, and
the resulting physical transpose. It does not assume that H is
orthogonal with unit scale.

All 96 ordinary physical rows of A equal those of E. All 96
ordinary columns of `A^T` equal those of E. In each mode block,
the nonpivot row support of `A^T` is the old support. Its
pivot-column coefficients are the old coefficients multiplied by
`-(k-3)`, which is -3 or -5. A native emitter must change those
weights explicitly.

## Stronger uniqueness for this actual pivot set

The exact retained factor `U_R` has rank 16. Since V has full row
rank, the ordinary displacement rows `(E-I)_R=U_R V` have row
space equal to the full row space of V.

Let Z be any rational matrix with the same 96 ordinary rows as E,
`rank(Z-I)=16`, and `Z^2=I`. The retained displacement rows
already span a 16-dimensional space. Therefore every row of `Z-I`
lies in `row(V)`, and there is a matrix T with

```text
Z-I = T V,    T_R=U_R.
```

The rank of T is 16. The involution equation gives
`T(2I+VT)V=0`. A left inverse of T and a right inverse of V imply
`VT=-2I`. The invertible selected minor now forces

```text
T_P = V_P^-1(-2I-V_R U_R).
```

Hence Z=A. This proves uniqueness among all rank-sixteen involutive
row completions for this fixed actual set P, not only within a
factor family chosen in advance. It applies in particular to dyadic
candidates. It does not assert uniqueness for a different pivot set
or for a completion of larger displacement rank.

## A sharp dyadic row-count bound

The producer proposed this separate extension during review. The
reviewer derived it independently and checked the required actual
modular ranks.

The old physical response is block diagonal on its large 48-port
component and its small 64-port component. Modulo five, the large
component has rank 40 and left-nullity eight. Modulo seven, the
small component has rank 56 and left-nullity eight.

These nullities also follow from the signed blocks. A six-mode block
has one null direction modulo five, since `d^T d=6=1 mod 5`.
An eight-mode block has one null direction modulo seven. The pair
code is invertible modulo both primes, so similarity preserves the
nullities.

Suppose a new matrix changes fewer than eight rows in the large
component. In its eight-dimensional old left kernel modulo five,
impose zero on the coordinates of those changed rows. A nonzero
vector remains. Extend it by zero on the small component. It
annihilates the original matrix, and it annihilates every row
replacement because its coefficients vanish at every changed row.
It is therefore a nonzero left-null vector of the new matrix.

Any matrix with an inverse over `Z[1/2]` remains invertible modulo
five. The preceding conclusion is a contradiction. Thus at least
eight large rows must change. The same argument modulo seven
requires at least eight small rows.

Consequently every dyadic-unit row replacement of this fixed E
changes at least sixteen rows. The replacement entries can mix the
two components; the proof still applies. A is a dyadic involution
and changes exactly eight rows in each component, so it attains the
bound.

This is a bound on row replacement in the stated common scalar
representation. It excludes neither odd-grid inverses nor changes
to the columns, the frames, or the required interface. It is not a
native lower bound or a lower bound for the required computation.

## Literal words, arbitrary state, and exact prices

The short scalar word first applies H. In each mode block it forms
`x_p+d_R^T x_R`, subtracts its signed fanout from the ordinary
coordinates, negates the pivot, and subtracts the updated reader.
An explicit expansion gives

```text
x'_p = (k-2)x_p+(k-3)d_R^T x_R,
x'_R = -d_R x_p+(I-d_R d_R^T)x_R.
```

The word then applies `H^-1`. Each size-six block costs 122 old
real scalar units, and each size-eight block costs 170. H and its
inverse each cost 470. The total is
`8*122+8*170+2*470=3276`.

Reversing the order and transposing each elementary gate gives the
literal transpose word with the same invoice. The longer direct
physical word has cost 5600. The checker verifies both
implementations and their squares by reverse propagation on all
640 arbitrary field inputs. The other 528 fields are unchanged.
A separate forward pass checks the exact scalar invoice and every
prefix.

The late query words preserve arbitrary target baselines. They
add `A[P,*]X` or `A^T[P,*]X` into the selected Y fields. They
leave all source fields and all other fields unchanged. All 640
outputs pass the reverse check, including the 224 data inputs.

| Word | Old real scalar units | Prefix row one-norm | Binary denominator height |
| --- | ---: | ---: | ---: |
| Short A | 3276 | 68 | 1 |
| Short transpose | 3276 | 18 | 1 |
| Direct A | 5600 | 69 | 2 |
| Direct transpose | 5600 | 14 | 2 |
| Late A query | 2960 | 70 | 1 |
| Late transpose query | 1984 | 30 | 1 |

Every SCALE is a signed power of two. No owned field, CLEAR, or
odd-arithmetic service occurs. These are scalar words in a common
admissible frame. The prefix bounds do not include any recursive
native child, owner map, or routed chart conversion.

The normalized row code also satisfies

```text
C A C^-1 = [[-I,0],[U_R V_P,I]].
```

The lower fanout is retained in both the proof and the check.
It must not be replaced by a diagonal code without a further word.

## Symmetric completion and its general form

The addendum gives a distinct response

```text
S = C A = E-Pi_P = C^T D C,
D = I-2 Pi_P.
```

The checker constructs S directly from the old E and the selected
diagonal projector. It does not obtain S from a producer matrix.
It then checks all three other expressions, symmetry, both inverse
orders, determinant one, and `rank(S-I)=32`. Thus the displacement
rank is larger than that of A, although only the same sixteen rows
change from E.

There is a general proof of the congruence. Suppose E is symmetric,
`E=I+UV`, `V_P` is invertible, and `E[P,P]=0`. Set
`B=V_P^-1 V_R`. The zero selected block gives
`U_P=-V_P^-1`, so the selected ordinary block of E is `-B`.
Symmetry then gives `U_R V_P=-B^T`. Therefore

```text
E = [[0,-B],[-B^T,I-B^T B]],
E-Pi_P = [[-I,-B],[-B^T,I-B^T B]]
       = [[I,0],[B^T,I]] [[-I,0],[0,I]] [[I,B],[0,I]].
```

The outer matrices are the transpose pair `C^T,C`. They are units
over the same coefficient ring. Consequently the symmetric
completion is a unit, with

```text
S^-1 = C^-1 D C^-T.
```

This proof does not require the actual block sizes, an eigenvalue
bound, or division by an odd integer. The selected diagonal
completion is enough under its stated zero-minor and factor
hypotheses. In an operator setting with an adjoint, the same
ordered block proof holds with every transpose replaced by the
adjoint, provided E is self-adjoint and the specified inverse
minor exists. It does not make the resulting operator codes free.

In one actual mode block, the literal word first forms
`x_p+d_R^T x_R`, negates the pivot, and adds the signed fanout
of that negated pivot into `x_R`. This is S. It has two signed ADD passes and
one pivot sign. Its reverse word is the exact inverse. The
complete physical word, including H and its inverse, costs
`8*82+8*114+2*470=2508` old real units in each direction.

The selected rows are exactly `-V_P^-1 V`. The late query therefore
costs 1904 units. Its arbitrary target baseline is retained.
Both complete scalar words, both literal inverse orders, and
the late query pass all 640 reverse-output checks.

| Symmetric word | Old real scalar units | Prefix row one-norm | Binary denominator height |
| --- | ---: | ---: | ---: |
| S | 2508 | 22 | 1 |
| Inverse of S | 2508 | 28 | 1 |
| Late S query | 1904 | 24 | 1 |

The ordinary diagonal entries of `S^-1` are nonzero. The original
off-diagonal native grammar therefore does not supply a native
inverse of S by an automatic substitution. The scalar inverse
word is a common-frame service with its own access premise.

## The involution's diagonal metric

Define a second metric M by `M_pp=k-3` at each block pivot and
`M_ii=-1` on its nonpivot coordinates. In a mode block,

```text
A = I+M d d^T.
```

It follows directly that

```text
A^T = M^-1 A M,
A^T M^-1 A = M^-1.
```

The actual physical pair code commutes with M: every selected
large pair has value 3 on both coordinates, every ordinary pair
has value -1 on both, and the small component has no pair code.
The checker verifies the physical identities and all metric
entries. The inverse metric has denominators three and five.

Let Z be any field-diagonal unitary spatial operator that commutes
with M, and put `L=ZA`. No commutation between Z and A is needed:

```text
L^* = A^T Z^-1
    = M^-1 A M Z^-1
    = M^-1 A Z^-1 M
    = M^-1 L^-1 M.
```

This is an ordered identity at every spatial width. It is not a
dyadic implementation of the metric wrapper. A caller that
executes `M^-1` must establish its representation and arithmetic
service. The identity does not require odd arithmetic in every
implementation of `A^T`; the separately checked 3276-unit word
already implements that matrix using dyadic units.

## Native and caller scope

The review supplies exact response matrices, query rows, transfer
weights, scalar implementations, and an actual transpose identity
for the separate native emitter. It does not verify a new native
program. In particular, `A^-1=A` does not imply that the hybrid
FULL/hole output types compose with an old backward input.

The stage responses can differ after routing. Their ordered
composition, legal current-source access, final raw output, helper
progress, and complete recursive cost remain obligations of the
caller. No complete supplier or kappa improvement is claimed.

AI assistance was used. No PR, push, or publication is authorized.
Before any PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
