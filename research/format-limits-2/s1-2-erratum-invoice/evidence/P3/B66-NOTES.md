# B66 NOTES: exchange rate of a helper (SETTLED). ship=false. Tools: work/b66prof.py, rate.py, dec.py, dec2.py (short single-process runs, no heavy job)
Scope: PLAN.json profiles of PR heads (#649, #645, #646, #635, #626) + B15 invoice root + B15 per-register climb shapes (#626 canonical word, same helper skeleton as #649). Base = #649.
## Gate (PASSED, exact)
b(#649)=0.00165526410310589141 (=README to 21 digits), #645 kappa 1.649483702558979e-3, #646 kappa 1.627103256702062e-3, #635 1.636241501576388e-3: all reproduced from PLAN profile {r:n} via root of sum r n_r/(mW) (m/r)^a = 1.
## Rate table: % b per helper removed (all 72 calls, climbs leave, width w returns to idle), on #649; linear in k (k=1,5,12,35 within 3%)
| w | no merge (narrow w-child) | merge into 48-bins | k=35 w9 (narrow / merge48) |
| 9 | 0.0725 | 0.141 | +2.48% / +5.11% |
| 8 | 0.050 | 0.119 | |
| 7 | 0.038 | 0.101 | |
| 5 | 0.031 | 0.084 | |
| 4 | 0.026 | 0.072 | |
(re-pack with own packer = the merge48 column is its upper bound; see #646 below: realised ~ narrow.)
## #646 decomposition (vs #635, its true parent; #645 is NOT its parent: #646 has 22 ends, no gauge)
Realised db = -0.559% (kappa 1.636242 -> 1.627103e-3). Per-call width inventory change: w4 -6, w7 -14, w8 +6, w9 +2 (net -12 helpers; sum width -55.7/call).
- Pure helper-count/width effect, priced at B15 shapes: +0.31% (narrow) / +1.00% (merge48). POSITIVE.
- Realised minus predicted profile: +4100 unit, +4973 width-2 children, -1458 w5, -796 w4, -930 w7 (mass pushed into 1/2-wide climbs: surviving helpers' transported residuals climb more) => residual -0.87% (narrow) / -1.54% (merge48).
- Packing: realised 48-window count +9 vs +97 needed for full merge: #646 realised ~ NO-MERGE (narrow) hosting.
So helper-removal is not negative; -0.9% is the climb/shape cost of the #646 transport, an unpriced side effect (loses cheap early endings), not a negative rate.
## Why the register disagreed
B15 0.068 = w9 narrow; 0.137-0.143 = w9 merge48 (best case, needs re-packing that #646 did not realise); B2 0.043 gross/0.027 net = mostly width-7 helpers (narrow w7 = 0.038) minus lost cold ends and read climbs; #646 negative = a different package-wide climb change, not the rate. All consistent once width and merge rule are stated.
## Settled rate
Per w9 helper: 0.072% b (realised/no-merge), 0.14% only with perfect 48-merge. Realised rates incl. side costs of triangle-style removals: ~0.0 to 0.03% (B2 net, #646 -0.56%/12). Use 0.07% as the GO-bar rate for a clean (climb-neutral) removal; 0.027% for triangle-type removals.
## Re-priced GO helper counts (cap +4.72% b, GO ~ +0.3% kappa)
- 35 w9 helpers: +2.5% b (clean, narrow), +5.1% only with merge (B54's +5% is the merge case). Cap reached at ~65 w9 (narrow), ~33 (merge48).
- GO (+0.3%): ~4-5 w9 clean; ~11 at triangle-type net 0.027%.
- 56 cross-block totals (B7/X4 are a hypothetical skeleton per judge, not a shipped word; width unknown): at w9 = +4.1% (narrow) / +7.9% (merge); at w7 = +2.1% / +5.7%; i.e. about half the register's 8% figure when no-merge.
- Un-triangled 504 Gauge56 (SYN-2 vs B56): helper axis alone is +0.31% .. +1.0% for the 12 helpers back or forth; sign hinges on the climb residual (-0.9% for 8 triangles); SYN-2's + side needs the climb cost to be avoided. Not resolved by rate alone; the rate is positive, B56's "net negative" is the transport residual.
Not done: #656 profile; true re-pack with a package packer (merge-vs-narrow bracketed, #646 shows near-narrow).
