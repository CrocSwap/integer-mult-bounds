# Validation record

Executed locally on Windows with CPython 3.12.10 (64 bit), standard library
only, on 2026-10-12 America/Los_Angeles. Prepared by OpenAI Codex for @ssteeper;
no independent human review or external CI execution is claimed.

## Mathematical checks

```sh
python3 -I -B research/complex-center-quarter/verify.py
python3 -I -B research/complex-center-quarter/check_blocks.py
python3 -I -B research/complex-center-quarter/test_verify.py
python3 -I -B scripts/verify_selected_result.py
```

- The exact primitive construction checks all 32 original/replacement block
  pairs, each on 31 arbitrary inputs including center and coefficient work.
- Complete macro replay checks all 724 formal inputs in both orientations of
  both providers, for both original and factored programs. All 492 helpers
  restore and all eight private centers clear.
- The unchanged native auditor accepts each candidate, reproduces the selected
  paid profile and exact prefix bound, and rejects its 25 controls per provider.
- The 32 new block controls pass, including two endpoint-correct rewrites whose
  inputs to recursive calls are wrong. This distinction is verified directly
  in the focused tests.
- A separate integer-grid implementation checks 57,600 matrix entries in 64
  original/candidate blocks against direct gather/scatter formulas and rejects
  32 missing-clear controls. It shares source binding and rewrite code, but
  imports neither the primitive interpreter nor its costing/prefix engine.
- Five focused tests pass: call-boundary sensitivity, arbitrary incoming center
  dirt, endpoint-neutral precision inflation, coefficient-work alias/clearing,
  and native rejection of the new quarter scale at the wrong frame in each
  orientation. The last test executes the pinned native auditor in a subprocess
  and checks the actual frame assertion.
- The original complete local invoices reproduce exactly from SPEC. The
  factored programs add 128 generic adapter allowances, so each local bound
  increases by `3,319,594,144`, while staying below `2^48`. No net supplier-cost
  or exponent improvement is inferred from the scalar saving.
- The selected-record inventory check passes. All selected inputs and
  `upstream/` remain unchanged.

## Portability and failure detection

The primary checker also passes under `python -I -O -B`; its native child
process explicitly uses `-I -B` so assertions stay enabled. A minimal checkout
containing only this package and its pinned inputs is copied into a path with
spaces and invoked from outside that checkout. All four compressed inputs are
repacked with a different gzip timestamp and compression level; the replay and
integer checker still pass.

In that disposable checkout, changing a canonical-word payload is rejected by
the source pin. A later check also rejects an altered pinned invoice source and
a receipt that omits the 128 new adapter allowances. Changing the expected cost
is rejected by complete receipt comparison. The explicit receipt-output mode rejects an existing file and
preserves its bytes. Before/after SHA-256 snapshots confirm that the primary
command leaves package inputs unchanged. Scratch directories are confined to
the system temporary root and removed after use.

The initial Windows sandbox temporary location could be created but was not
writable. Reproduction succeeded after setting `TEMP` and `TMP` to the writable
workspace scratch directory. This was an environment failure before native
execution, not a failed identity or an accepted mathematical result.

## Scope limits

The tests use the pinned emitted programs and native local checker. They do
not cold-regenerate the entire construction, rerun global owner/phase admission,
or implement a grouped center-microcircuit invoice. The 864-primitive saving is
for scalar work under the retained lowering. Literal generic local accounting
gets worse; the exact increase is part of the receipt and research result.

Full `make verify`, `make frontier626-verify`, Lean, and remote Linux CI were
not run for this isolated research addition. The inherited all-size, physical,
precision/tape and analytic assumptions remain. This is finite exact evidence,
not formal verification of the multiplication theorem.
