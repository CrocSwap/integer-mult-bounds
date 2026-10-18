# Bit word R480: PR #493's word with its nine totals on dead registers

**This package makes one change to PR #493's E8 bit word (R = 489).** The nine decoder totals no longer get nine
fresh registers. Each one is formed on a register that is already dead, and the host is the **last** eligible
register of the total's combination instead of the first. Everything else is #493's word, gate for gate: the
partition, plan, sources, carriers, cells, quads, Q-nodes, phase B and literal cleanup. The result is
**R = 480**. That is the R ≥ 480 bound #493's README argues for its family (an analysis under its stated hypotheses: this partition, three branches per source, totals in phase A; not machine-checked).

| quantity | value |
|---|---|
| bit c, eleven stages, eight pooled replicas, every residual whole and hosted (10^-24 grid; #472's pipeline as #493 runs it) | `393688338238452162729/250000000000000000000000` = **0.001574753352953808650916** |
| PR #493 (R = 489), same pipeline, reproduced by `verify.py` | 0.001565442026981656908596 |
| change | **+0.5948%** |
| κ with #484's complex b (draft; its Lemmas A and G), complex-bound | `662515748707749/500000000000000000` = 0.001325031497415498 (unchanged) |
| κ with #471's complex b, complex-bound | `260706019542937/200000000000000000` = 0.001303530097714685 (unchanged) |
| κ with #458's complex b, complex-bound | `323880830669511/250000000000000000` = 0.001295523322678044 (unchanged) |

The bit side does not bind, so κ does not move with any of the three cited complex suppliers. The gain is on the
bit side: it is how far c can fall before the bit side binds again, and it carries over to any composition whose
complex b rises above #493's c.

## What changed and why it was left on the table

#493's generator (`code/skeleton/gen.py`) already supports totals on dead registers. Its dead pool is the 120 zz-D6
outputs that become dead after the needer rules, plus the 60 Q-node leftovers, and the decoder space lies in its span.
With dead hosts the generator picks the **first** eligible register of each total's combination (`next(r for r in
sorted(combo) ...)`). That word fails the official five-stage checker's finite-prefix bill: the payload is 129 bits,
against a limit of `payload < 2^104`. #493 therefore shipped nine fresh total registers (100 bits, R = 489). Its
README notes that "R = 480 is reached with the totals on leftover registers, but its prefix payload is 129 bits > 104".

The payload depends on which register hosts each total. With literal cleanup, C undoes `host ^= others` first. That
leaves the host with an inflated cancellation-free norm, which then flows back through the reversed gates of every
gate that read the host earlier. The registers in a combination differ in how much of the program they fed, so the
choice of host changes the bill. Choosing the last eligible register keeps all nine totals under the limit.
Measured with the official checkers:

| totals host | R | five-stage payload | columns_h |
|---|---|---|---|
| fresh registers (#493) | 489 | 100 bits | PASS |
| dead, first eligible register (#493's generator, no fresh totals) | 480 | 129 bits | **refused** (`payloadfiniteprefix2^104`) |
| dead, **last** eligible register (this package) | **480** | **102 bits** | **PASS** (eleven-stage `columns_k`: 102 bits) |

The local paid histogram per call goes from {1: 1200, 2: 1440, 4: 180, 6: 120, 8: 18} to {…, 8: 9}: the nine fresh
0 → FULL climbs disappear, and with them 9 × 88 hosted residuals. Total rank mass is fixed (745,536), so the freed idle
mass stays in whole rank-56 children (2628 → 2742), which cost less per coordinate than the eliminated rank-8 climbs.

## The change, exactly

`code/adapt.py` writes three files from #493's package. It makes 8 string edits and checks that each anchor occurs
exactly once:
- `gen_r480.py` = #493's `gen.py` with `sorted(combo)` → `sorted(combo, reverse=True)` in the dead-host choice (and
  the parent's skeleton directory on `sys.path`). Run as `gen_r480.py OUT 0 fresh0` (no fresh totals, literal
  cleanup), it rebuilds `data/bitE8mut-r480.json.gz` **byte for byte** from #493's frozen plan.
- `eleven/audit.py`, `eleven/local_audit.py` = #493's adapted #472 audit with R = 480 (960 formal columns, 720
  registers, the audited word = the R480 word).

Every other script, including the emitter, assembly, checkers, geometry and hosting programme, is #493's file,
unchanged and run from #493's package directory.

## Checks (`verify.py`)

0. This package's `MANIFEST.json` and #493's `MANIFEST.sha256` (every parent file).
P. (full mode) #493's `verify.sh`, unchanged: its word, all its checkers, pipeline, controls and compositions.
1. The R480 word rebuilt from #493's plan is byte-identical to the shipped word. It has the same frames, sources,
   phase B and gate counts as #493's word, and its nine totals sit on dead registers. Control: #493's generator,
   unchanged, builds the first-register variant.
2. #370's stock checker refuses the word (`x register written`, as for #493). #493's relaxed copy passes it: exact
   F2 replay of every column, frames, price. `interface.py` passes (#425's hypotheses: literal C = U⁻¹ at the
   full frame, no target feeds a source or helper, D at frame zero, B writes only targets). #493's 11 word-level
   mutants are rejected, and so are its 2 hypothesis controls.
3. Official cohort checkers at R = 480: legality (NCOPY = 9), five-stage formal columns (prefix payload 102 bits <
   104), eleven-stage formal columns (`columns_k`, KPAIRS = 5, 24/24 omitted-bridge controls rejected), the
   KPAIRS = 2 regression, #370's record mutants and #493's mutable-source record mutants. Control: the first-register
   variant is **refused** by `columns_h`. Its payload is 129 bits, reported by a copy of `columns_h.cpp` that has the
   payload assertion removed and is used only for that number.
4. Exact Gram determinants and prime witnesses on all 672 frames.
5. #386 nine-stage and #445 eleven-stage geometry. #442's hosting programme (#493's `discovery/host_select.py`)
   rediscovers `data/hosting-r480.json` exactly. Then #472's emitter, the R = 480 audit (all 42,240 residuals hosted
   whole, all template mutations rejected), #472's bit invoice and both moment engines, and the outer assembly
   (47 strict inequalities and its controls) with #484's, #471's and #458's cited complex b.
6. Control: #493's R489 word through #493's own unmodified emitter, audit and assembly reproduces its c exactly.
7. Every number above against `EXPECTED.json`.

```sh
python -m pip install -r research/e8-bit-carrier-skeleton/requirements.txt scipy
BOOST_INCLUDE=/path/to/boost python research/e8-r480-dead-totals/verify.py /absolute/new/output --light   # about 3 minutes
BOOST_INCLUDE=/path/to/boost python research/e8-r480-dead-totals/verify.py /absolute/new/output           # + #493's verify.sh
```

## Finite invoice

The dead-hosted totals have long cancellation-free chains, so #472's chronological physical prefix grows: 2,119 bits
become **5,479**, charged at 5,504. The three-level coefficient grows from 6,411 to **16,491** bits, charged at
16,512. Both are above #473's precedent of 3,456 and 10,304. They enter only the finite cutoffs, and every assertion
of #472's invoice passes: maximum child 56, three-level halving, row coefficient 19,431 < 20,161.

## Scope

Everything #493 is conditional on, this package inherits unchanged. That covers #472's eleven-stage composition
interfaces (the all-size bit/Gaussian compiler, mutable-basis and target-label realisation, whole-call
correlated-helper hosting, compressed windows, restored work, common grid and tape, precision, row and analytic
contracts) and #425's mutable-source interface, checked here by #493's `interface.py`. Complex savings are cited
from their PRs' receipts, not rebuilt. The κ with #484 also rests on #484's Lemmas A and G. No unconditional
multiplication theorem, Lean proof or κ = 1 result is claimed.

## Credits

eumemic (#493: the R489 carrier-skeleton word, its generator with the dead-register option, the relaxed checker and
interface checks, and the family bound R ≥ 480). Through #493: Zhihao Chen (#425, #386), DreamingOfClouds (#463, #315,
#484), DaysSky (#442, #381), chafreaky (#445, #451, #472, #458), Dylan Crow (#370), icekylinx (#433), Dugongue
(#471, #483), Jacob Sussman (the E8 unit). Details in `NOTICE.md`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0 (`LICENSE`).
