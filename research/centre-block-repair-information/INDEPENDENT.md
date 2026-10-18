# Independent bounded-block information argument

For the declared selected calls 0/4 source model, arbitrary linear repair
observations may mix the sources within each block of a disjoint partition of
physical owners. A global, possibly nonlinear decoder receives every old
transcript and every block repair. If a block has b<=6 owners, its exact minimum
repair dimension remains **104b complex scalars**. This is total information per
block; mixed observations need not be allocated to individual owners.

No paid implementation, recursive rank mass, new kappa, or saving for a block
of seven or more owners is established here.

## Source model and finite premises

Let G be the finite group acting on its regular cover. Every owner g has an
independent source vector x(g) in C^112. Helper and target dirt are held equal in
the executions being compared. Source differences are constant in payload and
spectator factors. The observations are

```
z(g)=R x(g),
y(d)=sum_p H[:,p] x_p(d rho_p),       H=R/4.
```

R has rank eight. Every one- or two-column subset is independent. The 112 route
matrices are distinct involutions in O_73(F_2), and all 12,432 ordered products
rho_p rho_q, p!=q, are different. These finite premises belong to this selected
source pair; they are not general assertions about suppliers.

A repair for block B is an arbitrary complex-linear map E_B of its 112|B|
initial source coordinates to r_B complex scalars. The decoder receives all old
transcripts and all repairs, with arbitrary computation and routing granted.
Other source-dependent observations are excluded. Nonlinear decoding is allowed;
nonlinear encoding by E_B is outside the contract.

The native application inherits the predecessor's common-frame conjugation,
complete first-call constant-source endpoint, and retained local-view/regular-
cover premises. This check does not reprove those native identities. Its
later-row reconstruction explicitly uses the first-call identification of D/T
source differences.

## General counting lemma

Suppose every set of fewer than s columns of R is independent, H has the same
columns up to one common nonzero scalar, routes are distinct, and at most M
ordered pairs p!=q yield any given relative route rho_p^-1 rho_q. For a finite
source set B let S_B be its old observation and T_B its contribution to the
entire later field. A nonzero x_B in both kernels, supported on b active owners,
necessarily satisfies

```
M(b-1) >= s(s-1).
```

Fix an active source owner g. Its nonzero port support P_g has size at least s
because R x(g)=0. These ports go to distinct output owners d_p=g rho_p^-1.
At each such output, the nonzero term H[:,p]x_p(g) must cancel with terms from
at least s-1 other active owners: distinct contributing owners use distinct
port labels, and fewer than s columns are independent.

For a fixed other owner h, sharing an output through ports p,q implies

```
g^-1 h = rho_p^-1 rho_q.
```

Thus g and h share at most M output destinations. Counting the other-owner
incidences needed at the destinations from P_g gives

```
(s-1)|P_g| <= M(b-1).
```

As |P_g|>=s, the lemma follows. This is an all-parameter written implication;
it does not enumerate owners, blocks, group elements, or input coefficients.

## Exact block repair dimension

The checked premises allow s=3 and give M=1. A nonzero joint-kernel vector
therefore requires at least seven active source owners. For every |B|<=6,

```
ker S_B intersect ker T_B = {0}.
```

Vary only the source coordinates in one block B. All other blocks' repairs and
all other old transcripts are zero on this difference. Correctness of any
nonlinear decoder forces

```
ker S_B intersect ker E_B subset ker T_B,
```

hence E_B must be injective on ker S_B. The old observation is a direct sum of
rank-eight maps, so

```
r_B >= dim ker S_B = (112-8)|B| = 104|B|.
```

This argument is unaffected by decoding across partition blocks. Its crucial
restriction is that repairs have disjoint source domains.

For equality choose eight pivot columns J of R. At each owner retain the 104
source coordinates outside J. Subtract their known contribution from z(g) and
invert R[:,J] to recover every source vector, then reconstruct every later
query using the route formula. These 104|B| coordinate reads are permitted by
the block contract. This supplies an abstract information interface only.

Seven owners are merely a necessary threshold for a possible joint-kernel
vector. There is no claim that such a vector exists for seven owners, or that
larger blocks admit a saving.

## Independent finite verification

Run from the repository root:

```
python3 -I -O -B research/centre-block-repair-information/independent.py
```

The checker imports neither the parent checker nor any predecessor checker.
It authenticates these source bytes before decoding unique regular members:

* Archive research/community-frontier1094-audit/selected-replay.tar.gz:
  SHA-256 f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6.
* Canonical word member
  candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz:
  compressed SHA-256
  16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219.
* Route member
  candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json:
  SHA-256 c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa.

It reconstructs old query covectors by reverse exact rational adjoints of the
canonical additions and scalings. Later covectors use the canonical inverse-
transpose generators and cut, then the explicit inherited D/T identification.
The resulting R/H must equal the predecessor receipt exactly, with H=R/4.
Exact rational elimination checks rank eight; one nonzero rational 2x2 minor
is found for each of 6,216 column pairs. These equalities and nonzero rational
minors remain valid over C.

For each route, the independent implementation decomposes a local vector in
the orthonormal chart (q,b_0,...,b_7), fixes its q coefficient, swaps each b_j
coefficient with coordinate 9+j, and fixes coordinates 17 through 72. It checks
all 73 columns for orthogonality and involution, then forms every ordered
distinct-port product on all 73 columns. It does not use the predecessor's
transvection formula. The product-multiplicity histogram must be {1:12432}.
Output includes hashes of the complete pair-minor and route-product
certificates. Negative controls reject a parallel-column alteration and
malformed or collapsed route source/order data; these are premise checks,
not native executions.

Finite coverage is precisely 112 columns, 6,216 unordered column pairs, 112
routes and 12,432 ordered distinct-port products. The written lemma covers
all finite disjoint partitions of the retained regular cover whose blocks
have one through six owners and every complex source difference in the
stated slice. There is no formal-kernel proof, full native cold replay,
nonconstant native-input rank calculation, larger-block classification,
paid recursive bill, or kappa claim.

The source matrix, scalar quarter identity, selected route recipes and native
source interpretation are predecessor work credited in
research/centre-owner-observation-floor/README.md. This independent check and
bounded-block argument were prepared with OpenAI Codex assistance. The checker
is licensed Apache-2.0.
