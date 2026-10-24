# Phase-coded callers and exact translation sections

This package preserves four reviewed local results: phase-coded D25 and
D73 callers, the exact section geometry of the separate eight-row query,
translation services for that query, and closure criteria for current
scalar stage codes. It contains the full source proofs, programs, source
pins, reviews, and a portable replay. These are existing campaign
results. This extraction adds no new research claim.

The paid D25 and D73 caller profiles have native masses `224*25` and
`224*73`. They do not give a strict moment gain or improve the complete
kappa calculation. A recursive consumer for the common q factor, a
complete host, map costs, owner schedules, and a numerical-grid proof
remain open. The packaging base is
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`. The selected PR #4470 at
that base is context only. Historical input pins remain unchanged.

A separate [fixed-code appendix](annexes/fixed-code-interface/PROOF.md)
gives the projector-graph criterion for one fixed scalar code. Its
112-port consequence and its independent review are separate from the
current changing-stage scalar-code theorem.

Read the [proof and scope](PROOF.md), [source map](CLAIMS.json),
[replay specification](VALIDATION.md), and [credit](NOTICE.md).
The [map-cost correction](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/inplace-service-review/MAP-COST-CORRECTION.md) is binding: all 144 simultaneous
translations in the one-bank inverse retain the applicable packed-map
cost, in addition to sixteen outer views. The frozen earlier review
contains a withdrawn O(V) map shortcut. Do not use that shortcut.
The historical translation-service review also omits the record count
in one odd-scan bit-cost sentence. The correct bound is
`64*n*(w_g+1)`, plus stream control, for n complex entries per field.

## Results and interfaces

| Result | Exact scope | Remaining boundary |
| --- | --- | --- |
| Phase-coded local word | Both inherited providers; all 640 inputs, including 416 arbitrary helpers; 4,632 real scalar primitives per local call | Native spatial kernels and adapters retain their pinned proof contracts |
| Three-call D25 endpoint | Three FULL shears give `(-F25 q Y0, F25 q X0)` for arbitrary physical inputs | The direct terminal adds 224 rank-one lines for the Q-entry variant, or 208 for the I-entry variant; each complete native mass is 5,600 |
| Nine-call D73 endpoint | The actual nine routes give `(F73 q Y0, -F73 q X0)` with one common q | The direct terminal adds 224 lines; complete native mass is 16,352 |
| Eight-row section geometry | Spectrum `±{1,3,5,11,13}` at every positive width; positive-line right section norm `sqrt(13)` and condition number 13; oblique projector norm 13 | Odd-power obstruction is proved at width at least five; no minimum-width claim |
| Translation services | Exact signed T and T inverse shears, coded exchange, and one-bank T inverse; zero native children under stated bank and C0 contracts | Odd-grid operations, outer views, and all translation maps remain explicit costs |
| Current scalar-code closure | Logical monomial closure at width at least two; physical closure and Q commutation at width at least three; general-stage sufficient bounds T and T+1 | Current invertible scalar codes only; no decoder cost lower bound |

The caller uses a **16/96 split** and `D=-H*`. The section and translation
services use a **different 8/104 split** and `D=B*`. The symbols belong
to different interfaces. The one-bank section inverse does not decode
the common q endpoint of the phase-coded caller.

The exact D25 scalar subtotal is `3*4632+6144=20040`, before terminal
wrappers and maps. The nine-call subtotal is `9*4632+18432=60120` with
the same exclusion. The prospective 2,912-scalar local word is not a
source of either claim. Scalar counts, native rank mass, and map counts
are separate quantities.

## Replay

Use Python 3.11 or later, the standard library, one worker, and a new
output directory. No Git checkout, source workspace, NumPy, or network
is needed. Keep at least 3 GiB free.

```sh
python3 -I -B research/phase-coded-callers/replay.py --out /tmp/phase-coded-callers-check
```

When this folder is elsewhere, replace only the script path. The default
runs all seven core jobs in normal and optimized Python modes. The final line
is:

```text
PASS_PHASE_CODED_CALLERS
```

The fixed-code appendix has a separate replay. Run it as well for the
full package check:

```sh
python3 -I -B research/phase-coded-callers/annexes/fixed-code-interface/replay.py --out /tmp/fixed-code-interface-check
```

Its final line is `PASS_SCOPED_SUPPORT_PROOF_REPLAY`.

Each core job runs in a private copy. The source files are hash-checked before
and after the run. The replay checks every output field against its
frozen receipt. It normalizes only repository locations, validated hashes
of generated normalized artifacts, and the recorded self-hash of one
path-only checker adaptation. The local payload and both execution modes
must agree. See [VALIDATION.md](VALIDATION.md) for all checks and limits.

## Package contents

[DIRECT-SOURCES.json](DIRECT-SOURCES.json) records all 50 selected
entrypoints. [SOURCES.json](SOURCES.json) records the exact dependency
closure with original paths, byte lengths, and SHA256 hashes. Files in
`frozen/` retain their original bytes and relative repository paths.
The one portable source-path adaptation is documented in
[PORTABLE-ADAPTATION.json](PORTABLE-ADAPTATION.json) and its complete
[diff](PORTABLE-ADAPTATION.patch). No imported module is changed.

[PACKAGE-SHA256.json](PACKAGE-SHA256.json) binds the package files except
itself. [REPLAY.json](REPLAY.json) records the core packaging replay, and
[ANNEX-REPLAY.json](ANNEX-REPLAY.json) records the separate appendix replay. Full
independent publication review is stored outside this frozen package.
The inherited reviews are separate agent checks, not maintainer approval.

## Open next questions

- Can a recursive caller consume the common q endpoint? This would make
  the D25 and D73 constructions usable without the direct paid terminal.
  A first step is to state one consumer with the exact gathered input
  types. A complete endpoint, owner schedule, and recursive cost remain
  blockers. The retained interface note does not supply them.
- Can the 144 simultaneous translations be lowered at the actual packed
  addresses? A first step is to specify one interleaved selected-bit map
  and price its extraction, permutation, and return. The absent lowering
  and its cost block the withdrawn general O(V) claim.
- Can a different code interface give a useful terminal? A first step is
  to state which code changes between cuts or which joint array operator
  is allowed. The current-scalar and fixed-code theorems constrain their
  stated classes only. A native program, safe owner use, and a full map
  and precision invoice remain necessary.
