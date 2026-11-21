# A smaller positive stopping margin for the paired single-band multiplier

The complete paired multiplier certifies **conditional κ ≥ 0.0038901152865907** with a near-crossing installation. The gain over [#8033](https://github.com/CrocSwap/integer-mult-bounds/pull/8033) is exactly `0.0000000000002387`. A second installation at #8033's original rank and activation exponents certifies **conditional κ ≥ 0.0038901152863924**, a gain of `0.0000000000000404`.

The positive recursion's cutoff is now a profile parameter. Its all-size terminal estimate works for a smaller positive exponent `g=10^-17`. The same value funds the signed caller's strict inequalities. The runtime and the price checker share the denominator, including fixed-program preparation and the actual numerical call path. [Proof](PROOF.md)

| Resource | Fixed stock | Near crossing |
| --- | ---: | ---: |
| Binary factors | 268 | 285 |
| Largest binary carrier exponent | 112000000000000 | 7168000000000000 |
| Sufficient public activation exponent | 119466661575676 | 7645866239991957 |
| Full BIT debit, bits | 21 | 22 |
| Full positive debit, bits | 10 | 10 |
| Signed κ | 0.0038901152863924 | 0.0038901152865907 |

Both installations preserve the 36 native BIT calls and 48 native rational calls of the exact paired word. The near-crossing installation enlarges the binary ranks by a factor of 64. The fixed-word directed raw upper is `0.003890115286594461129996943`, leaving a gap of about `3.76113e-15` above the strongest lower. [Receipt](RESULT.json)

## Sources and replay

The archived package has the exact #8030 source, `6285dd829114705862e8d91facaedc1f31d3cfcb`. The 36/48-call physical interfaces are from #8027 at `fb9b6a7b0d27da1cf98430893a3016bf811e2aa4`. The split-tail refinement is from #8033 at `a1313ff9f84fd00d50b282fe432e522191277821`. The signed arithmetic expressions are pinned to `4f7c67ae387cc91580f469aeda4d508b372b9ec1`. The archive and `OVERLAY.json` authenticate the precise source and modified files.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-single-band-signed-margin
```

Replay covers both directed BIT prices, the retained positive price, 54 strict and four functional outer checks at each profile, the integer stopping guard, band loans, dense operators, actual BIT and rational words, ownership and precision, and both finite signed product controls. The old margin, vanishing margin, equality at either paid supplier gate, and extra paid rank-one position are rejection controls.

The all-size guarantee uses the five inherited premises for all-column native action, owned erasure and restoration, compiler transfer, precision and tape services, and analytic recovery. The finite operator and product replays exercise feasible tapes. The sufficient activation is a proved resource bound, and the least practical crossover remains open.

## Open next questions

Can an exact operator-preserving change raise the paid BIT word's raw crossing? A changed set of priced events needs complete role, typed owner and signed tape verification. The fixed rank histogram supplies the current obstruction.

## Attribution

Ali Romman supplied the paired circuits and single-band tape application. DreamingOfClouds and the P104 dual-supplier contributors supplied the signed gate machinery. Other predecessor credit and licenses are retained in the pinned archive. Clear1nsight contributed the stopping parameter proof and the two installations. OpenAI Codex materially assisted research, implementation and verification. New material is Apache-2.0.
