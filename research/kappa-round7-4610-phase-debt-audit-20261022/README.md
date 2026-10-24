# Independent rank-debt premise audit and Lean extension

Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.

The analytic argument is credited to **Cinna Davis,
[PR4696](https://github.com/CrocSwap/integer-mult-bounds/pull/4696)**,
head `def829364e8e53a74eac7997b49b5366afd5bc29`. This package independently
checks its precise applicability and formalizes its finite-list inequality.
It claims no increased kappa and no new native supplier.

## Premise audit

The upstream [statement](https://github.com/CrocSwap/integer-mult-bounds/blob/def829364e8e53a74eac7997b49b5366afd5bc29/research/phase-rank-debt/PROOF.md#L5)
fixes the old subspaces, scalar graph/order/coefficients, logical warp maps,
main operator and adapter boundaries. It permits arbitrary compatible
helper and owned-center symmetric forms, higher paid ranks and paid
corrections at old rank-zero transitions. A shared scalar contact retains
one chart. The owned center stays uncredited. Its native phase-rank grammar
is an explicit premise, rather than a consequence of ordinary matrix rank.

For each helper, every original scalar-contact block has at most one
positive paid job. Its old rank r is at most the endpoint rank h. The
endpoint's additional rank g is bounded by the sum of that helper's added
paid ranks delta. The [concavity argument](https://github.com/CrocSwap/integer-mult-bounds/blob/def829364e8e53a74eac7997b49b5366afd5bc29/research/phase-rank-debt/PROOF.md#L104)
then bounds helper moment gain by its own paid increase. Distinct helper
owners prevent double charging; extra main/owned cost is nonnegative.
This reasoning is valid under those stated premises.

The source audit authenticates the actual original bytes and replays the
upstream checker, then removes every inert adapter marker and checks both
orientations again. All 448 markers refer to main fields 0 through 223;
none cuts a helper path. Removing them preserves all other certified path
facts, including the 19817 zero-job and 2208 one-job helper blocks, all 408
pointwise-fixed helper entrance spaces, paid/helper profiles and rank
telescopes. Thus a new graph which merely removes textual adapter freezes
does not escape this helper debt. Compatible owned-phase relaxation is
already covered by the upstream statement. No metadata-only boundary
change supplies a gain.

The active-chart palette in the separate frozen phase package changes
Fourier rowspaces: for example a unit mask changes an active rank k to
k-1. It therefore falls outside the fixed-subspace grammar's
`r_new=r_old+delta`, `delta>=0` premise. This is a precise scope distinction,
not positive evidence: the tested actual palette still returned the old
construction. A shared paid multi-owner operation, fusion across a scalar
contact, a changed main operator or a changed center protocol also needs a
new physical contract before the theorem can be applied or evaded.

## Lean boundary

`RankDebt.lean` proves five scoped facts, using elementary concavity rather
than differentiating at zero:

1. Equal-length increments of a concave function decrease with the base.
2. This applies to real powers for `0<=t<=1` on nonnegative arguments.
3. A finite sum of nonnegative added ranks is nonnegative.
4. For any finite list `(r,delta)` with `0<=r<=h`, `delta>=0`,
   `(h+sum delta)^t-h^t <= sum ((r+delta)^t-r^t)`.
5. If `0<=g<=sum delta`, the same paid sum bounds `(h+g)^t-h^t`.

The fourth result is slightly more general analytically: it does not need
the native old-path equality `sum r=h`. The actual source still establishes
that equality. The formal theorem uses Lean's real-power convention at
`t=0`; the job convention that omits rank-zero jobs is a separate simple
counting argument, as in the upstream proof. The actual recursive exponent
is positive. Native rank identities, all-column physical execution and the
complete multiplication transfer are not formalized by this module.

The fresh replay binds source, log, local ignored object, runtime,
dependencies, pinned axiom auditor and actual five `#print axioms` reports.
Only `propext`, `Classical.choice` and `Quot.sound` are allowed.

## Reproduce

From the repository root, using global Python 3.14:

```powershell
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round7-4610-phase-debt-audit-20261022/replay_lean.py
& 'C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe' research/kappa-round7-4610-phase-debt-audit-20261022/verify.py
```

Exact upstream copies and Git commit/blob/SHA provenance are in
`SOURCES.json`. Their original attribution and licenses are retained.

## Open next questions

The feasible next step is a changed owner protocol at one actual scalar
contact: write its complete arbitrary-input multi-owner operator and
compare its actual paid Fourier invoice with separate corrections. The
blocker is a funded complete physical operation with all owner returns,
not a missing fixed-graph phase search. Alternatively a changed-subspace
palette needs a profitable full actual invoice before any recursive gain
can be claimed. Current finite negative screens are not a universal
impossibility theorem for either changed family.
