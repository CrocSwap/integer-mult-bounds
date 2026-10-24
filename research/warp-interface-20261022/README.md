# A verified paid-profile improvement from changed native maps

TL;DR: changing native G maps jointly with the scalar contact graph removes
**12 paid children per local call**, while preserving all productive helpers
and external interfaces. The parent p16 assembly gives conditional
**kappa = 0.00302152**, above PR4535's 0.003020165 by 0.000001355.
This retains the project's analytic/native/physical/compiler assumptions.

The exact local change is

```
old paid: {1:2237,2:388,3:494,4:147,5:36,8:8}
new paid: {1:2201,2:412,3:506,4:135,5:36,8:8}
helpers:  {4:28,7:7,8:47,9:326}  (unchanged)
```

All paid rank mass, scalar coefficients, 632 persistent inputs, 408 arbitrary
helpers, owned jobs and external interfaces remain unchanged. The new paid
moment is strictly lower for every real exponent `0<t<1`, with an exact
rational interval proof. See [PROOF.md](PROOF.md) for the construction and scope,
and the separate [whole assembly](../kappa-interface-round2-20261022/ARITHMETIC.json).

Prepared with substantial OpenAI Codex assistance, Apache-2.0. Credit Cinna
Davis's PR4470 native supplier and cumulative sources, Dugongue's transported
warp-frame lemma, zxv's native/compiler work and Jacob Alan Sussman's mixed-target
recursion. `SOURCES.json` pins the exact inherited inputs and attribution.

## What changed

The old joint frame optimizer fixed the native G maps. Here sixty operator labels
can change their one nontrivial frame pair because their other occurrences use
zero/full frames. Equal-dimensional subspaces are matched by an explicit
invertible G. A global contact model then finds a profitable joint choice that
the single-map and nearest-contact searches did not find. The actual patch
changes 422 scalar contact labels, 19 warp frame pairs and 34 G matrices.

SciPy/HiGHS discovery reported an optimum in its finite model; no solver result
is trusted for admission. `PATCH.json` and the emitted word are independently
replayed and physically lowered. Discovery statuses are preserved in immutable
`CANDIDATE*` files; current admission status is in `NATIVE-VALIDATION.json` and
`PHASE-VALIDATION.json.gz`.

## Reproduce without a solver

Run from the repository root with Python 3.14:

```
python3.14 -B research/warp-interface-20261022/regenerate.py
python3.14 -B research/warp-interface-20261022/verify_candidate.py --part native
python3.14 -B research/warp-interface-20261022/verify_candidate.py --part phases
python3.14 -B research/warp-interface-20261022/uniform_gain.py
python3.14 -B research/kappa-interface-round2-20261022/price_profile.py --native research/warp-interface-20261022/NATIVE-VALIDATION.json
```

This Windows workspace uses the global executable
`C:\Users\caoyi\AppData\Local\Python\pythoncore-3.14-64\python.exe`; the `py -3.14`
launcher currently fails. No virtual environment is created or activated.

The local native gate takes a few seconds; all new phase admission takes about
half a minute. Both retained interpreters pass all 632 arbitrary-input columns
in both orientations. The phase gate checks all 180 actual warp classes and
128 new paid pairs in both orientations, plus all 512 columns of each changed
bare native K operator. Semantic/frame/rank/phase corruption controls pass.
The two orientation pair sets, old basis prefix and inherited bytes are checked
explicitly. Regeneration compares canonical decompressed payload bytes rather
than relying on a regenerated gzip stream hash.

## Discovery and unsuccessful models

`free_warp_milp.py --operator all --seconds 120` reproduces optional discovery.
It uses SciPy 1.18.1 and NumPy 2.5.4, installed only in ignored `.deps/` with the
same global interpreter. Installation required a project-local TEMP/TMP folder
because the sandbox's default pip temporary directory was inaccessible. No
global environment or system setting changed. Proof replay needs only the
standard library and the pinned local source files, not those packages.

The all-map model had 586,626 variables and 126,905 constraints; complete frame
intervals had quotient dimension at most five. Its discovered paid profile is
the checked witness; its floating optimality report is not an exact ceiling.
Early single-map outputs are numerical negative screens, not impossibility proofs.

Other retained screens tested fixed-neighbor warp mergers, adjacent contact
retiming, 5,052 single-line warp seeds with least-join continuation, the same
seeds with charged reverse endpoint repairs, and 4,632 semantic inverse-ADD
pairs over the whole word. None produced a paid-profile gain in those models.
These negative results motivated freeing the native maps jointly. Their exact
domains and limitations are recorded in the respective scripts and JSON files.

## Open next questions

- Model the twelve warp labels with additional prelude contacts, preserving
  every occurrence's shared G matrix and actual frame/phase contract.
- Jointly change helper boundaries with the new native maps, then recount the
  actual productive profile and rebuild the complete invoice.
- Try changed scalar orders or larger native graphs. The present optimum report
  does not cover those domains, and further improvements are not assumed.
