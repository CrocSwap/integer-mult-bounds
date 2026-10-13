# Exhaustive finite relaxation

Per replica the idle stock consists of 672 cap-8 bins and 448 bins of each of
capacities 16, 32 and 48. Nine calls supply respectively 720, 288, 486, 1098 and
1944 helpers of widths 4, 5, 7, 8 and 9. The unused rank mass is therefore

```
M(T) = T*(672*8+448*(16+32+48)-9*3778) = 14382*T.
```

Use PR795's integer width prices `(-1,-20,-8,-2,4)` and capacity bonuses
`(2,4,8,-13)`. For each attainable remainder r define u(r) as the maximum
bonus-plus-width-price over every legal bin count vector leaving r. The
independent checker exhausts 1163 vectors; the producer derives the same table
by an unbounded-knapsack recurrence. In particular `u(0)=0`, `u(48)=-13`.
The sum of bonuses and helper prices is `-3892*T`, so every feasible remainder
profile n satisfies

```
sum_r r*n_r = 14382*T,
sum_r u(r)*n_r >= -3892*T.
```

Eliminate rank 48. For each non-48 remainder define integer credit
`v(r)=48*u(r)+13*r`. The necessary constraints become

```
sum_(r<48) v(r)*n_r >= 150*T,
sum_(r<48) r*n_r == 30*T (mod 48),
sum_(r<48) r*n_r <= 14382*T.
```

Rank zero can be omitted. Only attainable remainders enter the enumeration.
These are necessary conditions; no sufficiency of the signed dual is assumed.

At the fixed successor endpoint

```
z = 1664724476433282815290 / 10^24,
phi(r) = r*(73/r)^z,
c(r) = 48*phi(r)-r*phi(48),
```

every non-48 cost c(r) is strictly positive. The idle contribution is a fixed
mass term plus `sum c(r)*n_r/48`. After dividing by T, every other part of the
moment is the same. Thus comparing normalized excess `sum c(r)*n_r/T` suffices.

The producer obtains an incumbent for each `T=1,...,22` from multisets of at
most four non-48 remainders. Those are only initial bounds. It then exhausts
every count vector whose outward-rounded lower cost does not exceed the largest
incumbent upper cost. Positivity makes this a finite, complete enumeration;
vectors with up to seven non-48 terms are actually visited. A vector outside
that bound cannot beat any of the incumbents. No heuristic pruning is used.

The independent checker treats the producer table only as proposed incumbents.
It recomputes all costs with the separate base-two moment implementation and
multiplies one finite count-vector factor per remainder rank. Each count is
included up to the exact lower-cost cutoff. It independently reaches 3729
complete vectors, checks every applicable mass/congruence/credit constraint for
all 22 values of T, and strictly excludes every competing profile at the
corresponding candidate price. All comparisons use outward rational intervals.

The unique best normalized relaxed profile is T21 with idle
`{48:6292,3:1,1:3}`. Its full U8 moment at z has the independently certified
lower bound

```
1000000000000000000000002624643 / 10^30 > 1.
```

Consequently every feasible whole-owner packing in this family rejects z.
All moments are increasing in the saving exponent, since every child rank is
strictly between zero and 73. No such packing can certify a complex endpoint
at or above z. The companion construction accepts `z-10^-24`.

The retained outer map is monotone in its common saving in this range. To see
this directly, each update is `a_next=s*(1-s+a_old)`; throughout `0<s<0.002`
and `a_old>=0`, its derivative in s is positive, and its derivative in a_old
is s>0. The final map `a -> (1-eta)*(1-2*eta)*a/(1+(1-2*eta)*a)` is increasing.
Using z in place of the admissible complex saving is therefore an upper
relaxation. The unchanged exact outer helper still gives the grid value
`1661957774647029/10^18` and rejects its successor. Thus neither an alternative
replica count nor an alternative whole-helper placement in this fixed family
can improve the reported κ grid using the same outer recipe.

The bound is conditional on the stated finite family and retained accounting.
It neither proves the all-size interfaces nor excludes improvements to them.
