# Bind actual HPE wrapper events to Lean recipe literals

The opt-in checker accepts all **30 non-cold hyperplane-ended helpers** in both
regenerated selected k8 local programs. Each program has 24,767 events. The
actual pre/post events select `3:998` for 16 helpers and `2:999` for 14 helpers.
Their selected monomials equal the retained Lean `pair2` and `pair3` literals,
including global phase. Every helper's scalar and climb touches lie between
its wrappers, with consistent helper frame tags.

This is a finite certificate-to-theorem-data binding. It proves no new Lean
statement and makes no supplier or kappa claim. The selected frontier and all
predecessor files remain unchanged.

## What this adds

Riquelme Soares's [PR #2706](https://github.com/CrocSwap/integer-mult-bounds/pull/2706),
head `94d77d2cf19b5fbf3d14cd145fc5fd6ad8d24bd6`, shows that two lightweight HPE
checkers do not inspect a synthetic `pre_wrappers` annotation. Those checkers
read canonical words and recipe records, not `LOCAL-PROGRAMS.json.gz`.
The real emitter instead writes events such as:

```text
["residual_adapter", "pre", 450, 2, 999]
... actual helper touches ...
["residual_adapter", "post", 450, 2, 999]
```

The fifth field selects the `2:999` recipe, not the FULL-ended `"2"` recipe.
`factor_iff_pre` requires the executed right monomial to be the certified one.
The new checker reads those actual events and compares the selected right/left
monomials with the Lean pair data. An unused annotation cannot supply a missing
event, and changing that annotation alone does not change execution.

This is **not a newly discovered production-checker defect**. The retained
`hpe_audit_local.py` already checks emitted wrapper references, order and
presence. Hanson Sun's [k8 helper-450 package](../k8-hpe450-binding/README.md)
also checks wrapper chronology throughout the word and binds helper 450's
recipe and scalar row/column to `pair3`. The new contribution is a reusable,
separately implemented event-to-literal check for every non-cold HPE helper.
It does not repeat the independent Clifford operator audit in
[PR #1415](../hpe-lean-semantic-binding/README.md).

## Evidence and reproduction

Base main is `bd1b3bc7174cddbfa4e30ac073dc134f48aa6e77`, priority revision 5.
[TASK.json](TASK.json) records the scope and
[the claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2703).
[SOURCES.json](SOURCES.json) pins every external input. [RESULT.json](RESULT.json)
records all 60 helper/orientation bindings and canonical JSON SHA256 digests
of the regenerated canonical word, complete programs and adapter records.
Gzip headers do not determine equality.

Run from the repository root with standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/hpe-wrapper-event-binding
```

The registered command checks pins, regenerates the genuine k8 inputs in a
temporary directory, compares the receipt and runs ten tests. Direct commands:

```sh
python3.12 -I -B research/hpe-wrapper-event-binding/verify.py
python3.12 -I -B -m unittest discover -s research/hpe-wrapper-event-binding -p test_verify.py
python3.12 -I -B research/hpe-wrapper-event-binding/verify.py --run /path/to/emitted/run
```

`--run` requires both orientations and checks the supplied artifacts, not their
membership in the selected construction. Without it, the pinned producer harness
reconstructs the selected k8 word and authenticates its canonical/program hashes
against `SLOT-PINS-k8.json`. The selected manifest's slot pin is also checked.
`--write-result NEW_PATH` writes a separate receipt and refuses to overwrite.
Normal verification never rewrites committed evidence.

The ten tests include **360 per-helper rejection cases**. For both wrapper
sides of every helper in both orientations, they delete the event, omit its
terminal field or change its terminal to FULL. Further controls reject duplicate
and premature wrappers, reads after the post wrapper, an ordinary adapter in
place of a wrapper, changed global phases, substitution of the FULL recipe,
missing recipes, false integer fields, incorrect frame tags and unknown events.
A real CLI negative run also rejects a deleted pre-wrapper under `-O`.
Controls call the semantic checker without checksum rejection as a substitute.

The tests and receipt replay passed locally on CPython 3.12.15 and 3.13.5 on
Linux. Ruff checks `E4,E7,E9,F,B,I,UP` pass. No Lean build or full
selected cold replay ran.

## Independence and limits

`binding.py` imports no producer checker. Its state machine tracks actual helper
touches and reads the event-selected recipe fields. The harness reuses only
`rebuild` from the pinned helper-450 package to generate and authenticate inputs;
it never calls that package's `audit`, `controls` or row/column routines. The
literal reader parses the same three retained data records, not a new proof of
their operator semantics. The original production wrapper audit is pinned as
context and is not the new oracle.

Coverage excludes cold and FULL-ended helpers. A non-cold HPE pair absent from
the three Lean literals fails rather than silently disappearing from coverage.
The checker assumes the emitter's ZERO/FULL frame-ID convention and validates
it. It checks event grammar and the covered helpers' frame-tag continuity, not
all other roles' labels, subspace incidence or native recipes.

Scalar endpoint restoration and isolated columns remain separate obligations.
So do `RecipesExact` for other events, serialization-to-Lean correspondence,
footprints, ownership, whole-call hosting, all-size compilation, precision/tape,
complete cost and analytic transfer. Wrapper identity alone does not discharge
`hrec` or instantiate `hpe_word_exact`.

## Implementation bounds

The checker has no recursive traversal. It admits at most 4,096 local registers,
4,096 frames with at most nine rows each, and 100,000 events per orientation.
JSON reads stop at 32 MiB of decoded data and reject duplicate keys. Functions
remain below 60 lines. Runtime contracts use exceptions, so `-O` cannot remove
them. Producer subprocesses retain their three explicit 120-second timeouts.

Power-of-ten deviations for rules 3, 8 and 9 apply to managed-runtime allocation
and dynamic module loading. Python/JSON allocate during checking, but decoded
artifact and collection limits bound live input and state. Temporary producer
output is scoped and removed on every exit. Module loading has only two explicit
local targets, the new checker and the pinned producer harness. It is needed for
isolated script execution and reuse without copying frozen code. The local loader
compiles at most 1 MiB of source per target and never substitutes a timestamp-valid
bytecode cache for that source. The size-limit, optimized rejection, stale-cache
and genuine fixture tests exercise these controls. A future port requiring fixed
allocation must replace JSON/Python; a producer API would remove the dynamic import.
No independent subagent review capability was available in this session.

## Open next questions

Can an explicit emitted Lean event word discharge the remaining serialization
boundary? Start with the existing helper-450 row/column certificate and represent
its private COPY/CLEAR lifetimes and extended wrapper labels. This would connect
finite Python evidence to `hpe_block`; the blocker is a correspondence proof,
not another calculation of the three Clifford identities. Physical hosting and
complete supplier admission remain separate even after that proof.

## Credit and license

Nick Petalas contributed this successor check. Riquelme Soares supplied the
PR #2706 diagnosis. Hanson Sun supplied the reusable pinned k8 regeneration
harness and helper-450 binding. Jeremy Kothe supplied the HPE formalization and
k8 construction; DreamingOfClouds supplied the wrapper and Lemma A/G work;
icekylinx supplied the retained compiler. Rohan Arun, Josie Elliston and Sagar
Thakrar retain the selected packing, raw-word and independent-audit credit.
Underlying realization credit and notices remain those of the original packages.

Apache-2.0. Substantial AI assistance covered analysis, implementation,
verification and writing. No independent human review is claimed.
