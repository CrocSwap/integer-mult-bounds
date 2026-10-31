# Checked characteristic-five connector exclusion

Alexander Richard Towell, with substantial OpenAI Codex assistance.

This packet adds a replayable finite certificate to
[Josie Elliston's PR6141](https://github.com/CrocSwap/integer-mult-bounds/pull/6141).
The mathematical exclusion was already reported there using SAT solver output.
Our contribution is checked evidence, the written word-to-CNF implication,
and reproducible failure controls. No new multiplication exponent is claimed.

## Exact scope

No length-30 word on six sources, each occurring five times, realizes every
nonzero binary six-vector as the sum of two prefix-count vectors modulo five.
Already the sixteen masks of weights two and six cannot all be realized.
This is the unchanged unsigned dirty connector's depth-two block model from
PR4231/4248. Repeated boundaries and boundary zero are permitted. It does not
exclude deeper blocks, arbitrary floor words, other characteristics or interfaces.

[PROOF.md](PROOF.md) gives the written reduction to the certified formula.
It explains symmetry, pruning, endpoint replacement, and a constructive meaning
for every anonymous cardinality variable. The two C checkers establish the
finite refutation; this is not a Lean proof or human peer review.

## Reproduce

Tested on Linux x86_64, Python 3.13.15 and GCC 13.3; requires Python 3.10
or newer, GCC and about 2 GB temporary disk space.
Install the exact dependencies in a virtual environment, then run from this
directory:

```sh
python -m pip install -r requirements.txt
python -O reproduce.py
python -m unittest -q test_checks test_reproduce test_native test_generate
```

Expected: JSON status `PASS_CONNECTOR_C5_CERTIFICATE`, both `s VERIFIED` and
`c VERIFIED`, twelve counter blocks checked, and three native rejecting
controls. Source corruption must additionally fail in normal and optimized
Python. The reproduction regenerates the exact 4,278-variable/52,672-clause
formula, authenticates vendored checker sources, builds them, verifies the
trimmed DRAT, converts it to temporary LRAT and checks that independently.
It also replays the predecessor's original positive-word controls in both
Python modes. It never reruns the SAT search.

The compressed proof is approximately 37 MiB; decompressed DRAT is 264 MiB.
Conversion creates a larger temporary LRAT file. Allow several minutes on a
typical host; the wrapper bounds each native check at 300 seconds.

## Provenance and verification

Predecessor generator: `d192172f57b10647ddcff9410c69d48ac06862c1`.
Upstream main inspected: `a5bff3bf133e482541c09eba4e773884bdb2b1b7`.
PySAT: `1.9.dev15`; proof-producing solver: CaDiCaL 1.9.5.
DRAT-trim source: `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`.
LRAT-check source: haskiindahouse's pending
[PR43](https://github.com/marijnheule/drat-trim/pull/43), exact head
`0ca925b4f5b4ed04d02d830807cfd614483e7320`.
[SOURCES.json](SOURCES.json) pins every vendored file and decompressed payload.
Compression headers are not proof-relevant; raw payload hashes are checked.
Source copies and all third-party licenses remain unchanged.

The original logged solve took approximately 158 seconds. Its complete binary
trace passed DRAT-trim. The original LRAT checker falsely accepted a fake
refutation of a satisfiable formula, reproducing the already reported
[issue42](https://github.com/marijnheule/drat-trim/issues/42). Its positive
output is not relied on. The corrected checker from PR43 rejects that control
and verifies the full target, including fresh LRAT from the archived trimmed
DRAT. This is use of a predecessor correction, not a new checker fix or a
general audit of either checker. Other known malformed-input issues are not
resolved. The exact
commands and results are retained in `logs/` and the final result record.
Finite controls cover all 116 small floor words in three declared parameter
cases, constructive counter extensions and a satisfiable weight-two-only
relaxation of the target. These controls support the written bridge; they are
not its unrestricted proof. See [NOTICE](NOTICE) for detailed attribution.

## Regenerate the search evidence (optional)

```sh
timeout 480 python generate.py /tmp/new-connector-c5-run
gcc -std=c99 -O2 vendor/drat-trim/drat-trim.c -o /tmp/drat-trim
/tmp/drat-trim /tmp/new-connector-c5-run/instance.cnf \
  /tmp/new-connector-c5-run/proof.bdrat -i -l /tmp/new-trimmed.drat
```

This repeats the costly search with proof logging; it is unnecessary for
certificate replay. Search stopping rule: solve the single pinned instance
or stop after 480 seconds. The solver's deterministic default configuration
was used; no random restarts, larger domain, or characteristic-seven run was
requested. Generated proof bytes need not be identical to this archived trace.
The pinned PySAT native stream needs a C stdio flush before its binary proof
is copied; the optional generator uses POSIX `fflush(NULL)` and tests it on
a tiny actual refutation. Its Linux/POSIX scope is explicit.

## Open next questions

The characteristic-six exclusion in PR6141 still needs a checked certificate;
its reported unlogged solve is substantially slower, so budget it separately.
An elementary proof from the weight-two and all-ones constraints would remove
the SAT-encoding/tool trust. Characteristic seven remains outside this visit;
refresh current claims before pursuing it. None of these is an automatic next
cycle. This contribution is ready for scoped external review once the recorded
verification and final code review are complete; acceptance is separate.
