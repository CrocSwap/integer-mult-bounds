# Independent pricing review of the 90 enlarged masks

By @CubeJerry with substantial OpenAI GPT-6 assistance, 2026-11-08. This review
covers prices, counters, rounding and the derivative bound. Geometry and the
carrier-capacity formula are reviewed separately by the block-helper worker.
There is no new kappa, attained idle cover or change to the admitted BIT budget.

## Exact scope and complete census

The family fixes L=18, pivot p=8, the literal 8|9 uncovered-pivot query word,
and n=18 independent main fields. For kl=0,...,8 and kr=0,...,9, add the kl
left fields nearest the pivot to every right mask and the kr right fields
nearest the pivot to every left mask. These are precisely 90 specified masks,
not all mask enlargements or all pivot positions.

Number coordinates as A=0, F0,...,F7=1,...,8, F9,...,F17=9,...,17. Independently
reconstructed idle demands are

```
d = (kr,1+kr,...,7+kr, 16, 8+kl,7+kl,...,kl),
sum d = 80 + 9 kl + 8 kr.
```

Main targets comprise A at rank145; F_i for i<8 at rank
`8*(9-i+9*[i>=8-kl])+1`; and F_j for j>8 at rank
`8*(j-7+8*[j<=8+kr])+1`. A separate coordinate-mask census matches this formula
at all 90 cases. There are exactly 18 main targets per port and one rank-one
thin query. Their rank-mass surplus after all idle incidences is exactly305.

The complete comparison includes 18 copies of the authenticated #6833 native
helper and paid dictionaries, plus104 copies of the outer targets, thin query
and idle price. Consequently the complete rank-mass surplus is760. Main target
count is1872, native helper target count10152, total12024. The price relaxation
is not an actual paid histogram: it lower-bounds the entire idle bill.

## Rational dual and rounding directions

Let S=10^18, lambda_i be the stored nonnegative integer site weights, and
`c_m=floor(S*l_m)`, where l_m is the rational lower enclosure of
`(8m)^(1-.00337180)`. For every individually admissible job support J, the
geometry checker verifies

```
sum_(i in J) lambda_i <= c_|J| <= S*(8|J|)^(1-.00337180).
```

Summing over any whole-idle cover gives paid idle moment at least
`sum_i d_i lambda_i/S`. This remains a relaxation: it does not assert that
individually allowed carriers can all coexist or that the dual bound is attained.
If extra nonnegative charges or redundant incidences are present, they cannot
improve the margin. Nonnegative prices also allow an at-least-demand cover
relaxation. Such a cover can be trimmed to exact demands by deleting incidences;
job feasibility is hereditary under taking subsets and prices decrease when a
job is shortened. Thus exact-demand covers suffice for the optimistic envelope.

The independent price calculation directly forms the signed native/helper/main
histogram, subtracts104 rank-one thin calls, evaluates its rational upper moment,
and subtracts104 times the integer dual objective/S. This independently agrees
with the author's virtual rank-eight incidence bill plus exact addback. Taking
`ceil(S*upper)` is conservative even for negative bounds. No diagnostic float is
used in any sign or equality test. Flooring tariffs only weakens the paid lower
bound; interval widths and decimal rounding therefore cannot create a false
negative margin.

All90 exact objectives and complete margins matched. The largest upper margin
is at (kl,kr)=(7,8):

```
margin <= -0.210890121535325573.
```

The independent price pass enumerated all23,592,870 possible nonempty support
price inequalities, finding3,720,360 price-violating supports. Price arithmetic
alone does not certify those supports impossible: the author's all90 capacity
checker supplies this geometry implication. The separate geometry reviewer
independently tested every subset at four cases, with exactly matching violation
counts and complete margins: (0,0):41156; (5,5):7584; (7,8):214; (8,9):48.

## Uniform no-reentry bound through kappa=.01

For any fixed exact-demand cover let its job lengths be m_j. Its sorted lengths
are majorized by the Ferrers sequence `v_l=#{i:d_i>=l}`. Indeed the k longest
jobs contribute at most min(k,d_i) incidences at each site, so their partial sum
is at most `sum_i min(k,d_i)`, the first k Ferrers partial sum. Both totals are
sum d. This bound ignores geometry and is therefore valid for every admissible
cover, even when carrier choices vary between covers.

Put `h_k(r)=r^(1-k) ln r`, with h_k(0)=0 on job rank0. For 0<=k<=K=.01 and
8<=r<=144,

```
h_k''(r) = r^(-1-k) * [(1-k)(-k) ln r +1-2k]
          >= r^(-1-k) * [1-K*(2+ln144)] >0.
```

The linear extension from0 to8 is convex too, since
`h_k'(8)-h_k(8)/8=8^(-k)*(1-k ln8)>0`. Thus Karamata gives
`sum_j h_k(8m_j) <= sum_l h_k(8v_l) <= sum_l 8v_l ln(8v_l)`.

Let F(k) be complete target moment minus complete paid moment. Its derivative
is negative target rank-log moments plus positive paid rank-log moments.
Bound every native paid term by its k=0 entropy and every native/main target
term below by its k=K value. Thin rank1 has derivative zero. The resulting
shape-specific, cover-independent upper bound is

```
U =18*sum(native_paid_r*r*ln r)
   +104*sum_l(8v_l*ln(8v_l))
   -18*sum(native_target_r*r^(.99)*ln r)
   -104*sum(main_target_r*r^(.99)*ln r).
```

All90 rational upper bounds are negative. The largest is

```
U <= -166817.003849584388739881   for 0<=k<=.01.
```

The k=.01 powers use the same proved logarithm/Taylor formulas directly;
`.01*ln145<1` satisfies the alternating-series enclosure condition. The frozen
accounting engine's .0034 public guard is not modified. Logarithm upper bounds
are used on positive entropy terms; power and logarithm lower bounds are used
on subtracted target derivatives.

For each cover, its benchmark margin is bounded above by its shape's negative
site-dual margin M. Integration gives `F(k)<=M+(k-.00337180)*U<0` through .01.
The argument applies to every cover separately, so choosing a different cover
at a different exponent cannot reenter the favorable region. This excludes
these90 mask enlargements through the retained rank-power moment criterion on
`[.00337180,.01]`; it is not a new raw crossing location or an exclusion beyond
.01. The ordinary/admitted BIT budget is unchanged.

## Replay and provenance

The reviewed final stripped DUALS.json has SHA256
`3bf3996e901de919d05c757384f3c88dff1e3feedea1a5c8270f44ebc3903c90`.
Every integer field was compared against the90 source records; stripping only
removed diagnostic floats. The arithmetic dependency is the reviewed accounting
verifier SHA256
`116ed12d5aaeef8a5fb084c95db50febb50a9df04825a3506eab633e4abffa3f`.
Its native source authentication is run before pricing. This review shares that
rational interval engine with the author; its mask census, full signed bill,
subset price enumeration and derivative proof were derived separately.

Local executed checks returned PASS_ENLARGEMENT_PRICE_HALF and
PASS_ENLARGED_PIVOT_NO_REENTRY. Portable scripts compare PRICE-RESULT.json and
DERIVATIVE-RESULT.json read-only by default; --emit explicitly regenerates them.
The result records all90 histograms, site demands, objectives, margins, price
violation counts and derivative bounds. Geometry review remains a separate
obligation; no full native operator, compiler or outer theorem replay is claimed.
