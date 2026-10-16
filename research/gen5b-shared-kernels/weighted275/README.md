# Shared-donor kernels on the pinned weighted-matching word

This additive PR302 experiment composes shared-donor kernels with PR275's
weighted-matching word. It preserves the parent directory's original pinned
70/72-pivot and co-retiming evidence. It does **not** transfer the old final12
stock saving: every one of those twelve helpers is now a matched recipient,
whose earlier donor lifetime still needs its unchanged FULL cleanup.

## Conditional results

| Fixed case | κ | Literal stock | Five-stage calls | Rank mass |
|---|---:|---:|---:|---:|
| Pinned PR275 baseline | 0.000751075693834608 | 1,229,735 | 482,100 | 2,455,070 |
| Weighted word + transported 70 | 0.000751090249287618 | 1,229,560 | 482,535 | 2,454,720 |
| Weighted word + reclosed 166 | **0.000751097723288767** | **1,229,320** | **483,150** | **2,454,240** |

The 166 case improves the pinned baseline by about **0.00293305%**. These are
exact rational grid choices with denominator 10^18, conditional on the retained
physical decoder, compiler, primitive and all-size interfaces. This is a small
finite-recipe improvement, with no global priority, optimality or unconditional
multiplication-theorem claim.

The final candidate has 166 pivots, 210 distinct donors and 376 physical helper
slots, including 105 reused donor slots. It has 2,587 setup ADDs and the same
number of inverse ADDs. Its measured local histogram change is
`{1:+210, 2:+306, 3:-306, 4:+70, 5:-70}`. The residual-width change is
`{24:-166, 23:+166}`. The deficit remains 4,400 in the unreplicated profile.

Fresh scalar bounds are F=433,193 and B=14,098,095. The exact payload upper bound
is 1,034,058,550,487,293,134,087,986,294,683,200 (110 bits). The original 104-bit
assertion fails; the separately reviewed, explicitly named 112-bit fixed-recipe
certificate passes. This distinction is intentional and tested. See PROOF.md
for the static source audit and the remaining quantified constants.

## Immutable inputs and attribution

The base is `lydakis/integer-mult-bounds` at
`10b40041d4ab8a6610083e95bc571aee3468bca2`, package
`research/gen5b-weighted-matching`. It already includes its remapped inherited
kernels, descents, 440 restorations and seven sinks. Those transforms are not
added again. One separately pinned PR299 word is used only for the old-to-new
role-map diagnostic. The two pure arithmetic helpers, original 70 witness and
final12 diagnostic are reused from the unchanged parent PR302 package.

`inputs.json` pins 39 inert input files (about 10.9 MB) by immutable URL,
byte count, SHA-256 and Git blob ID. All downloaded Python files are stored as
`.py.txt` and read or parsed as data. No upstream producer, verifier or module
is executed. Large source bundles, generated chart programs and complete bank
tables are deliberately not committed. See NOTICE.md for credit and AI disclosure.

## Reproduce from the PR302 checkout

Python 3.11+ and the standard library suffice. Assertions must remain enabled.
From this `weighted275` directory:

```sh
python3 -B fetch_inputs.py --output /tmp/weighted275-inputs
export PR275_INPUTS=/tmp/weighted275-inputs
export PR275_OUTPUTS=/tmp/weighted275-results
python3 -B -m unittest discover -s . -p 'test_*.py' -v
python3 -B run_checks.py --check --inputs "$PR275_INPUTS" --output "$PR275_OUTPUTS"
```

Absolute invocation from another working directory also works. Existing input
files are accepted only after hash verification. The aggregate independently
rebuilds both cases, baseline and complex arithmetic, full role/replica bank
addresses, changed chart programs, finite invoices, the 276-line screen and
both declared overlap-resolution orders. Generated data stays in the chosen
output directory. `--case 70` or `--case 166` selects one case; `--skip-screen`
omits discovery replay but does not skip that case's admission checks.

The parent directory's existing test/replay commands remain unchanged. Its
original source inputs are separate; fetching the new weighted inputs does not
replace them.

## What this update checks

- Exact virtual-to-physical alias map, source pins and all 1,720 old kernel
  response relations and cut triples on the new word.
- The final 166 relations, complete chronological donor/recipient paths,
  2,561 exact containments and final FULL endpoints.
- Forward/inverse compositional F2 equality on all 18,952 physical columns,
  assuming the inherited complete decoder. This is not a literal regeneration
  of the entire upstream scalar stream.
- 304 distinct exact rational chart programs, bound to 752 role uses. The
  maximum is 508 factors; factor numerators/denominators are at most 615/810.
  The retained combined normalizer bound is 815.
- All 15,425 helper roles in 60 replicas: 925,500 explicit addresses per stage,
  five disjoint stages, 4,627,500 total assignments. Every width-120 bank is full.
- Sink-aware forward/inverse scalar majorants, every added setup/restore ADD,
  selector bound 905,876,591,400, and displayed finite coefficient
  90,433,795,441,918,801, strictly below 2^80.
- Exact bit-root bracket
  `[751662295432463, 751662295432464] / 10^18`, three bootstrap steps, all 47
  strict rational inequalities and rejection of the next κ grid tick.
- Negative controls for mapping/relation/frame/alias errors, omission of shear
  factors, bank/stock/replica drift, missing chart paths and the old payload cap.

## Bounded discovery scope

The corrected eligible domain has 8,085 unused physical helpers, including
1,591 reused donor slots. Recipient keys, existing kernel members, both descent
supports, early-restored endpoints, sources and sinks remain excluded.

The experiment tests all 276 contrast lines `e_i-e_j` in 24 dimensions using a
fixed role-order response basis. A maximum-closure calculation charges shared
donors once and optimizes a 10^9-rounded entropy surrogate, not κ itself. Three
groups survive: 136 pivots on line16/17, 36 on line6/7 and 12 on line2/3.

There are four overlapping logical roles between the first two groups; the
third is disjoint. We evaluate exactly two priority orders. Preserving the
136- and 12-pivot groups leaves 29 nonconflicting secondary relations; closure
selects 19, then a declared deterministic parity trim removes pivot10764,
leaving 18. Thus the winner is 136+12+18=166. The reverse priority order selects
no additional surviving primary relations and returns the 48-pivot union.
The two naive prune-and-retain variants are comparison cases, not further
search domains. No optimum over all bases, active sets or conflict resolutions
is asserted.
