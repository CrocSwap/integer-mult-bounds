# Local validation

Executed on Linux with CPython **3.14.8**, 2026-10-13. The optional independent
check used **SymPy 1.14.0**. No additional package was installed. Research
checks ran inside the contributor's shared CPU/memory cap.

## Reproduction

```sh
python3 -B research/e8-p111-pairing-floor/verify.py
python3 -I -B -O research/e8-p111-pairing-floor/verify.py
python3 -B research/e8-p111-pairing-floor/independent_check.py
python3 -B scripts/verify_selected_result.py
```

The first two commands produce the same deterministic receipt and report
cost 63, 511 exact support checks, 261,121 classified functional pairs and
12 rejected negative controls. The main checker uses explicit exceptions;
its proof-relevant checks remain active under optimized Python.

The independent script passed all 511 support ranks and 81 pairings using
SymPy and coordinates read directly from the pinned parent word. Its separate
small-domain check exhausts four invertible symmetric 3-by-3 binary forms
with unit diagonal and all 168 binary bases, for 672 factorizations. These
examples calibrate the written general argument; they do not replace it.

The selected-record check passed at
`51110230636731/31250000000000000`, verifying the original selected source
inventory and proof supplements. No selected-frontier files were edited.

## Relocation and tampering controls

A fresh temporary directory contained only this package and the nine inputs
listed in `SOURCES.json::local_sha256`. Running from an unrelated working
directory passed in normal and isolated optimized modes. A newly written
receipt compared byte-for-byte equal with the committed `RESULTS.json`.

In that disposable copy:

- Changing the receipt's minimum from 63 to 62 exited with code 1 and
  `committed receipt differs`.
- Appending bytes to the pinned compressed supplier input exited with code 1
  at the source-hash check, before decoding the changed input.

The default verifier's twelve mathematical/geometry controls reject a zero
root, changed puncture, missing diagonal premise, wrong inverse, forbidden
discount, omitted total, underpriced star, changed source functional,
unpunctured rank-seven claim, missing diagonal obstruction, rank-one block
substituted for rank two, and the alternative root numbering.

## Scope of the checks

The only changes are this research package. No existing generator or supplier
was changed; the expensive repository-wide `make verify` and selected cold
replay were not run. The targeted exact checks and selected-record integrity
check cover the changed scope. No remote CI pass, independent human review,
second Python-version pass or formal theorem verification is claimed.
