# A Lucas formula for the resonant disjointness repair

## Result and dependency boundary

Let F be a field of characteristic five, h=4k with k>=1, and A_h the
disjointness matrix on the nonempty proper subsets of [h]. Let L_0=2,
L_1=1 and L_(n+2)=L_(n+1)+L_n be the Lucas numbers. Then

```text
rank_F(I-A_h) = (4*2^h - 2*L_h - 5)/5.                 (1)
```

This is an explicit evaluation of Brian / JoyboyBrian's PR5221 theorem,
not a new proof of its matrix or endpoint-deletion claims. The precise
premises used from that package are:

1. Its ordinary integer multiplicities c_(h,j) start at (1,0,0,0,0).
2. One step applies the replacements
   `1 -> 2; 2 -> 1+3; 3 -> 2+4; 4 -> 3+5; 5 -> 5+5`.
3. For h=4k>=4, its rank is `2^h-1-b_h`, where `b_h=sum_j c_(h,j)`.

The new step is the arithmetic identity

```text
b_h = (2^h + 2*L_h)/5  for every even h>=0.            (2)
```

Combining the cited rank theorem with (2) gives (1). Consequently (1) is
also the exact number of additive scalar rank-one corrections, under the
same algebraic repair model as PR5221. No physical correction cost is inferred.

## Evaluate the recurrence

Write c_h=(a_h,b_h',d_h,e_h,p_h), using b_h' to distinguish the second
multiplicity from the total block count b_h. The cited replacements give

```text
c_(h+1) = (b_h', a_h+d_h, b_h'+e_h, d_h, e_h+2*p_h).
```

At even h, only the first, third and fifth multiplicities can be nonzero.
At odd h, only the second, fourth and fifth can be nonzero. This follows
inductively from the displayed update, starting at h=0.

Let F_0=0, F_1=1 and F_(n+2)=F_(n+1)+F_n. For every even h>=2,

```text
a_h=F_(h-1),  d_h=F_h,  b_h'=e_h=0.                  (3)
```

Indeed c_2=(1,0,1,0,0). Two steps send the first and third
multiplicities (a,d) to (a+d,a+2d). The Fibonacci recurrence sends
(F_(h-1),F_h) to (F_(h+1),F_(h+2)) by exactly that map. Induction
proves (3). This Fibonacci pattern is classical; it is not new here.

The weighted dimension identity is

```text
sum_(j=1)^5 j*c_(h,j) = 2^h.                         (4)
```

For completeness, each replacement doubles its label's weight:
2=2*1, 1+3=2*2, 2+4=2*3, 3+5=2*4 and 5+5=2*5.
The initial weight is one, so induction gives (4) as an integer identity.

For even h>=2, subtract (4) from five times the block count and use (3):

```text
5*b_h - 2^h = 4*F_(h-1) + 2*F_h
             = 2*(F_(h-1)+F_(h+1))
             = 2*L_h.
```

The identity `L_h=F_(h-1)+F_(h+1)` for h>=1 follows from the two
recurrences and their initial values. At h=0, (2) holds separately since
b_0=1 and L_0=2. This proves (2) for all even h, including its exact
divisibility by five. Substitution in PR5221's rank formula proves (1).

For example (1) gives 9 at h=4 and 185 at h=8, the inherited examples.
Those evaluations are not new independent matrix-rank checks.

## Credit and scope

The source is PR5221 at `ad83478022fed6c1d6a6014096bd8b443e8c9d9a`,
retained in this package's base. Its Jordan rules and endpoint theorem are
cited premises. Its predecessors include Ali Romman / PR4962, Nick
Petalas / PR5173, mikey1201 / PR172, and icekylinx / PR144.

The modular Jordan/Fibonacci description is classical. See David Benson,
[Commutative Banach algebras, representations of finite groups, and
Hilbert space](https://homepages.abdn.ac.uk/d.j.benson/pages/papers/b/benson/banach-book.pdf),
Section 5.1, page 83, for the same tensor-product rules and Fibonacci
multiplicities. The proof above is self-contained arithmetic once PR5221's
premises are granted. The contribution here is the explicit Lucas-number
specialization to the repository's resonant proper-subset repair rank.
No general literature-priority claim is made.

This scoped written proof was produced by Nick Petalas. Independent human
and formal proof-kernel review are unclaimed. Apache-2.0.

This proof does not decide nonresonant ranks, validate PR5221's algebraic
premises, supply a physical caller, or reduce the number of required repairs.
It replaces the recurrence presentation by a closed formula for the same
quantity. All five selected framework assumptions remain. No selected-frontier
change or complete multiplication theorem is claimed.
