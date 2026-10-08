# A stronger exclusion for higher odd subset labels

This follow-up changes no multiplication claim. It closes one tempting route
under the current linear assembly: replacing triples by all odd-sized subsets
and compressing their side circuit. Unlike the previous bounded screen, the
bound below permits **zero auxiliary roles** and covers every ground size in
the stated family. It also permits the cheaper source-span center labels.

For odd `k=2t+1>=5`, take all k-subsets of `[h]`, with `h>=2k`, and the
canonical rational Gram kernel

    P(|S intersect T|),  P(x)=product_{j=1}^t (x-(2j-1)).

The binary scalar gather/scatter is still point incidence. Its odd
off-diagonal intersections are canceled by the side circuit. Retain three
tensor stages and the h point centers, each returned through the zero
component as in the aligned-bit schedule. The statement allows any side
circuit with those center trajectories. It does not cover different scalar
factorizations, higher-rank labels, non-polynomial Gram matrices, or special
subfamilies of the k-subsets.

Under these hypotheses the bit saving is strictly below

    1 / [16 (2*275^3-1)] < 1.503e-9,

and hence the fast-resampling assembly gives `kappa < 7.514e-10`, below the
current `1.624e-9`. Better side circuits alone cannot rescue this family.

## Rank bounds including the cheaper centers

Write `d_t(h)=C(h,t)-C(h,t-1)`. Expand the degree-t polynomial in the
binomial basis `B_j(S,T)=C(|S intersect T|,j)`. Its coefficient of B_t is
`t!`. On the t-th Johnson harmonic level B_j is zero for j<t, whereas B_t
has the positive eigenvalue `C(h-2t,k-t)`. Consequently the ambient label
dimension is at least

    r = d_t(h).

For a fixed point i, restrict the Gram matrix to subsets containing i.
This is the same degree-t polynomial `P(1+x)` on the `(k-1)`-subsets of
`h-1` points. Its t-th harmonic eigenvalue is again nonzero. Therefore
the span of those source labels has dimension at least

    rho = d_t(h-1).

This remains a lower bound if that span is degenerate and the implementation
has to enlarge it to a nondegenerate label. Thus even the cheaper center
trajectory loses at least rho dimensions. This is a lower bound on the
specified return through zero, not a general lower bound on center circuits.

Put `v=C(h,k)`. The all-role endpoint calculation then gives

    N=v^3, m>=r^3, W>=2v^3, L>=3v^2*h*rho,
    eta <= (v-6h*rho)/(2v*r^3).

The lower bound on W makes every auxiliary role free. If the numerator is
nonpositive there is no saving. Otherwise the right side gives an optimistic
upper bound even if the ambient and star dimensions cannot simultaneously
attain their lower bounds.

## Infinite tail and the finite remainder

For `r>=275`, discard all center losses as a further favorable relaxation:

    eta <= 1/(2r^3),
    -log(1-eta)/log(r^3) < 1/[16(2*275^3-1)],

because `log(275^3)>16`. An exact rational logarithm enclosure verifies the
last comparison and the strict comparison to the existing bit saving.

The cases with `r<275` are exactly `t=2,h=10,...,24` and `t=3,h=14`.
Indeed d_t(h) increases with h in this range; the next ranks are
`d_2(25)=275` and `d_3(15)=350`. For t>=4, the least admissible h is
`4t+2`, and `d_t(4t+2)>=d_4(18)=2244`. This last sequence increases:
use `d_t(4t+2)=C(4t+2,t)*(2t+3)/(3t+3)`; the binomial factor more than
doubles at each step, while the second factor decreases by less than a
factor of two.

Only `t=2,h=22,23,24` have a positive optimistic numerator in the finite
remainder. Their exact logarithm enclosures are all below the tail bound.
The largest of these three optimistic scores is approximately `4.159e-10`
at `h=24`; this is not asserted to be the global optimum of the relaxed
family, since the coarser tail bound already proves the desired exclusion.

Run the dependency-free audit with:

```sh
python3 scripts/experiments/label_breakthrough_polynomial_screen.py
```

## Even free triple scratch buys less than a factor of 27

The [kappa-target audit](../../scripts/audit_kappa_targets.py) gives an
all-ground-size ceiling for any side-circuit change
that retains the aligned triple label geometry and its center losses. Make
every auxiliary role free, so W is only `2v^3`. Then

    eta <= (v-6h(h-1))/(2v*h^3),  v=C(h,3).

Positive deficit requires `h>=39`. Exact logarithm enclosures identify h=50
as the unique maximum over `39<=h<200`, with optimistic bit saving
approximately `8.520744882e-8`. For `h>=200`, discarding center losses gives
a decreasing bound, already below that maximum.

Consequently the fast-resampling assembly has
`kappa < 4.260372441e-8`, less than **26.234 times** the present witness,
even with an impossible zero-cost side circuit. Raising kappa by many more
orders therefore needs a changed label dimension, central-loss mechanism,
number of tensor factors, or assembly interface. Ground-size tuning and
side-role compression alone cannot do it under these hypotheses.

## Other label directions considered

A tensor product of a characteristic-separation seed with v labels,
rational rank r and binary central rank c changes `v/(rc)` to its tensor
power, but changes the outer network address dimension to `r^(3t)`.
The singular `h=9` triple seed has `(v,r,c)=(84,8,9)` and ratio `7/6`;
it needs twelve tensor copies before this ratio exceeds six. This is an
uncompetitive address dimension, even before charging a scalar circuit.
For nonsingular triple seeds with h>=10, any genuine tensor amplification
uses at least two copies and therefore has effective rational dimension at
least 100, exceeding the current dimension 50. Smaller triple seeds have
`v/(rc)<=1` and cannot cross the threshold under amplification. This is a
rejection of amplifying the known triple seeds, not of other
characteristic-separation seeds.

Keeping rational dimension h with a different constant-weight set family
would escape the polynomial exclusion if every off-diagonal odd
intersection were a single value c. The rank-one labels would then use
`I-(c/k^2)J`. No suitably dense family or compatible full circuit has been
constructed here. Appending a fixed even core to each triple only recovers
the old triple geometry and supplies no rank gain.
