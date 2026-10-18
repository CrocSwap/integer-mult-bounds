# Conditional κ = 0.001672780159952542 from four lower entrance frames

The exact conditional certificate is **836390079976271 / 500000000000000000**.
It improves pinned PR1087's `0.001672654541898561` by
`125618053981 / 10^18`. The conservative certificate is
`0.001672780157102838`; the native complex lower endpoint is
`1675583042021589509879 / 10^24`. The retained PR589 bit supplier is unchanged
and freshly repriced. This is a finite conditional construction, not an
unconditional multiplication theorem or a claim of κ > 0.01.

The change reverses one of the entrance promotions introduced by PR664 and
retained in the k8 construction. Helpers **635, 637, 638, 639** enter at
`span(298,170,102,30)` instead of `span(298,170,102,30,1)`; twelve phase-B
frames, at indices 372 through 383, decrease accordingly. Every scalar
instruction, source access, center, helper end and cleanup instruction is
unchanged. The new helper widths are five instead of four.

A wider helper is useful here because PR1087 leaves many one-rank gaps next
to width-four roles. At each of 109 eligible complete calls, a deterministic
permutation of equal-width owner positions puts the four affected helpers in
four such gaps, and their increased widths fill those gaps. The permutation
stays within a call, preserving its occupied families and event windows.
Affected bins are repacked contiguously and checked in full. The other 35
calls use the original word. There is no split helper or additional call.

## Complete cost

Writing H_r for a paid rank-r child, the local change per altered call is
`-8 H1 + 8 H2 + 4 H3 - 4 H4`, with rank mass +4. Filling four unit gaps
removes another `4 H1`. The global delta is therefore exactly
`109 * (-12 H1 + 8 H2 + 4 H3 - 4 H4)`, with zero change in total rank mass.
This is a change to the paid recursive profile, not merely an ADD/XOR count.
The exact moment engines price the literal aggregate rather than extrapolating
from a numerical local score.

| Quantity | Certificate |
|---|---:|
| Complete calls / whole helper roles | 144 / 69,120 |
| Original / changed provider calls | 35 / 109 |
| Paid rank mass / deficit | 1,041,408 / 5,120 |
| Idle children | 1,844 H1 + 378 H3 + 6 H7 + 4,866 H48 |
| Exact prefix / charged prefix bits | 397 / 512 |
| Physical row coefficient / retained budget | 16,469 / 20,161 |

The full global profile is
`348300 H1 + 61064 H2 + 63022 H3 + 20012 H4 + 11808 H5 + 6 H7 + 1152 H8 + 4866 H48`.
The unchanged controller checks source access, both orientations, wrappers,
restoration, charts, every recursive child, the finite invoice and all 47
strict outer inequalities. No purported saving is credited outside that invoice.

## Reproduce

From a full repository checkout, with Python 3.12+ and Git:

```sh
python3 -B research/demote635-t16/reproduce.py --out /tmp/demote635-fresh
```

The output directory must be new. Expected final line:

```text
PASS_DEMOTE635_T16_COMPLETE_ADMISSION 0.001672780159952542
```

The first run fetches missing immutable source commits. `--main /path/to/repo`
can supply the main dependency tree when this package is checked out sparsely.
No optimizer or third-party Python package is needed. `SOURCES.json` pins
base **2921874911956718fcaaaf9396fe8267b3cfa9f0**, PR1087 at
**589d1cedf5ef5f231182f4ec86408616311a8af0**, and the PR635 native verifier at
**a6895a69f8ad98ab45777b03e9e6f48888c39f6f**. The parent manifest and every
consumed main-file pin are checked. The literal baseline word is bound to
PR1087's construction payload hash.

The command reconstructs the changed word and owner permutation, freshly
replays both 704-column scalar words in both orientations, both sets of
2,896 exact phase edges, wrappers and independent frame/cone audits, and then
replays the parent and mixed global admissions. It rejects 19 additional
frame/scalar/profile mutations, 23 controller mutations, 114 admission
mutations, 12 bit-supplier mutations and six independent owner mutations.
Each native word also carries its 25 native controls. Optimized Python is
rejected before any output is created. Regenerated containers are compared
through the inherited semantic identities; committed source containers retain
exact hashes.

The portable command starts from the pinned literal word. It does not rerun
the historical k8 search/generator chain or the unchanged PR589 bit circuit.
Those are inherited evidence, not claimed as fresh work. The affected native
and global checks are fresh. This package changes no shared generator,
selected-frontier artifact or `upstream/` file; repository-wide historical
suites and hosted CI are separate from its scoped verification.

## Scope, prior work and overlap

PR664 established entrance promotion; PR685 and the subsequent k8 lineage
composed it with other changes. This contribution reverses one group against
the new T16 owner geometry. The older observation that promoting every group
can lose to packing costs is retained. The new evidence is the explicit
opposite transformation, within-call placement and admitted complete profile
on PR1087. It does not claim a new general optimization theorem.

PR1090 independently constructs narrower k8 ends and explicitly reports a
smaller pending κ. Our saved earlier helper543 narrow-end experiment was
also superseded. Neither is a dependency of this word. PR1094's verified
`0.001672660197076918` and PR1107's reported fully replayed
`0.001672765980186726` were checked during preparation and are below this
result. `VALIDATION.json` records the final metadata refresh. Neither
concurrent owner map is consumed. Historical and bounded unsuccessful investigations are
summarized in `SEARCH.json`; none is an impossibility proof.

All-size recursive compilation, common labels and mutable-source realization,
whole-call physical hosting, precision/tape accounting, exact recovery,
analytic transfer and PR589 bit assumptions H1–H5 remain inherited obligations.
The finite checks neither discharge these contracts nor constitute a full
Lean proof. Contributor credit and substantial AI assistance are disclosed in
`NOTICE.md`.
