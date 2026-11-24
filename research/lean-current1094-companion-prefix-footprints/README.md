# [Lean] Certify complete selected companion prefix footprints and cuts

At source-matched κ = 836330098538459/500000000000000000 = 0.001672660197076918, this Lean certificate accounts for both selected 16,508-mark prefixes, all six phases, exactly 23 tracked companion label writes, and all 23 move/seven ADD-query arithmetic cuts. It proves finite mark/label footprints and conditional projected cursor facts, retaining the explicit L508 start2/terminal999 hypotheses. JSON-byte-to-typed-mark correspondence, successful full guarded lowering, RecipesExact, full-phase operator equality, physical execution and cost remain explicit gaps; it does not change κ or prove the full multiplication theorem.

Both raw prefixes [0,16508) are accounted for, with 66 finite block roots, one core and one exhaustive join. Exactly 23 writes to L157/L219/L230/L508 and six phases are retained; all 23 move and seven ADD-query cuts are checked. The mark model includes COPY’s dynamic stored tag. This does not discard any physical operation or prove successful whole-word lowering.

## Existing accepted evidence

Final source 625a27a8/object 82232134 and independent terminal 3fbe6bb2. Existing 68 fresh roots have 727 complete probes, 141.875897878 seconds total compiler time. The original monolith timeout, namespace/reflexivity and append-association failures remain preserved in owner history. Only accepted block 58 has two preserved style warnings; no warning suppression or rerun.

SOURCE_MANIFEST gives every exact source, immutable provenance, ordered import and reference object hash. Historical uncompiled preparation comments stay unchanged; current acceptance is recorded separately.

## Reproduce the exact source layout

Use Python 3 and a Git input repository containing these public immutable commits. No private worktree path is required by the materializer.

```sh
git init public-inputs
cd public-inputs
git fetch --depth=1 https://github.com/CrocSwap/integer-mult-bounds.git 0b1cccf86e2f5132ed286a26ef0a681a495740ea
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

Credit icekylinx’s selected emitter, DreamingOfClouds LemmaG semantics, Jeremy Kothe HyperplaneEnd labels (Claude Opus5.5 in omp), Hanson Sun PR1611 helper450 lead and Lean/Mathlib contributors. Full upstream headers are unchanged. The selected input/binding evidence is source-reviewed; it is not a Lean JSON byte-parser theorem.
