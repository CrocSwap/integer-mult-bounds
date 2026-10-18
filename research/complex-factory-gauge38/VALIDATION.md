# Executed validation

The original standalone validation below is preserved. The later PR922/924
composition, its exact heads and reproduction command are documented in
[COMPOSITION.md](COMPOSITION.md); it has a separate frozen receipt and controls.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Executed on Linux, CPython **3.12.14**, 2026-10-13. Verification uses only the
standard library. Optional nomination used NumPy **2.3.5** / SciPy **1.17.0**.

## Results

| Executed check | Result |
| --- | --- |
| `python3 -I -B research/complex-factory-gauge38/verify.py` | PASS; frozen full receipt matches |
| Same full command with `-O` | PASS; same receipt, inherited child assertions enabled |
| `python3 -I -B research/complex-factory-gauge38/test_package.py` | PASS, nine tests |
| Full optimized replay in a minimal directory with spaces, no Git metadata, only 16 pinned inputs, repacked gzip sources | PASS; included in the nine tests |
| Optional `nominate.py` | PASS; exact tension 9, class optimum 67, feasible 34-macro cost 77 |
| `make selected-record-check` | PASS; selected κ `1661634653669567/10^18` |
| Python compilation of the three scripts | PASS |
| Scoped source/diff checks | Only this package added; `upstream/` and selected artifacts unchanged |

Full reproduction ends with:

```text
PASS_COMPLEX_FACTORY_GAUGE38 baseline=81 budget=77 class_optimum=67 controls=46 blocks=14 saved=224,224 local_bill_delta=-224 no_new_kappa
```

The normal and optimized runs compare every deterministic field in
`EXPECTED.json`, including complete-word hashes, literal primitive-stream
hashes, counts, prefix and fractional-depth measurements. This is not merely
a check for a PASS string. Generated gzip containers are not equality oracles;
source payloads and complete canonical JSON data are compared where appropriate.

The full replay freshly executes the raw constructor, binds all fourteen
physical windows, and checks the baseline, useful candidate, and cheaper-scalar
accounting control in both orientations. Each primitive projection checks all
**725 arbitrary input columns**; inherited frame/wrapper checks cover 716
logical columns. The useful candidate's exact prefix row-l1 peaks are still
124/107, and both fractional depths are still two bits.

## Adverse and neutral controls

- **46 local rejections:** over-capacity and unbalanced dual flows, zero dual,
  fractional/boolean gauges, unpaid boundary gauge, a falsely low price,
  missing restoration, changed addition sign/frame, endpoint-neutral extra
  work, uncleared arbitrary coefficient work, and deletion of each of the
  34 shipped candidate gates. Every control must fail for its specified reason.
- **One physical-boundary rejection:** corrupt the frame of seed-selected
  block 10; the unchanged predecessor binder rejects the boundary mismatch.
- **Four inherited negative controls per rebuilt native word:** wrong scale,
  missing center, wrong common frame, and wrong child rank; all three words
  retain these checks.
- **Two valid neutral controls:** move either doubling alone; complete maps
  agree but neither saves primitives. The joint change does.
- **One valid inferior accounting control:** the 67-primitive circuit passes
  its identities but increases the complete local PR696 bound by 46,474,329,328.
  It is not counted as an identity rejection.
- **Nine package tests:** minimal optimized relocation, full isolated/repacked
  replay, recompression acceptance, source corruption/missing-source rejection,
  malformed dual/boolean-gauge rejection, altered-receipt rejection and existing
  output preservation.

No implementation or mathematical check remains failed. Early exploratory
nomination of the 67-primitive circuit failed the useful-cost objective; the
explicit macro-budget revision is the verified 77-primitive construction.

## Source and publication boundary

Exact starting commit: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
The review-time upstream refresh reached
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`, a review-planning update. All sixteen
consumed inputs and the selected κ were unchanged. The contribution retains
its original base; no upstream branch was modified. The live selected pointer
is contextual evidence, not a runtime dependency of this historical circuit.

`OVERLAP.json` preserves the scoped public-HTML review. No pinned sprint
coordination issue was available, and the task explicitly excluded GitHub API
publication. The claim/result are local; branch publication and its remote
commit are reported in the final handoff.

The last overlap refresh found PR922, whose different 32-macro contraction
targets the same historical factory. Its reported marginal PR696 saving is
also 224. The README records the exact observed head, the different mechanism
and additional proof/replay coverage here. No combined saving is claimed and
PR922 was not replayed as part of this validation.

Not run or claimed: full `make verify`, selected frontier799 cold replay,
later provider transport, Clifford phase lowering, whole-owner/global invoice
or outer-assembly replay, Lean, another Python version, or remote CI. These
are separate from the completed raw-constructor/native/primitive verification.
No independent human or delegated-agent review is claimed.

## PR922/924 composition follow-up

Executed on 2026-10-14 (Australia/Sydney), Linux, CPython 3.12.14. Both pinned
heads and exact scope are recorded in `COMPOSITION.md`.

| Executed check | Result |
| --- | --- |
| `python3 -I -B research/complex-factory-gauge38/compose_pr922.py` | PASS, complete frozen receipt matches |
| `python3 -I -B research/complex-factory-gauge38/test_composition.py` | PASS, seven tests |
| Full isolated optimized replay with `-O -S`, minimal source closure, spaces and repacked inputs | PASS, included in the seven tests |
| Fresh PR922 native record versus its pinned retained `RESULT.json` | Exact match; one-time comparison |
| Both application orders, all four local orientations, eight complete primitive projections with 725 columns each | PASS |
| 38 local rejection controls, one complete missing-cleanup control, four inherited controls per native word | PASS |
| Original PR924 `verify.py --local-only` | PASS, original class certificate and all 46 controls unchanged |
| `make selected-record-check` and whitespace checks | PASS |

The combination uses 32 macros and 73 PR696 primitives per component per block.
Full counts are 123,320 forward and 123,336 backward. The saving against either
standalone PR is 224 per orientation. The selected κ remains unchanged.

Only the historical raw circuit and its retained local cost formula were
replayed. Full `make verify`, selected-provider transport, frontier799 cold
replay, phase/global/outer assembly, Lean, other Python versions and remote CI
were not run for this follow-up. The original PR924 full suite was not rerun;
its source files are unchanged, its local suite passes, and its useful full
candidate is freshly reproduced and matched by the composition command.
