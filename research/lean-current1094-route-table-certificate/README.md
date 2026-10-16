# [Lean] Bind all 144 selected parsed route tables to certified owners

At source-matched κ = 836330098538459/500000000000000000 = 0.001672660197076918, this Lean certificate connects all 144 ordered selected route tables’ parsed values to the accepted per-call owner assignment. JSON-byte-to-parsed-value correspondence remains source-reviewed; actual physical charts, private C allocation/operator semantics and executor refinement remain explicit suppliers. It does not prove the full multiplication theorem or change κ.

All 101,376 ordered rows (32,256 data and 69,120 helper rows) are covered. The 26 newly accepted compiler roots include six catalog modules, 18 call blocks, the repaired generic decoder bridge and the final join; shared syntax and owner decoder are retained. All strict decoder guards are discharged. Per-call injection is proved, not global cross-call disjointness.

## Existing accepted evidence

Final source 1845c1f7/object 174289ab and independent terminal 16746648. The 26 new roots have 32 exact standard-only probes; accepted compiler time totals 75.665844489 seconds. This is existing evidence, not a packaging replay.

SOURCE_MANIFEST gives every exact source, immutable provenance, ordered import and reference object hash. Historical uncompiled preparation comments stay unchanged; current acceptance is recorded separately.

## Reproduce the exact source layout

Use Python 3 and a Git input repository containing these public immutable commits. No private worktree path is required by the materializer.

```sh
git init public-inputs
cd public-inputs
git fetch --depth=1 https://github.com/CrocSwap/integer-mult-bounds.git 0b1cccf86e2f5132ed286a26ef0a681a495740ea
git fetch --depth=1 https://github.com/jamesyc/integer-mult-bounds.git 457c6c315598ba1a05692fed55e3f47d99dbb184
cd ..
python3 "$PACKAGE/prepare_sources.py" public-inputs fresh-output
```

The script performs no fetch, install or compiler run. It checks all input lengths, SHA256 and public Git blob identities before creating an absent output directory. Public import substitution, if any, is declared and exactly inverted. Dotted modules are materialized with directory components, including HyperplaneEnd/Labels.lean. It preserves previous outputs by refusing existing destinations.

Install official Lean 4.21.0 and Mathlib at 308445d7985027f538e281e18df29ca16ede2ba3, with its exact lake-manifest.json 5143be87 and pinned packages. Use the official `lake exe cache get`. Set LEAN_PREFIX and MATHLIB to those roots, and OUT to the absolute fresh-output directory. Build topologically in BUILD_ORDER.txt with only OUT/objects followed by pinned package object directories, Mathlib objects and the Lean sysroot on LEAN_PATH; do not mix alternate copies of these modules.

```sh
export LEAN_SYSROOT="$LEAN_PREFIX" LEAN_NUM_THREADS=1
export LEAN_PATH="$OUT/objects"
for p in Cli batteries Qq aesop proofwidgets importGraph LeanSearchClient plausible; do
  export LEAN_PATH="$LEAN_PATH:$MATHLIB/.lake/packages/$p/.lake/build/lib/lean"
done
export LEAN_PATH="$LEAN_PATH:$MATHLIB/.lake/build/lib/lean:$LEAN_PREFIX/lib/lean"
while IFS= read -r module; do
  rel=$(printf %s "$module" | tr . /)
  mkdir -p "$OUT/objects/$(dirname "$rel")"
  "$LEAN_PREFIX/bin/lean" -j1 -o "$OUT/objects/$rel.olean" "$OUT/sources/$rel.lean" >"$OUT/logs/$module.stdout" 2>"$OUT/logs/$module.stderr" || exit $?
done < "$PACKAGE/BUILD_ORDER.txt"
```

Use bounded supervision appropriate to the recorded per-root native receipts; a new relocated total-budget fit is not claimed. Stop on any failure and preserve output. Check every existing axiom probe and complete warning block, including known inherited warnings. SOURCE_MANIFEST retains reference object identities but a path-dependent replay difference must be diagnosed rather than treated as source acceptance.

## Publication scope and evidence boundary

The source closure is packaged without another compiler or CI pre-review. Candidate CI follows publication; generic repository checks are not evidence that this Lean closure ran. The accepted source/transcription checks and native terminals are reused. Original JSON-byte correspondence and the explicit physical/full-construction suppliers remain outside the theorem.

Credit Rohan Arun PR1094, Jeremy Kothe T16/hyperplane-ended emitter, Hao Yan PR514/484/507 lineage, columbia-git PR1553, DreamingOfClouds PR509 Stream and PR516 Realize, and Lean/Mathlib/Batteries contributors. Original borrowed source headers remain byte-identical. The exact PR1807 owner certificate is a reused prerequisite, not a new owner assignment.
