# Validation and review handoff

Exact base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`.
Assignment seed: 42, generated with Windows OS cryptographic randomness.
Validation host: Windows, bundled CPython **3.12.14**, standard library.

## Reproduction

From the repository root:

```sh
python -I -O -B research/five-cube-coded-copy-seed42/verify.py
python -I -O -B research/five-cube-coded-copy-seed42/independent.py --exhaustive-factorizations
python -I -O -B research/five-cube-coded-copy-seed42/test_package.py
```

Expected markers:

```text
PASS_FIVE_CUBE_CODED_COPY pairs=3969 copy_floor=32 peak_floor=8 witnesses=2 controls=8 pins=6 no_new_kappa
PASS_FIVE_CUBE_CODED_COPY_INDEPENDENT ranks=3969 observation_rank=6 decoder_rank=2 copy_min=32 peak_min=8 all_stage_deficit<=-32 controls=9 exhaustive=true
PASS_FIVE_CUBE_CODED_COPY_PACKAGE tests=6 optimized_relocation=true corruption_rejected=true
```

Normal and isolated optimized primary/independent replays pass. The
independent exhaustive replay checks the complete committed receipt,
including all 1,324,327 reduced-span source assignments. It took about
10.2 seconds on this host; this is a local runtime observation, not a
before/after performance claim.

The package tests relocate the whole package to a path containing spaces
and run both checkers with `-I -O -B`. They require rejection of altered
source bytes, a missing manifest entry, an altered primary rank entry and
an altered independent receipt. Both exclusive-output commands reject an
existing filename and preserve its bytes. These exercise mathematical
binding and failure detection, not just formatting.

The predecessor and selected-record checks also pass:

```sh
python -I -O -B research/five-port-quadratic-decoder/verify.py
python -B scripts/verify_selected_result.py
```

Expected predecessor marker:
`PASS_FIVE_PORT_QUADRATIC_DECODER witnesses=17 ceiling=125/76433 tail=250/170739 controls=9 no_new_kappa`.
The selected-record check reports the unchanged conditional
`1661960547713947/1000000000000000000`.

`git diff --check` passes. The new package is the only changed directory;
no selected certificate, upstream file, global generator or pre-existing
source is edited. Raw Git source bytes are used for the six snapshots,
avoiding Windows newline translation in immutable pins.

## Evidence and bounds

The primary census covers all 63 nonzero affine forms in each orientation,
for 3,969 ordered support pairs. The independent census reconstructs the
quadratic Gram from actual coordinate-set intersections and computes
rational ranks with integer elimination. It imports no primary code and
matches every entry of the complete primary table.

The primary checker also computes exact rational ranks for the whole Gram
and both literal witnesses. Both decoder witnesses are checked at every
one of 1,024 source/target entries. The primary has eight controls and the
independent checker has nine, addressing omitted/changed factors, invalid
geometry, false diagonal coverage, source binding, unsupported copy charge
and elimination pivots.

The optional experiment exhausts one dimension-two and 15 dimension-three
reader subspaces containing the decoder code `U`, with distinct nonzero
reader subsets of at most five elements. Every binary source assignment
solving the full coefficient matrix is visited; zero source factors are
counted separately. Coverage is complete and termination occurs only after
the finite domain is exhausted. This is deterministic; the OS assignment
seed selected the research object, not a randomized partial search.
The global theorem uses only exclusion below 32, plus Sylvester's rank
inequality and the six-per-term floor for longer factorizations. The
reduced-span minima 32/35/32/43 are not unrestricted fixed-length minima.

One separate AI worker implemented the integer census and enumeration.
A second AI worker audited the Sylvester, diagonal, modular/rational and
proxy/physical arguments, and ran default and optimized exhaustive checks.
Neither found a proof-relevant flaw. No independent human or proof-assistant
review is claimed.

## Overlap and limits

Initial orientation inspected 718 open PR metadata entries. A final refresh
through **PR1045** immediately before submission found no overlapping affine five-cube copy result; main
remained at the exact base. PR958 is closed/incorporated, with original
head `28d68c88f0184835d8c8a7266ab8d0dad3f18a8a`. Its separate-total theorem
explicitly leaves coded combinations outside scope. The continuing PR669
campaign uses a different Gram/odd-diagonal premise. Their attribution
is preserved and no pending implementation is imported.

This package proves a finite algebraic objective and a conditional negative
budget consequence. It supplies no source/gather/frame/restoration program,
hosted controller, exact precision invoice or new kappa. Changing its Gram,
affine support class, full matrix identity, stage persistence or additive
copying model can evade the stated premises and must be priced separately.

The repository-wide `make verify`, selected supplier cold replay, Linux CI
and an all-size theorem were not run for this isolated research package.
The affected predecessor, package and selected-record checks are recorded
above; no unrelated artifact regeneration was performed.

Submitted once as [PR1046](https://github.com/CrocSwap/integer-mult-bounds/pull/1046),
with the local sprint claim updated to its result and link. No PR was merged,
no other PR was closed, and the selected frontier was not edited.
