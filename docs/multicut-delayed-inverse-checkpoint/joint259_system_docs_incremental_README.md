# Incremental vector-page builds

This is a documentation cache for the selected hybrid construction. It does not
cache or substitute for scientific verification. The authoritative source-tree
integrity check still runs before and after the documentation build.

## One command: PDF and SVG

From `processor_architectures`, with the pinned Python requirements installed:

```sh
python -B joint259_system_docs_incremental.py \
  --source pr259_interval_compatibility_20261010/hybrid_package \
  --cache joint259-page-cache.json \
  --output joint259-docs-new \
  --svg
```

Choose a **new output directory** each time. Reuse the same cache file. Remove
`--svg` for a Python-only PDF build. SVG requires Poppler's `pdftocairo` on PATH;
the exact converter version is recorded. Graphviz is not used. The command
creates the same document/index families as the ordinary builder, plus linked
per-page SVG files and `incremental_receipt.json`.

`--clean` ignores the saved cache. `--emit-json` emits `{files, cache,
measurements}` without filesystem writes, for environments with managed write
tools. An explicit `--cache` can still be read in this mode. The ordinary builder
remains available as an independent full-render reference.

## What is actually incremental

1. Execute the original document functions with a recording canvas. This is
   lightweight layout and dependency planning; it does not paint PDF pages.
2. Hash each page's actual drawing commands, including text, geometry, colors,
   widths and page-number text. This is a precise projection of the model fields
   that affect that page. Unused model metadata does not repaint unrelated pages.
3. Bind that page hash to renderer and imported renderer code, cache code,
   configuration, source manifest, font bytes, pinned requirements file and
   installed package versions.
4. Check cached entry schema, keys, content digest and single-page structure.
   Repaint only missing, changed or damaged entries. Retain old entries so an undo
   can reuse the original pages.
5. Assemble the current ordered pages; rebuild every bookmark, outline and
   internal/external link from the current plan. Deduplicate repeated font
   resources. Regenerate all indexes and receipts from current inputs.

Navigation is intentionally not part of a page's paint key. A link-target-only
edit reuses the page appearance and rebuilds the correct link. Added/deleted
pages can repaint later pages because their visible page numbers change.
Renderer/font/configuration/source-pin/dependency changes conservatively
invalidate all page paintings. Model changes repaint only affected appearances.

SVGs are self-contained vector exports of the same one-page PDFs, with current
clickable link overlays. Their cache also depends on the converter version.
Text is exported as vector glyph outlines. No raster images are introduced.

This implementation is single-process: its short-lived renderer substitution
is not thread-safe. Run independent CLI processes rather than concurrent calls
to `Engine.render` inside one Python process. The cache is trusted local build
state, with accidental-corruption/staleness checks, not an authenticated store
against someone who can replace both an entry and its hashes.

## Reproducibility contract

A clean build through the incremental command and a warm/changed incremental
build produce byte-identical final PDFs for identical inputs. Their page content
streams, extracted text, link rectangles/targets and rasterized appearance are
also compared against the original monolithic renderer. The original renderer's
PDF object/resource layout differs, so its whole-file bytes are not expected to
match the assembled output.

Cache reuse means only that the visual page bytes match the recorded build key.
It does not imply human visual approval or scientific correctness. A full model
digest and auxiliary hierarchy digest remain in the receipt even when no page
painting changes. `QA.json` retains the ordinary builder's stated scope.

## Tests and measured timing

```sh
python -B joint259_system_docs_incremental_test.py --source /path/to/verified/construction --raster-dpi 40
```

Tests run in memory and print JSON. They do not edit the selected source package
or write generated files. Poppler's `pdftoppm` is required for raster equality;
`--raster-dpi 0` skips those checks, and `--skip-svg` skips SVG checks.

The suite checks all three document families, byte-identical cold/warm/clean
results, exact decoded drawing-stream/text/link agreement with the original,
and every page's raster pixels at the stated resolution. Controlled edits cover
block behavior, visible names, summary text, requirements, source-index hashes,
diagram wiring, index formulas, catalog add/delete/ID rename, index-only edits,
navigation-only edits, stale receipts/content, wrong source pins and undo.
Dependency invalidation uses changed-digest overrides in memory rather than
modifying immutable source files. Changed variants compare to a fresh clean
build and check the first repainted page's pixels. SVG checks parse every output,
verify internal targets, count preserved external links and reject raster images.

The JSON reports actual cold, warm and changed timings. These are local single
runs, not a statistical performance guarantee. Final assembly, validation and
source hashing still run, so speedup depends on workload and filesystem speed.
Human layout review remains separate from automated pixel equality.
