# Bounded finite search provenance

The sweep evaluates only radii \(6,7,9,11\), using \(H_4/2\), error cap one,
and the threshold associated with each radius in README.md. For each
radius it enumerates sorted nonnegative coordinate patterns with squared
norm at most \(R^2\), divides them into \(W(D_4)\) orbit keys, and generates
the 9 or 16 complete nearest error-one outputs at each input representative.
No full point set is expanded by applying all 192 group elements.

| Radius | Input orbits | Inputs | Output orbits | Candidate outputs | Error-one edges | Distinct attained edge gaps |
|---:|---:|---:|---:|---:|---:|---:|
| 6 | 98 | 6,577 | 142 | 10,713 | 81,873 | 380 |
| 7 | 154 | 11,833 | 222 | 18,457 | 149,505 | 608 |
| 9 | 350 | 32,633 | 470 | 46,401 | 410,569 | 1,287 |
| 11 | 690 | 72,465 | 886 | 96,449 | 909,113 | 2,346 |

For the exact optimum, the ascending distinct gaps are compared using the
integer radical comparator documented in PROOF.md. Binary search records
each exact index and max-flow value in RESULT.json:

| Radius | Optimum gap index (zero based) | Binary flow probes | Optimum gap |
|---:|---:|---:|---|
| 6 | 213 | 9 | \(\sqrt{31}-\sqrt{28}\) |
| 7 | 347 | 10 | \(\sqrt{31}-\sqrt{28}\) |
| 9 | 763 | 11 | \(\sqrt{78}-\sqrt{73}\) |
| 11 | 1,413 | 12 | \(\sqrt{78}-\sqrt{73}\) |

The exact target-threshold tests and the optimum upper-flow/strict-lower-cut
receipts are included in full. The threshold graph at \(R=6\) is deficient by
32; the three other target graphs saturate all inputs. No radius outside
\(6,7,9,11\) was evaluated.
