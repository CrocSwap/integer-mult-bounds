# A total-cost floor of 200 at peak rank 30

This contribution was produced by Nick Petalas. Apache-2.0.

This is a scoped written mathematical proof. The application uses Hanson Sun's
[PR1564](https://github.com/CrocSwap/integer-mult-bounds/pull/1564) low-rank
classification as a cited premise. It does not reprove or replay that census.
The new step is the support-sensitive factor-span bound below and its cost
consequence. Sylvester's rank inequality and elementary binary linear algebra
are classical; no general literature-priority claim is made.

## The sparse-factor lemma

Let n and d be positive integers with d <= n. Put p=(1,...,1) in F2^n.
For x,y in F2^n, define B_n(x,y)=1+p.x+p.y. Suppose a finite affine
factorization, with repetitions allowed, satisfies

```text
B_n(x,y) = sum_{i=1}^m f_i(x) g_i(y)    over F2, for every x,y,
f_i(x) = a_i.x + c_i,   g_i(y) = b_i.y + e_i,
weight(a_i), weight(b_i) <= d.
```

Then m >= 2 ceil(n/d). Pure constant factors are permitted in this lemma.

Identify each affine form with its n+1 coefficient vector, constant last.
Let F,H have those vectors as their m columns. Put u=(p,0), v=(0,1).
Independence of the affine coordinate functions makes exactness equivalent to

```text
F H^T = K = u v^T + v u^T + v v^T.
```

The vectors u,v are independent; K has rank two, with column and row spaces
both span(u,v). Thus col(F) and col(H) contain both u and v.

Project col(F) to its first n coordinates and choose a basis from the a_i.
If its dimension is r, its basis vectors have weight at most d. Since their
span contains p, the union of their supports contains every coordinate.
Thus rd >= n. The vector v is a nonzero kernel vector of this projection,
so rank(F) >= ceil(n/d)+1. The same holds for H. Sylvester's inequality gives

```text
2 = rank(F H^T) >= rank(F)+rank(H)-m >= 2 ceil(n/d)+2-m.
```

This proves the bound for every finite m, without independence or minimality
of the factors. Zero terms and repetitions cannot escape it.

## Application to the seven-cube

Use exactly PR1564's affine binary model on F2^7, with

```text
G[x,y] = (4/3)(j-1)(j-3)(j-5),  j=7-weight(x XOR y).
```

A nonzero term's cost is rank_Q G[support(f),support(g)]. Its binary sum
must equal B_7 on every port pair. A peak cap of 30 applies term by term.
The precise cited part of PR1564's rank-orbit classification is:

| Cost | Linear parts a,b | Constants |
| --- | --- | --- |
| 20 | a=b, weight(a) in {1,2} | Different |
| 30 | Disjoint supports, ordered weights (1,2), (2,1), or (2,2) | Any |

These are all nonzero terms costing at most 30. Discard zero factors.
Every retained linear part has weight at most two, so the lemma gives
m >= 2 ceil(7/2) = 8.

Let k count cost-30 terms. Cost-20 factors are complementary, so their
product vanishes on x=y. A cost-30 pair has independent linear parts,
so f(x)=g(x)=1 has exactly 2^(7-2)=32 solutions. But B_7(x,x)=1 at
all 128 ports. Each port needs at least one such term, even if other terms
overlap there. Counting with multiplicity gives 32k >= 128, hence k >= 4.
Consequently

```text
C_total = 20(m-k)+30k = 20m+10k >= 20*8+10*4 = 200.
```

PR1564 reports a lower bound of 140 and an eight-term cost-240 witness at
this peak cap. Citing that upper construction gives the new interval
200 <= optimum total cost at peak rank 30 <= 240.
The relaxed counts m=8,k=4 are not asserted to form a decoder. Attainment
of 200, the exact optimum and the sharp number of cost-30 terms remain open.
The predecessor's total-cost-128 optimum, minimum peak 30 and unfavorable
additive stage budget are unchanged.

## Evidence boundary

The checker corroborates the new span lemma on support-one/two generated
spaces through seven variables, computes exact small factorization distances
by an independent complete XOR-state search, and checks general diagonal
facts and boundary controls. It does not recompute seven-cube Gram ranks,
repeat the predecessor's factorization census or replay its upper witness.
The all-n and arbitrary-finite-m claims rest on the written argument.

No physical program, legal producer/consumer boundary, dirty restoration,
native routing, precision, stock, tapes, compiler or outer admission is supplied.
This is not a complete multiplication theorem or a new kappa. Independent
human and formal proof-kernel review are unclaimed.
