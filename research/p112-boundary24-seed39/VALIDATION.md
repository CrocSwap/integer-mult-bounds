# Validation of the fixed-boundary result

Executed locally on 2026-10-14 UTC (October 13 in America/New_York), with
CPython 3.12.13 on macOS 27.0.1 arm64. No third-party packages are required.
The base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.

## Executed checks

```sh
python3.12 -B scripts/research_package.py --package research/p112-boundary24-seed39
python3.12 -I -O -B research/p112-boundary24-seed39/verify.py
python3.12 -I -O -B research/p112-boundary24-seed39/independent_check.py
python3.12 -B -m unittest discover -s tests -p 'test_research_*.py'
python3 -B scripts/verify_selected_result.py
```

All pass. The registered replay validates the metadata, source Git blobs and
SHA256 pins, then executes both mathematical checks. The workflow suite runs
20 tests, with no skips. The selected-record check confirms its original
source inventory and proof supplements; it is not a supplier cold replay.
The task card's first working example, `research/complex-decoder-field-extension-seed44/verify.py`,
also passes (25 attainments, 14,400 pairing entries, seven controls).

Primary receipt:

```text
PASS_P112_BOUNDARY24_S39 pairings=655 proper_deletions=24 fixtures=9 entries=112896 controls=9 copy_floor=64
```

Separate direct-geometry receipt:

```text
PASS_P112_BOUNDARY24_INDEPENDENT pairings=655 identities=25088 rank9_minors=2 controls=6 copy_floor=64
```

The finite data show the boundary's span change `8 -> 7`, all 600 maximal
proper-deletion ranks (384 eight, 216 nine), and the fully coupled cancellation
profile `(7,8,7)`. Nonzero minors of determinant 16 certify both nine-column
factors of the rank-nine attaining completion. These support the scoped
written proof; they do not formalize its quantified complex argument.

## Additional delivery checks

Both mathematical commands pass under `-I -O -B` from a minimal relocated
export with its package and two pinned live inputs, from an unrelated working
directory. Files and directories were set read-only, and content digests were
unchanged after both commands. This checks path portability and avoids relying
on removable Python assertions.

Five separate subprocesses exit nonzero for the intended reason:

1. Changed restoration rank: primary receipt comparison rejects it.
2. The same changed rank: independent finite-premise comparison rejects it.
3. Missing matrix fixture: primary full-receipt comparison rejects it.
4. Changed rank-nine minor: independent receipt comparison rejects it.
5. Changed geometry source bytes: primary source preflight rejects them before
   import. Only the disposable export was changed and it was restored exactly.

These supplement the 15 in-package controls, which include wrong pairing
parity, inverse/transpose mistakes, conjugation, singular factor changes,
nonfree support, and omitted required compensation. The two mathematical
implementations share the same contributor; no human peer review is claimed.

## Evidence boundary

No selected cold replay (`make frontier1094-verify`), native compiler, Lean
build, hosted CI, full supplier invoice or all-size multiplication theorem
was run or established. This package does not modify the selected frontier,
predecessor packages, frozen evidence or `upstream/`.

The final live overlap snapshot at 00:40:36 UTC completely paginated 788 open
PRs and 146 discussion records, without warnings. PR1375's source head was
rechecked. The exact boundary remained its explicit next question; another
agent mentioned it among candidates but chose a different task. Source scans
are overlap evidence with the limitations recorded in TASK.json, not a proof
of universal novelty.

Hanson Sun / bbMisk; substantial OpenAI Codex assistance. Apache-2.0.

Concurrent-main check: `410026dc5513b87db92ae98571d1d5984c69a983` retains
all four pinned main-tree blobs, including both live inputs and the selected
record. The new package path is absent there; the original research base is
retained.
