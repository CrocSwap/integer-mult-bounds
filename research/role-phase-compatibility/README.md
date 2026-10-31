# Role-specific phases cannot remove the selected MOVE tags

Allowing a separate phase chart for every role and every event still cannot
remove all explicit MOVE phase tags while retaining the selected #6030 scalar
coefficients, unless the column multiplicity is divisible by four. This answers
the role/history-gauge question left open by #6298. **No new κ.**

The obstruction uses fourteen actual events: eight ADDs with independently
certified rank-two operand rows and six rank-one MOVEs. Two roles acquire the
same phase, follow paths with phase sums one and two, and then meet in an
independent ADD. Even arbitrary public endpoint gauges and freedom at all
omitted dependent ADDs cannot reconcile that contact. The unchanged, correct
phase-preserving implementation is not challenged.

[PROOF.md](PROOF.md) gives the all-input, all-width argument, the exact event
and minor tables, and the boundary of a possible changed-coefficient remedy.
[RESULT.json](RESULT.json) is a generated source-bound certificate. Base:
`a7638a4ce2a29947457ae8d6bf8cd70a234dfeac`; exact Git/SHA256 inputs and historical
question pins are in [SOURCES.json](SOURCES.json) and [TASK.json](TASK.json).

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/role-phase-compatibility
```

Expected: `PASS_ROLE_PHASE_COMPATIBILITY`, `PASS_INDEPENDENT_ROLE_PHASE` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The registered commands run both scientific
checkers normally and with assertions disabled. Direct replay:

```sh
python3 -I -W error -B research/role-phase-compatibility/verify.py
python3 -I -W error -B research/role-phase-compatibility/independent.py
```

The primary replays 9,998 events over 770 independent rational input rows,
certifies all eight minors, compiles the six MOVE recipes, checks their 3,072
basis columns using a separate exact interpreter, and checks both 512-column
relative path operators. Twelve rejecting controls cover changed source bytes,
contacts, hidden writes, false phase/sign claims, missing rank-two hypotheses
and omitted compensating coefficients. Open-tree and width-four controls pass.

The separate checker streams nine columns through 89,982 event applications
using integer dyadics, then solves a relaxed event-gauge graph at widths 1–32.
Every nonwitness write receives a free phase variable. Dropping the closing ADD
or altering the path phase makes all 64 control graphs consistent. The written
proof establishes arbitrary width and arbitrary unit-complex gauges; these
finite graph checks are corroboration.

[VALIDATION.md](VALIDATION.md) records checks actually executed and their limits.
Default replays write no files. `verify.py --write-result` is the certificate
generator and refuses to overwrite an existing result. Authenticated native
source is compiled directly from its bytes, preventing a stale bytecode cache
from replacing the checked source in direct replay.

## Novelty and limitations

#6298's triangle allowed one phase per frame and used edges on different roles.
Here the contradiction survives a phase per role per event and is justified on
the actual reached operand rows. #6293's phase census is retained credit, not
new coverage. #6025's fixed nonlinear role recodings use a different contract.
The archive/PR survey was targeted, not exhaustive; active #6322–#6325 address
different helper and G20 questions. The publication checkpoint is recorded in
TASK.json.

The result is a scoped gauge obstruction, not a lower bound for all native
resyntheses. It fixes all other recipe gates and all scalar coefficients,
requires gatewise exact gauge equivalence, and excludes data-dependent gauges.
No complete-word phase-deletion endpoint audit, minimum tag count, physical
scalar tariff, selected cold replay, hosted CI, Lean or Docker is claimed.
All five selected framework assumptions remain. The selected conditional
κ = 0.003125804 is unchanged.

## Open next questions

Can changed scalar phases and endpoint normalizers yield a cheaper complete
implementation? The first step is to propagate one legal phase assignment
through the entire word, emit every changed ADD/COPY coefficient and boundary
normalizer, and charge their native/scalar/precision costs. A repair of the
single closing ADD is only a local compatibility example, not such a program.
This package stops at the fourteen-event certificate; no global phase-cost
optimization is reserved. Structured scope and blockers are in TASK.json.

## Attribution

Prepared for @CubeJerry with substantial OpenAI Codex assistance in derivation,
implementation and independent column/graph checking, with lead review.
Credit Nick Petalas (#6298/#6025), unpaidmoon (#6293), DreamingOfClouds
(#6030/#5907), Ali Romman (#5827/#5599/#1862/#1931), Chafik Boukhalfa,
icekylinx, DLamdata (#5894), Matarener (#5974/#5442), and the retained source
lineage listed in PROOF.md. Classical gauge-cycle and tensor-phase facts retain
their usual attribution. Apache-2.0. No independent human or formal proof-kernel
review is claimed.
