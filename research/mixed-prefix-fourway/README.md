# Four-provider joint-prefix packing

This package chooses among four independently verified local suppliers from
PR569, PR571 and PR572 and reconstructs a new literal owner assignment.
It admits the conditional finite witness

```
kappa = 0.001600848528154892
b     = 0.001603415353263184744465
H     = {1:169296, 2:41043, 3:25943, 4:13824,
         5:4032, 6:4032, 7:3, 8:576, 48:1817}
```

This is 0.01037836% above the independently replayed PR571 value
`0.001600682403612293`. The conservative complex model separately gives
`kappa = 0.001600848525369710`. Dimension 73, live stock 7168, physical stock
7682, total rank mass 520704 and deficit 2560 are unchanged. The cited
unchanged PR543 bit supplier is repriced and remains nonbinding.

| Local supplier | Calls | Provenance |
|---|---:|---|
| Plain four-cold | 2 | PR569 |
| Plain eight-cold | 4 | PR568, cold replayed by PR572 |
| Width-seven eight-cold | 8 | PR568 + PR569, cold replayed by PR572 |
| Joint-prefix width-seven eight-cold | 58 | PR571 |

The new contribution is the joint provider selection and literal assignment
of all 36,288 helper roles. No scalar word is newly optimized here. Every
selected provider is rebuilt from its pinned construction, and each complete
invocation keeps one physical owner per helper. The final 3,038 positive idle
remainders have profile `{2:27,3:1191,7:3,48:1817}`.

## Reproduce

Python 3.11 or later, standard library only, with assertions enabled:

```sh
python3 -B research/mixed-prefix-fourway/verify.py --work /absolute/new/fourway
```

The output directory must be absent. The verifier first cold-replays the
entire pinned PR572 package, including its PR568 dependency. It then rebuilds
the four-cold and joint-prefix suppliers, checks all columns and both reflected
ledgers, wrappers, full phase recipes and kernel omissions, and binds the four
fresh suppliers to the frozen plan. It does not reuse retained proof outputs.
Only the two new phase jobs run concurrently, with disjoint output files.

A separate owner audit reconstructs actual chronology, charts and spectators.
A fresh invoice recounts every selected scalar macro, wrapper and compiler
allowance. Both exact moment engines, both complex recurrence models, seven
bootstrap levels, 47 strict outer inequalities, 109 assembly rejection controls,
four timing accept/reject pairs, four actual recompressions and 72 proof/reference
mutations must pass. All proof-relevant generated fields remain pinned; gzip
containers are compared by decompressed content. Exact hashes are retained for
immutable sources. Validation receipts are kept outside this source manifest.

See [PROOF.md](PROOF.md), [CONTRACTS.json](CONTRACTS.json),
[SOURCE-PINS.json](SOURCE-PINS.json) and [NOTICE.md](NOTICE.md).

## Scope

This is conditional finite evidence. It retains the inherited all-size
compiler, common-label/mutable-source, normalized recursive residual,
whole-call hosting, precision/tape and analytic-transfer obligations, including
the bit supplier's H1–H5. It is not an unconditional multiplication theorem,
complete Lean proof, measured runtime improvement or κ = 1 result. Solver
optimality and global packing optimality are not claimed.
