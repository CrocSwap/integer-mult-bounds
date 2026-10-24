# Exact closure limits for three current-chart scalar codes

Three invertible scalar codes in the actual D25 charts have a monomial
global product only if all three scalar codes are monomial. In addition,
their global product commutes with the intrinsic line operator Q only if
all three scalar codes are diagonal. These conclusions apply at every
payload tensor width f at least 3.

The proof uses one common basis input to separate all paths. It does not
infer operator independence from distinct route matrices. No claim is
made for width one. The logical monomial result also holds at width two.

The actual unitary centre code C and its adjoint C* fail both closure
conditions for all eight choices at the three stages. This removes one
proposed free terminal. It does not give a native decoder lower bound or
an improvement in the complete kappa calculation.

## The code and representation

Let C0, C1, and C2 be constant invertible scalar matrices on the 112
physical ports. Scalars can be Gaussian dyadic numbers. In global
logical coordinates, their stage maps are

```text
A_s = G_s C_s G_s,
G_s = diag(P_(rho_(s,p))),
G_0 = I,
K = A_2 A_1 A_0.
```

Each G_s is only the portwise orthogonal route. The stage entry and exit
maps include their literal translations. They do not include an unpaid
native transform. The proposed all-hole caller has end codes `Q K q`
and K, where `q=Q^-1`. That caller is a separate construction.

Use the position convention `P_A |x> = |A x>`. At width f, the same
route acts on each of f payload columns. A monomial operator has exactly
one nonzero coefficient in each coordinate row and column. It can use
any coordinate permutation, not only a route listed in this packet.

The declared D25 caller uses the full regular owner cover. The tests
below also hold in the spatial representation with the stated tensor
widths. This representation is a permitted covariant subspace of the
regular cover: set

```text
f(d; z_1,...,z_f) = g(d^-1 z_1,...,d^-1 z_f).
```

For the accepted owner view
`M_(h,delta) f(d,z)=f(dh,z+d delta)`, the induced position map on g is
`T_delta P_h`. The intrinsic line at owner d is `d q_p`, so its induced
line on g is q_p. Thus a spatial operator failure is also a failure on
the declared arbitrary-input cover. The direct witnesses below do not
need independence of different owner coordinates.

The covariant point basis has disjoint supports of equal size, namely
the number of owners. A full weighted coordinate permutation preserves
the size of each support. If it preserves the covariant subspace, its
image is a union of complete supports of that same size, so it contains
exactly one. Thus a full-cover monomial induces a spatial monomial.
The spatial monomial obstruction therefore also applies to the declared
full cover, including arbitrary coordinate permutations.

## Exact route signatures

Let Omega be the sum of the first nine unit vectors. Let e1 and e2 be
the sums of the eight unit vectors in fresh blocks 1 and 2.

At port p, the intrinsic line q_p and its eight ordered root-complement
vectors form an orthonormal basis of the first nine coordinates. Their
characteristic-vector identity gives

```text
sum_l b_(p,l) = Omega+q_p.
```

The stage-s route exchanges this complement with fresh block s. It
fixes q_p and the other fresh block. Hence

```text
rho_(1,p) e1 = Omega+q_p,
rho_(2,p) e2 = Omega+q_p,
rho_(1,p) e2 = e2,
rho_(2,p) e1 = e1.
```

All 112 q_p are distinct. The checker verifies these statements against
every literal D25 route. It also checks orthogonality and involution.

For fixed output port p, a path through intermediate ports j and r has
the ordered matrix

```text
M_(p,j,r) = rho_(2,p) rho_(2,j) rho_(1,j) rho_(1,r).
```

Remove the known left factor rho_(2,p), and call the result N_(j,r).
Then

```text
N_(j,r) e2 = Omega+q_j,
N_(j,r) e1 = rho_(2,j) rho_(1,j) (Omega+q_r).
```

The first image gives j. Apply `rho_(1,j) rho_(2,j)` to the second
image to obtain `Omega+q_r`. This gives r. The checker stores all
12,544 signatures and reconstructs both indices from each signature.

Now use ONE position basis input with columns `(e2,e1)` for all paths.
The resulting output pairs are distinct. A linear combination of the
path operators can therefore vanish only if every coefficient vanishes.
This proves logical path independence at f=2. Zero columns extend this
result to larger widths.

## Literal physical affine paths

At a common completed FULL cut, the stage-s view at port p is

```text
W_(s,p) = T_(delta_(s,p)) P_(rho_(s,p)),
delta_(s,p) = literal_stage_alignment.exit_X.
```

The checker verifies that each W is an involution. The physical path is

```text
W_(2,p) W_(2,j) W_(1,j) W_(1,r).
```

Its linear part is M_(p,j,r). Write its translation as t. The checker
calculates t from the four literal translations in their ordered
composition. It does not omit the physical phase correction.

Use ONE position basis input with columns `(0,e2,e1)`. Its output is

```text
(t, M e2+t, M e1+t).
```

The first output gives t. Taking its differences from the other two
gives the two separating linear images. Thus all paths have distinct
outputs on this common input. This proves physical path independence
at f=3. The checker verifies all 12,544 affine output triples for p=0.
Every other p is a common invertible left view, so the result holds for
all output ports. A scalar phase on a path cannot change its support.

## Monomial closure criterion

The input-k to output-p block is

```text
K_(p,k) =
  sum_(j,r) (C2)_(p,j) (C1)_(j,r) (C0)_(r,k) P_(M_(p,j,r)).
```

For fixed p and k, the common input separates all nonzero path terms.
Different input ports are different source coordinates. The exact
number of route terms in port row p is therefore

```text
sum_(j in supp row_p C2)
    sum_(r in supp row_j C1) |supp row_r C0|.
```

If a p,k block has two terms, the common input produces at least two
output coordinates from one input coordinate. This excludes a
monomial operator. If every block has at most one term but port row p
has two terms, they come from different input ports. Every output
coordinate then has two source coordinates, which also excludes a
monomial operator. Thus a monomial product has one term per port row.

Each row of C1 and C0 is nonzero. The support formula first forces each
row of C2 to have one entry. Invertibility makes C2 a scalar monomial
matrix. Its port permutation reaches every row of C1, so C1 is
monomial. The same argument gives C0 monomial. The converse follows
by composition. Therefore

```text
K is monomial  if and only if  C0, C1, and C2 are monomial.
```

This holds at logical width f at least 2 and physical width f at least
3. It permits different matrices at each stage, diagonal phases, signs,
and scalar port permutations. It does not require zero diagonals.

## Exact Q-commutator criterion

Define the Fourier character `|chi>=sum_x (-1)^(chi dot x)|x>`.
An orthogonal A acts on its label by A. An affine path acts by

```text
T_t P_A |chi> = (-1)^(t dot A chi) |A chi>,
Q_p |chi> = i^parity(q_p dot chi) |chi>.
```

Choose a nonzero path coefficient c in block p,k and put A=M_(p,j,r).
For f character columns, its contribution to `QK-KQ` has coefficient

```text
c (-1)^sum_l(t dot A chi_l) [i^L-i^R],
L = sum_l parity(q_p dot A chi_l),
R = sum_l parity(q_k dot chi_l).
```

Use e2,e1 as the first two character columns. They separate every path
output. If `A^T q_p != q_k`, there is a third character that makes the
bracket nonzero. If the exponent difference on the first two columns
is nonzero modulo four, take the third character to be zero. Otherwise,
take a unit vector on which `A^T q_p` and q_k differ. The third parity
difference is then 1 or -1. The chosen path has a unique output, so no
other path cancels it. Literal affine signs are nonzero and are equal
on both sides of the commutator.

It remains to identify the line-preserving paths. The pulled line is

```text
M_(p,j,r)^T q_p = rho_(1,r) rho_(1,j) rho_(2,j) q_p.
```

If j differs from p, `rho_(2,j) q_p` has a nonzero fresh2 component.
Indeed, a root vector has zero fresh2 image under rho_(2,j) only if it
is in the span of q_j; distinct nonzero q_p is not in that span.
Both stage-1 factors fix this component. The result cannot be q_k.

If j=p, the expression is `rho_(1,r) q_p`. If r differs from p, the
same argument gives a nonzero fresh1 component. If j=r=p, the path is
the identity and its line equals q_k only if k=p. Thus

```text
M_(p,j,r)^T q_p = q_k  if and only if  j=r=k=p.
```

If Q commutes with K, every nonzero path must satisfy this condition.
Every nonzero entry of C2 has a nonzero continuation through C1 and C0,
so C2 must be diagonal. Its diagonal entries are nonzero. The same
argument then forces C1 and C0 diagonal. Conversely, diagonal scalar
matrices commute with all portwise routes and lines. Hence, for f at
least 3,

```text
Q K = K Q  if and only if  C0, C1, and C2 are diagonal.
```

The same result holds for the physical code `F K F^-1`: F commutes
with Q, and the checker also includes the literal affine signs. No
claim is made for f=1 or f=2.

## Actual unitary code and consequences

The unitary source is
`new-core-transfer-20261017/low-displacement-20261020/metric-completion-20261020/unitary-v2-normal/UNITARY-COMPLETION.json.gz`,
with decompressed SHA256
`fd3b442caa13104cef4b7c046e1c2781f2ffa216d8d098b4e2a4e51e6063f428`.
The checker reads `code` and `inverse_and_adjoint`, verifies the
adjoint relation, and verifies both unitary product orders.

The physical rows of C have lengths 2, 4, 8, or 16. The rows of C*
have lengths 3, 8, or 12. All eight three-stage choices fail monomial
closure and Q commutation in every output row. For each row of each
choice, the checker stores a common-input two-output basis witness and
an exact three-character commutator witness, including its affine sign.
There are 896 witnesses of each type.

For C/C/C, the exact route count is 54,976, with at least eighteen
terms in each port row. The scalar constant-sector matrix C^3 has
1,066 nonzero entries. This smaller calculation does not certify
closure of the full routed product.

The original sixteen centre readers use all 112 input ports. A scalar
monomial code only permutes and rescales individual inputs. Thirty-two
selected output ports omit an input on which a reader depends. Thus
such a code cannot retain all these readers in those outputs. A new
construction that does not require this retention is outside this
conclusion.

The theorem leaves open a proved consumer for the nonmonomial endpoint,
a native implementation of its conjugated decoder, an operator-valued
code with admitted extra access, and a changed owner or gathered-axis
interface. Route counts are not native child counts.

## Verification, credit, and limits

The route source is
`bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json`,
SHA256
`125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473`.
The new-core lane supplied C and C*. The cover lane supplied the
conditional all-hole caller and the fresh-edge line test. The bridge
lane supplied the literal views. The independent owner-review lane
checked the common-input argument and the diagonal criterion without
importing this checker. Its standalone proof is
`owner-review/unitary-code-closure-review-20261020/REVIEW.md`,
SHA256 `f5bc725b9f14032e5a61341ed73306b45797b90612e256e6e3caa52e6360a3dc`.
This work used AI assistance.

Run with fresh output directories:

```text
python3 -B check_closure.py --out <new-directory>
python3 -O -B check_closure.py --out <another-new-directory>
```

The final normal and optimized outputs must be byte-identical. Checks
cover source hashes, all route signatures, literal affine paths, both
unitary orders, all eight support profiles, both sets of 896 witnesses,
and the 112-port reader support. The general criteria are proved above;
they are not inferred from the eight finite cases.

No native decoder, recursive host, precision bound, or complete supplier
is claimed. No PR, commit, push, or publication is authorized. Before
any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
