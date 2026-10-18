# Quadratic augmentation of the five-cube parity code

This is a finite, computer-assisted structural result. It is not a formal
proof of the multiplication theorem or an implemented supplier.

## Statement

Use PR958/PR1046's 32 ports `x in F2^5`, with

```text
j(x,y) = 5 - HammingDistance(x,y)
G[x,y] = 2(j(x,y)-1)(j(x,y)-3)                 over Q
B[x,y] = 1 + parity(x) + parity(y)            over F2.
```

Let `E=1+parity` and `O=parity`. For a Boolean polynomial `h` of degree
at most two, outside `U=span_F2{E,O}`, define `C_h=span_F2{E,O,h}`.
Allow any finite list of nonzero functions `f_i,g_i in C_h` satisfying

```text
sum_i f_i(x) g_i(y) = B[x,y]                  over F2, for all x,y.
cost = sum_i rank_Q G[supp(f_i),supp(g_i)].
```

Both factors must lie in the **same** code `C_h`. The factors may differ,
repeat, cancel or have zero pairing rank. There is no term-count cap.
The nonlinear functions here select ports; messages remain linear XOR
sums of input data.

**Result.** The minimum cost is exactly **32** for each of the **16,383**
distinct codes. Of these, **16,368** have a nonzero quadratic part. In
every such code, requiring each term's rank to be at most **15** forces
cost at least **34**, or makes the factorization impossible. The bound
34 is attained in exactly **60** of these codes. In particular, any
cost-32 factorization in a genuinely quadratic code has a rank-16 term.

The two parity totals already attain 32; that value and witness belong
to PR1046 and its predecessors. PR1177 separately treats arbitrary
masks with at most three terms. The new coverage here is every term
count in every common quadratic-augmented parity code.

## Complete domain and symmetry reduction

Boolean polynomials of degree at most two in five variables have the
16 independent squarefree monomials `1`, five `x_i`, and ten `x_i*x_j`.
Quotienting by `U=span{1,parity}` leaves dimension 14. Each nonzero
quotient element defines one three-dimensional code, since the scalar
field is F2. Thus there are `2^14-1=16383` codes. Exactly `2^4-1=15`
are affine; the remaining 16368 are genuinely quadratic.

The generator represents each coset by constant coefficient zero and
`x_4` coefficient zero. Its fourteen bits encode `x_0,...,x_3`, followed
by the ten quadratic monomials in lexicographic pair order.

Coordinate flips and coordinate permutations preserve Hamming distance,
G and B. They preserve degree and U and consequently carry a code's
factorizations to those of the image code, with identical termwise
costs. The nine generators are the five flips and four adjacent swaps.
The certificate contains a transport tree for **every** nonzero quotient
element, rooted at **64** representatives. Closure under all nine
generators proves these connected classes are precisely the orbits.

The separate checker evaluates all 65536 polynomials and all four
members of each quotient class. It checks the transport edges using
polynomial substitution, whereas the generator uses truth-table
permutations. It also checks each proposed isometry on all port pairs.
No unverified symmetry classification is a premise.

## Why 512 states cover arbitrarily many terms

Fix a representative. Let F be the 32-by-3 binary evaluation matrix
with columns E,O,h. It has column rank three. Consequently the map
`M -> F M F^t` on 3-by-3 binary matrices is injective: a binary left
inverse L of F recovers `M=L(FMF^t)L^t`.

A nonzero factor is specified by one of seven coefficient vectors.
There are therefore **49 ordered** allowed dyads `a b^t`, with exact
weights `w(a,b)=rank_Q G[supp(Fa),supp(Fb)]`. Factorization of B is
equivalent to their XOR sum being

```text
M_B = diag(1,1,0).
```

The 512 binary 3-by-3 matrices form a graph: from state M, a term
`(a,b)` moves to `M + a b^t` and costs `w(a,b)`. Every finite
factorization is a path from zero to M_B, and conversely. This includes
overcomplete decompositions and arbitrary repetitions. Zero-weight
edges are retained. No positive per-term bound or bounded word length
is used to exclude a cheaper factorization.

For every representative, the package computes all 49 rational ranks
and emits a potential d on the reachable states, together with an
attaining word. The independent checker verifies

```text
d(0)=0,
|d(M+a b^t)-d(M)| <= w(a,b)                   for every allowed edge.
```

Summing along any path proves its cost is at least `d(M_B)`.
The displayed word attains this value and is checked on all 1024 port
pairs. This proves the minimum without trusting Dijkstra's algorithm
or its stopping rule. The unrestricted certificates check **1,605,632**
directed edge inequalities. A second set retains only edges of rank
at most 15. Unreachable targets are certified by the exact binary span
of the allowed dyads; the checker recomputes that span.

Integer elimination with gcd normalization generates the weights.
The separate checker uses rational `Fraction` elimination on all
**3,136 ordered** restricted Gram matrices. Neither uses floating-point
ranks, a modular-rank guess, or predecessor executable code.

## Sharp rank-15 tradeoff

The capped minima, weighted by the number of codes in each orbit, are:

| Minimum total with each rank at most 15 | Codes |
|---|---:|
| 32 (affine codes only) | 15 |
| 34 | 60 |
| 35 | 180 |
| 38 | 240 |
| 39 | 690 |
| 41 | 900 |
| 44 | 80 |
| 45 | 3660 |
| 52 | 3808 |
| No such factorization | 6750 |

An attaining representative for 34 is code 7920:

```text
h = x0*x1 + x0*x2 + x0*x3 + x0*x4
  + x1*x3 + x1*x4 + x2*x3 + x2*x4              over F2.

B = E h^t + O (E+O+h)^t + (E+O)(E+h)^t.
term ranks = 13, 13, 8; total = 34.
```

This witness lies in the three-total parameterization described by
Ross Richardson's pending PR1177. The new certificate proves that
adding more terms within these codes cannot beat 34 under the cap.
It does not claim a new three-total identity or priority for that family.

## Accounting implication and limits

Retain PR1046's explicit additive per-total copy pricing and per-replica
stage ledger, with `v=32` and `s>=3`:

```text
D <= (s-1)*v - s*cost <= (s-1)*32 - s*32 = -32.
```

This grants source access, gathers, arithmetic, helpers, frame changes,
restoration, idle work and all other recursive/precision/hosting expenses
zero additional cost. Nonnegative extra expenses cannot create a positive
deficit. With a genuinely quadratic code and the rank-15 cap the bound
is stronger: `D <= -32-2s`. This is an optimistic exclusion within the
stated ledger, not a proposed complete supplier invoice.

The result excludes different source/reader codes, more than one
additional independent mask, higher-degree masks, other cubes or Grams,
masked rather than all-pairs identities, interacting data messages, and
changed copying/stage accounting. Source-access realization, native
frames, physical precision, restoration, whole-call hosting, bit H1-H5,
all-size compilation and analytic transfer are not discharged. The
selected frontier is unchanged. No new kappa, runtime gain, full cold
supplier replay, proof-assistant verification or human review is claimed.
