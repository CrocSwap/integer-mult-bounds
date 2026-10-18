# Replica-local global-prefix audit

At the pinned base below, the then-selected #626 invoice uses the sufficient prefix estimate
`101 + 37 + 72 + 72 + 4 = 286` bits. Under the same normalized endpoint,
local scalar/Horner, and physical realization assumptions, the eight
interleaved replica controllers admit the sharper sufficient estimate
**`101 + 37 + 18 + 4 = 160` bits**. Each replica has nine local shears and
nine bridges. Borrowing a helper from another replica does not increase
that owner's norm at the completed invocation boundary: its physical
endpoint is a unitary transform within that family.

This is a **mathematical audit / conditional precision-accounting
refinement**, with no new kappa. The 126-bit reduction is in a sufficient
estimate, not a measurement of the minimum necessary precision. The
production allowance remains 512 bits, and all production files are unchanged.
No runtime improvement, stronger multiplication bound, or complete theorem
formalization follows.

Upstream adopted a newer frontier while this completed audit awaited a
writable fork. References to "selected" in this package mean #626 at the
pinned base, not the current upstream selection. The 160-bit estimate has
not been transported to the newer construction.

## Reproduce

From a checkout containing the source-pinned inputs, using Python 3.10+
and only the standard library:

```sh
python3 -B research/replica-prefix-audit/verify.py
```

Expected:

```text
PASS_REPLICA_PREFIX_AUDIT calls=72 owner_roles=35424 prefix_bits=286->160 retained_payload=512 no_new_kappa
```

The default command is offline and writes nothing. It verifies all source
pins, compares its complete result with `EXPECTED.json`, and runs negative
controls. Checks remain enabled under `-I -O`. `--repo PATH` selects an
alternative input root. `--record NEW_PATH` writes a new receipt and refuses
to overwrite any existing file; it is an evidence-generation mode, not a
comparison with the committed expectation.

## What is checked

- All 72 selected calls and their provider/orientation/program bindings;
  all 240 projected replica events; all nine local and nine bridge events
  in each source controller.
- All 35,424 helper roles, including 28,404 cross-replica roles, for the
  family membership and non-aliasing conditions used here. This is not a
  new owner-window, orthogonal-chart or capacity audit.
- The retained source's 224 data-owner families in every call stay within
  that call's replica. Existing source checks preserve these data owners
  through supplier substitution and final hosting.
- Existing local scalar/Horner receipts and program hashes bind the
  inherited 101-bit allowance. Their full native arithmetic, frames and
  phases are not replayed by this command.
- Independent exact finite dirty-helper models and counterexamples test
  the boundary/prefix distinction. These corroborate the written proof in
  [PROOF.md](PROOF.md); they do not prove the all-size interfaces by enumeration.

The selected generated `GLOBAL-TEMPLATE.json.gz` is not committed in the
review receipt directory. This audit explicitly uses the retained parent
template, selected plan and owners, pinned substitution/emitter/audit
source, and frozen selected receipts. It does **not** claim to have
regenerated the missing template or rerun the cold construction. The exact
dependency boundary is in the proof and [SOURCES.json](SOURCES.json).

## Provenance and overlap

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected #626 source: `660de893d27bb7abd1d5b01b1640207528a5c851`.
Construction #622 source: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
The pinned baseline's kappa is `51110230636731/31250000000000000`.
All consumed files have exact byte or complete decompressed-payload hashes.

This builds on eumemic's #496 global maximum-stream norm argument,
adding individual replica counters for the selected asynchronous schedule.
It credits #675's separate owner-boundary/scalar-omission audit and
#696/#734/#783's local primitive and prefix work. It does not depend on
their code. The present addition concerns the global norm allowance for
asynchronous complete calls, not local scalar lowering, owner allocation,
or reconstruction of the selected moment. See [CLAIM.md](CLAIM.md) for
the seed, candidate selection and bounded stopping rule, and
[VALIDATION.md](VALIDATION.md) for actual execution results.

Contribution by **Brody Arbon**, with substantial **OpenAI Codex assistance**
in source inspection, derivation, implementation, tests, writing and review.
Separate Codex agents reviewed the proof and source dependencies; this is
not independent human peer review or proof-assistant verification.
Apache-2.0. See [NOTICE.md](NOTICE.md) for predecessor credit.
