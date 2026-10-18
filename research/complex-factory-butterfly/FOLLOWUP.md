# Review continuation, 2026-10-16

The maintainer's [180-second batch-review continuation](https://github.com/CrocSwap/integer-mult-bounds/pull/931#issuecomment-6161268201)
requested completion of all 78,728 recipes and the full losing-witness
comparisons. A fresh CPython 3.12 replay at exact PR head
`4e2925b076050f8035b054f95416029a63af64fa` completed in 80.545 seconds:

```text
PASS_FACTORY_BUTTERFLY blocks=14 gates={'baseline681': 34, 'butterfly': 42} pr696_saved={'forward': -672, 'backward': -672} kappa=unchanged
```

The command was `python3.12 -I -B
research/complex-factory-butterfly/verify.py --out <new-external-directory>`.
The checkout was clean before and after, and its head was unchanged. The full
result matched `EXPECTED.json`, including both complete recipe stream digests,
all 78,728 dirty-input map checks with zero failed pivots, fourteen physical
windows, both complete native/emitted scalar orientations, independent
four-orientation checks, primitive bills, prefix bounds and adverse controls.
Separate optimized local tests pass all ten cases. The best labeled recipe
also regenerates the retained losing witness exactly.

The result remains scoped: minima are 95/46 and 93/42 primitives/macros against
81/34. The nearest witness costs 672 extra real primitives per complete
orientation and 92,948,660,896 extra units in the pinned arithmetic local
recount. It still fails the original stronger sufficient envelope criterion at
`cleanup: endpoint growth increased`. No replacement, uniform precision
improvement, universal circuit bound, whole-owner/global invoice, new kappa or
formal-kernel theorem follows.

Current main `38746ad3f6ffebcc0275e286b1dbb733d7c696dd` has three different
historical source hashes: the selected record, the predecessor verifier, and
its former transport auditor. The new `pinned_replay.py` entry point retrieves
the original 29 SHA256-checked blobs from the historical base into a fresh
private export. It copies the current package and invokes its unchanged
`verify.py` with `-I -B`, removing `PYTHONOPTIMIZE`, `PYTHONPATH` and
`PYTHONHOME` from the subprocess environment. The original manifest, experiment, checker, candidate, search
streams and frozen receipt retain their original bytes and scientific base.

Eight focused export tests pass under `-I -O -B`, covering manifest corruption,
unsafe paths, exact Git blob bytes, corrupt blob digests, missing history,
symlink/bytecode exclusion, active assertions, and checkout change detection.
The source-only export check does not establish complete enumeration. A new
integration commit's full wrapper replay is separate evidence from the exact
historical-head completion above.

The dedicated `Complete historical butterfly replay` workflow uses a
full-history checkout, pinned actions and Python 3.12. It runs the eight export
controls and complete historical replay with a 15-minute cap. Its hosted
result is separate from local execution; the PR follow-up records exact heads
and the observed CI state.

Prepared by Ross Richardson with substantial OpenAI Codex assistance,
including a separate scoped mathematical audit. No independent human review
is claimed. All predecessor attribution and historical limits remain in
README.md, PROOF.md and VALIDATION.md.
