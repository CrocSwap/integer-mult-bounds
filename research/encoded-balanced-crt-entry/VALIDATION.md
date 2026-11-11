# Executed validation and review status

Base e54523517d0f03e58352e647c403a5af3e525a57. Prepared for CubeJerry with
substantial OpenAI assistance. Environment: CPython3.12.14, Clang22.1.3,
Linux x86_64, glibc2.41, standard library only.

## Author checks completed on2026-11-10

The metadata/source-pin check passed with12 live scientific inputs and two
historical provenance rows. The initial normal and optimized registered
replays passed on the warm-source-tail receipt in3.813 seconds combined,
well inside the individual60-second limits. After the scoped review
corrections below, the receipt was regenerated and the metadata check and
both registered modes passed again:

```sh
python -B scripts/research_package.py --package research/encoded-balanced-crt-entry --check-only
python -B scripts/research_package.py --package research/encoded-balanced-crt-entry
```

Each registered verifier printed:

```text
PASS_ENCODED_BALANCED_CRT_ENTRY nodes=14 owned_roles=78 controls=8
```

The runner printed:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/encoded-balanced-crt-entry outcome=completed
```

Both normal and optimized modes authenticate scientific inputs before
execution and compare the same type-sensitive frozen JSON receipt. The
runtime source parser and counter controller actually run; the actual
Entry and numerical producer are unchanged. None of the oracle's decoded
coordinates or widths enters runtime state. The same source snapshots and
all owned-role histories are checked at every boundary.

The eight-axis fixture includes97 pre-existing source-tail cells; its
raw-action envelope uses logical M, while retained storage counts the entire source
backing. Non-dyadic shape rejection and early retired-boundary close
physically clear the owned histories and return the source head.

A separate direct Port-method calibration of the guide-driven protected
word routine at precisions5,11,5,31 measured792,1464,792,3704 raw actions
for all eight words. These equal8(14P+29), including every guide rewind.
The quantified count is proved in PROOF.md; these four observations are
corroboration, not its universal justification.

## Scoped review corrections

Lead and independent review identified two overstatements in the earlier
author freeze. The physical API now states the linear-use current-lease
protocol. Immediate current-phase misuse is distinct from the interpreter's
extra protection against stale Python object identities retained through
later entries; that historical-handle service is not a physical theorem.

The earlier literal32-instruction finite-control premise had no enumerated
primitive expansion. It has been removed, along with the resulting explicit
complete-control majorant. The explicit `2^16(M+2)^2` bound now applies only
to raw local Port actions. Complete frontend work is `C_front(M+2)^2` for
a fixed input-independent refinement constant; the uniform `O(p^4)` result
is unchanged. The receipt labels its finite comparison `raw_action_bound`
and records both cost and lease scope. The mathematical and executable
numerical pipeline is unchanged.

## Independent review gate

A separate ownership research worker completed the source/proof review at
addb3c9a404df9a5a7b7543ae2984477db784233 after the two corrections.
Its independent checker uses a different node-order derivation and direct
CRT-sum oracle, importing no author verifier or oracle. Normal and optimized
checks print PASS_INDEPENDENT_BALANCED_ENTRY 63 78 6 3. Coverage separates
57 topology nodes with actual Entry/Bank and explicitly dummy arithmetic
from six actual numerical nodes. It checks all78 retained role histories,
warm inaccessible source tails, exact varying-width guards,16 record-action
calibrations and three controls. See independent-review/REVIEW.md for exact
pins, universal derivations, scope and reproduction. This is separate
AI-assisted review, not human or proof-kernel acceptance.

No full CRT row/ROM/payload program, binary transition program, selected cold
replay, human review or proof-kernel verification has been executed.
