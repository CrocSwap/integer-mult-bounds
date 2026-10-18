# Validation and limitations

## Executed checks

The complete source-bound checker passed on macOS arm64 / CPython 3.9.6
under isolated normal execution and isolated optimized execution. The full
parsed EXPECTED.json receipt matched, including all exact cases, phases,
holonomies, matrix digests, rounded-output digest, maximum rational error
ratio, counts and controls. The first full run took 11.71 seconds; this is
an environment observation, not a before/after performance claim.

Commands from the repository root:

```sh
python3 -B -I research/cyclic-stride-independent/verify.py --check research/cyclic-stride-independent/EXPECTED.json
python3 -B -I -O research/cyclic-stride-independent/verify.py --check research/cyclic-stride-independent/EXPECTED.json
python3 -B -I research/cyclic-stride-independent/test_verify.py
python3 -B -I -O research/cyclic-stride-independent/test_verify.py
```

Both modes retain 266 exact cases, 252,730 matrix-entry obligations,
4,256 rounded cases / 53,472 coordinates, and 16 rejected controls.
All eight focused tests pass in both modes. These additionally exercise
actual corrupt-manifest and missing-Git-object paths, exact scalar and
zero-root formulas, the asymmetric closure witness, one singular cycle,
and cycle partitions for every stride from -L through L, L=1..31.

A separate CLI test decremented only `rounded_cases` in a temporary copy of
EXPECTED.json. Optimized full execution exited 1 with
`FAIL: complete receipt mismatch`. The checked-in receipt was not modified.
This is in addition to the 16 controls, not counted as a seventeenth member
of the deterministic receipt.

An oracle-only run on Linux x86_64 / CPython 3.13.5 passed the same 266
exact cases. Its complete exact-evidence projection matched the macOS
full run, SHA-256:

    391d48638394375d3255ca3c8c9377a37a67a3b4708c9a70f939a5b704063cf2

The projection keys are listed in VALIDATION.json. Canonicalize that
subdictionary with `json.dumps(..., sort_keys=True, separators=(',', ':'))`
and hash its UTF-8 bytes. This verifies agreement of all retained exact
case data, not merely a count. A full Linux predecessor replay is NOT
claimed; only the independent oracle was executed there.

## Scope integrity and review status

The selected record was compared byte-for-byte to the base. Its referenced
ASSEMBLY.json SHA-256 matched the selected certificate's declared hash.
The construction proof note and maintainer review were also compared to
the base. No existing tracked file, including upstream/, was changed.
Staged whitespace and isolated-base-index patch applicability were checked
when packaging. These are source-integrity checks, not a fresh cold rebuild.

`make verify` and `make frontier626-verify` were not run: the change adds a
standalone research package, not a generator, supplier, selected record,
root build rule or imported certificate. No root-wide regeneration or
full-kernel/cascade/layout replay is claimed. No remote CI pass, formal
proof-assistant run, independent human review or new kappa is claimed.

The PR queue was refreshed before publication. OVERLAP.json records the
relevant exact heads and the distinction from scalar-gauge stride routing,
CRT resultants, composite lifting and dirty restoration. Newer supplier
headlines were not treated as the selected frontier.
