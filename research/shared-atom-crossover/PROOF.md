# Exact crossover at fixed total exponent

This scoped proof was produced by Nick Petalas. Apache-2.0.

## 1. Contract and cited premise

Fix integers I>=1 and w>=1. Three distinct owned Count outputs have borrowed,
canonical, unsigned I-bit exponents e_0,e_1,e_2, each in [0,2^I-1]. The fixed
radix is q and the admitted modulus is q^w. Compare the original and shared
atom-power methods of Tekalign / tekuuu's PR4077, at
90b658330f0357975337b41d67927ae84b72c851. Their successful-input equivalence,
blank-counter lifecycle and complete source-action difference in PROOF.md
sections 3 and 4 are cited premises. This proof does not verify those premises.

An action here is one record, residue-Word or index-Word read, write or unit
move, with unit weight for each of those nine kinds. Let rho be the sum of
one complete radix validator's residue actions, including its cleanup. It is
an input to the theorem, not an estimated or newly measured source cost.
No physical exchange rate among the action kinds is assumed.

Write E=sum e_j, k=#{j:e_j>0}, S=sum popcount(e_j), and
B=sum bitlength(e_j), using bitlength(0)=0. The main theorem concerns E>=2;
sections 2 and 4 also treat E=0 and E=1.

## 2. Complete scalar cost identity

For a positive exponent e with b=bitlength(e), the cited construction tariff
J, rundown R, probe P and index-copy C have the following scalar totals:

```
J(e,I) = 9I - 4b + 8,
R(e,I) = 15e - 5 popcount(e) + 9I + 29,
P(e,I) = 9I + b + 20,
C(I)   = 5I + 7.
```

These follow by adding the three components of each cited vector. In R,
the +4b from the decrement sum cancels the -4b in J. A positive probe
closes its unconsumed counter, with scalar cost 5b+12. For e=0, the cited
R(0,I)=P(0,I), so the original rundown and new probe cancel exactly.

For E>0, PR4077 section 4 therefore gives the exact old-minus-new scalar
saving

```
Delta = (E-1) rho - H(e_0,e_1,e_2;I,w),
H     = 15(w-1)E - 5(w-1)S + B + k(14wI + 36w - 9).       (1)
```

Indeed the non-radix overhead is
sum_(e_j>0) [(w-1)R(e_j,I) + P(e_j,I) + w C(I)]. Substitution yields (1).
This retains every negative savings lane in the original difference before
summing. Output Count operations cancel by the cited successful-input
contract. The identity adds no uncharged runtime selector.

For E=0 both methods have the same probes/rundowns, no radix traversal and
no new index copies, hence Delta=0. Formula (1)'s (E-1)rho term must not be
used in that case. For E=1, exactly one exponent is one, and
H=14wI+46w-18>0; Delta=-H. Strict saving is impossible in both cases.

## 3. An exact maximum with at most 24 states per bit

Let H_max(I,w,E) maximize H over all ordered I-bit triples with sum E.
Every integer E in [0,3(2^I-1)] has such a triple. Put

```
C = 14wI + 36w - 9,
Q(e) = B - 5(w-1)S + Ck.
```

The first term 15(w-1)E in H is fixed. The following maximum-weight
binary carry calculation computes max Q and one attaining triple.

Process bit positions i=I-1,...,0 from most significant to least
significant. A state is (c,A), where c in {0,1,2} is the outgoing carry
from bit i to bit i+1, and A is the three-bit mask of exponents with an
already nonzero higher prefix. Start at (floor(E/2^I),0), with score zero.
For each proposed operand-bit mask u in {0,...,7}, put

```
c' = E_i + 2c - popcount(u),
A' = A OR u.
```

Discard c' outside {0,1,2}. Otherwise move to (c',A') with added score

```
popcount(A') - 5(w-1)popcount(u)
  + C [popcount(A')-popcount(A)].                         (2)
```

Keep the largest score per new state and an attaining prefix. After the
last bit accept only carry zero; maximize over its active masks. Add
15(w-1)E to obtain H_max. Ties may retain any attaining prefix.

To prove the arithmetic constraint, ordinary column addition says
popcount(u)+c'=E_i+2c. The initial high carry and final zero low carry
make these equations equivalent to the exact unreduced sum of the three
I-bit operands. Conversely, every such triple supplies a unique path of
bit masks and carries. Thus this procedure omits no triple and adds none.

For each operand e, its active flag after processing bit i is one exactly
when e>=2^i. Summing that flag over all I positions gives bitlength(e).
The bit-mask populations sum to S. Newly active flags telescope to k.
Consequently the total of (2) is exactly Q(e).

Two prefixes with the same (c,A) have the same legal suffixes and the
same additional scores. Keeping only the larger prefix score therefore
preserves a global optimum. Induction on the processed positions proves
exactness. The stored witness attains it. There are at most 3*8=24 states
and at most 8 proposed masks per state at every bit, so at most 192I mask
trials suffice. This is an arithmetic-operation bound. Integer bit costs,
witness storage and execution of the encoded source caller are separate.
The reference retains at most two state layers, each with 24 records and
three I-bit witness integers per record.

## 4. Sharp uniform affordability criterion

For E>=2, the shared method strictly saves scalar source actions for
EVERY ordered I-bit exponent triple of sum E if and only if

```
(E-1)rho > H_max(I,w,E).                                (3)
```

Sufficiency follows from (1) and the maximum. Necessity follows by
substituting its attaining triple. In particular, for integral rho the
least admissible threshold is

```
rho_min = floor(H_max(I,w,E)/(E-1)) + 1.                 (4)
```

Equality in (3) is not strict saving. The theorem is parametric in rho;
it does not assert that every small integer rho is realized by an actual
radix validator.

The actual child-extent exponents of PR4077 section 5 are
(a,b-a-c,2n-b-c), whose sum is E=2(n-c). When all three fit I bits,
substituting this E into (3) gives a uniform sufficient condition without
knowing their placement. Its necessity is over ALL sum-E triples. Actual
Layout guards, the external gap and native child placements can restrict
that set, so no sharpness claim for those narrower geometries follows.

## 5. First explicit strict improvement

At I=4,w=1,E=10, formula (1) reduces to H=B+83k. If k<=2, then H<=174.
For k=3, having B>=9 would require either lengths at least (3,3,3),
(4,3,2), or (4,4,1), up to order. Their minimum positive sums are 12,
14 and 17 respectively. All exceed 10. Thus B<=8. The triple (4,4,2)
has B=8,k=3, so H_max=257. Equation (4) gives rho_min=29.

At rho=29 the minimum saving is 9*29-257=4 actions. At rho=28 the same
witness loses five actions. The elementary separate bounds k<=3 and
B<=3I instead give H<=261 and only certify integral rho>=30. The exact
sum constraint therefore certifies the additional value rho=29. That
coarse comparison is derived here; it is not a previously published
PR4077 threshold or a newly measured physical speedup.

## 6. Scope and next obligations

The new result is the exact sum-conditioned cost maximum and crossover,
conditional on the cited lane tariffs. Classical binary digit dynamic
programming supplies the method. Finite checks corroborate its new maximum;
they neither audit PR4077's implementation nor replace this all-size proof.

A runtime guard would have to obtain or encode rho and pay for selection.
A physical tariff would have to price the nine action kinds. A complete
caller still needs Context/directory composition, storage and backing,
source admission, payload, control, precision and restoration obligations.
All five selected framework assumptions remain. No complete multiplication
theorem, supplier admission or new kappa is claimed. Independent human and
formal proof-kernel review are unclaimed.
