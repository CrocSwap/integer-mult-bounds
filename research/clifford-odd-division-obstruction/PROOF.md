# Odd division in the canonical Clifford decoder

This is a scoped negative result with a written proof and exact arithmetic
certificates. It supplies a necessary coefficient requirement for one
decoder. No new kappa follows.

## Statement and boundary

Let `R=Z[i,1/2]`. Use the full projective four-qubit Clifford tensor map
`A_f` from the retained spectral proofs. Its columns are
`vec(U_a^(tensor f))/16^(f/2)`, one Gaussian-dyadic unitary per scalar
coset. There are `N=12,128,668,876,800` columns. The normalization
`16^(f/2)=2^(2f)` is a unit in R. Thus A_f has entries in R. Write

```text
K_f = A_f* A_f,
B_f = A_f^+ = K_f^(-1) A_f*.
```

The star denotes conjugate transpose. The
[odd-width proof](https://github.com/aliromman/integer-mult-bounds/blob/9a8ce06644700ffa576d99316450bcb52835d6dc/research/clifford-odd-width-spectrum/PROOF.md)
and the
[Bell-sector proof](https://github.com/aliromman/integer-mult-bounds/blob/a5aa2ae21ae68338390f584b8fca58ecba0df409/research/clifford-bell-sector-spectrum/PROOF.md)
give full column rank for every odd f>=13 and every f>=14 with
f=2 modulo 4. At every such width, neither K_f^(-1) nor B_f has all
entries in R.

More precisely, the proof gives one positive odd integer M_f>1.
If a positive odd integer D clears all odd denominators of K_f^(-1),
then M_f divides D. If D clears all odd denominators of B_f, then
M_f divides D^2. Consequently every prime divisor of M_f must be
available in any rational localization of R that contains either map.
These are necessary conditions. They need not suffice.

A finite linear circuit with coefficients in R and clean auxiliary
registers has an input-output matrix in R. It therefore cannot implement
the exact full canonical map B_f on arbitrary observations. This does
not rule out another left inverse, a restricted input contract, a
subalphabet, approximation, or a scalar service with odd division.
Widths divisible by four are outside this theorem.

## 1. A rational-eigenvalue lemma

If a finite square matrix C over R has a rational eigenvalue r, then
r belongs to Z[1/2]. Indeed, its monic characteristic polynomial q has
coefficients in R. The product of q with its coefficientwise conjugate
is monic, has coefficients in Z[1/2], and has r as a root. Write r=a/b
in lowest terms. Clear the powers of two in this monic equation and
multiply by the required power of b. Reduction modulo any odd prime
dividing b leaves a nonzero leading term and zero for every other term.
This is a contradiction. Thus b is a power of two.

The same proof works over Z[i,1/2,1/S] for a set S of odd primes.
Every odd prime in the reduced denominator of r must belong to S.
No statement about irrational eigenvalues is needed.

## 2. One eigenvalue at every covered width

The trivial quotient row in the odd sector has eigenvalue P(x). The
trivial minus-stabilizer row in the Bell sector has eigenvalue H(x).
Both are actual blocks of the full Gram matrix, not just a submatrix.
Their coefficient lists, in increasing degree, are

```text
P: [1, 255, 32300, 2034900, 63083328, 946249920,
    6623744000, 19871232000, 19871236096]
H: [1, 136, 8619, 271320, 4205460, 31541664,
    110396096, 165593600, 82796544].

Odd sector:  p=(f-1)/2, sigma=(-1)^floor((f+1)/4).
Bell sector: p=(f-2)/2, sigma=(-1)^(p/2).
Both:        x=sigma*2^(-p), p>=6.
```

The Bell exponent p is even. The following calculation works for either
sign and every integer p>=6. For coefficients a_r, the valuations and
the gaps from the degree-eight term at p=6 are

| Polynomial | v_2(a_0),...,v_2(a_8) | Gaps for r=0,...,7 |
|---|---|---|
| P | 0,0,2,2,6,6,12,12,16 | 32,26,22,16,14,8,8,2 |
| H | 0,3,0,3,2,5,6,9,13 | 35,32,23,20,13,10,5,2 |

For general p the r-th gap increases by `(8-r)(p-6)`. Every gap
is positive. The degree-eight term is therefore the unique term of
least 2-adic valuation. It cannot cancel. In lowest terms,

```text
P(sigma*2^(-p)) = M_f / 2^(8p-16),   M_f odd,
H(sigma*2^(-p)) = M_f / 2^(8p-13),   M_f odd.
```

It remains to exclude M_f=1. All coefficients are positive, so the
value at positive x is at least one. For negative x, put x=-y/64.
The retained certificates express P(-y/64) and H(-y/64) in the
degree-eight Bernstein basis on [0,1]. This basis is nonnegative and
sums to one. The least coefficients are respectively

```text
470624175 / 2^32,
5741614935 / 2^35.
```

The checker expands both certificates into the power basis exactly.
Since the reduced denominators above are at least 2^32 and 2^35,
respectively, M_f is at least 470624175 or 5741614935. In particular,
M_f is positive, odd and greater than one at every covered width.

## 3. Inverse and decoder consequences

The reciprocal of the selected eigenvalue is `2^e/M_f`. If D times
K_f^(-1) has entries in R, the rational-eigenvalue lemma applied to
that matrix gives `D*2^e/M_f` in Z[1/2]. Since M_f is odd, M_f divides D.
Taking D=1 proves the Gram inverse obstruction.

For the canonical map, direct multiplication gives

```text
B_f B_f* = K_f^(-1) A_f* A_f K_f^(-1) = K_f^(-1).
```

If D times B_f has entries in R, then D^2 times K_f^(-1) has entries
in R. Thus M_f divides D^2. In particular B_f cannot have all entries
in R. If `M_f=product q^e_q`, every such odd D is a multiple of
`product q^ceil(e_q/2)`. This divisor is a lower bound, not a claimed
minimum denominator for the complete matrix.

At width 13 the selected numerator is
`3^6*5^2*7^2*17*31=470624175`; the decoder divisor is 498015.
At width 14 it is `3^6*5*7^2*17*31*61=5741614935`; the decoder
divisor is 30378915. Both factorizations are checked by complete trial
division. Other blocks or projectors may impose additional factors.

The denominator argument is classical localization arithmetic. Nick
Petalas's related
[helper-capacity theorem](https://github.com/petalas/integer-mult-bounds/blob/7de4bd6bd4a6f7fae59b90c941ae5a3b9b3e652d/research/odd-budget-helper-capacity/PROOF.md)
uses Smith factors to obtain exact two-sided budgets for a different
real pairing contract. We do not claim priority for that arithmetic or
reuse its capacity conclusion here.

## 4. The left-inverse distinction is necessary

For `A=(1,2)^T`, the Gram scalar is 5. The canonical decoder is
`A^+=(1/5,2/5)`, which is not dyadic. However, `(1,0) A=1` gives a
dyadic left inverse on noise-free data. The checker verifies this
example. Thus a Gram denominator obstruction alone cannot exclude
every exact recovery map on the image of A. The theorem concerns the
canonical map on the entire observation space.

## Verification and limits

The executable authenticates eight retained files. It checks both
symbolic valuation arguments and both positive polynomial identities.
It corroborates them at 59 odd widths from 13 through 129 and 30 Bell
widths from 14 through 130. The proof supplies the infinite quantifier.

A separate calculation constructs all 24 one-qubit projective
operators, checks their 576 products, and forms their full width-six
normalized Gram matrix. Exact Gaussian elimination gives an inverse
whose common denominator is 45 and whose first diagonal entry is 10/9.
Both matrix products are checked against the identity, for 1,152 scalar
entries in total. This is a small-case calibration, not a four-qubit
matrix expansion. Six controls reject altered valuations, invalid
certificates and wrong width domains. A dyadic-unit scalar supplies a
positive control.

The spectral proofs and their character-table identifications remain
mathematical inputs. Their source suites and table archive are not
replayed here. Only generic Gaussian operations are imported from the
retained conditioning checker. No full four-qubit inverse, arbitrary
left-inverse classification, physical decoder, Lean or independent
human acceptance is supplied. Preparation, odd division, precision,
routing, storage, restoration and the complete caller remain unpriced.
All five assumptions and the selected frontier remain unchanged.

## Open next questions

Find sufficient common denominators for the full canonical inverse.
The one-block necessary divisor does not settle that question.

Determine whether the saturated column module admits a different
Gaussian-dyadic left inverse. This requires module information beyond
the Gram spectrum.
