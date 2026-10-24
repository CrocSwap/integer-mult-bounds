# Independent review of the unnormalised rank-thirty code

The stated scalar code and its complete dyadic image test pass this
review. There is no material algebra finding. This result uses the
actual 112-port matrices and the chosen thirty source rows. It does
not admit an elementary capture invoice, a native caller, a physical
view, a helper endpoint, or a complete kappa calculation.

The review binds `UNNORMALISED-CODE.md` at SHA256
`a89acbfead19cf4fdbeedafc8544f8910705fd27569f44301e1e8087746a719f`.
`SOURCE-MANIFEST.json` gives all source paths and hashes. The checker
does not import or execute producer code. It reconstructs both code
matrices from U and V. It also computes the selected minor inverse
without using the supplied inverse. Only then does it compare with
the serialized matrices.

## Exact source reconstruction

Let A be the thirty selected physical ports in the source order and
let O be the other eighty-two ports. Exact elimination gives

```text
det(U_A) = -1/256,       U_A^-1 has integer entries.
```

The product VU is exactly the stated direct sum: eight copies of
`[[-4,1],[2,-2]]`, eleven scalar blocks -5, and three scalar blocks
-3. The -3 centre indices are 25, 26, and 27. All off-block entries
are zero.

Put T=U_A^-1 select_A. The independent capture is

```text
(Csum a)_A = V a,
(Csum a)_O = a_O - U_O T a.
```

Put P(c,r)=c-V_O r. The independent inverse is

```text
Csum^-1(c,r) = U B0^-1 P(c,r) + (0,r).
```

Both 112-column inverse orders are the identity. Both matrices
equal the final producer payload. The capture has binary denominator
height one and has no odd denominator. The checker also verifies

```text
Csum = diag(B0,I_O) C0,
P Csum = B0 T.
```

It reconstructs E=I+UV and E^-1=I-U G0^-1 V and compares them with
both actual response matrices. Both inverse orders pass. If
H=diag(G0,I_O), both identities pass on all 112 input columns:

```text
Csum E Csum^-1 = H,
Csum E^-1 Csum^-1 = H^-1.
```

## Complete image criterion over the stated ring

Use R0=Z[i,1/2]. For z=(c,r) in R0^112, let w=Pz. Since U_A is
a unit matrix over R0,

```text
z is in Csum R0^112  if and only if  w is in B0 R0^30.
```

For one two-coordinate block, its inverse is

```text
[[-1/3,-1/6],[-1/3,-2/3]].
```

Both inverse numerators vanish modulo three exactly when
w0-w1 vanishes modulo three. The factor two is a unit in R0.
The scalar -3 and -5 blocks give their coordinate conditions.
These conditions are sufficient as well as necessary; no higher
odd power occurs.

Thus the image Lambda is exactly the joint kernel of L3 and L5
modulo their indicated primes. Each has eleven rows. The checker
reconstructs both matrices, checks every actual capture column, and
checks an exact integral right inverse. The right inverse columns
are unit vectors at these physical ports:

```text
L3: 0,9,11,20,37,41,76,78,18,19,39
L5: 5,3,24,23,1,8,29,26,4,6,31.
```

This verifies surjectivity without a field hypothesis. As a separate
real-matrix check, each Lp has rank eleven and Csum has rank 101
over Fp, for p=3 and p=5. Those rank checks are not the proof of
sufficiency over the Gaussian ring.

The quotient at five is split:

```text
R0/5R0 -> F5 x F5,
a+ib -> (a+2b,a-2b).
```

The checker verifies the bijection and both ring operations on all
625 pairs of elements. In particular, this quotient is not F25.
The right inverses and the Chinese remainder theorem give

```text
R0^112/Lambda is isomorphic to
(R0/3R0)^11 direct-sum (R0/5R0)^11.
```

This is the full quotient. It is not only a count of necessary
congruences.

## Middle operations and arbitrary roles

For a dyadic matrix M, the following three statements are equivalent:

```text
M Lambda is contained in Lambda;
ker(Lp) is contained in ker(Lp M), for p=3,5;
Lp M = Sp Lp modulo p, for some Sp and p=3,5.
```

For necessity, fix a residue in ker Lp. The Chinese remainder
theorem lifts it to a vector with that residue at p and zero residue
at the other prime. This lift belongs to Lambda. Apply M and take
the p residue. For factorization, choose the explicit right inverse
Rp. The vector z-Rp Lp z belongs to ker Lp, so one can take
Sp=Lp M Rp. These arguments work in both residue rings, including
the split ring at five.

Both H and H^-1 act as the identity on both quotients. The checker
verifies Lp H=Lp=Lp H^-1 modulo p. They preserve Lambda in both
directions, not only in one direction.

Two negative controls show why the full premise is needed.

- Set the first two centre coordinates to (1,1), with all other
  code coordinates zero. This is a valid code value. The unit ADD
  from physical port 27 to port 0 changes this pair to (2,1).
  Its first mod3 syndrome is one, and its decoded value is not
  dyadic. Thus even a unit ADD can leave Lambda.
- Start with zero data and an arbitrary helper value one. An ADD
  from that helper to physical port 5 has an identity data-to-data
  block, but its helper column has mod5 syndrome one. The decoded
  data require an odd denominator. A data-only matrix check would
  miss this failure.

For arbitrary additional roles, append zero columns to each Lp
and test the complete M. At field width N, the check acts through
Lp tensor I_N. If a middle operation mixes addresses, its full
operator must pass the check. The scalar 112-coordinate calculation
does not establish that condition for a native middle operation.

## Exact constant decode on valid inputs

The literal B0^-1 word comes from the separately reviewed centre
constant packet. This review replays that word on B0 itself and
on the three actual decoder arguments

```text
P Csum,       P H Csum,       P H^-1 Csum.
```

Every division by three or five is exact on every dyadic input
coefficient at that prefix. There are 22 real divisions by three
and 22 by five in each replay. Every resulting prefix is dyadic.
There is no added odd root scale.

The following bounds apply only to this B0^-1 segment, measured
against the indicated input parameters:

| Initial argument | Maximum stored row norm | Binary height | Odd height |
| --- | ---: | ---: | ---: |
| B0, relative to its thirty parameters | 5 | 0 | 0 |
| P Csum, relative to raw data | 10 | 0 | 0 |
| P H Csum, relative to raw data | 38 | 0 | 0 |
| P H^-1 Csum, relative to raw data | 28 | 2 | 0 |

The omitted B0^-1 word has 204 old real scalar units. Its separate
odd scan counts agree with the stated relative capture saving.
This does not supply the complete capture word or its prefix and
address-map costs. The dyadic capture matrix alone cannot prove
the costs of an arbitrary implementation.

The valid-code result does not remove the common odd-grid premise
for a generic input to B0^-1. It also does not justify a division
on an arbitrary borrowed role. Physical access and sufficient
binary precision remain separate obligations.

## Transport and validation scope

For dyadic units Pleft and Pright, the image of
Pleft Csum Pright is Pleft Lambda. The corresponding image test
is Lp Pleft^-1. This formal transport statement is correct.
The producer's Q transport remains conditional on the stated
phase and common-advance hypotheses. The pair-phase operations
and their costs are not supplied by this image test.

The independent normal and optimized runs have identical receipts:

```text
python3 -I -B check_review.py --out fresh-normal
python3 -I -O -B check_review.py --out fresh-optimized
```

Both return `PASS_INDEPENDENT_UNNORMALISED_CODE_REVIEW`.
The checker also checks that the producer's final normal and
optimized payloads are identical. It checks all pinned input bytes
again after the review computations. No source file changed.
No native 640-column replay was performed in this packet.

No publication is authorized. Before any future PR description,
read `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
