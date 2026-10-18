# Validation receipt

Investigation base: `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
Environment: macOS; command-line Python 3.11.15 and analysis Python 3.14.8.
Completed 2026-10-13. Standard library only.

## Completed checks

- Normal Python 3.11 replay: pass.
- Isolated optimized Python 3.11 replay (`-I -O -B`): pass, identical result.
- Optimized `--emit` regeneration: exact parsed JSON equality with the
  committed certificate. Container whitespace is deliberately irrelevant.
- Every one of 14,400 signed output coefficients reconstructed from argument
  arithmetic, without calling the historical assertion-based verifier.
- Seven pinned runtime source hashes match.
- The loaded repository-local module inventory equals those seven pins.
- All 2,271 nodes, 4,673 minimum frames and 9,832 eligible endpoint pairs
  covered. Characteristic-vector and literal-residual decisions agree.
- All 1,155 endpoint extension subspaces for the selected 80 edges agree
  between one-vector extension and exhaustive quotient-subset closure.
- All 580 incident-safe extended endpoint frames and their edge pairings
  checked; 30 impossible edges and 50 one-dimension local repairs reproduced.
- Ten built-in geometric/control checks: five legal/illegal transfer
  examples, rejection of three simplified incorrect transfer rules, a
  degenerate-space check and a common-span obstruction. All run with `-O`.
- Four separate in-memory corruption trials rejected: changed impossible /
  repairable counts, removal of a failed edge, alteration of an endpoint
  frame, and a wrong scalar-DAG source hash. No committed artifact was
  modified for these trials.
- Four existing `tests/test_parity_side.py` tests: pass.
- `scripts/verify_selected_result.py`: pass; selected kappa remains
  `1661960547713947/1000000000000000000`.
- Staged diff whitespace check passes; all seven additions are confined to
  `research/parity-edge-compatibility-seed46/`.

The scoped checker takes about one second on this machine; this is a rough
reproduction observation, not a benchmark or performance claim.

## Freshness and limitations

Before submission, open-PR metadata was refreshed through #1012. The heads
of #920, #972 and #993 still matched `SOURCES.json`; no internal-edge census
overlap was found. Main had advanced to
`2921874911956718fcaaaf9396fe8267b3cfa9f0`. All seven runtime sources and the
selected kappa were unchanged there. The investigation base was retained.

Only this research directory is added. The relevant existing tests and
selected-record check were run; the expensive repository-wide `make verify`
and full selected-supplier cold replay were not run for this additions-only
finite geometry note. No Linux run, proof-assistant formalization, globally
compatible frame assignment, full supplier invoice, or multiplication
theorem verification is claimed.
