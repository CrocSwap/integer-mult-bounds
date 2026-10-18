# Mixed endpoints and a literal TWOSIDE caller

Let K be a characteristic-zero field. On the fixed 112 nonframe E8 root
lines, let C be the root-evaluation code. Binary support rank means the rank
over F2 of the nine-bit labels in a vector's support. Write pi_S for deletion
of one common set S of coordinates.

**Mixed shortening theorem.** If |S| <= 37 and three vectors q_1,q_2,q_3
have binary support ranks at most 5,5,6 respectively, then

```
dim_K(pi_S(C) intersect span_K(pi_S(q_1),pi_S(q_2),pi_S(q_3))) <= 1.
```

No independence, quotient-basis, modal-shift or real-coefficient hypothesis is
imposed on the pieces. The bound also applies when the rank conditions hold
only after deletion. This is a sufficient threshold, with no sharpness claim.

## Exact inherited premises

PR3249 at `22c7bf316d55e59f381cc9ba833afccc7702fd58` supplies the rank-five
live-support capacity 12 and full E8 A2 projective-fiber capacity 10.
PR3255 at `2977a895c35fa019f53f181edee45177c77ec436` supplies the rank-six
live-support capacity 20 and fiber capacity 16. Their proofs and complete
receipts are retained byte for byte. The global 3,309,747 five-flat and
788,035 six-flat censuses are inherited and are not rerun here.

This package rechecks the 1,120 A2 planes, their P112 union sizes 78 or 80,
the chamber inventories and the three 27-line fibers of a representative
A2 plane. It checks every 2,667 codimension-two subspace and every 127
hyperplanes in each fiber's seven-dimensional binary span, giving maxima
10 and 16. Every nonzero projective fiber has size 27 or 1. As proved in
the retained sources, simple reflections preserve label rank and are
transitive on A2 planes. These uniform transport facts are inherited here.

The standard real Weyl-chamber theorem and the characteristic-zero
rational-nullspace transfer remain written dependencies. Neither finite
checks nor this proof constitute proof-kernel verification.

## Prove classification before counting

Suppose the displayed intersection contains two independent vectors. Choose
codeword lifts c_h,c_k, and let U be the union of their full supports.
Their restricted coordinates are linear combinations of the three pieces.
The global capacities give

```
|U| <= |S| + 12 + 12 + 20 <= 81.
```

For ranks bounded only after deletion, replace each q_i by its zero extension
from the remaining coordinates. This preserves the restricted span and gives
the same capacity bounds. In particular the two lifted directions h,k are
independent. At least 31 live root lines are perpendicular to both. The
rational span of all perpendicular full E8 roots has rank at most six,
since its rational matrix has the two independent vectors h,k in its kernel
over K. Rational matrix rank is unchanged by characteristic-zero extension.

Choose a generic real vector perpendicular to this rational root span. Its
perpendicular roots are exactly the same set: an additional root cannot lie
in the rational span without being perpendicular to h,k, and the other
finitely many coincidences can be avoided. Weyl-chamber classification makes
this subsystem conjugate to a parabolic subsystem of rank at most six.
Among the rank-six parabolics, only E6 has more than 30 root lines. All
lower-rank parabolics embed in one of these. Thus the subsystem is E6 and
the two-dimensional normal plane is an A2 plane. Its P112 nonzero evaluation
union has size at least 78.

This argument does not use the inequality |S|+20<53, which fails at this
support size. It does not use the rank-six quotient-normalization proof in
PR3255. At support 38, the bound becomes 82 and leaves only 30 perpendicular
live roots. The present classification argument then stops. This is not a
counterexample or a sharp boundary for the theorem.

## Count singleton coordinates

Replace h,k by a rational basis of the A2 normal plane. For every t outside
S, a fixed two-by-three matrix A satisfies

```
(c_h(t),c_k(t))^T = A * (q_1(t),q_2(t),q_3(t))^T.
```

Let N=|U minus S|, so N>=78-|S|. At a site in this union where exactly one
piece is nonzero, the evaluation pair is proportional to the corresponding
column of A. The singleton sites assigned to one piece therefore lie in
one A2 projective fiber. A zero column has no singleton sites. The rank
conditions and inherited fiber capacities give at most 10,10,16 such sites
for the three pieces. Their total L is at most 36.

Let M count all piece incidences on U minus S. The global support capacities
give M<=12+12+20=44. Each nonsingleton site has at least two incidences, so

```
2N <= M+L <= 44+36 = 80.
```

But |S|<=37 gives N>=41, hence 82<=80, a contradiction. Arbitrary piece
values, dependencies, cancellations, and incidences outside U are permitted.
No common shift is optimized or assumed modal.

## Apply the theorem to 5^5,6^5

Suppose ten independent pieces span T with dim(T intersect C)>=6 and binary
rank bounds `5,5,5,5,5,6,6,6,6,6`. Delete four weight-six pieces and let T'
be the span of the other six. Projection onto the four deleted coefficients
has rank at most four on T intersect C. Thus

```
dim(T' intersect C) >= 6-4 = 2.
```

The three first rank-five pieces have one common support S with
|S|<=3*12=36. The remaining endpoints have ranks 5,5,6. Restriction to the
complement of S is injective on C because every nonzero codeword has support
at least 53 and 36<53. The two code dimensions therefore survive restriction
and lie in the span of the three restricted endpoints. The theorem gives
dimension at most one. Numerically its contradiction here is 84<=80.

The deleted pieces need no support or coefficient restriction for this
projection argument. Their stated rank-six bounds matter only for binding
the original literal profile. All statements are over K.

## Historical binding, scope and credit

The profile belongs to PR3154's historical TWOSIDE `(b,t)=(6,4)` cell. Its
excess is 35<36. The local transcription and unchanged original bk 2 b functions
agree on every multiset in that cell and reproduce all 69 historical survivors.
The original root/label data bind to the current convention by an invertible
nine-bit map, checked on all 112 entries. Historical survival is not a claim
that the other 68 profiles remain unresolved.

Earlier uniform support thresholds for A2/A3/A4/A5 do not directly cover the
common support 36. A pre-reservation `4,5^9` candidate was rejected because
PR3171 already covers it. No result for that profile is counted here. The
public overlap scan is not an exhaustive logical implication or novelty audit.

The contribution is the mixed-rank proof and this literal caller implication.
It does not establish full C5, the decoder floor, a physical supplier, native
restoration, an all-size multiplication theorem, new kappa or a selected result.
Credit DreamingOfClouds/PR3154, Nick Petalas/PR3249/3255 and the retained
root-simplex/E8/P112 lineage including joaqcoo. Frozen predecessors are unchanged.
