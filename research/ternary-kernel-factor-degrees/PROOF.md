# Even factor degrees for the ternary prime-power kernel

This scoped arithmetic proof was produced by Nick Petalas. Apache-2.0.

Let a>=1, r=3^a, u a primitive r-th root, K=Q_3(u), and pi=1-u.
Normalize v(pi)=1. The integral kernel of Ali Romman's PR621 is

```text
f_r(Z) = sum_(j=0)^(r-1) a_j Z^j,
a_j = product_(s=j+1)^(r-1) (1-u^s).
```

The product is empty at j=r-1. Multiplying by the nonzero scalar r does
not change factor degrees, so the assertions also apply to P=f_r/r.

## Statement

Every irreducible factor of f_r over K has even degree. More precisely,
an irreducible factor belonging to the k-th Newton slope has degree
divisible by

```text
2 d_k,     d_k = 3/gcd(3,k-1),     1<=k<=a.
```

The first slope block is an irreducible quadratic defining an unramified
extension of K. If a>=2, the second slope block is an irreducible sextic;
its root field has ramification index three and residue degree two.
In particular f_r has no root in K and has no factor of odd degree over
K or over the embedded global cyclotomic field Q(u).

This does not classify all higher slope blocks or give complex root locations.
The claimed irreducibility of the first two blocks is local over K, not
global irreducibility of f_r over Q(u).

## Cited Newton polygon

Hao Yan / FanPUYen's [PR796](https://github.com/CrocSwap/integer-mult-bounds/pull/796),
head `22902155c7875139e43e4fdf15723142d6709bdd`, supplies the following
premises. Its proof is retained at `research/prime-power-newton-audit/PROOF.md`.
They are used here without replaying its scientific verifier or census.

K has residue field F3 and v(3)=e=2*3^(a-1). For m=r-j,

```text
v(a_j) = A(m) = sum_(b=1)^(m-1) 3^(v_3(b)).
```

The k-th edge has root valuation lambda_k=(2k+1)/3 and horizontal length
2*3^(k-1). Its coefficient contacts are exactly

```text
j = r-t*3^(k-1),       t=1,2,3.
```

Every other coefficient is strictly above that edge's supporting line.
Here v_3(3)=1 is the ordinary integer valuation and differs from v.
The new calculation below determines the units at these contacts.

## 1. Leading units of the factors and coefficients

For s=3^h b with 3 not dividing b and 1<=s<r,

```text
(1-u^s)/pi^(3^h) = b mod pi.                         (1)
```

Indeed, factor 1-u^(3^h) as the product of 1-xi*u over all 3^h-th
roots xi. Write xi=u^(c*3^(a-h)). Each exponent 1+c*3^(a-h) is
one modulo three, so (1-xi*u)/pi has residue one. The product therefore
has residue one. Passing to its b-th power multiplies the leading unit
by b, using the geometric sum. This also proves (1) for every primitive
choice of u when pi is defined from that choice.

For m=r-j, replace s by r-b in the coefficient product. Since b<r,
the residue of the unit part of r-b is the negative of the unit part of b.
Consequently

```text
a_(r-m)/pi^A(m) = (-1)^(m-1) V(m-1) mod pi,
V(n) = product_(b=1)^n b/3^(v_3(b)) mod 3.            (2)
```

Set q=3^(k-1) and m=tq with 1<=t<=3. Sorting the factors defining V
by their exact three-adic valuations gives

```text
V(tq-1) = (-1)^(t(k-1)) (t-1)! mod 3.               (3)
```

To see this directly, for each h<k-1 the relevant nonmultiples of three
run through 1..t*3^(k-1-h)-1. Every complete pair of nonzero residues has
product -1. Their total product is (-1)^t. At h=k-1 the remaining
product is (t-1)!, and there are no higher nonempty levels. Thus (3)
has exactly k-1 copies of the first contribution. As q is odd,
(-1)^(tq-1)=(-1)^(t-1). Equations (2)-(3) give the new contact units

```text
c_(k,t) = (-1)^(tk-1) (t-1)! mod 3,
(c_(k,1),c_(k,2),c_(k,3)) = (1,2,2) for odd k,
                            (2,2,1) for even k.     (4)
```

## 2. A quadratic in the residue field of every root

Let alpha be any root with v(alpha)=lambda_k and put q=3^(k-1).
The number lambda_k*q is an integer, including k=1. Thus

```text
beta = alpha^q / pi^(lambda_k*q)
```

belongs to K(alpha) and is a unit. Divide f_r(alpha)=0 by
pi^A(3q)*alpha^(r-3q). Every term has nonnegative valuation. Reducing
modulo the maximal ideal removes every term strictly above the k-th
supporting line. The three contact terms give

```text
c_(k,1) beta_bar^2 + c_(k,2) beta_bar + c_(k,3) = 0.  (5)
```

For odd k this is X^2+2X+2; for even k it is 2X^2+2X+1.
Their discriminants are both two in F3, the nonsquare. Equivalently,
their values at 0,1,2 are respectively (2,2,1) and (1,2,1).
Both quadratics are irreducible. Therefore the residue field of
K(alpha) contains F9, and its degree over F3 is even.

## 3. Field degree and the first two blocks

Write E_alpha and F_alpha for the ramification index and residue degree
of K(alpha)/K. The value group is (1/E_alpha) Z, so the denominator d_k
of lambda_k divides E_alpha. Equation (5) gives 2 dividing F_alpha.
The local-field degree formula is

```text
[K(alpha):K] = E_alpha * F_alpha.
```

It follows that 2d_k divides the degree of alpha's minimal polynomial.
Conjugates over the complete field K have the same valuation, so each
irreducible factor belongs to one edge. This proves the stated divisor.

The slope-one block has degree two. It can contain only this one
irreducible quadratic, with multiplicity one. Its residue degree is two,
so its ramification index is one. The slope-five-thirds block has degree
six. Its factors must have degree divisible by six, so it is a single
irreducible sextic, again with multiplicity one. Its ramification index
is divisible by three and its residue degree is even. Their product six
forces the exact pair (3,2).

Every K-factor is a product of irreducibles, and hence has even degree.
Any factor over Q(u) remains a factor after embedding into K, proving
the global odd-degree exclusion. This last assertion does not identify
the local slope blocks with global factors.

Classical local-field inputs are [J. S. Milne, Algebraic Number Theory,
version 3.08](https://www.jmilne.org/math/CourseNotes/ANTc.pdf): Theorem 7.38
for uniqueness of the extended valuation, Corollary 7.42 and Remark 7.43
for the degree and value-group formulas, and Proposition 7.44 for
K-defined slope blocks. These are cited standard theorems. The new step
is their application through (4)-(5), not a new general factorization theorem.

## Verification and limits

The standalone checker computes the new contact units by exact multiplication
in Z[u]/(u^r-1), cyclotomic reduction, and the integer basis change u=1-pi
for r=3,9,27,81,243. A separate dense uniformizer-basis multiplication
agrees at every distinct contact for r=3,9,27. It also checks literal
unit products through k=9, both residual quadratics, denominator arithmetic
and rejection controls. No predecessor executable is imported or run.

For the arithmetic extraction, Phi_r(1-X) has constant coefficient three,
leading coefficient one, and every intermediate coefficient divisible by
three. Hence 3/pi^e has residue -1. In the pi power basis, terms c_i*pi^i
have valuations e*v_3(c_i)+i with distinct residues modulo e. The unique
minimum determines both the valuation and its leading unit, including
the factor (-1)^v_3(c_i). This explains the normalization used by both
finite coefficient engines; their multiplications use different bases.

The infinite quantifiers and field-degree conclusions rest on this written
proof and its stated premises. The program does not construct p-adic
irreducible factors or solve for roots. It does not establish optimal
degree divisors for k>=3. Complex conditioning, coefficient preparation,
rounded inverse execution, native hosting, ownership/restoration,
compiler/stock/tape costs, supplier admission and the multiplication theorem
are unchanged. All five selected assumptions remain. Independent human and
formal proof-kernel review are unclaimed.

Credit Hao Yan / FanPUYen for the exact coefficient polygon and valuations,
Ali Romman for the kernel, and the classical cyclotomic, Newton-polygon and
local-field lineage. No literature-wide priority is claimed. No predecessor
credit or frozen source is changed.
