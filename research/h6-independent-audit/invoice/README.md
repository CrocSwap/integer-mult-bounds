# Independent H6 fixed-invoice audit

The imported H6 arithmetic is correct for its stated complex invoice. The
historical PR890 and pending PR1424 boundaries reproduce, and a fresh comparison
with `certificates/selected-result.json` gives **79,880 / 88,765 / 79,778 helpers**
for L=3/5/7. This is a nominal budget comparison, with **no new κ and no
construction claim**.

The source H6 package is attributed to DreamingOfClouds at commit
`b496aed769dd724cd1ff6b921cade626562be27b`; its inherited banked accounting,
geometry and COSTS screens are PR606 by Dominik Scholz. All source files remain
unchanged. The independent oracle and receipt are confined to this directory.
The concurrent [discussion1635](https://github.com/CrocSwap/integer-mult-bounds/discussions/1635)
by an664 also audits fixed helper thresholds. This work claims an independent
rational-series replay and the explicit COSTS/banked-model qualification;
it does not claim novelty of the published helper boundaries.

## Reproduce

From the repository root, with Python >=3.11 and its standard library:

```sh
python3 -B research/h6-independent-audit/invoice/verify.py
```

The command writes `RESULT.json` deterministically. It constructs the terms
independently, certifies target pressures, checks adjacent strict signs, compares
both original comparison modes, and requires the original price script's output
to equal its published output. The original invoice is imported only for these
differential checks. Deliberately omitting padding or replacing [1,7,8,1] by
[17] changes every audited boundary; the receipt records the altered counts.

## Audited accounting

The fixed inputs are N=30,960, h=17, data path [16], helper path [1,7,8,1],
ordinary zero-to-full helpers, and center histogram {17:256,15:560}. Thus
C=12,752, m=16L+1, W0=(L-1)N, and D=W0-LC. The base pressure consists of
active mass 2NL·16 at rank16, center masses L·17·256 and L·15·560 at their
respective ranks, and the explicitly retained idle masses 2N·r at rank r.

| L | m | D | q=floor(m/17) | pad=m-17q | idle ranks |
|---|---:|---:|---:|---:|---|
| 3 | 49 | 23,664 | 2 | 15 | none |
| 5 | 81 | 60,080 | 4 | 13 | 32,32,16 |
| 7 | 113 | 96,496 | 6 | 11 | 64,32,16,32,64,16 |

One helper adds stock L/q and rank mass Lm/q. Consequently D is unchanged.
At alpha=κ/(1-κ), its positive pressure is

```
P_helper = L * [ Σ(r in [1,7,8,1]) r*((m/r)^alpha-1)
                + (pad/q)*((m/pad)^alpha-1) ].
```

The oracle bounds logarithms by a 64-term atanh series with an explicit
geometric tail, and exponentials by a degree32 Taylor series with an explicit
tail. Every operation is rational; outward rounding to denominator 10^60
preserves enclosures. At the exact target it encloses
(D-P_base)/P_helper in a single open unit interval. The adjacent certified
slacks satisfy D-P_base-R*P_helper>0 and
D-P_base-(R+1)*P_helper<0.

This also proves the global helper-count boundary for each fixed L: for alpha>0,
P_helper>0, so pressure increases strictly with R. Every child base exceeds one,
so pressure increases strictly with alpha. The proof requires no sampled
monotonicity assumption and no floating nomination. It does not optimize L.

| exact target | L3 R* | L5 R* | L7 R* |
|---|---:|---:|---:|
| PR890 checkpoint, 0.001661957774647029 | 80,558 | 89,683 | 80,753 |
| PR1424 pending title, 0.001676855229071321886206381217337893 | 79,617 | 88,409 | 79,399 |
| selected record, 0.001672660197076918 | 79,880 | 88,765 | 79,778 |

PR890's rounded target 0.001661957775 gives the same boundaries. The original
float and exact scaled-lower-endpoint conventions both agree with these
independent true-root boundaries. Both complete source root intervals lie
strictly on the required side of each target, so interval width and endpoint
rounding cannot change these decisions.

For the selected record, N/R* is about 0.38758 / 0.34879 / 0.38808 respectively.
These numbers express a hypothetical compensation demand per helper; they do
not establish helper capacity. PR606's full real compensation rank 30,960 is a
rank-one rectangle lower bound, with reusable arithmetic DAGs explicitly outside
that consequence.

## Paper ratio qualification

The reported ×1.538281 is correctly the ratio of COSTS.txt's printed
zero-helper screens, exactly 6,945,535,353/4,515,128,332. The independently
recertified fixed-stage COSTS root intervals bound their true ratio between
1.538280828721049644277917 and 1.538280828723830455555642.

This is a **COSTS-screen comparison**, rather than a ratio of the banked
invoices. `costs.instance` relaxes idle child rank to max(r,h), whereas
`banked.base` charges actual idle ranks, splitting only when the child cap
requires it. The E8 reference's L5 rank8 idle slot is relaxed to rank9 by COSTS.
Its actual banked zero-helper L5 interval is
[0.004476887197386231,0.004476887197391187], below the COSTS reference
[0.004515128332412823,0.004515128332417779]. The Pauli L3 optimum has no idle
slots. This audit recertifies the two fixed-stage root intervals; it does not
repeat PR606's inherited global odd-stage optimizer or tail proof.

## Provenance and limits

The receipt binds the exact H6 and PR606 sources, historical PR890 checkpoint,
PR1424 packet head `bfe423c24555baf35dab991a8d6fe723a038945c`, and selected
record, review and source manifest with SHA256. PR1424 is retained as a numerical
planning target; the maintainer efficient500 review leaves its PR1319-family
admission unresolved. The selected record names PR1094's reviewed conditional
finite construction and `make frontier1094-verify`; that construction has not
been replayed or repriced by this invoice audit.

Missing obligations remain: a scalar compensation word, legal frame histories
and restoration chronology, complete encoder and spectator costs, physical
helper loading and banking, a compatible bit supplier, and outer transfer. A
uniform helper path does not cover arbitrary routes or shared-stage savings.
No theorem or architecture-wide barrier follows.

## Open next questions

- Realize a compensated dirty-state word and recount its actual data and helper
  paths. First certify the complete word and frame histories; then replace this
  planning invoice with the emitted inventory.
- Establish a capacity/chronology lemma for the proposed helpers. The real-rank
  ratio alone gives neither an implementation nor a reusable-DAG lower bound.
- Audit joint bit/complex assembly only after both complete suppliers are paid.
  The current result compares a complex nominal root to a final κ target as a
  necessary planning screen, without claiming that the overall target is met.

Prepared with substantial OpenAI Codex assistance, retaining predecessor
attribution. Apache-2.0.
