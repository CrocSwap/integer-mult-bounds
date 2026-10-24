# Exact identity-pivot Schur dimension over every field

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with finite corroboration. For every field K
and every prescribed H in M_d(K), d >= 1, the minimum ambient dimension for
commuting idempotents P,Q with common leading blocks I_d, leading product block
H, and Schur-commutator rank 2d is

```text
n_min(H) = 4d + nullity(H(I-H)).
```

This extends ssafwann's binary fixed-H theorem in
[PR #4671](https://github.com/CrocSwap/integer-mult-bounds/pull/4671), at
`8d2e3bc76aa7d43e5c629daaf1e72d4dd5a81ed9`, to arbitrary characteristic.
The new part is the signed sector formulation and construction outside F2.
The binary conclusion and its six-map argument retain predecessor credit.
No predecessor result is being audited. No kappa is claimed.

In particular, over every field with more than two elements, the unrestricted
identity-pivot minimum is **4d for every d >= 1**. The common identity-pivot
restriction matters. Ryanson Jonathan's #4609 already supplies the unrestricted
ternary scalar minimum four; the general prescribed-H and identity-pivot
statements here are stronger restrictions, not a claim to discover that value.

## Statement

All ranks and nullities are over K. Matrices need not be symmetric. Write

```text
P = [[I,R],[C,D]],  Q = [[I,L],[E,F]],  P²=P, Q²=Q, PQ=QP,
S = D-CR,          Z = F-EL,           K0 = SZ-ZS.
```

Let U=K^d, i:U -> V=K^n be coordinate inclusion, and pi:V -> U be coordinate
projection. The prescribed matrix is H=pi PQ i. Put W=I-H,
a=nullity(H), and b=nullity(W). Then

```text
n_min(H) = 4d+a+b,
(r00,r10,r01,r11) >= (d-b,d+b,d+b,d+a),
rank(P), rank(Q) >= 2d+a+b.
```

Here r_ab is the dimension of the simultaneous (a,b) eigenspace of P,Q.
Every sharp pair obeys the componentwise bounds. All equalities, including
both input-rank bounds, are simultaneously attained for every prescribed H.

The identity nullity(HW)=a+b holds without semisimplicity. Indeed, if HWx=0,
then x=Wx+Hx with Wx in ker H and Hx in ker W. These kernels have zero
intersection because H+W=I. The reverse inclusion is immediate.

## Signed sector criterion

Commuting idempotents give a direct decomposition into four joint eigenspaces,
over every field, using the mutually annihilating projectors

```text
E00=(I-P)(I-Q), E10=P(I-Q), E01=(I-P)Q, E11=PQ.
```

Let Y_j=E_j i:U -> V_j and X_j=pi|V_j:V_j -> U. Compression gives

```text
X00 Y00 = -W,  X10 Y10 = W,  X01 Y01 = W,  X11 Y11 = H.       (1)
```

The minus sign in the 00 sector is essential outside characteristic two.
In particular, the four products sum to I.

Nick Petalas's ordered block factorization from
[PR #4597](https://github.com/CrocSwap/integer-mult-bounds/pull/4597), at
`dfeb8ca729a04aea4aa290438f2ed50a37a9c7cb`, specializes to

```text
K0 = [G-EH, C-E] [R-L; -T+HL],                              (2)
G=(PQ)21, T=(PQ)12.
```

For clarity, define its ambient factors

```text
A = [PQ i-Q i H, (P-Q)i] : U² -> V,
B = [pi(P-Q); -pi PQ+H pi Q] : V -> U².
```

They satisfy pi A=0 and Bi=0. Their nonzero coordinate blocks are exactly
the two factors in (2). In joint-sector coordinates they act as

```text
A(x,y) = (0, Y10 y, -Y01(Hx+y), Y11 W x),
B(v00,v10,v01,v11) = (X10 v10-X01 v01,
                       H X01 v01-W X11 v11).                (3)
```

**Criterion.** rank K0=2d exactly when Y10,Y01,Y11 are injective and
X10,X01,X11 are surjective.

For necessity, rank K0=2d forces A injective and B onto by (2).
If Y10 z=0 for z != 0, (1) gives Hz=z, and A(z,-z)=0.
If Y01 z=0, again Hz=z, and A(z,0)=0.
If Y11 z=0, then Hz=0, and A(z,0)=0.
Each contradicts injectivity. Applying this argument to P transpose and
Q transpose proves surjectivity of the three X maps. Their sector inclusion
ranks are the ranks of E_j transpose i, equal to rank(pi E_j)=rank X_j.
The transpose commutator is minus K0 transpose, so its rank is unchanged.

For sufficiency, injectivity of Y10 first gives y=0 when A(x,y)=0.
The other two sectors give Hx=Wx=0, hence x=0. If a covector (u,v)
annihilates B, evaluating on sectors 10,01,11 and using surjectivity gives
u=0, -u+vH=0, and vW=0. Thus vH=vW=0, so v=0. Therefore B is onto.
Since Bi=0, B restricted to ker pi is onto as well. The product of the
coordinate factors in (2) consequently has rank 2d. This proves the criterion.

## Lower bound and attaining construction

For each active sector j=10,01,11, the criterion and the rank inequality for
a product give rank(X_j Y_j) >= 2d-r_j. Equation (1) therefore gives
r10,r01 >= d+b and r11 >= d+a. The 00 sector only needs
r00 >= rank(-W)=d-b. Their sum is 4d+a+b. Also
rank P=r10+r11 and rank Q=r01+r11, proving the input-rank bounds.

To attain all bounds, factor each active compressed product T through a space
of dimension d+nullity(T). Choose columns N_T complementing im T and set

```text
X_T = [T N_T],  Y_T = [I;0].
```

Then X_T is onto, Y_T is injective and X_T Y_T=T. Use this for W in sectors
10 and 01, and H in sector 11. In sector 00 use a rank factorization of
**-W** through dimension rank W, allowing a zero-dimensional sector.
Stack the four Y maps to make i and concatenate the X maps to make pi.
Equation (1) gives pi i=-W+W+W+H=I.

On this direct sum use P0=diag(0,I,0,I), Q0=diag(0,0,I,I).
Then pi P0 i=pi Q0 i=W+H=I and pi P0 Q0 i=H. Complete i by a basis N of
ker pi. The square matrix M=[i N] is invertible since pi i=I. Thus

```text
P=M^-1 P0 M, Q=M^-1 Q0 M
```

have the prescribed coordinate pivots and product. All six active maps have
the required full ranks, so the criterion attains commutator rank 2d.
The dimension is exactly (d-b)+2(d+b)+(d+a)=4d+a+b.

For |K|>2 choose any lambda outside {0,1} and H=lambda I. Then a=b=0,
so n=4d is attainable and minimal for every d. The exceptional binary scalar
case has minimum five, already proved in #4671. The binary d>=2 minimum
4d also remains that predecessor's result.

## Evidence and reproduction

The standard-library verifier imports no predecessor executable. It constructs
the full P,Q matrices, directly checks idempotence, commutation, pivots,
prescribed product, Schur complements, input ranks, sector dimensions and the
ordered factorization. Its exhaustive fixed-H domains are d=1,2 over
F2,F3,F4,F5, with respectively **18,84,260,630** constructions, totaling 992.
F4 uses x²+x+1, not arithmetic modulo four.

It also checks 12 nonbinary 4d witnesses at d=1,...,4, 12 nondiagonal
size-three product blocks, and 18 premise-preserving controls deleting one
active injection or surjection. Three malformed/singular/capacity inputs are
rejected. An odd-characteristic control distinguishes subtraction from the
binary plus formula. Counts are generated by the executed loops, not estimates.
The universal theorem rests on the written proof, not finite extrapolation.

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/all-field-identity-schur/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/all-field-identity-schur/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/all-field-identity-schur
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/all-field-identity-schur --check-source-history
```

The marker is `PASS_ALL_FIELD_IDENTITY_SCHUR`. The generated stdout receipt
binds all package files by SHA256. It writes no files. No handwritten receipt
is committed. A different CPython 3.12 path may replace the local path.

## Scope and code constraints

This is one common identity-pivot deletion over a field. Nonidentity pivots,
coefficient rings, later orbit distributions and header counts are outside the
claim. Header selection/emission, reads, restoration, stock, precision and the
complete consumer costs remain unknown. No selected scientific cold replay,
Lean, Docker, independent human or proof-kernel review is claimed.

All verifier calls are direct, with no recursion, subprocesses or generated
code. The fixed main program uses only q=2,3,4,5 and d<=4. Mathematical matrices
have at most 18 rows. Elimination enforces a capacity of 24 rows and
48 augmented columns. Every exhaustive scan has at most 625 matrices;
only the current construction and counters persist. Functions stay below
60 lines. Explicit exceptions keep checks active under -O. Warnings are errors.
CPython's dynamic arithmetic and collection allocation is a managed-runtime
deviation from Power of Ten rule 3, with live state bounded by these domains.
No external static analyzer is required or claimed.

The formal-interface-lemma card is explicitly changed to this algebraic side
theorem. It transfers an existing binary structural result to the odd-field
domain relevant to the retained normalizer, without claiming physical admission
or expanding a supplier family. The historical card baseline was attempted
and stopped at omitted sparse-checkout input
`research/fresh-helper-boundary/ARITHMETIC-RESULT.json`; no baseline pass is claimed.

## Open next questions

1. Determine the prescribed-product minimum for common nonidentity scalar
   pivots. First derive the four compressed sector products and the exact
   full-rank criterion. The identity-pivot six-map argument does not supply it.
2. Extend the binary one-block header count of #4678 to odd fields with the
   shared-H dependence retained. First count one fixed scalar sector profile.
   An actual header cover and its physical bill remain separate obligations.

## Credit

ssafwann's #4671 supplies the binary fixed-H theorem, six-map criterion and
split-factor construction; #4657 supplies the identity-pivot precursor.
Nick Petalas's #4597 supplies the ordered block identity, and #4278/#4259/#4228
retain the scalar Schur, laminar-header and single-request lineage.
Ryanson Jonathan's #4609/#4617 and lee-phys's #4634 supply the earlier field
sharpness and dimension constructions. Cinna Davis's #4100 supplies the BIT
request context and retains the normalizer lineage of source527,
commdata2338 and Jose Manuel. No predecessor files or credit lines are changed.
Exact pending-head citations are recorded in TASK.json; they are citations,
not runtime inputs or claims of Git ancestry.
