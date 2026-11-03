# Shared-donor kernels composed with co-retiming and PR300

This standalone research verifier adds a 70-pivot shared-donor construction to
pinned PR300 plus the 12-helper co-retiming from PR301. A separately checked
72-pivot construction is retained as a fallback. The package is a small diff
against main; it fetches immutable pending-PR data explicitly and does not
assume those inputs are already on main.

## Conditional results

| Case | Conditional kappa | Literal stock | Calls | Rank mass |
|---|---:|---:|---:|---:|
| PR300 + final12 + 70 pivots | 0.000749940157923873 | 1,229,560 | 483,425 | 2,454,720 |
| PR300 + final12 + 72 pivots | 0.000749936120273400 | 1,229,555 | 483,455 | 2,454,710 |
| PR299 + final12 + 72 pivots | 0.000749917402998347 | 1,229,555 | 483,130 | 2,454,710 |

All values use the retained compiler and analytic/all-size hypotheses. They are
exact rational grid choices with denominator 10^18, rather than floating-point
optimizations or claims of global priority/optimality.

The 70-pivot construction has 87 distinct donors, 157 affected helpers and 601
setup/restore shear pairs. It shares donor lines across different pivots while
preserving the helper response relations. Complete per-role bank allocation
uses 161,432 full width-120 banks per stage and five disjoint stage namespaces.
Every one of the 15,427 helper roles is assigned in all 60 replicas: 925,620
assignments per stage, 4,628,100 in total.

The 70-case finite coefficient is 90,466,979,917,115,701 (<2^80). Its corrected
sink-aware row bounds are F=191,659 and B=5,356,455; the 104-bit payload is
strictly below 2^104. The 72-case has 473 shear pairs and a smaller 102-bit
payload. The arithmetic selects the 70-case despite its five extra stock rows.

## Immutable dependencies

- PR299: `5f6bd3fbc0e6796dd31263cef1f06dc968186f64`, package
  `research/five-stage-gen5b-kernels-restorations-sinks`.
- PR300: `fd516176fd068e4fa7af14b40cd878ce8c305296`, package
  `research/five-stage-gen5b-full`, from `rohanarun/integer-mult-bounds`.
- The included final12 construction is the independently authored contribution
  in PR301, head `ebd6a08ed7d517387794c066490aa02aadcc78d4`. Its code is included
  here for standalone reproduction; PR301 itself is unchanged and need not be
  merged first.

`inputs.json` pins all 16 external files by immutable commit, byte count,
SHA-256 and Git blob hash. The fetched `portable_bit.py` is read only as inert
text to check loader order; it is never imported or executed. No upstream
producer or verifier runs. New witness JSON, proof notes and compact receipts
are included; large source bundles and generated full tables are omitted.

## Reproduce

Python 3.11 or later and its standard library suffice. Do not use `python -O`:
assertions are part of these research checks. From this directory:

```sh
python3 -B fetch_inputs.py --destination /tmp/shared-kernel-inputs
export CORETIME_SOURCE_DIR=/tmp/shared-kernel-inputs
python3 -B -m unittest discover -s . -p 'test_*.py' -v
python3 -B run_checks.py --check
```

An already downloaded directory is accepted only after every pin is verified.
All paths are relative to the verifier or the explicit input directory, so
absolute invocation from another working directory also works. A main checkout
alone is insufficient until the data-acquisition step above has succeeded.

For optional complete chart factor programs and deterministic role-bank address
tables, generate them outside the checkout:

```sh
python3 -B run_checks.py --check --output-dir /tmp/shared-kernel-results
```

Add `--write-streams` to emit both complete final12 scalar suffixes. Generated
full outputs are not needed in the committed diff. `run_coretime12.py --check`
reproduces the final12-only checkpoint independently.

## What is checked

- Original response relations, common dirty-read cut, selected helper support,
  and exact rational chronological frames for both shared-donor candidates.
- Compositional forward/inverse F2 identities on all 18,954 columns, assuming
  the inherited complete-word decoder; this is not a literal full-word replay.
- Final12's full 55,985-event scalar suffix in both directions over F2, the
  integers and absolute-coefficient majorants; 212 frame containments.
- PR300's 89 selected scalar incidences, 154-helper support disjointness from
  each new kernel and the broader 84-stream final12 closure, unchanged 440
  restoration and seven sink entries, and 65 exact Gram determinant checks.
- Every changed first-frame quotient, donor entrance and pivot residual chart,
  plus 18 final12 charts, using exact factorizations and role-to-program bindings.
- Full-width bank inventory and explicit role/replica allocation for each case.
- Sink-aware scalar majorants, all added scalar costs, selector/finite budgets,
  exact root brackets, three bootstrap steps, 47 strict outer inequalities and
  adjacent-grid rejection checks.
- Negative controls for wrong relations, missing setup/restoration, frame
  overlap, omitted sinks, chart or bank drift, duplicate roles and changed pins.

## Verification boundary

The original PR299 decoder/prefix and source-span admission remain hypotheses.
PR300's complete chronological/source-span admission is inherited as well;
matching its selected events and checking support/nondegeneracy do not reprove
that admission. Unchanged weighted-chart, address-normalizer, cover, routing,
prime, recovery, setup, finite-compiler, complex-supplier and analytic/all-size
interfaces are retained. The original row bounds are inherited before the
new sink-aware transport is applied.

No full upstream `make verify`, `make entrance-bank-verify`, physical producer,
or complete all-size proof has been executed. Main's selected certificate,
production guards, `upstream/` and manuscript patch are unchanged. The displayed
finite coefficient does not set the inherited unknown `C_full` to zero.
These are conditional changed-stage certificates, not formal verification of
the multiplication theorem. See [PROOF.md](PROOF.md), the retained component
proofs, and [NOTICE.md](NOTICE.md) for scope and attribution.
