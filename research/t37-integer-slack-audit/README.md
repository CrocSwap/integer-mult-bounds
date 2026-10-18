# Quantitative integer gap in the historical U8/T37 bound

For every positive integer replica count T not divisible by37, every integer
residual histogram satisfying the pinned U8 mass and signed-credit conditions
has normalized moment strictly more than `29/(313958400*T)` above the formal
T37 residual relaxation, at the pinned upper endpoint. The previous package
already proves that equality requires a multiple of37. This note supplies an
explicit positive margin and the exact period37 credit slack for the extremal
rank-only subclass. It does not improve the selected k8 construction or kappa.

## Proof and exact arithmetic

Use the definitions and **historical fixed family** in
`research/complex-t37-owners/ALL-T-PROOF.md`. Let
`z=0.001664727258740678855773`, `phi(r)=r*(73/r)^z`,
`v(r)=48*u(r)+13*r`, `c(r)=48*phi(r)-r*phi(48)`, and
`lambda=c(1)/925`. In particular `c(0)=v(0)=c(48)=v(48)=0`.
The 1163-bin predecessor enumeration determines the attainable ranks and u.

An independently implemented fill recurrence reconstructs every u(r). A
rational range-reduced atanh/Taylor computation, importing no predecessor
numerical code, certifies `lambda>1/3000` and
`delta(r)=c(r)-lambda*v(r)>29/100` for every attainable rank other than0,1,48.
At rank1 delta is zero by definition. The checker uses the correct interval
endpoint when v is negative. All acceptance decisions are exact rational.

Let counts n_r be nonnegative integers. The retained necessary constraints are
`sum r*n_r=14382*T` and `C=sum v(r)*n_r>=150*T`. Therefore

`G=sum c(r)*n_r-150*lambda*T = sum delta(r)*n_r + lambda*(C-150*T)`.

If a nonextremal rank occurs, its integer multiplicity is at least one, so
`G>29/100`. Otherwise only ranks0,1,48 occur. Rank0 makes no contribution.
The mass congruence gives `n1=30*T+48*k` for an integer k, and hence

`C-150*T = 925*n1-150*T = 1200*(23*T+37*k)`.

The minimum nonnegative arithmetic slack is
`1200*(23*T mod37)`. A realizing arithmetic pair is returned by pure_profile;
its n1 and n48 are nonnegative for all positive T: the explicit37 representatives
are checked and T -> T+37 adds6 to n1 and11086 to n48. This does **not** assert
that those counts fit physical bins. If37 does not divide T the slack is at
least1200, so `G>1200/3000=2/5>29/100`.

Finally, the residual phi-sum difference from the formal T37 profile is G/48.
All local terms cancel, and the normalized full moment divides by73*896*T.
Thus its strict gap is `29/(100*48*73*896*T)`. The result uses the explicit
historical896 roles per replica; no new outer-transfer computation is claimed.

For logarithms, write x=2^k*y with1<=y<2 and use t=(y-1)/(y+1).
After N=48 terms, the positive atanh tail is at most
`2*t^(2*N+1)/((2*N+1)*(1-t*t))`. For exp with0<=y<1, after degree24 the
tail is at most the next term divided by `1-y/26`. These elementary bounds
justify the enclosure computation independently of the retained engines.

## Reproduction and controls

```text
python -I -O -B research/t37-integer-slack-audit/verify.py
python -X utf8 scripts/research_package.py --package research/t37-integer-slack-audit --check-only
```

The registered command uses Python3.12. RESULT.json records every residue,
source/table coverage and rational floors. Meaningful controls remove integer
counts (the fractional T=1 profile attains zero), remove the nonmultiple premise
(T=37 attains zero), omit credit, omit the mass congruence, or change rank-one
credit. These delimit assumptions; finite controls do not replace the proof.
The theorem drops bin count/time/geometry/payload constraints and cannot admit
a construction or prove a sharp packing optimum. No native or cold supplier
replay was run for this arithmetic-only result.

## Open next questions

For one T not divisible by37, add actual bin counts and timing to determine
whether the present strict margin can be strengthened. This matters for search
pruning; first solve the residual integer program. Physical realization remains
the blocker. The question and scope are recorded in TASK.json.

## Credit

The signed prices and all-T equality result are Jonathan Capalbo's PR942/T37
lineage, inheriting Chafik Boukhalfa's PR795/890 signed dual and the credited
U8 construction. This package adds the quantitative integer margin only.
Prepared for woklerx with substantial OpenAI Codex assistance and a separate
Codex algebra sanity check; no independent human review. Apache-2.0.
