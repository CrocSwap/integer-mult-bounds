# T16 concavity audit: a power-cost reversal between frozen owner maps

The selected PR1042 owner map improves its admitted exponent, but does not
dominate its PR1031 predecessor for every concave moment cost. Its residual
change is `{0:-3, 3:+11, 7:-7, 16:-2, 48:+1}`. Exact rational enclosures show
lower cost at b=1/2 and higher cost at b=3/4 for
`phi_b(r)=73^b*r^(1-b)-r`. This does not change the selected kappa.

This source-bound audit independently reconstructs all 276,480 helper roles
across the four admitted maps PR1022/1028/1031/1042, compares all six pairs,
and finds only PR1028 -> PR1031 ordered by majorization. Five pairs are
incomparable. It is a concrete limitation on an all-concave interpretation
of joint owner packing, not a correction to the valid selected moment proof.

| PR | rank 0 | rank 1 | rank 2 | rank 3 | rank 7 | rank 16 | rank 48 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1022 | 24719 | 2241 | 16 | 344 | 33 | 58 | 4845 |
| 1028 | 24708 | 2251 | 0 | 389 | 10 | 49 | 4849 |
| 1031 | 24709 | 2249 | 1 | 389 | 10 | 49 | 4849 |
| 1042 | 24706 | 2249 | 1 | 400 | 3 | 47 | 4850 |

Every row has 32,256 residuals and total rank 237,024. The full local paid
profile is unchanged, so residual cost differences are also global profile
cost differences. Zero residuals are retained for equal-length comparisons.

From repository root, Python 3.11+ and only the standard library:

```sh
python -I -O -B research/t16-concavity-audit61/verify.py
python -I -O -B research/t16-concavity-audit61/independent.py
python -I -O -B research/t16-concavity-audit61/controls.py
```

Expected: `PASS_T16_CONCAVITY_AUDIT`, `PASS_INDEPENDENT_T16_CONCAVITY`, and
`PASS_T16_CONCAVITY_CONTROLS`. Primary replay is about 3 seconds here; controls
are about 15 seconds. Checks remain active under `-O`. `--write-certificate`
is reserved for a missing certificate and refuses to overwrite one.

`PROOF.md` establishes the exact scope. `CERTIFICATE.json` retains every
histogram, all 294 stop-loss margins, twelve rational power-sign enclosures
and explicit concave counterexamples. The independent checker uses dense
occupied-coordinate arrays, all 193,536 sorted prefix comparisons and
Fraction bisection. Controls include omitted zero padding, direction reversal,
whole-width/call/window faults, typed certificate mutations, exact pin
inventory deletion, source tampering and relocation to a path with spaces.

The fixed base is `ba82555c64e1879e4b7decce28186f208fcb8262`, selected PR1042
with kappa `1672188119205421/10^18`. The frozen selected snapshot is bound;
future changes to the repository's selected pointer do not invalidate this
historical audit. Upstream admission supplies physical chart/window legality,
native supplier semantics, complete invoices and all inherited conditional
interfaces. This package does not rerun those obligations, produce a new
owner map, prove optimization, admit a supplier, or change kappa.

By @woklerx with substantial OpenAI Codex assistance. Original constructions
and the classical majorization argument are credited in `NOTICE.md` and
`PROVENANCE.md`.
