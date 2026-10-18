# A concrete one-third-density replacement geometry

This construction was investigated as an actual replacement for the paired-plane
proposal. It reaches the necessary port density, but its scalar decoder does
not meet the target cost. The accompanying finite controls are not a supplier.

Let q=2^k and work in F_q^3 with the nondegenerate symmetric form

    B((a,t,b),(c,u,d)) = a*d+t*u+b*c.

Take one port E_(a,b)=F_q*(a,1,b) for every (a,b) in F_q^2. Restrict scalars to
F_2 and use Tr(B). The ambient binary dimension is h=3k; each port has binary
dimension k. The restriction to a port is the field trace pairing Tr(x*y),
so each E is nondegenerate. The linear map (a,t,b) -> (t+a,t+a+b,t+b)
identifies B with the standard dot product over F_q. The binary trace form
is likewise nonalternating and nonsingular. The construction therefore has
ordinary binary symplectic frame interpretations, rather than treating a
coefficient-payload multiplicity as extra address dimension.

For two ports, the entire cross pairing is zero exactly when

    a*d+b*c = 1.

Otherwise it has binary rank k. More generally a pairing between spans of
whole ports has rank k times its F_q rank. Thus a nonzero charged scalar-total
query in the inherited support-span tariff costs at least k. The zero-cost
queries have orthogonal support rectangles only.

Two distinct nonzero vectors in F_q^2 have at most one common neighbor in
this free-pair graph: the two equations specifying a common neighbor have
one solution if the vectors are independent and none if they are distinct
scalar multiples. The zero vector is isolated. Hence the graph has no C4.
This fact is what makes the stronger all-q obstruction in
[the field-line audit](../kappa01-fieldline-repair/README.md) applicable.

## Exact finite controls

For an independent check, we construct large sets with no free pairs using
the maximal-arc construction in Mubayi and Williford,
[Theorem 6](https://homepages.math.uic.edu/~mubayi/papers/erdosrenyi_revised.pdf).
For even k, put r=sqrt(q), choose s of absolute trace one, and take all (a,b)
for which Q(a,b)=b^2+a*b+s*a^2 belongs to F_r. There are q*r-q+r such points.
The verifier builds this set and checks every possible free neighbor exactly
for q=4,16,64,256; it does not trust the external cardinality claim.

Here is also a direct algebraic verification of independence. Put
D=a*d+b*c and T=b*d+s*a*c+b*c. Expansion in characteristic two gives

    Q(a,b)*Q(c,d) = T^2+T*D+s*D^2.

If D=1, the right side has absolute trace one, whereas the left side belongs
to F_r and therefore has absolute trace zero. This is a contradiction.
The cardinality follows by taking a=0 (r choices of b); for a nonzero,
put b=a*t. Each t in F_q and each nonzero lambda in F_r determines a unique
a through a^2=lambda/(t^2+t+s). There are q*(r-1) such points.

A fitting matrix restricted to this set is the identity. After removing
zero-cost queries, its rank still forces at least alpha=q*r-q+r charged
rank-one totals, each of tariff at least k. With the ideal three-stage
parameters m=7k and W=2q^2, the full moment is at least

    3*(2/7)^(8/9) + (3*alpha/(2*q^2))*(1/7)^(8/9).

This grants all non-copy overhead free and is still greater than one:

| q | k | Number of ports | Independent set | Moment lower bound |
|---:|---:|---:|---:|---:|
| 4 | 2 | 16 | 6 | 1.084909083443493742 |
| 16 | 4 | 256 | 52 | 1.039189137057888958 |
| 64 | 6 | 4096 | 456 | 1.014770529329213675 |
| 256 | 8 | 65536 | 3856 | 1.000807761612019033 |

At q=1024 this particular lower bound is below one. The replay checks this
scope boundary rather than treating a passing lower bound as a construction.
The separate C4-free complex-minrank theorem rules out the entire family,
including larger q, in the stated scalar-total model.

Run `python3 -I -O -B research/kappa01-repair/field_geometry.py`.
It checks finite field inverses, every trace-multiplication pairing rank,
subfield membership, explicit cocliques, and (at q<=16) all common-neighbor
counts. Moment endpoints use outward rational ninth-root bounds. No floating
point determines acceptance. Sources and external theorem dependencies are
listed here; `FIELD-RESULT.json` is the frozen computed receipt.

## Open next questions

This attempted repair changes actual port geometry but retains scalar totals
and separate active frame changes. To proceed, a construction must change
one of those hypotheses, or use a different high-density block geometry whose
free-pair graph is not covered by the C4-free obstruction. A concrete first
step is an exact small block decoder with its complete rank histogram; no
favorable density or algebraic rank by itself supplies that histogram.

Substantial mathematical and implementation assistance: OpenAI Codex.
