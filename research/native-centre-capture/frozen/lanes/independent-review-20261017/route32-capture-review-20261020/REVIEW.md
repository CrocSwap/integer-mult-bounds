# Independent review of the route32 response and capture codes

Result: PASS within the scope below. There is no material finding in the
frozen producer packet. This review makes the target of the transported
code explicit.

## Scope and inputs

The producer packet is
`new-core-transfer-20261017/low-displacement-20261020/route32`.
Its freeze hash is
`28354cf747adc5c2a10393f02035a936e0e0fa3f666717b419f4eaaeed1814af`.
The exact input hashes are in `check_review.py` and the receipt.

This review covers the 112 by 112 response, its rational inverse, both
scalar capture codes, their literal inverses, their entry translations,
their costs, and their relation to the actual route labels. It does not
repeat the native phase review. It does not establish a complete supplier,
a physical terminal, a recursive precision bound, or a kappa improvement.

The review checker imports no producer code. It reconstructs the groups
from the frozen cyclic pair geometry and the prior selected-mode
assignment. It evaluates response columns from signed block sums. A
separate reverse interpreter checks each scalar output row. A forward row
interpreter checks the maximum norm and denominator of every prefix.

## Response and selection

Let H be the actual pair code. Its large-sector two by two blocks have
entries in {+1,-1} and satisfy H H^T=2I. It is the identity on the small
sector. Each pair has one route label.

The route is the least element r of the ordered root space for which
q_p dot r=1. The exact class sizes are

```text
r=30: 64 ports
r=45: 32 ports
r=75: 16 ports.
```

Each large vertex has four modes in class 30 and two in class 75.
Each old small eight-clique has four modes in each of classes 30 and 45.
The split gives eight large four-mode blocks, eight large two-mode
blocks, and sixteen small four-mode blocks.

For a block of size k with sign vector d, put

```text
M=I-dd^T,
M^-1=I-dd^T/(k-1).
```

Since d^T d=k, the two products are I. The eigenvalue on d is 1-k;
the other k-1 eigenvalues are 1. Thus each block contributes one to
rank(M-I). The physical response is E=H^-1 M H. It follows that

```text
rank(E-I)=32,
det(E)=(-3)^24(-1)^8=3^24=282429536481.
```

The checker independently verifies both inverse orders on all 112 input
columns. It also verifies the serialized rank32 correction factors, their
ranks, physical symmetry, and the zero physical diagonal.

The old selected-eight principal block is the zero matrix. It is not a
valid selected interface for this response. The packet uses empty
selection, so its ordinary response is the entire invertible E.
The inverse has no odd denominator other than three. It is a rational
unit; a dyadic inverse implementation is not asserted.

## Pivot code

In one block let p be the first port. The direct formula for the pivot
code P is

```text
(Pz)_p = sum_i d_i z_i,
(Pz)_i = d_i z_i-d_p z_p       for i != p.
```

Hence P d=k e_p and the p-th row of P is d^T. Therefore
d^T P^-1=e_p^T, and

```text
P(I-dd^T)P^-1 = I-k e_p e_p^T.
```

The complete code C is the direct sum of these P blocks after H.
It puts the 32 centre sums in existing pivot fields and keeps 80
independent complement coordinates. No zero input is required.

The reverse interpreter verifies all 640 output rows for both literal
inverse orders. All events refer to fields 0 through 111, so the other
528 fields remain arbitrary and unchanged. The full scalar cost is
1,870 units in each direction. The maximum prefix row one-norm is 8
forward and 4 backward. The maximum binary denominator height is zero
forward and three backward.

## Four-mode reflection code

For each four-mode block, put

```text
s=d-2d_p e_p,
S=I-ss^T/2.
```

Then s^T s=4 and s^T d=2. Consequently S^2=I,
rank(S-I)=1, and S d=2d_p e_p. As S is symmetric,

```text
S(I-dd^T)S = I-4 e_p e_p^T.
```

The producer's no-scratch word has the same matrix. To see this
directly, write t=sum_(i!=p) d_i z_i. After its first four groups of
operations, the pivot is (d_p/2)(d_p z_p+t). Each complement output
is then z_i+(d_i d_p/2)z_p-(d_i/2)t. These are the rows of S.

The word has nine unit ADDs and scales -2 and 1/2. Under the source
tariff, its cost is 9*8+4+2=78. The complete code uses this word on
24 four-mode blocks and the pivot word on the eight two-mode blocks.
It includes the actual H pair code.

The independent full cost is 2,486 units in each direction. All 640
literal output rows and both inverse orders pass. The maximum prefix
row one-norm is 8 forward and 4 backward. The maximum binary
denominator height is one forward and two backward. There are no
owned fields, native children, or odd-division events.

For either complete code,

```text
C E C^-1 = D,
D = diag(-3 on 24 pivots, -1 on 8 pivots, +1 on 80 complements).
```

The pivot positions are those in the frozen payload. This equation
does not assign a physical implementation to D^-1 at another frame.
In particular, D^-1 contains 24 factors -1/3.

## Route and ordered-frame use

Every nonzero response coefficient and every scalar ADD in both
capture words connects equal route labels. Thus the response and
codes commute with diag(A_(r_p)) for any chosen spatial operators A_r.
This is an exact block-matrix identity.

For the actual unshifted D11 stages, the transvection direction is
u=(511 xor r) xor e_(8+s), with s=1,2. The checker verifies the
complete eleven columns of each route matrix and their orthogonality.
Equal r gives the same route matrix, permutation, and ordered circuit
P_kappa^-1 F9 P_kappa. It therefore gives the same phase as well.
This permits the stated commutation with these advances.

This conclusion does not cover added field-dependent views or phase
corrections. It does not permit Q to commute with C. The checker
rejects that commutation on the actual payload.

The literal input word is C Q^2: all 112 input translations occur
before the scalar code. The reverse interpreter retains the translation
label on each original source field. It checks all 640 outputs and
the literal spatial inverse. The invoice includes 112 explicit maps
in addition to the scalar invoice.

For clarity, the formal output code q C q diagonalizes the response
Q E q, where q=Q^-1:

```text
(q C q)(Q E q)(Q C^-1 Q)
  = q C E C^-1 Q
  = q D Q
  = D.
```

Only adjacent inverse cancellations and commutation of the diagonal
scalar D with Q are used. This is not a formula for conjugating E
alone, and it does not give a native-free implementation of q C q.

The relative q spaces have dimensions one on the eight two-mode
blocks and three on the other 24 blocks. Only the eight one-dimensional
spaces lie in the common root space. Thus route preservation alone
does not prove a common-root encoding or terminal cost.

## Restricted partition minimum

The reviewed maximal-clique list contains 896 four-cliques and 64
eight-cliques. Every eight-clique has four ports in each small route
class. The largest monochromatic clique has size four.

This gives a sharp rank32 minimum in the following restricted family.
Use the same H. Partition each large vertex into route-homogeneous
blocks, with no block shared by two vertices. Partition the small
sector into route-homogeneous cliques. Use I-dd^T on every block.
Do not mix the large and small sectors.

Each large vertex needs at least two blocks because it has two route
classes. The eight vertices therefore need at least 16 blocks. The
64 small ports need at least 16 cliques because a monochromatic
clique has at most four ports. Each block contributes one to
rank(E-I), so the total rank is at least 32. The packet attains 32.

This is a minimum for this partition family. It is not a lower bound
for arbitrary native responses, other pair codes, shared blocks,
cross-sector constructions, or centre-information encoding.

## Reproduction and credit

Run from the workspace root:

```text
python3 work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/route32-capture-review-20261020/check_review.py --out /tmp/route32-review-normal
python3 -O work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/route32-capture-review-20261020/check_review.py --out /tmp/route32-review-optimized
```

Each output directory must be absent before its run. The expected
status is `PASS_INDEPENDENT_ROUTE32_RESPONSE_AND_CAPTURE`.
The normal and optimized receipts have the same bytes.
The checker also rejects an omitted scalar transfer and the wrong
side of the Q^2 entry translations.

The route split and reflection formula came from the coordinating
researcher. The producer built the exact model and literal words.
The common-root geometry, cyclic pair code, and complete clique
list are earlier campaign inputs, with their hashes in the receipt.
This review adds an independent derivation and exact replay.
AI assistance was used. No publication is authorized.
