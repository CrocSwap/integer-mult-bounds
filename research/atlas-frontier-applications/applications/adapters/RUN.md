# Run the portable adapter selection

Use Python 3.10 or newer with its standard library. All commands below are run from this directory. Substitute `python3` for `python` if that is your installed interpreter name. No installation, network access, Lean, GPU, configuration change or external Python package is needed for the Pauli replay.

Copy every file listed in `MANIFEST.json`, plus `MANIFEST.json` itself. Keep the `six-qubit-recovery` subdirectory. The upstream native words are intentionally external inputs and are not part of this selection.

## Verify the packaged files

```text
python -B -c "import json,hashlib; from pathlib import Path; m=json.loads(Path('MANIFEST.json').read_text(encoding='utf-8')); assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in m.items()); assert not any(Path('.').rglob('*.pyc')), 'Use a fresh selection without bytecode caches'; print('PASS_MANIFEST')"
```

The source manifest excludes itself. The preflight also rejects existing bytecode caches: `-B` prevents cache writes but does not prevent reading a stale cache. Use a fresh extracted selection if this check fails. These instructions use a sibling `adapter-runs` directory for generated outputs, preserving the supplied fixtures and receipts. Each output must be fresh: the tools reject an existing file or fixture directory. For a repeat run, choose new output names.

## Offline Pauli recovery and independent replay

Validate the supplied six-qubit object with the checker that imports no recovery code:

```text
python -B verify_pauli_recovery.py six-qubit-recovery
```

Expected status: `PASS_INDEPENDENT_LITERAL_PAULI_RECOVERY`. It checks 65 classes, 4,095 nonidentity Pauli observables and 4,160 rank-one projector recipes, with exact inter-class overlap 1/64.

Recover the missing class from the supplied 64-class input into a fresh receipt:

```text
python -B pauli_recovery.py --input six-qubit-recovery/INPUT.json --out ../adapter-runs/recovered-pauli.json
```

Expected status: `PASS_EXACT_UNIQUE_MISSING_PAULI_CLASS`. The returned missing generators are `[2076, 1069, 564, 314, 133, 83]`. This command only reads the input and writes the fresh output.

Optionally regenerate the complete deterministic fixture, including all 65 possible one-class erasures, dimensions 1–5 and six corruption controls:

```text
python -B pauli_recovery.py --make-fixture --out ../adapter-runs/fresh-six-qubit
python -B verify_pauli_recovery.py ../adapter-runs/fresh-six-qubit
```

The generic input format is JSON with integer `qubits` and `classes`, a list of exactly `2**qubits` classes. Each class supplies `qubits` independent, mutually commuting binary Pauli generators, encoded by `label = x + (z << qubits)`. Classes must intersect only in the identity. The tool supports 1–10 qubits; the explicit fixture constructor supports 1–8. It repairs exactly one missing maximal class, not arbitrary damaged or smaller partial collections. `APPLICATIONS.md` supplies the sufficient theorem, projector semantics and classical attribution.

## Native reader checks require external pinned words

These commands check a scalar helper-reader primitive on the actual PR #2833 words inherited by PR #2848. Obtain the two word exports separately and place them at the following sibling paths:

```text
../native-inputs/PR2833-WORD-base.json.gz
../native-inputs/PR2833-WORD-extra.json.gz
```

Verify their exact compressed-file hashes before interpreting any result as a check of these source versions:

```text
python -B -c "import hashlib; from pathlib import Path; p=Path('../native-inputs/PR2833-WORD-base.json.gz'); assert hashlib.sha256(p.read_bytes()).hexdigest()=='dda9878455b3a3bec64ca16b1ac7789bbf5ffb603d5713b8df8644485e85b1b7'; print('PASS_BASE_PIN')"
python -B -c "import hashlib; from pathlib import Path; p=Path('../native-inputs/PR2833-WORD-extra.json.gz'); assert hashlib.sha256(p.read_bytes()).hexdigest()=='bbe6bcba59e45e827a8e932ee4b23650d56ed4a0b8e0875c14f23c36b9e47eac'; print('PASS_EXTRA_PIN')"
```

The reader checker records the supplied input hash and guards it before and after execution. It does not silently download a word or treat an arbitrary compatible input as the pinned frontier source.

```text
python -B reader_adapter.py --word ../native-inputs/PR2833-WORD-base.json.gz --out ../adapter-runs/current-reader-base.json
python -B reader_adapter.py --word ../native-inputs/PR2833-WORD-extra.json.gz --out ../adapter-runs/current-reader-extra.json
python -B reader_prefix.py --reader-receipt ../adapter-runs/current-reader-base.json --out ../adapter-runs/current-reader-prefix.json
python -B compare_sections.py --word ../native-inputs/PR2833-WORD-base.json.gz --out ../adapter-runs/current-weighted-section.json
```

The first two commands report `PASS_EXACT_SOURCE_BOUND_READER_ADAPTER_NOT_KAPPA_GAIN`: 234 dyadic scalar operations, no new scratch field, zero positive-rank children added and three rejected corruptions. The prefix command reports `PASS_EXACT_EVERY_PREFIX_SCHUR_BOUND`, with squared norm bound 315 over all 234 prefixes, covered by five amplification bits. The section comparison reports `PASS_EXACT_WEIGHTED_SECTION_COMPARISON_NOT_NATIVE_GAIN`; its minimum-noise decoder has nondyadic coefficients, so it is not substituted into the retained native language.

These are standard-library exact finite checks once the words are available. They do not rerun the full native Clifford, hosting, supplier, precision or outer admission. The supplied `reader-PR2833-*` receipts bind the current source; `reader-base.json`, `reader-extra.json` and `WEIGHTED-SECTION-COMPARISON.json` preserve older PR #2802 checks separately. The native application does not claim a new kappa, a completed consumer, Euclidean unitarity or free insertion at an arbitrary interior boundary.

## Contents and attribution

- `pauli_recovery.py`, `verify_pauli_recovery.py` and `six-qubit-recovery/`: complete offline measurement-class repair application.
- `reader_adapter.py`, `reader_prefix.py`, `compare_sections.py` and their receipts: external-word reader application and bounded comparison.
- `APPLICATIONS.md`: sufficient proofs, exact costs, limitations and primary references.
- `PR2805-OVERLAP.md`, `PR2805-SOURCE-PINS.json`: explicit overlap/credit and immutable source metadata for the earlier transported-shear construction. Upstream source bytes are not vendored here.
- `SOURCES.json`: logical source labels and exact inspection hashes, without operator-specific local paths.
- `MANIFEST.json`: hashes of this portable selection.

The finite-geometry and Pauli/MUB mechanisms are classical. PR #2805 and its predecessors already develop related dirty-state transported shears. The supplied reader involution has a different endpoint and no claimed superiority over that complete two-bank construction.
