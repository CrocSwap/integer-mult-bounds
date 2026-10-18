# PR3044 R2: independent native slice and residual wrappers

This package follows [PR3146's released next question](https://github.com/CrocSwap/integer-mult-bounds/pull/3146):
independently interpret the native phase/residual-adapter boundary of Nick
Petalas's R2 shared restore. It checks the actual **base and extra** providers
of [PR3044](https://github.com/CrocSwap/integer-mult-bounds/pull/3044), head
`1f922b25abff2d7fd87fa5b29619160862a06b59`, as archived at canonical main
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`.

**Result:** the three changed native child recipes, four ordinary source
endpoint adapters, and all **54 used residual recipes per provider** satisfy
their exact operator identities on all 512 complex coordinates, including
global phase, in both orientations. The emitted tail and final steps and every
residual wrapper's owner, side and phase agree with independently reconstructed
source boundaries. This is a finite, scoped verification result. It supplies
no new construction, kappa, physical realization or supplier admission.

## Missing coverage and independence

PR3044 already checks rational R1/R2 equality, frame charges and a complete
release using its native engine. Hiroki Kumazaki's PR3146 independently runs
that release and adds separate local/binding checks, while explicitly leaving
native semantics dependent on the inherited engine.

The new `verify.py` does not import the producer, lowering compiler, original
R2 evaluator or frame tracer. Its new source/event binding uses explicit finite
binary spans and sparse rational rows. For native arithmetic it **reuses**, with
an exact source pin, Sagar Thakrar's separately implemented
[`clifford.py`](../frontier1094-recipes-exact-seed76/clifford.py). That established
stdlib kernel interprets primitive circuits as packed Gaussian-integer matrices
with a proved non-aliasing radix. This package does not claim a new kernel or
independence from that auditor. Hand calibrations cover C squared, inverse and
global-phase sensitivity. New fault controls test the changed boundary.

The eight retained native artifacts were freshly regenerated using the original
six source-bound engine files. All eight raw artifact hashes matched PR3044's
published native receipt in the recorded environment. Generation and checking
are distinct: producer PASS messages establish no independent native identity.
The default verifier authenticates the complete artifacts, then interprets
their selected semantic payloads itself. JSON artifacts are gzip-compressed for
storage; their uncompressed original bytes are authenticated. Existing `.gz`
artifacts retain their original bytes.

## Exact scope and argument

Write W = span(256,128,64,34,17,11,4), E =
span(256,128,64,34,16,10,4,1), and F for the full nine-dimensional frame.
R2 forms X40 − 2 X54 at W, serves the X18 and X22 consumers at E, then
restores X40 at F. The changed native trace, using zero-based restore indices,
is:

| Restore index | Register | Transition | Charged rank |
|---|---|---|---|
| 163 | X40 | W → E | 1 |
| 203 | X40 | E → F | 1 |
| 203 | X54 | W → F | 2 |

For each serialized child, the checker proves `L F_r R = T_new T_old^-1`
with every phase retained, and proves that composing the two rank-one recipes
equals the rank-two recipe. A componentwise rational scalar commutes with the
common frame operator. Provided the unchanged native operations realize their
declared frame maps, these identities validate the changed R2 lowering in
physical coordinates. The full 204-gate scalar tail is compared with the
reconstructed R1 control on all 632 arbitrary input columns in both orientations.
This corroborates the earlier scalar check and connects it to the native slice.

The four named registers are ordinary sources, with source endpoint adapters
and FULL exits, **not residual-wrapped helpers**. Their source endpoint identities
are separately checked. The current source maps also determine every wrapped
helper. For each of the 54 used residual recipes the checker proves
`L^-1 T_terminal T_entrance^-1 R^-1 = F_width`; the inverse-transpose orientation
uses complex conjugation of these unitary frame operators. All emitted pre/post
wrapper occurrences must have the correct helper, side, entrance/terminal IDs
and phase. This validates wrapper identities and placement; it does not prove
that every intervening native operation realizes its declared reference map.

The source A/B frame trace is reconstructed from word data. A separate scan of
the emitted prefix checks frame transition chronology and its tail entrance.
Prefix native phase semantics are an explicit premise. No end-to-end physical
executor or all-register native theorem is inferred from these checks.

## Reproduction

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/pr3044-r2-native-slice
python3 -I -O -B research/pr3044-r2-native-slice/verify.py
```

The registered command reads source-bound saved artifacts; it does not generate
them. Its semantic controls operate **after authentication**, requiring each
mutant to fail the named semantic predicate. They cover both fan-in signs,
the rank-two charge, phase order, source frame chronology, dirty restoration,
an extra observer, ordinary source exits, wrapper side/owner and post-cleanup ordering, child phase/rank/
translation and residual phase/translation. `RESULT.json` records exact counts.

Optional producer regeneration requires NumPy (the recorded run used 2.3.5):

```sh
python3 -B research/pr3044-r2-native-slice/reproduce.py --output /tmp/r2-native-fresh
```

Use a new output directory. This runs four inherited stages sequentially for
each provider, then compares every proof-relevant JSON field with the
authenticated retained artifacts. Container bytes may differ with Python/zlib;
payload equality is the portable regeneration gate. The full PR3044/3146
13-stage source/admission/outer replay was not repeated here. See
`ENVIRONMENT.json` and `evidence/` for this session's exact generation evidence.

## Limits

Other native child recipes, warp semantics, full-frame cleanup semantics,
physical owner geometry/stock, precision/tape, caller contracts, all-size
compilation, analytic transfer and universal block-energy obligations remain.
The earlier all-input and complete-release results retain their original
evidence status. No selected-frontier record or predecessor file is changed.

## Open next questions

1. Extend the native interpretation to the remaining R2 dependency cone,
   especially the full-frame inverse cleanup and its private buffers. Begin
   with the authenticated `LOCAL-PROGRAMS` and the source restore-to-cleanup
   mapping. The gap is the complete physical map, not artifact availability.
2. Independently check the physical executor's use of the serialized native
   records and their actual owner locations. Begin with these three child events
   and the current hosted template. Exact recipe identities alone do not
   discharge executor, routing or ownership contracts.

Structured scope, original card, overlap coverage and next steps are in
`TASK.json`. This answers a specific historical handoff; it makes no claim to
the newest unreviewed candidate or exclusive novelty. Metadata/discussion
coverage does not include unpublished work or every historical diff.

## Credit

24kHandsome1201 with substantial OpenAI Codex assistance for analysis, code,
execution and writing. No independent human or proof-kernel review is claimed.
Nick Petalas contributed R2, its finite checks and original release; Jeremy
Kothe contributed R1 and the literal rewrite/cleanup machinery; Marius-Paul
Dumitrean contributed the joint rank-7 words/allocation; Hiroki Kumazaki supplied
the external cold replay and this handoff. Sagar Thakrar supplied the reused
independent exact kernel. The earlier V45 event-binding audit is credited for
the source-to-native audit approach; its checker is not imported.

Credit also Cinna Davis, DreamingOfClouds, icekylinx, chafreaky, Mason Hale,
Jeremy Diviney, Yiyang Lu, Tekalign, Ross Richardson and the retained native,
geometry and owner lineage. Existing notices remain in their source packages,
including [PR3015 credits](../rank7-shared-restore-fanin/vendor/PR3015-CREDITS.md)
and [notice](../rank7-shared-restore-fanin/vendor/PR3015-NOTICE).
Code and generated data retain Apache-2.0 licensing.
