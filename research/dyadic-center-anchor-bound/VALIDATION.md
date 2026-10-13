# Executed validation and review boundary

Base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
Environment: macOS, CPython 3.14.6, standard library only.
Prepared by Ross Richardson with substantial OpenAI Codex assistance.

The following commands passed on 2026-10-13 UTC (2026-10-14 Melbourne):

```sh
python3 -I -B research/dyadic-center-anchor-bound/verify.py
python3 -I -O -B research/dyadic-center-anchor-bound/test_package.py
python3 -B -m unittest discover -s tests -p test_complex_centers.py
make selected-record-check
git diff --check
```

- Main replay: 26 h26 cardinality orbits covering 33,554,432 binary anchors
  by the proved permutation symmetry; 15,276 admissible anchors; unique
  fixed-pivot minimum 42,600 at k=0. This is not 33 million literal replays.
- Complete literal small censuses: all 128 h8 and 512 h10 anchors. In each
  case, admissibility, numerator multiplicities, the affine map and actual
  table costs agree with the orbit formulas.
- Four exact rational polynomial identities agree coefficient by coefficient.
  Their nonnegative binomial-basis coefficients prove the all-h tail bound.
  The h8 exception is retained and checked.
- Twenty literal central commutator replays: five admissible sizes, h8/h10,
  both orientations. All 3,700 independent input-column/direction obligations
  pass, including arbitrary dirty centers and targets. Executed operations
  agree with the complete central invoice. Fourteen main controls pass.
- Nine package tests pass. They include 401,408 direct integer matrix-product
  entries (a different finite check from the affine quotient), all 16,384
  integer offsets in {-1,0,1,2}^7 for the gather reduction, all 1,024
  pivot/anchor pairs at h8, polynomial checks, dimension/type corruption,
  isolated optimized minimal relocation in a path with spaces, source and
  polynomial corruption, and a boolean-versus-integer receipt mutation.
  Failure cases preserve the existing receipt. No checker uses `assert` for
  its mathematical acceptance decisions.
- Four existing complex-center tests pass. The selected-record integrity
  check retains PR890's exact conditional κ and source/proof inventory.
- The original factor file's last change is
  `d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`; its Git blob payload matches the
  recorded SHA256. All eight inherited input files are hash-pinned.

Only `research/dyadic-center-anchor-bound/` is added. No selected supplier,
production generator, `upstream/`, existing certificate or review ledger is
modified. The broad `make verify` regeneration suite and selected cold replay
were not run: this additive note changes none of their inputs. No full side
phase replay, selected global admission, Lean proof or remote CI pass is
claimed. The historical side invoice and recursive/physical obligations are
inherited explicitly, not re-certified by the local result.

The complete overlap snapshot contained 717 open PRs through #946. Main
then advanced during publication to
`007664306fff84fbb1c9a1b4053b69f439764034`. A fresh fetch confirmed that all
eight mathematical inputs are byte-identical and PR890 remains selected at
0.001661957774647029. The branch retains its exact recorded starting base.
The immediately preceding submission check found no newer overlapping PR. PR809 and PR937 remain
at the pinned heads; the latter already owns the minimum construction and its
savings. This contribution supplies an all-even-h theorem for a defined
simultaneous-shear class, which neither predecessor claims. Other new PRs
concern coefficient schedules, connectors and reproducibility. There was no
pinned coordination issue, so the claim is local; `OVERLAP.json` records the
specific inspected heads. GitHub publication and any later CI are separate
from these local results.

Published result: [PR947](https://github.com/CrocSwap/integer-mult-bounds/pull/947).
The local sprint claim was updated once with this result and link.
