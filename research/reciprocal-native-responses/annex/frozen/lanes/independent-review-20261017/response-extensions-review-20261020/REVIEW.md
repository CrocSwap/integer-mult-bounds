# Independent review of the reciprocal and rank-sixteen matrices

Both final v2 extension models pass the matrix review. The reciprocal
extension gives the stated inverse response on the large 48-port
sector. The odd-grid extension gives an integer native response whose
full correction rank is 16 and whose exact inverse uses primes five
and seven. The selected ordinary normalization requires prime 31.

This review covers exact response algebra, actual clique geometry,
principal inverses, and the reciprocal extension's four scalar words.
The native phase and frame review is separate. The retained odd-grid
contract and a complete inverse-code implementation are also separate.
Earlier draft extension directories are not inputs to this review.

## Reciprocal large sector

Let E48 be the previously reviewed large response and C be the
fourteen-clique small response. The new response is

```text
A = E48^-T direct_sum C,
A^-1 = E48^T direct_sum C^-1.
```

The independent checker derives these actions from the pinned base
matrices. All 112 columns of each action equal the final extension
payload. Both full inverse orders pass. The raw backward convention
uses -A^T, so its large response is -E48^-1 as claimed.

This is reciprocal native access on the large sector only. The small
response remains C in the raw backward map, whereas C^-1 has nonzero
diagonal and is not the small response emitted by these paths.

Both selected principal blocks remain L. The ordinary inverse passes
both 104-column multiplication orders. The full and ordinary
determinants remain 2^25 and 2^21. The full correction rank remains 30.

The four literal common-frame scalar words are checked on all 112
columns each. Their instructions use arbitrary data fields only and
legal dyadic coefficients. Each costs 3210 real scalar primitives.
The receipt also gives the separately computed prefix row norms.
This scalar check does not establish access to a common frame in a
routed call.

## Rank sixteen from actual signed queries and eight-cliques

The checker constructs eight physical rows K directly from the pinned
pair-code rows and the selected-compatible vertex signs. Every row
has twelve signed unit entries. It verifies

```text
K K^T = 12 I.
```

On the large sector the two independently evaluated actions are

```text
E48 x = x-K^T Kx/2,
E48^-1 x = x-K^T Kx/10.
```

The inverse formula follows from
(K^T K)^2=12 K^T K. Each row direction has eigenvalue -5 under E48;
the complementary directions have eigenvalue one. Thus the large
determinant is 5^8 and its correction rank is eight.

The checker also verifies the actual partition of all 64 small ports
into eight orthonormal eight-cliques. On each clique the response is
I-J and its inverse is I-J/7. Each contributes determinant -7 and
one correction coordinate. The full response is symmetric, has
determinant 35^8, and has correction rank 16.

These formulas are evaluated on every physical basis column and
compared with the final matrices. Both full inverse orders pass.
The supplied U,V factors satisfy E-I=UV on all 112 columns; each
factor has rank 16.

## Which restriction is relaxed

The rank-two theorem requires both the native response and its
inverse to have zero diagonal. It holds over every field of
characteristic zero, including the rationals. Odd denominators
alone do not remove that restriction.

In the rank-sixteen extension, the six-mode response is I-dd^T and
its inverse is I-dd^T/5. The inverse has diagonal 4/5. The construction
therefore uses the inverse as a later scalar code, rather than as
another zero-diagonal response in the cyclic native family.

Its intended opportunity depends on both changes: the general
raw-backward controller must permit this use of scalar inverse codes,
and the retained representation must admit their odd denominators.
The local matrix packet does not prove either complete global duty.
It does not contradict the reviewed reciprocal rank-two minimum or
the disjoint dyadic clique bound.

## The selected split introduces 31

The selected block of E is still L, with L²=I/2. Restricting the
large inverse gives

```text
(E^-1)_SS = (4I+L)/5,
((E^-1)_SS)^-1 = 10(4I-L)/31.
```

Both orders of this eight-dimensional inverse are checked. The
identity uses
(4I+L)(4I-L)=16I-L²=(31/2)I.

Jacobi's identity now gives

```text
det(E_UU) = det(E) det((E^-1)_SS)
         = 7^8 * 31^4 / 16.
```

The supplied ordinary inverse passes both multiplication orders on
all 104 columns and has precisely these reduced denominators:

| Denominator | Nonzero entries |
| ---: | ---: |
| 7 | 512 |
| 31 | 568 |
| 62 | 640 |

Prime five cancels in this ordinary inverse. Prime 31 is present,
not just a possible denominator in a formula. By comparison, the
full E^-1 uses denominators 5, 7, and 10 only.

A grid contract that includes only primes five and seven can cover
the full inverse code, subject to its other obligations. It does not
cover this selected ordinary normalization. An interface with empty
selection can avoid that extra principal-inverse operation. It must
still prove and price its actual controller and terminal.

## Verification and inherited limits

The checker imports only matrix helpers from this lane's pinned
independent base review. It imports no producer or native compiler.
It authenticates the final extension proof, emitter, freeze, and both
decompressed payloads. It also authenticates the underlying base
matrix and geometry.

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/response-extensions-review-20261020/check_extensions.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/response-extensions-review-20261020/check_extensions.py
```

The expected status is `PASS_INDEPENDENT_RESPONSE_EXTENSIONS`.
The receipts must be byte-identical.

This review does not check the native event streams, their borrowed
state, exact phases, frame adapters, or recursive child invoices.
Those belong to the separate native review. It also does not price
division by five, seven, or 31, prove root-stream conversion, or give
an odd-denominator height bound. The native-escape grid packet owns
those representation duties. No completed supplier or exponent
improvement follows from this matrix review alone.

The new-core-transfer lane supplied the two extension models. The
root and earlier pair-code work supplied the underlying responses.
This lane supplied the independent matrix and principal-inverse
checks. OpenAI Codex assisted the work. No PR or publication is
authorized. Before any PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
