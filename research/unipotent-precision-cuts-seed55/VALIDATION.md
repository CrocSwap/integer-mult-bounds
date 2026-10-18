# Validation receipt

Research base: `64039f1bd3b6a523b96083fd858ad040a75e3030`.
Predecessor: PR1537 `407f00df6ca0bf86b455b5640f18ec2f62ee77b9`.
Refreshed main: `c5108f0f68d482e5712a8e26a5978d47762dfc16`.
Environment: macOS arm64; CPython 3.12.13 and 3.14.6; standard library only.
Contributor: Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.

Executed from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/unipotent-precision-cuts-seed55 --check-only
python3.12 -B scripts/research_package.py --package research/unipotent-precision-cuts-seed55
python3 -I -O -B research/unipotent-precision-cuts-seed55/verify.py
make selected-record-check
git diff --check
```

All pass after the repair described below. The registered replay includes the
isolated optimized mathematical checker and four artifact tests: corrupted
frozen input, read-only standalone relocation to a path with spaces, all saved
frontier dual witnesses plus a bad potential, and an on-disk false peak.
The test harness reports four tests passing in 42.483 seconds on this host;
this is an execution record, not a performance claim.

The first registered attempt correctly rejected the freshly emitted receipt
because the in-memory small-fixture list contained tuples while JSON reloads
lists. The repair changes only that metadata representation to lists. The
serialized mathematical receipt stays byte-identical, and full registered
replay then passes. No mathematical failure was suppressed or tolerance added.

Exact coverage:

- 1,431 intervals, 5,618 fused contextual replays, plus the complete canonical
  control graph. The written decomposition covers 2^52 contiguous partitions;
  these are not 2^52 individual program executions.
- 35 extended and 31 canonical frontier points, with paths and lower-bound
  potentials. Cap 256 fails the requested saving target; first saving cap 788.
- 216 independently derived boundary states; 132 directed Fraction basis
  columns and six exact attaining sign inputs.
- 2,429 literal small partitions per mode, 4,858 total; 366 cap decisions per
  mode, 732 total. Includes a genuine profitable fused planner control.
- Both nested complete maps on 32 dirty coordinates, exact inverse maps and
  the complete recursive invoice; no claim that local caps compose.
- Nine semantic/resource controls and the four artifact test groups above.
- All 31 canonical cost/cap points independently agree with concurrent PR1552
  at 4db7213c90288b1eb83983e08c5ef401d19b7844; its code is not imported.

The selected binding check passes, but the full selected-supplier cold replay
was not run for this isolated contribution. No physical supplier adoption,
Linux/hosted CI success, rounding/tape admission, independent human review,
proof-assistant formalization, measured multiplication speedup or new kappa is
claimed. Emulate's style pass was unavailable (18 word credits, 40 required),
as disclosed before delivery; prose was checked against the exact sources.

The staged patch applies cleanly to refreshed main `c5108f0f68d482e5712a8e26a5978d47762dfc16`, checked with a separate temporary Git index. Only the new research package is changed. The selected record and upstream tree have no staged changes.
