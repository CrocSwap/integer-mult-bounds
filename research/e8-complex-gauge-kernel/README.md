# Complex supplier b: shared-donor kernel and entrance gauges on the E8 complex word (DRAFT, status: work in progress)

Not a claim yet. The claim is CONDITIONAL on two new lemmas (see `PROOF.md`) and the global package is not built.

## Construction
On #442's complex word (#433's split-centre R560 word, m = 73, nine stages, idle-axis hosting), two tools of the
bit side are ported:
- **Shared-donor kernel** (#417/#435/#434/#439/#440 style): 79 pivots, rank-1 entrances, 14 entrance frames.
- **Entrance gauges** (#401/#408–#416 style): compensation moved to the entrance frame; 80 helpers, entrance
  rank 106 (62 rank-1, 14 rank-2, 4 rank-4), nested per target and per centre.
- Not portable on this word: elimination reuse and early resets (#436/#437): 0 helpers survive the frame-monotonicity
  check; block retiming (#441/#440): 0 improvement (frame cost unchanged after single-gate and closure moves).

## Measured (hosted b, exact moment engine; the hosting step is my replica of #442's, which reproduces #442's complex b
1.267453159029119e-3, live stock 8400 and rank deficit 2496 to the last digit)
| word | helpers entering | total entrance rank | b | gain | κ cap if complex-bound |
| --- | ---: | ---: | ---: | ---: | ---: |
| #442 complex | 0 | 0 | 1.267453e-3 | | 1.265849e-3 |
| kernel only | 79 | 79 | 1.310216e-3 | +3.37% | 1.308502e-3 |
| gauge only | 80 | 106 | 1.310916e-3 | +3.43% | 1.309200e-3 |
| gauge + kernel | 122 | 148 | **1.333854e-3** | **+5.24%** | 1.332077e-3 |
The combined word hosts all 40,320 residuals (live stock 7,680, no bank). The rank deficit is 2496 in every row.

## Checks that PASS (local word only; `sh check.sh DIR`)
- Exact arbitrary-dirt and inverse-transpose replay of the full word (800 columns), frame chain, paid profile.
- Emitted local program, literal scalar replay in both orientations on 800 columns with centre lifetimes.
- Exact Gaussian phase recipes for every used frame transition (`PHASES=1`): 2,932 / 2,940 / 2,952 edges.
- Entrance-adapter evidence: for all 16 entrance frames E→FULL = monomial · C_[9−e] · monomial exactly
  (`lower_child`: tableau and state-vector equality, global phase included).

## Plain statements about what is NOT met
- **The entrances are isotropic** (even-weight lines of F2^9). The bit-style coordinate-entrance criterion (#440's
  `validate_isometries`) is NOT met, and no orthogonal map of O(9,2) can meet it for these lines. Restricted to
  entrances that meet it, the gain is 0 (`code/iso1.py`).
- **#442's shipped complex audit and emit assume `w == 9` and `start == 0`.** No shipped complex word has a nonzero
  helper entrance. The audit, emit and phase scripts used here are PATCHED copies (`code/audit_cxg.py`, `emit_cxg.py`,
  `phases_cxg.py`: pre-ops, entrance starts, target levels, centre descent); their defaults are not yet shown to
  reproduce #442's files byte for byte.
- The claim is therefore **conditional on Lemma A (entrance adapter) and Lemma G (nonzero-frame compensation and centre
  scatter)**, which are the headline review points.

## Pending
Global template, owner tables and hosting generator for mixed residual widths (the hosted b above is a model);
residual-to-bank routes for each entrance frame; written proofs of Lemma A(ii) and Lemma G; mutation controls;
finite invoices and the outer assembly (47/47) with a bit word; byte-for-byte regression of the generalised scripts at
the #442 defaults; two fresh-copy replays.

## Files
`PROOF.md` lemmas and scope; `check.sh`; `data/words/*/FULL-WORD.json.gz` the three words; `data/selection/*.json`
frozen selections; `code/` checks (`audit_cxg.py`, `emit_cxg.py`, `phases_cxg.py`, `cxcheck.py`, `hostmodel.py`,
`final_eval.py`, `nec3.py`, `nec4.py`, `iso1.py`) and the search scripts that produced the selections
(`kern*.py`, `gauge*.py`, `retime.py`, `reuse*.py`).

## Credits
Builds on #442 (DaysSky, idle-axis hosting), #433 (icekylinx, split centres), #425 and #386 (jacklightChen / Zhihao
Chen, mutable packets, compressed windows), the shared-donor kernel of #417/#435 (chafreaky) and #434/#440 (rohanarun,
chafreaky), the entrance gauges of #401/#408–#416, #370 (Dylan Crow) and Jacob Sussman's E8 unit.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
