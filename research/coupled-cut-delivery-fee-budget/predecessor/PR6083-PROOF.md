# A one-cut delivery price screen for the PR6064 opportunity

This is a scoped invoice obstruction, not a universal bound on helper changes.
It uses the exact selected PR6030 bill and answers a particular application of
[PR6064](https://github.com/CrocSwap/integer-mult-bounds/pull/6064).

## Contract

Keep the existing complete targets and paid jobs. At one fixed cut per LOCAL,
add d eligible coordinates. Suppose the native realization satisfies PR6064's
fixed-prefix/full-module hypotheses and makes at most 2d **additional binary
helper splits** available per LOCAL. Each split replaces a rank-h helper by
independent rank-a and rank-(h-a) targets, with 1 <= a < h <= 9. Existing paid
jobs and all other target credits stay unchanged. Charge at least d new paid
jobs of positive integer rank in the **entire** assembly, not d per LOCAL.

These conditions are explicit. In particular, a bound on a module's capacity
increase is not automatically a bound on every changed supplier's productive
targets. The old realized channels must be retained, one additional unit must
produce at most one binary split, and old unused or previously incompatible
channels must not be relabelled as a new capacity increase. A different prefix,
changed boundary, multi-cut reuse, additional carrier targets, or joint delivery
of several coordinates by one paid job requires a new bill.

PR6064 proves that adjoining d coordinates increases the full dyadic pairing
capacity by at most 2d. Its proof and attaining matrix are retained verbatim in
predecessor/PR6064-README.md with the exact source head/hash in PREDECESSOR.json.
The implication above is the declared realization contract, not an admission
of that scalar example as a native P104 supplier.

## Whole-interval price

Write k for the proposed saving, p=1-k, and M(k) for the old complete raw
target moment minus the old complete paid moment. We examine the whole interval

    781451/250000000 <= k <= 17/5000.

The lower endpoint is selected kappa .003125804. The upper endpoint is the
unchanged admitted BIT saving .0034. The exact source contains 18 LOCALs and
no helper rank above 9. By concavity,

    a^p + (h-a)^p - h^p <= h^p (2^k - 1)
                              <= 9 (2^k - 1).

Since log(2)<7/10 and exp(x)<=1/(1-x) for 0<=x<1,

    total extra target credit <= 2 d * 18 * 9 * (7k/10)/(1-7k/10)
                              <= d * 12852/16627
                               < .773 d.

Each positive-rank paid job costs at least 1 at p>0. Therefore the changed
moment is at most M(k) - d*(3775/16627). This grants free scalar basis changes,
normalization, routing, restoration and every other unchanged obligation. Any
additional fees can only hurt this comparison.

It remains to check the small slack between the selected rounded claim and
the raw crossing. The verifier independently reconstructs the complete signed
profile from PR6030's source-bound RESULT.json. Exact rational logarithm and
Taylor bounds give

    M(.003125804) < 13/200,
    M'(k) < -234000                 for every 0 <= k <= .0034.

Consequently, for every integer d>=1 and every k in the stated interval,

    changed moment < 13/200 - d*(3775/16627)
                   <= -538849/3325400
                    < -.162.

Thus this route cannot even retain the selected saving. It cannot increase
kappa under the unchanged BIT and declared one-cut delivery contract. This is
a necessary raw-budget failure; compiler, tail and outer checks cannot rescue
a negative raw moment.

## Rational certificates without a sampling grid

For q in [1,2], z=(q-1)/(q+1) belongs to [0,1/3]. The first 32 terms of
2 sum z^(2j+1)/(2j+1) give a lower bound for log(q); the remaining tail is at
most 2 z^65/(65(1-z^2)). Range reduction gives bounds L_r<=log(r)<=U_r.

For x>=0, P3(x)<=exp(-x)<=P2(x), where

    P2(x)=1-x+x^2/2,   P3(x)=P2(x)-x^3/6.

Both polynomials decrease on the certified x interval [0,1/50]. At the lower
kappa endpoint, sum T_r r P2(k L_r) - sum P_r r P3(k U_r) bounds M from above.
For the derivative, r^(1-k)<=r and r^(1-k)>=r(1-k log r) give the uniform upper
bound

    sum P_r r U_r - sum T_r r L_r (1-(17/5000) U_r).

All arithmetic is rational. No finite grid is substituted for an interval
claim, addressing the failure mode in PR6049.

## Existing eligible coordinates on the selected word

Separately, the unmodified full-subspace census of
[Matarener](https://github.com/Matarener)'s
[PR5994](https://github.com/CrocSwap/integer-mult-bounds/pull/5994) is applied
to the selected PR6030 word. It considers **every role already at the cut
chart**, not only helpers in the boundary group. At 8,734 evaluations across
69 groups and 562 helpers, it finds no pure helper split: six two-sided group
classes have zero cut pairing. The more permissive boundary-support screen
also finds none (1,590 zero cut pairings and 11 zero boundary pairings).

An enlargement by coordinates already in these complete chart banks is a
restriction of a tested domain and therefore cannot bypass that exclusion.
This last statement concerns PR5599's pure-prefix/pure-suffix split contract;
it does not exclude PR5718 corrections or changed scalar programs. It is not
used to silently identify a rational census with PR6064's dyadic capacity.

The census implementation and its criterion belong to PR5994. The contribution
here is the current-word receipt and its applicability to the proposed free
eligibility route, alongside the new whole-interval delivery budget.

## Limits

This does not price a productive carrier, multi-coordinate paid transport,
different recursive boundary, multi-cut lifetime, changed paid trajectory,
new BIT cap or other helper architecture. It is not a complete multiplier,
native admission, global P104 ceiling, independent human review or formal proof
kernel check. The five selected framework assumptions remain.

Prepared by [zxv](https://github.com/zxv), with substantial OpenAI Codex assistance.
Credit [Ali Romman](https://github.com/aliromman)'s cut and P104 lineage,
[DreamingOfClouds](https://github.com/DreamingOfClouds)'s PR6030 word/bill,
[Matarener](https://github.com/Matarener)'s full-subspace census, and the retained
source authors. Apache-2.0.
