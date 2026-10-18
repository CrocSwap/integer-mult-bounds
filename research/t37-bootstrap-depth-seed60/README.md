# Six bootstrap levels suffice for the selected T37 grid

**Scoped mathematical audit and finite assembly witness; no new kappa.**
At base `8bddbee377e2f3ce1f1247196c4b290d55767d20`, PR942's selected native-complex
assembly branch uses seven affine bootstrap levels. **Six already admit the same conditional
kappa `0.001661960547713947` through all 47 strict outer inequalities.**
For the fixed starting saving and inherited supplier ceiling, zero through
five levels are impossible in this particular affine accounting class, even
with independent savings per level and optimistic zero reservation losses.

The six-level compact-margin slack is approximately `0.823649984 * 10^-18`.
The optimistic five-level margin misses the selected grid by approximately
`19.865327771 * 10^-18`. Both signs and every acceptance decision use exact
fractions; decimal approximations are explanatory only.

This removes one sufficient bootstrap level from the finite recipe. It does
not change the supplier, selected pointer, exponent, or native circuit, and
does not establish a measured runtime improvement or an all-size theorem.

## Reproduce

From the repository root, Python 3.11+ and standard library only:

```sh
python -I -B research/t37-bootstrap-depth-seed60/verify.py
python -I -B research/t37-bootstrap-depth-seed60/check_mutations.py
```

Expected:

```text
PASS_T37_BOOTSTRAP_DEPTH_S60 original=7 minimum=6 excluded=0..5 outer=47 negative_controls=11 positive_controls=1 kappa=0.001661960547713947
PASS_T37_BOOTSTRAP_SOURCE_CONTROLS rejected=3 historical_replay_without_selected_pointer=PASS
```

The verifier binds the exact consumed source inventory, extracts the original
bootstrap function without importing its supplier driver, applies the pinned
T37 payload adaptation, and first reproduces all seven published exponent/gap/
cutoff records and all 47 published outer slacks. Its only experimental source
edit is an in-memory change from `range(7)` to `range(6)`.

A separate closed-form calculation reconstructs every exponent and derives
each cutoff using integer cross-products. The first six cutoff records remain
unchanged and satisfy both original error/reserve inequalities. Their largest
`log2` cutoff is `30047027880383448577363131591267949447298`; the unused seventh
cutoff was `10842148173643272889999539096203012516204841615`.
These remain enormous sufficient thresholds, not practical input sizes.

The 47-condition replay uses the **retained source engine**, not an independent
implementation of those constraints. The independent work is the closed-form
depth envelope, cutoff arithmetic, and boundary controls. `SELECTED-SNAPSHOT.json`
preserves the exact base's selected record; replay does not read the mutable
current frontier pointer. No native, complete supplier, moment-engine, CI or
repository-wide success is implied. See [VALIDATION.md](VALIDATION.md).

## Novelty and dependencies

BagMan9's [PR768](https://github.com/CrocSwap/integer-mult-bounds/pull/768)
already proves the affine envelope method for the historical PR387 grid.
This package credits and reuses that mathematical argument, applying it to
the selected PR942 endpoint and discovering that its recorded seventh level
is unnecessary. It additionally replays all 47 outer constraints and all
original per-level cutoff obligations at six levels. PR768 expressly scoped
its six-level check to the compact margin and recurrence gaps.

tekuuu's [PR991](https://github.com/CrocSwap/integer-mult-bounds/pull/991)
checks T37 payload/binding and shows its recorded cutoff values agree under
512/1024 reserve choices; it does not establish this least-depth boundary.
Jonathan Capalbo's PR942 supplies the selected T37 construction; its moment
brackets and supplier admission are inherited. Full predecessor attribution
is in [NOTICE.md](NOTICE.md), and the exact class argument is in [PROOF.md](PROOF.md).

Prepared for **@woklerx with substantial OpenAI Codex assistance**. Apache-2.0.
