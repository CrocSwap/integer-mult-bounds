# Completed validation

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Completed 2026-10-13, Windows Python 3.14.0 and Ubuntu 24.04 / Python 3.12.3
under WSL. Both use only the standard library for mathematical replay.

The following commands passed on both environments:

```sh
python3 -I -B research/jp8-additive-coefficient-routes/verify.py
python3 -I -B research/jp8-additive-coefficient-routes/independent.py
python3 -I -B research/jp8-additive-coefficient-routes/native_replay.py --output NEW_SCRATCH_DIRECTORY
python3 -I -B research/jp8-additive-coefficient-routes/test_verify.py
```

- Complete literal forward/backward primitive replay: 725 arbitrary columns
  each, including all 492 dirty helpers and nine private inputs; costs
  224,422 / 257,280; original positive prefix values and recursive profiles.
- Independent integer checker: 780 magnitude pairs, 849,420 exponent pairs,
  1,091 block matrices, 6,776 local input columns; 32,810 total real saving.
- Twelve construction controls, four independent matrix/prefix controls and
  25 inherited frame/wrapper controls rejected.
- Four packaging tests pass. These execute both new checkers with `-O -I -B`
  from a different working directory in a minimal copied tree containing
  only this package and its seven pinned inputs. They accept equivalent
  recompressed inputs, confirm read-only execution, and reject altered source
  payloads, a changed transition certificate and an undercharged receipt.
- All seven immutable input bytes match the base Git blobs. Compressed
  mathematical artifacts are checked by decompressed payload and SPEC
  semantic hashes, not gzip headers.
- `python -B scripts/verify_selected_result.py` passes, retaining the exact
  selected fraction `51110230636731/31250000000000000`.
- Ruff 0.17.0 checks the five new Python files. Git whitespace checking and
  the focused diff review cover only this new research directory.

The full repository suite, full selected cold reconstruction, global
invoice/admission regeneration, remote CI and Lean were not run. No original
construction file or selected frontier was modified. The native replay
checks the unchanged macro program; it does not silently integrate the new
primitive lowering. The separate local-budget calculation explicitly shows
that the unchanged backward maximum prevents a local-invoice improvement.

The one-line expected outputs and independently reproducible commands in
README.md are the handoff contract. No verification depends on scratch files,
pending-PR code, network access or unshipped tooling.
