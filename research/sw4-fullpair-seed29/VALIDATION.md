# Validation

## Commands (from the repository root, standard-library Python only)

```sh
python3 -B -I research/sw4-fullpair-seed29/verify.py
```

Expected final line:

```text
PASS_SW4_FULLPAIR_SEED29 pairs=703 triples=8436 legal=9139 no_beats_sw4 seconds=...
```

Evidence regeneration:

```sh
python3 -B -I research/sw4-fullpair-seed29/search.py --out <dir> --arity 2 3
```

`<dir>/EVIDENCE.json` must gunzip-compare against the committed
`EVIDENCE.json.gz` payload (canonical JSON bytes).

## Recorded runs

- `search.py --out <dir> --arity 2 3`: 18.2 s wall.
  `BASELINE_OK 0390ec65...`, 54 pairs / 602 single subsets / 564 cap /
  38 legal, arity-2 groups 703 legal, arity-3 groups 8,436 legal.
- `verify.py`: 77.3 s wall (includes the 9,139-case replay, 13
  explicit-subspace spot checks, and three exact mod-p B-end-state passes).
  Python 3.13.15, Windows, assertions enabled (`-I` keeps `__debug__`;
  no `-O`).
- Staged output (abridged):

```text
RECONSTRUCT_OK d232183f233899961bf55cac67a18545ed33548d9a7ca7078990d1a83d557c59
PAIRS_OK n=54 subsets=602
SINGLES_OK {'single_total': 602, 'single_cap': 564, 'single_legal': 38}
REPLAY_OK total=9139 beats_sw4=0
EXPLICIT_OK cases=13
CONTROLS_OK exactness=preserved flip=trips tamper=trips partial=['cap', 1193, 169]
PASS_SW4_FULLPAIR_SEED29 pairs=703 triples=8436 legal=9139 no_beats_sw4 seconds=77.3
```

## Additional corroboration (development time, not part of `verify.py`)

All 703 pair outcomes were replayed with PR #775's evaluator source (used as
a read-only harness, not imported or vendored): 703/703 identical outcomes
and profiles.

## Coverage and limits

Complete enumeration of the stated class: all C(38,2) pairs and C(38,3)
triples of the legal full single-pair exchanges on bare P6k4 (9,139/9,139).
The lone-partial control fails frames at `('cap', B1193, register 169)`; the
recipe's own N2 partial pins a different site and is unaffected. No global
assembly, bit-supplier, owner, invoice, outer-constraint, Lean, or remote-CI
replay was run; none is needed for this scoped supplier-level negative
result. Inherited all-size/compiler, hosting, precision/tape, and analytic
assumptions remain.
