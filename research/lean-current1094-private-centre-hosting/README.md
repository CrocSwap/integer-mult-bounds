# [Lean] Conditional private-centre hosting for the selected 1094 register interface

Local publication preparation only. No new PR or candidate-specific CI is claimed.

## Author-checked source context

κ = **836330098538459/500000000000000000 = 0.001672660197076918**.
The source author independently checked the exact selected-result and full
ASSEMBLY certificate and approved the paragraph preserved in AUTHOR_CHECK.json.
The scientific inputs remain identical at applicability commit
0b1cccf86e2f5132ed286a26ef0a681a495740ea. That is a source-applicability pin,
not a reserved future publication base.

This package proves three conditional hosting facts for `Fin 704 ⊕ Fin 8`.
It does not establish the full selected construction or the multiplication
exponent above. The 704 ordinary registers comprise 224 data/target registers
and 480 helpers. The eight private centres are tagged separately from the
14,336 live families.

## Exact checked scope

The new source is Current1094PrivateCentreHosting.lean, 4,110 bytes,
SHA256 f4ddb193fc07a44f56ed53cb903f80d0776474d06e890984f9a3e29b9fac0589.
It proves:

1. A supplied injective live-owner map remains injective after adding the
   disjoint private-centre tags.
2. An actual Hosting owner map is injective when its family projection equals
   that declared family map for every register.
3. If the full actual invocation function equals `LemmaA.realizeRun`, reading
   that invocation through the supplied charts equals the local event run.

The live-owner injection, full family-projection equation and full-function
actual-executor equality are hypotheses, not extracted from an emitted table.
Actual numeric addresses, labels, recipes/full phases, whole-word execution,
intervening schedule, norms, precision/roundoff and uniform physical costs remain
separate suppliers. This package imports no concrete owner-table decision,
ScalarWriteSupport, Schedule/Tensor modules or selected full-word decoder.

## Reuse and attribution

Two existing source dependencies are derived rather than copied into this
package. Both come from merged upstream PRs by DreamingOfClouds:

- PR509, immutable 7b9c720ecc9f483c383e7cd9c2ab81f06ee5df59:
  research/e8-lemma-g-lean/LemmaG/Stream.lean. Its 15,263 bytes are unchanged;
  only the prepared filename is FreshScalarSupportStream.lean.
- PR516, immutable 1c6b6ff9366a94e1f86a6c5d661a7df75c6ff814:
  research/e8-lemma-a-lean/LemmaA/Realize.lean. Replace exactly one line
  `import LemmaG.Stream` by `import FreshScalarSupportStream`. The inverse
  recovers every raw byte; the prepared file is 8,119 bytes.

No inherited theorem is re-proved or presented as new. SOURCE_MANIFEST.json
pins original Git blobs, complete input/output hashes, exact replacement and
compile order. The original notices and licence are included. The new adapter
was prepared with OpenAI assistance; the inherited sources credit Claude Opus
5.5 (Anthropic), via Claude Code. Further upstream credits are preserved verbatim.

Existing PR581 already uses the same raw Stream under a different module name.
That historical object is not silently substituted for this fresh alias object.
Use one coherent provider for each unchanged LemmaG/LemmaA namespace. Never put
raw, PR509Stream, PR516Realize and these fresh aliases together in one closure.

## Reconstruct all three accepted source bodies

The following source-only steps require Git and Python 3. They do not install
or run Lean, execute an upstream supplier, or require private workspace paths.
Choose a new source repository and an absent stage. If the two commits already
exist locally, reuse that repository and omit the fetch.

```sh
PACKAGE=/absolute/path/to/this/package
SOURCE_REPO=/absolute/path/to/new/source-repository
STAGE=/absolute/path/to/absent/hosting-stage

git init "$SOURCE_REPO"
git -C "$SOURCE_REPO" fetch --no-tags \
  https://github.com/DreamingOfClouds/integer-mult-bounds.git \
  7b9c720ecc9f483c383e7cd9c2ab81f06ee5df59 \
  1c6b6ff9366a94e1f86a6c5d661a7df75c6ff814
python3 "$PACKAGE/prepare_sources.py" "$SOURCE_REPO" "$STAGE"
```

The preparer checks SHA256, Git blob, byte counts, unique import substitution
and exact inverse before writing. It refuses an existing stage and leaves
partial output available for diagnosis. Its local source-materialization test
reconstructed all three accepted hashes exactly using the declared public Git
objects; no network fetch or compiler was needed for that test.

## Exact compiler command reference

Use official Lean **4.21.0** and Mathlib commit
**308445d7985027f538e281e18df29ca16ede2ba3**, with the eight package revisions
pinned in REPRODUCTION.json. Matching installed/cache objects are prerequisites;
this package does not install or rebuild Mathlib. LEAN_ROOT denotes the extracted
Lean distribution, MATHLIB the exact checkout and STAGE the prepared directory.
Clear inherited LEAN_* variables before applying the explicit environment.

```sh
set -eu
export LEAN_SYSROOT="$LEAN_ROOT" LEAN_NUM_THREADS=1 MIMALLOC_ARENA_RESERVE=64MiB
export LEAN_PATH="$STAGE/objects:$MATHLIB/.lake/packages/Cli/.lake/build/lib/lean:$MATHLIB/.lake/packages/batteries/.lake/build/lib/lean:$MATHLIB/.lake/packages/Qq/.lake/build/lib/lean:$MATHLIB/.lake/packages/aesop/.lake/build/lib/lean:$MATHLIB/.lake/packages/proofwidgets/.lake/build/lib/lean:$MATHLIB/.lake/packages/importGraph/.lake/build/lib/lean:$MATHLIB/.lake/packages/LeanSearchClient/.lake/build/lib/lean:$MATHLIB/.lake/packages/plausible/.lake/build/lib/lean:$MATHLIB/.lake/build/lib/lean:$LEAN_ROOT/lib/lean"
cd "$STAGE/sources"
"$LEAN_ROOT/bin/lean" -s65536 -j1 -o "$STAGE/objects/FreshScalarSupportStream.olean" "$STAGE/sources/FreshScalarSupportStream.lean"
"$LEAN_ROOT/bin/lean" -s65536 -j1 -o "$STAGE/objects/FreshScalarSupportRealize.olean" "$STAGE/sources/FreshScalarSupportRealize.lean"
"$LEAN_ROOT/bin/lean" -s65536 -j1 -o "$STAGE/objects/Current1094PrivateCentreHosting.olean" "$STAGE/sources/Current1094PrivateCentreHosting.lean"
```

These are the actual accepted command shapes after only path parameterization.
They are a declarative reproduction reference, not a resource-monitoring wrapper.
A future admitted public replay must use the recorded serial source/runtime and
ordered-first-match guards, absent outputs, per-root 40-second/3.5-GiB review and
60-second/4-GiB hard limits, 120-second aggregate phase and 8-GiB disk floor.
No portable-package compiler replay has been run. Compare complete logs, all
three probes, both full printed types and object hashes to ACCEPTED_CHECKS.json;
a process exit alone is insufficient. Stop and preserve evidence on mismatch.

## Accepted native evidence and publication boundary

All three exact roots compiled in 6.875752744 seconds, with sampled maximum
virtual memory 3,301,359,616 bytes. The original supervisor initially marked the
lane failed because its printed-type parser expected no leading `@` and expected
proof-binder names that Lean elides. Original outputs remain preserved. A separate
read-only type audit and source/runtime postguard resolved the parser issue
without a source change or compiler retry. Independent terminal 766f77bb accepts
all three modules with their explicit premises; TERMINAL_REVIEW.json is exact.

The source headers retain their pre-run “source-only/uncompiled” wording because
accepted proof bytes were not edited for publication prose. The acceptance
records above describe the actual subsequent checks.

This is one coherent physical-interface chunk. Generic sorted owners, the
normalized-cost envelope/descent and the XOR adapters remain separate chunks.
The existing XOR publication draft is unchanged. Its green fork CI does not
apply to a future Hosting candidate. GitHub creation returned HTTP403 previously;
no retry or new upstream write is made here. Before publication, the designated
publisher must resolve the exact current base/head/duplicates, finalize the
candidate and preserve this author-checked κ and conditional scope.
