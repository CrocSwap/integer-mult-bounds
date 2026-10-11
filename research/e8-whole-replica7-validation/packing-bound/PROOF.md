# Fixed-inventory whole-residual packing bound

Scope: the unchanged complex word, eleven stages in dimension89, whole rank9
residuals, every residual hosted, the same idle-child inventory and fallback bill.
This is not a bound over different words, bank layouts, program portfolios,
stage schedules or operator contracts.

For saving s in(0,1), let f_s(r)=r(89/r)^s. This is strictly concave for r>0.
A rank-r family holding k whole rank9 residuals pays f_s(r-9k). Its minimum
remainder is r mod9, always positive for the ranks8,16,32,48,64 here. Concavity
bounds its cost below by the chord joining the empty and maximally full states.
Thus the saving per hosted residual is at most

`[f_s(r)-f_s(r mod9)] / floor(r/9)`.

Exact rational logarithm/exponential enclosures prove the strict order
rank16 > rank32 > rank48 > rank64 throughout the certified endpoint interval.
The interval calculation is in RESULT.json; there is no floating optimization
in this certificate. Rank8 cannot hold a rank9 residual.

Ignore all window constraints and allow fractional fully occupied families.
Fill ranks16,32,48 in order, then the remaining demand on rank64. This fractional
knapsack relaxation lower-bounds every feasible moment. At seven replicas its
counts are integers: all3,360families of each rank16/32/48 are full;1,840 of the
3,360rank64families are full, and1,520 stay untouched. The6,720rank8families are
unchanged. The emitted whole7 construction realizes exactly this profile while
satisfying all windows. The normalized relaxation scales identically for every
replica count. The number of paid idle children, and hence the fallback charge,
is fixed because none of these remainders can be zero.

At s=0.001268170953505109056983 the exact lower enclosure of the relaxed moment
is already above1. Therefore no packing in this fixed model at any replica count
can have its moment root at or above that upper endpoint. The realized root lies
between this endpoint and the preceding10^-24 grid point. This is a scoped exact
upper bound; it does not validate any of the inherited all-size interfaces.

Reproduce using a completedPR456complex output and the pinned sibling research
packages:

```sh
python -B research/e8-whole-replica7-validation/packing-bound/verify.py \
  /path/to/whole7-output/complex research /path/to/new-bound-output
```

Prepared by Rohan Arun with OpenAI Codex assistance. Exact interval engines and
underlying local word retain their authors' notices in the source packages.
