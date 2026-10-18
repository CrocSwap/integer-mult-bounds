# Independent PR1042 replay-capsule closure

**Status:** independent verification; no new construction and no new kappa.

This package independently checks the frozen publication capsule behind selected PR1042, conditional kappa `1672188119205421 / 10^18`. It was selected by OS-random seed **75** at base `ba82555c64e1879e4b7decce28186f208fcb8262`.

## Result

`verify.py` treats `research/community-frontier1042-audit/selected-replay.tar.gz` as untrusted data, uses only the Python standard library, never extracts a member, and imports no construction code. It authenticates 458 safe regular members (45,647,427 expanded bytes), all 457 declared artifact digests, exact inventory closure, ten successful stage/log bindings, six promoted receipts, and the selected/integration publication pins.

`SELECTED-RESULT.json` is the byte-for-byte historical `certificates/selected-result.json` from base `ba82555c64e1879e4b7decce28186f208fcb8262`, also retained at `certificates/checkpoints/frontier1042.json`. Its original SHA-256, `207d1f49f113c585024b9d3c17eadbb8b1be17c1321e3d190aabe2f18ce1c5b7`, remains pinned in `PINS.json`. The checker reads this package-local snapshot. It does not read the live `certificates/selected-result.json`, so later selected frontiers do not invalidate this historical audit.

## Reproduce

```sh
make frontier1042-capsule-closure-verify
```

Expected final markers: `PASS_FRONTIER1042_CAPSULE_CLOSURE`, nine tests, `OK`. The target compares both normal and optimized verifier receipts byte-for-byte with the committed `RESULT.json`, then runs the suite in both modes so checks cannot depend on removable assertions.

The same checks can be run directly with Python 3.9+:

```sh
python3 -B research/frontier1042-capsule-closure-seed75/verify.py --check
python3 -O -B research/frontier1042-capsule-closure-seed75/verify.py --check
python3 -B research/frontier1042-capsule-closure-seed75/test_package.py
python3 -O -B research/frontier1042-capsule-closure-seed75/test_package.py
```

Current selected-pointer validation remains the separate `make selected-record-check` target. It is not a prerequisite of the historical capsule target.

## Controls

The suite rejects path traversal, duplicate members, undeclared members, mutated artifact bytes, a nonzero stage, and a promoted-receipt mismatch.

Regression controls run the complete checker in an isolated fixture: it must pass with the live selected pointer absent or advanced to a later frontier, and reject mutated bytes in the frozen selected record. The original `RESULT.json` is unchanged.

## Scope

This is finite integrity and binding evidence about the committed capsule. It does not establish that recorded commands ran, independently recompute T16 mathematics, verify named source packages, discharge inherited interfaces, prove analytic transfer, benchmark multiplication, or formalize the full theorem.

## Attribution

Martin Rv (@martinxxx9), with substantial Perplexity AI assistance in research, implementation, verification and writing. It preserves all PR1042 and batch1047 predecessor attribution. Apache-2.0.

The historical-record portability fix, reproduction target, and regression controls were prepared with OpenAI Codex assistance in response to the maintainer review.
