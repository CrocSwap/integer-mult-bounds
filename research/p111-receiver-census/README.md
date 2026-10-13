# Receiver choices cannot lower this frozen P111 word below 439 helpers

**Scoped negative result; no new kappa.** PR555's discovery sampled receiver
choices for its nine pseudo-target totals. For its frozen puncture set and
keeper plan (inherited by PR589), this package exhausts all **19,683** choices.
None uses fewer than the shipped **439 helpers**. Exactly **2,646** attain 439.

| Helpers | Receiver assignments |
|---:|---:|
| 439 | 2,646 |
| 440 | 8,127 |
| 441 | 6,642 |
| 442 | 2,052 |
| 443 | 216 |

The complete cost is `429 + extra carriers + newly allocated junk wires`.
It includes the 240 carrier helpers, 180 cell-empty helpers, nine totals,
every carrier added by the generator's missing-response closure, and every
remaining independent dirt direction needed by phase B. An extra carrier
reused as a junk direction is still paid once. All 60 block-local cases have
enough eligible carriers for their rank deficits, so no additional junk wire
is allocated in this particular domain.

This closes **receiver choice alone** as a route to fewer helpers in this
specific generator family. It does not close further optimization of the
2,646 equal-helper words' ADD counts, frame profiles, or precision costs.
It does not optimize the punctured set or keeper plan.

## Reproduce

From the repository root, using ordinary Python 3.11+ and the predecessor's
NumPy dependency:

```sh
python3 -I -B research/p111-receiver-census/verify.py
python3 -I -B research/p111-receiver-census/independent.py
python3 -I -B research/p111-receiver-census/test_package.py
```

The first command takes less than a second on the recorded machine and prints:

```text
PASS_P111_RECEIVER_CENSUS cases=19683 local_rows=60 min_helpers=439 minimizers=2646 no_new_kappa
```

The independent command takes about 20 seconds and compares the complete
assignment digest, helper histogram and selected-word calibration. It also
runs 59 completed original-generator controls (55 distinct global vectors),
including every changing block-table entry. The test command repeats both
checkers from a minimal offline directory with spaces, checks preservation
of all input files, and tests mathematical and package failure modes.
Optimized Python (`-O`) is explicitly rejected because the retained geometry
setup and direct generator controls use assertions. No network or solver is
needed; default checks do not write artifacts or bytecode.

`EXPECTED.json` retains every block-local record, exact residual-carrier set,
Q-response rank and source form, closure pass count, full histogram and record
digest. Each global record is serialized in sorted-puncture lexicographic
order as `[receiver_vector,R,extra_count,junk_count,nonempty_block_carrier_sets,
block_ranks]`, with compact JSON followed by a newline. Both engines obtain
SHA-256 `5598bbe4112493b6f6b55051a0364b7e576e253b8c2a85f8f05dcbb5d2ef7316`.

## Why the result is checkable

The main checker reduces the receiver cube to ten independent supplying-block
tables (60 entries), then enumerates the full Cartesian product. The separate
checker uses sets of source indices, symmetric difference and its own Gaussian
elimination; it propagates all 19,683 complete receiver vectors directly.
They share only the pinned predecessor geometry and frozen keeper-plan setup,
not receiver propagation or rank routines. [PROOF.md](PROOF.md) explains the
separation and full helper bill.

A concrete control catches an undercount: if a failed mini-node write updates
its destination anyway, block 0 with choices `(2,1,1)` appears to need only
three extra carriers instead of four. Other controls cover punctured source
111's zero response, carrier reuse versus new junk allocation, invalid receiver
values and exact span membership. This tests failure modes rather than only
the final minimum.

## Pins, stopping rule and limits

Base: `007664306fff84fbb1c9a1b4053b69f439764034`. At this base the selected
conditional result is PR890, kappa `1661957774647029/10^18`, using PR589 on
PR555 for the bit supplier. [SOURCES.json](SOURCES.json) pins all twelve
consumed source/input files with SHA-256 and base Git blob identities.
The current selected pointer is contextual, not a mutable input to this census.

The domain fixes the punctures `[10,15,51,53,56,66,72,89,111]`, skeleton plan,
`plan_thirds` seed 552, the generator's ordered mini-node elimination and
missing-carrier rule, and its extra-carrier reuse policy. Assignment seed 15
selected this task; it did not replace the predecessor's seed 552. The stopping
rule was one complete receiver census and verification of its result. Coverage
is complete; no search of another keeper plan or circuit family followed.

No new circuit is installed and no supplier invoice or new kappa is claimed.
The shared historical geometry setup uses NumPy numerical span calculations;
this package does not independently reconstruct or formally prove that geometry.
Its new arithmetic is exact F2 helper accounting. Full arbitrary-dirt/frame
replay of every receiver word, physical realization, whole-call hosting,
uniform recursive compilation, precision/tape accounting and analytic transfer
are not established here. A replacement supplier would still need those checks.
Full repository verification, selected cold replay, Linux/hosted CI and a full
formal multiplication proof were not run or claimed.

Credit eumemic (PR543/555), DreamingOfClouds (PR545/589), and the retained
construction lineage; see [NOTICE.md](NOTICE.md). Prepared for **ToikY** with
substantial **OpenAI Codex assistance**, including separately written checks
and model review. No independent human review is claimed. Apache-2.0.
