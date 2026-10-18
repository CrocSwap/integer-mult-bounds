# Native P104 low-rank channel

Concrete finite Clifford recipes for the complete low-rank channel in
[Rohan Arun's PR1972](https://github.com/CrocSwap/integer-mult-bounds/pull/1972),
head `fd82d172f46933fd253c2c6de4bd5eaff5429cfd`. Its scalar/frame construction
is retained, not claimed new. This package replaces its conditional free-chart
realization with exact Gaussian-dyadic primitive recipes and intrinsic data
endpoint adapters.

**No complete P104 supplier or new kappa.** The `I-G/2` side correction,
chronological global hosting, precision and all-size admission remain open.
The selected frontier is unchanged.

## Result

For the frozen 104 root ports, source logical values `x`, target values `y`
and 72 independent arbitrary dirty helpers, the channel implements
`y <- y + (G/2)x`, with the prescribed source/target transports. All 72 helper
logical values are restored at the full frame. A separate owned private copy
has eight explicit allocate/copy/descend/discard lifetimes under the inherited
private-copy contract; it is not one of the 72 dirty inputs.

[EXPECTED.json](EXPECTED.json) records:

- 740 distinct native transport recipes covering all 1410 paid occurrences;
- 208 monomial data endpoint adapters: 104 source entries and 104 target exits;
- all 280 arbitrary register input columns in a complete framed induction;
- 14,400 physical root-pairing checks and 4096 exact Gaussian private-drop columns;
- five rejecting controls, including global phase and missing query compensation/cleanup.

The exact profile remains
`1074 H1 + 58 H2 + 86 H3 + 104 H4 + 48 H5 + 24 H6 + 8 H7 + 8 H8`.
Its rank mass is **2368 = 2312 boundary coverage + COPY56**. This is the same
local boundary invoice as PR1972, not a globally hosted recursive price.

The compressed root labels require a nontrivial Gram isometry before using
ordinary physical binary dot products. [PROOF.md](PROOF.md) gives that binding,
the native operator check and the full-word induction.

## Reproduce

Standard-library Python. Default replay is read-only, needs no network or Git,
and imports neither the channel producer nor the Clifford compiler:

```sh
python3 -I -O -B research/p104-native-channel/verify.py
```

Also rebuild every recipe in temporary storage and compare the complete
decompressed payload:

```sh
python3 -I -O -B research/p104-native-channel/verify.py --regenerate
```

The registered hook runs both checks with a 300-second limit:

```sh
python3 scripts/research_package.py --package research/p104-native-channel --check-only
python3 scripts/research_package.py --package research/p104-native-channel
```

The generic metadata check needs Git provenance. The direct command also works
from a read-only source export. `--out PATH` writes a receipt exclusively to a
new caller-selected file. Source hashes and exact origins are in
[SOURCES.json](SOURCES.json); [TASK.json](TASK.json) records the changed audit scope.
Compression bytes are not used to compare regenerated mathematics.

## Open next questions

Integrate a fully charged `I-G/2` side word while the required source/target
frames remain available. Appending it after source completion is not justified.
Then assign actual chronological owners to the completed word, count all idle
and residual children, and compare the exact recursive moment. Those steps,
plus precision and all-size lifting, are required before a supplier or kappa
claim. Concrete first steps and blockers are in `TASK.json`.

## Credit

Rohan Arun / PR1972 supplies the complete scalar/frame channel; Adam Gall /
PR1940 supplies the schedule. The P104 fixture and decoder derive from Josie
Elliston / PR1071, with Ali Romman / PR1125 and the PR968/717/446/595/620 lineage.
The exact compiler is retained through icekylinx's frame-sa504 package; the
independent Gaussian interpreter comes from Ali Romman's PR1862, also retained
in PR1931. Exact predecessor notices are under `notices/`.

Native lowering, the independent physical binding and framed induction were
prepared for Chafik Boukhalfa with substantial OpenAI Codex assistance.
Apache-2.0. No independent human review, proof assistant or literature-priority
guarantee is claimed. The fresh overlap screen covered 470 open PRs and 614
discussions; its limits are recorded in `SOURCES.json`.
