# Price the minimal uncovered-pivot caller (no new kappa)

The uncovered-pivot `D_root` saving in
[#6868](https://github.com/CrocSwap/integer-mult-bounds/pull/6868) does not by itself
price a physical caller. At its uncovered pivot the fieldwise proxy counts one
more idle incidence than a rank-two native stage can have. Correcting this
preserves the required complete rank-mass surplus; it does not create free
surplus.

For the minimal singleton-host pivot masks `[min(i,p),max(i,p)]`, a universal
majorization proof bounds every whole-idle cover in the stated one-field,
whole-field contract, including transport by the literal queries. The best complete optimistic L=18 invoice, including
all native helpers/requests from
[#6833](https://github.com/CrocSwap/integer-mult-bounds/pull/6833), has raw crossing
in **(.0033334095468,.0033334095470)**. This is below #6833's .00337180 proposal.
Balanced arms 8|9 maximize the complete power moment over every pivot position,
not merely its derivative at exponent one. The optimistic paid cover need not
be attainable, so its unfavorable price stops this specified route through the retained
rank-power moment criterion.

[PROOF.md](PROOF.md) gives the contract, physical rank correction, universal
cover bound and balance proof. [RESULT.json](RESULT.json) records the complete
histograms and exact rational interval results. [SOURCE-PINS.json](SOURCE-PINS.json)
authenticates four retained source files, including their pending-source commit
and Git blob IDs. The replay is self-contained and does not require pending
Git objects or run source modules.

Reproduce with standard-library Python:

```sh
python3 -I -B research/p104-uncovered-pivot-root/accounting/verify.py
python3 -I -O -B research/p104-uncovered-pivot-root/accounting/verify.py
```

Expected final line: `PASS_PIVOT_CALLER_AUDIT`.

No selected result changes. This is a scoped exclusion and accounting repair,
not a native-word replay, compiler-admission proof, or general impossibility
result for uncovered pivots. Enlarged masks, changed query words and changed native/target contracts need
their own analysis. All five
framework assumptions remain.

## Open next questions

1. Can enlarged pivot masks change the cover tradeoff enough to beat this
   minimal-mask relaxation? Start by deriving their exact main targets and
   sitewise rank-two idle demands before solving their root algebra.
2. Does a changed query word or physical representation allow whole idle
   transport between the two arms? A proposed representation needs both source and destination
   line/dual equations through the literal query product, then a complete bill.
3. Can the same source profile use a noncoordinate or higher-rank native stage
   contract with a favorable complete margin? Native requests and target losses
   must be included before asserting a caller improvement.

## Attribution and limitations

Prepared by **@CubeJerry with substantial OpenAI GPT-6 assistance**. DreamingOfClouds
supplies #6868's uncovered-pivot observation and #6833's chain caller/native census,
with the original Claude Opus 5.5 disclosure retained. Credit zxv's #6726 caller,
thu-nmrc's whole-idle fusion, Ali Romman's native and caller interfaces, the
@CubeJerry #6805 native split, and the retained native/compiler/interval authors.
The companion root construction was developed independently by another agent
in the same authorized research team; this package owns the complete bill and
cover obstruction. Apache-2.0; retained source notices remain unchanged.
