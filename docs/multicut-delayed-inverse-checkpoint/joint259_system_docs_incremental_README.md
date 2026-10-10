# Functional architecture build and page cache

The retained incremental renderer builds only functional_architecture.pdf
and summary-functional.svg. It does not regenerate logical or combined output
families. The runtime and model dependencies are retained together with the
functional-only cache/navigation test runner.

## Build

    python -m pip install -r joint259_system_docs_requirements.txt
    python -B joint259_system_docs_incremental.py --source /path/to/construction --output /new/output --cache /path/to/page-cache.json --svg

The output and cache must be outside the immutable scientific package. Omit
--svg to build without Poppler. Linked per-page functional SVGs are local build
outputs and are excluded from the public allowlist. --clean ignores the cache.

Page drawing plans, renderer/configuration/font/source dependencies and PDF
hashes determine reuse. Navigation is rebuilt even when appearance is reused.
A missing or damaged cache causes rebuilding; it never bypasses source pins.
The cache is local acceleration state, not an authenticated proof receipt.

## Focused verification

    python -B joint259_system_docs_incremental_test.py --source /path/to/construction --raster-dpi 40

The fresh functional-only report covers 51 pages. It checks cold/warm/clean
byte equality, decoded drawing streams, page text, internal navigation, full
raster equality at the recorded resolution, controlled block and requirement
changes, dependency invalidation, damaged-cache repair, source-pin rejection,
JSON cache round trips and vector SVGs with resolved links. The old L04-only
case is removed because that output family is no longer present.

The retained independent review files clearly identify their original
three-family review as historical. The fresh narrowed-build test report is
separate evidence and does not reuse the historical 161-page PASS claim.
Neither build nor documentation tests replay the scientific construction.
