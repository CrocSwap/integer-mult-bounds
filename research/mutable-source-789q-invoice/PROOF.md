# Path-lowered 7–9 query invoices versus the six-query endpoint

Retain the five-source common-B mutable-source alphabet of PR1340/PR1898:
queries `Q_j: z += B x_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. Correctness is required for every admissible exact `B`, `A_m` and
every arbitrary dirty input, with sources, connector and scratch restored.

Specialize to length-one identity maps. Connector prefixes are vectors in
`F₂⁵`. A **path-lowered even-subset schedule** chooses a closed walk
`p_0=0,p_1,…,p_Q=0` whose increments span `F₂⁵`, reads each nonzero mask on a
minimum even subset of the identified slots `{p_0,…,p_{Q-1}}`, and implements
each multi-bit edge by compute/uncompute into one target source (cost
`2(wt(δ)-1)`).

The PR1898 abstract fixture charges `(b,a,x)=(38,2,2)` complete-call units, so

    tariff = 38 Q + 2 R + 2 X.

**Q=6.** PR1898 attains and proves minimum `R=96` with attained `X=8`, tariff
436. PR2455 proves `X≥8` at six queries, so 436 is exact in this class.

**Q=7.** Every 6-subset `S⊂F₂⁵\{0}` is scored for even-subset `R` on slots
`{0}∪S`. Covering sets attain only `R∈{82,88}` (histograms 97,216 and
486,080); none land in `{83..87}`. Beating the six-query endpoint under this
fixture requires `R+X<85`, so the excluded intermediate band cannot undercut
436 even at `X=0`, and every `R=88` schedule already pays at least
`38·7 + 2·88 = 442`. For each of the 97,216 sets with `R=82`, every full-rank
ordering closed at 0 is scored for path-local `X`. None has `X<6`; 14,595
attain `X=6`. Thus the `R=82` layer also pays at least
`38·7 + 2·82 + 2·6 = 442`. The champion `[0,1,2,6,12,24,16,0]` attains that
floor, so the exact minimum tariff is `442 > 436`.

**Q=8.** Among distinct 7-nonzero slot sets the minimum even-subset `R` is 74,
so with `X≥0` the tariff is at least `38·8 + 2·74 = 452 > 436`.

**Q=9.** Already `R≥62` (one even nonempty readout set per mask), so the tariff
is at least `38·9 + 2·62 = 466 > 436`.

Hence no path-lowered even-subset word with `Q∈{7,8,9}` beats the six-query
endpoint under this fixture. Words that share shear work across edges outside
path-local compute/uncompute are outside this theorem.
