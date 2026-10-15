# Full historical PR926 Boolean D-word certificate

This package gives a complete Lean certificate for the exact historical PR926
D word relative to its PR915 parent. For every state on 661 Boolean registers,
`CurrentMain.PR926FullDComposition.full_D` proves

```
run (helpers ++ preparation ++ encoded ++ preparation.reverse ++ helpers.reverse) s
  = run (preparation ++ original ++ preparation.reverse) s
```

and restores every off-target register to its incoming value. All 111 target
rows, coordinates 111 through 221, are joined. Every input coordinate is covered
by the checked finite-basis theorem. Incoming helper and target bits are
arbitrary. No missing-row, encoded-matrix equality or clean-state premise remains
in this finite theorem.

## Exact scope and source

The data is pinned to bitplane PR926
`0f216a345c37bc71cc0e22030ef11ec31b26a69e` and its PR915 parent
`e9daefe320a0043000bd9746664ed02c3287d056`. The candidate has 192 helper
preparation entries, 306 target preparation entries and 111 injection rows.
Ordered donor lists and multiplicity are preserved. The complete words contain
1107 and 723 entries respectively; injection entries may have multiple donors,
so these are not elementary ADD counts.

This is a Boolean interpreter result for those immutable historical words.
Physical/frame realization, integer lifting, rounded inverse cancellation,
precision and cost, adoption into the current selected construction, and a
complete integer-multiplication theorem remain separate.

## Author-checked current numerical context

At pinned upstream main `0b1cccf86e2f5132ed286a26ef0a681a495740ea`, the selected
conditional record is

`kappa = 836330098538459/500000000000000000 = 0.001672660197076918`.

The author directly read `certificates/selected-result.json` (SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`) and
`research/community-frontier1094-audit/ASSEMBLY.json` (SHA256
`1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`).
Both contain this value. This contribution does not change kappa or certify the
selected construction. `CURRENT_CONTEXT.json` retains the exact readback.

## Proof structure and reuse

The existing PR590 ordered multioperand XOR interpreter and PR597 reversal laws
are reused unchanged. PR774 already established generic XOR-linearity and
compensation algebra for a separate unary interpreter. The contribution here is
the complete source-bound PR926/PR915 instance, using the ordered interpreter,
finite-basis lifting, disjoint support and all 111 actual injection-row equations.

Donor permutation and pair cancellation are proved sound for arbitrary input
states before canonical rows are compared. A proved target-donor collector
avoids repeated whole-word expansion without dropping repeated donors or writes.
Every concrete row certificate is a separate kernel-checked root. The final
finite-index join imports every one exactly once. See `NOTICE.md` for credit.

## Existing checks and evidence

All 111 row roots and the final full-D join have independent acceptance. The
final source is SHA256
`3931c08707ef1b2019ed734489e950549a3043cc78f7310fa4a8b920e0521b56`, and its
native object is
`31cb711a9fd0a55c5b1d55182c48ea0e1844c5b04d8868c323414c364114b46c`.
Its two complete public axiom probes contain only `propext` and `Quot.sound`.
The final compiler took 1.463697 seconds, sampled peak virtual memory 736575488
bytes. The 111 successful row compilers took 589.820443 seconds in total.
The 76 collector-based rows took 158.444667 seconds, with largest observed
per-row runtime 4.729619 seconds and sampled virtual memory 1125773312 bytes.
These are actual saved measurements, not bounds for other machines.

`evidence/` contains the final raw receipt and independent source/terminal
readbacks. `CHECKED_OBJECTS.json` pins every accepted prerequisite object without
distributing generated objects. The owner checkpoint
`02fac1207ba4eedbfc813882a3731c53035f3541` retains the complete raw row records,
original failed attempts and their preimages. The first full-row client hit an
allocation limit; a later original row035 did likewise. A one-site elaboration
repair was needed in the generic normalizer and another in the final index
join. Accepted row objects were retained rather than rerun. Historical proposal
comments in unchanged Lean files are preserved; this README and the independent
receipts record their completed status.

This source packaging itself has not been rebuilt. There is no fresh CI or
repository-wide check claim. Subsequent CI outcomes must be reported separately.

## Fresh reproduction

Use Lean 4.21.0 on Linux with Bash, GNU timeout and sha256sum available. No
Mathlib dependency is required. From this directory run:

```
bash rebuild.sh
```

The script checks all source hashes, requires a fresh output directory and
compiles the exact 127-source topological order. It uses a 40-second per-root
timeout and 3.5 GiB address-space cap, preserves logs, and stops at the first
failure. It installs nothing. Set `LEAN_BIN` to an existing Lean 4.21.0 binary
if needed. The full reproduction spans the original bounded batches; the saved
native runs also had a 120-second aggregate limit per batch. This simple
reproduction script does not claim that aggregate monitor or the original
runtime telemetry. It is supplied for post-publication CI, not as a new checked
proof artifact.

Every packaged Lean byte matches an accepted source. `SOURCE_MANIFEST.json`
records imports, source hashes and expected printed declarations;
`SOURCE_SHA256SUMS` and `BUILD_ORDER.txt` give the portable source census/order.
The only external direct imports are Init and its FinRange/Sort modules.
