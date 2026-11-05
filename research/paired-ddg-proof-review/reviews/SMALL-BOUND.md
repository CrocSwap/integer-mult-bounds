# Coordinator hand bound for the credited small-pair inequality

Source-aware written deduction, no execution, import, numerical program or census. This is a nonsharp hand proof of the already claimed `(1,1)` inequality, not a new mean or sampler. The source's large exact rational expectation is not recalculated here. The coordinator had read the source README/code and received a peer's independently written general `2<E<7/2` argument before sealing this short note; no blind-independence claim is made.

For `(a,b)=(1,1)` the product weights are `(144,12,12,1)` and the denominator is169. Let `n_k=2^k-sum_i floor(2^k*w_i/169)`. Hand integer divisions give:

| k | Four floor counts | n_k |
| --- | --- | --- |
| 0 | (0,0,0,0) | 1 |
| 1 | (1,0,0,0) | 1 |
| 2 | (3,0,0,0) | 1 |
| 3 | (6,0,0,0) | 2 |
| 4 | (13,1,1,0) | 1 |
| 5 | (27,2,2,0) | 1 |

All four residues modulo169 are nonzero, so `1<=n_k<=3` for every k. The first six terms in the expected-tail sum are `67/32`. Bounding each later numerator by3 gives

`E[T] <= 67/32 + sum_(k>=6) 3/2^k = 67/32 + 3/32 = 35/16 < 9/4`.

This deduction uses the all-depth prefix-law/tail formula being audited. It does not verify the exact displayed fraction, all finite source fixtures or any physical runtime. zxv retains the small-pair inequality and exact expectation credit; the method is elementary tail bounding. The literal six divisions above and the geometric tail are written arithmetic, not new observed executions.
