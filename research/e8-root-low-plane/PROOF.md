# A root-low correction plane has exact basis tariff 78

Scoped proof and finite exact certificate produced by Nick Petalas.
Apache-2.0. The fixed root/label model and the 29-neighbor opening credit
conorholds' PR3755 and PR4052. No predecessor threshold or scientific
checker is replayed as a deliverable.

## 1. Fixed space and claim

Let K be any field of characteristic zero. Use the following rational
nine-coordinate realization of the 120 E8 root lines. Write R_x for the
listed vectors, and r_x=R_x/3 for the norm-two representatives.

- For 0<=i<j<=8, take R_x=3(e_i-e_j), with label
  u_x=511 XOR 2^i XOR 2^j.
- For each three-element subset A of {0,...,8}, take R_x with entry 2
  on A and -1 elsewhere, with label u_x=sum_{i in A}2^i.

The pairing on the binary nine-space is ordinary dot product. The labels
are distinct and span that space. They give the dense COPY pairing used
in PR4052. This is the A8 model from its retained geometry definitions.

Fix v=(0,1) and a=(0,2), the first two pair roots. Their labels are
u_v=508 and u_a=506. Their scalar inner product is one. Set

```
E_a(x) = r_x dot r_a = (R_x dot R_a)/9,
C = span_K of the eight columns R_x[0],...,R_x[7],
H_v = {x : u_v dot u_x = 0},
e = delta_a,
d = E_a restricted to H_v,
g = d-2e,
f = E_a-d,
D = span_K(e,d) = span_K(e,g),
S = C+D,                 T = span_K(e,g,f).
```

The code C has dimension eight and S has dimension ten. The correction d
has exactly 29 nonzero entries. This is the natural root-low correction
from PR4052's opening, supplemented by its own root coordinate. The
quantifier here concerns this one fixed space, not every correction space
on 29 neighbors.

For q in K^120 let w(q) be the dimension over F2 of the labels at its
nonzero scalar entries. The new result is the exact ordered minimum basis
profile of S:

```
(1,7,7,9,9,9,9,9,9,9).
```

Every basis has sorted weights at least these values coordinate by
coordinate, and a basis attains them. In particular its minimum linear
bill is 78. More generally, for every nondecreasing tariff F on {1,...,9},
the exact minimum is F(1)+2F(7)+7F(9). This includes every positive power
tariff. The statement prices a basis; it is not a complete supplier invoice.

## 2. Complete character-kernel certificate

For a nonzero binary character z define

```
O_z = {x : z dot u_x = 1},
K_z = {q in S : q vanishes on O_z}.
```

Use parameter coordinates (h_0,...,h_7,s,t), with
q_x=sum_j R_x[j]h_j+s delta_a(x)+t d(x). The 120-by-10 matrix M of this
map is injective. Each K_z is therefore the kernel of the submatrix of M
on O_z. The complete exact table is:

| Character condition | K_z | Number |
| --- | --- | ---: |
| z=508 | span(e,g) | 1 |
| z=506 | span(g,f) | 1 |
| z=505 | span(e,f) | 1 |
| z=6 | span(g) | 1 |
| z=3 | span(f) | 1 |
| z dot 506=0, excluding 508 and 505 | span(e) | 253 |
| Every remaining nonzero character | zero | 253 |

These disjoint rows account for all 511 nonzero characters. The executable
certificate constructs each integer submatrix and verifies the listed
kernel by two exact methods:

1. Rational elimination constructs its entire kernel and compares subspaces.
2. Direct integer products show that the prescribed vectors vanish. A
   separately implemented elimination modulo 101 proves matrix rank
   10-dim(K_z). This is a rational rank lower bound; the displayed kernel
   gives the matching upper bound. The prime is fixed and no random rank
   inference is used.

All matrices and displayed vectors are rational. The rational rank and
kernel remain unchanged under extension to K, so this finite certificate
proves the table over every characteristic-zero field. Positive
characteristics are outside the claim.

The pairwise disjoint supports of e,g,f have sizes 1,28,28. Exact binary
elimination gives ranks 1,7,7 on the individual supports, rank eight on
each two-support union, and rank nine on the three-support union. Since
the supports are disjoint, nonzero scalar coefficients cannot cancel
between them. Thus these ranks apply to every coefficient choice, not
only to the displayed rational samples.

## 3. The whole deficient locus and its span

The binary pairing is nondegenerate. Hence w(q)<=8 if and only if there
is a nonzero character z with q in K_z. The table proves

```
{q in S : w(q)<=8}
  = span(e,g) union span(e,f) union span(g,f).
```

Every vector outside this union has weight nine, including a vector in T
whose three coefficients are all nonzero. Within the union, the only
nonzero weight below seven is the e-axis, of weight one. The g- and
f-axes have weight seven. A vector with exactly two nonzero coefficients
has weight eight.

Writing V_k=span_K{q in S : w(q)<=k}, including zero, gives

```
dim V_0 = 0,
dim V_k = 1 for k=1,...,6,
dim V_7 = dim V_8 = 3,
dim V_9 = 10.
```

This is the new structural obstruction. Allowing the mixed weight-seven
word f does not supply eight cheap scalar normal directions. All deficient
words together still span only T. In particular, being a span of deficient
words does not make every member deficient.

## 4. Exact basis bill and attainment

In any basis of S, the number of members of weight at most k cannot
exceed dim V_k. Consequently the first sorted weight is at least one,
the second and third at least seven, and the other seven at least nine.
Equivalently, the integer sum is at least

```
9 dim(S) - sum_{k=0}^8 dim(V_k) = 90-(6+3+3) = 78.
```

The ten vectors e,g,f and the seven code columns indexed
0,1,3,4,5,6,7 form a basis. The missing code column 2 is recovered using
E_a=d+f=2e+g+f and E_a=(R[0]-R[2])/3. The certificate independently checks
their rank ten and exact weights (1,7,7,9,9,9,9,9,9,9). This proves
attainment. The sorted coordinate bounds also prove the nondecreasing
tariff statement without an analytic root search.

## 5. A conditional coupled consequence

Under PR4052's singleton-encoder hypotheses, an exact scalar-active
factorization with actual reader space S has COPY at least 77, provided
each exceptional left ray occurs at most once. The target and transpose
conventions must be those of that source. This follows from its strict-floor
corollary with L=77 and the new basis floor L+1=78. It is a lower bound,
not an exact COPY optimum or an attaining factorization. The source's
singleton classification and coupling argument are cited premises.

This leaves at least five units above 72 in that coupled model. It closes
this natural two-dimensional candidate at the first mixed-low boundary;
it does not extend the general 28-neighbor theorem to arbitrary 29-site
partial quotients. No native realization, physical access/restoration,
compiler, stock, precision/tape or outer-cost obligation is discharged.
