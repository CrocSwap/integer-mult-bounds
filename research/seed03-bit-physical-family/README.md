# One physical host family in the selected PR589 bit word

**Finite exact operator check; no new κ.** This package checks one concrete
physical family in the selected nine-stage PR589 R439 bit supplier. It
independently rebuilds the schedule and frozen slot assignment, then composes
the typed address operators for the deterministic highest-multiplicity family
that spans multiple idle children.

The selected family is `(pair=1, copy=0)` (side 0, port 0). It has four hosted
helper occurrences across idle children 0 and 7. For child 0, one rank-8
helper and a rank-6 remainder reproduce the original rank-14 pending map. For
child 7, three rank-8 helpers and a rank-4 remainder reproduce the original
rank-28 pending map. For each child interval, the actual product

```text
D(P_helper_1) ... D(P_helper_k) D(P_remainder)
```

equals `D(P_source)` exactly on all 128 standard basis vectors, where
`D(P) = [[I-P, P], [P, I-P]]`. The projectors use the selected port's exact
rational `q`-perp projector and the assigned external coordinate axes. The
schedule check confirms that each host call is in its source window and that
no local or bridge touch of the pair occurs before that child's idle event.

The child-7 helper factors are mutually orthogonal. All six permutations of
those three factors give the same exact operator. Four controls reject an
omitted helper, a duplicate helper, an equal-rank wrong axis, and a wrong
source port. This is a one-family operator realization, not a census of all
families.

## Reproduce

From the repository root, using only the standard library:

```sh
python3 -I -O -B research/seed03-bit-physical-family/verify.py
python3 -I -O -B research/seed03-bit-physical-family/test_package.py
python3.12 scripts/research_package.py --package research/seed03-bit-physical-family
```

The first command prints:

```text
PASS_PR589_PHYSICAL_FAMILY pair=1 copy=0 children=0,7 helpers=4 columns=128 controls=4 orderings=6 no_new_kappa
```

The first two commands were run with CPython 3.14.7 here. The registered
Python 3.12 wrapper also validates the source inventory and runs both checks,
but could not be run because Python 3.12 is not installed in this environment.
`RESULT.json` records the selected family, its host slots,
remainder axes, source hashes, matrix-column counts, positive order checks and
negative controls.

## Selection, pins, and overlap

- **Track and seed:** bit supplier, OS draw `2447174283`, seed `03`.
- **Base:** `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- **Selected result:** κ = `836330098538459/500000000000000000`; the selected
  assembly binds the tuned bit word to PR589 commit
  `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
- **Schedule inputs:** the selected nine-stage `recipe`, geometry idle table,
  `selection9-p111.json`, and the tuned PR589 word are pinned by Git blob and
  SHA-256 in `SOURCES.json`.
- **Nearest predecessor:** PR1307's all-family pending-projector census
  (head `4cb255ef445e2abc3ff8845fa01210b974e2cf6c`) establishes the geometric
  masks and slot census. This package adds an independent exact matrix replay
  for one actual mixed-child family; it does not import PR1307's checker.
- **Other checked overlap:** PR1334 prices relaxed selected-bit levers; PR1311
  checks a semantic-D bridge for a different PR1122 word. Neither checks this
  PR589 family map. The older seed-3 PR1023/PR1281 work concerns width-seven
  slot relaxations, a different object and method.
- **Late overlap refresh:** PR1345 (head
  `b54a856aa79857d91cd5d65f8f7144e26c8c084f`) exhausts fixed-word single/pair
  gate-order transports on PR589; it does not relocate helpers into
  idle-family projectors. PR1344 (head
  `a42e525e9868970f3fa2d99dccca45f014aa0fd3`) independently replays the
  separate R439 frame-509 local matrix. Both are distinct from the selected
  physical-family address-map identity checked here; exact heads and URLs are
  recorded in `SOURCES.json`.

The deterministic selector maximizes the number of hosted slots among
single-replica families that span multiple idle children, then chooses the
smallest `(pair, copy)` key. It returns `(1,0)` with four slots; the full
reconstruction has 3,951 selected slots and 444 mixed-child families per
replica. The test does not optimize the selection or claim that this family
is globally representative.

## Scope and remaining obligations

This result verifies finite rational address-operator identities under the
inherited PR589 projector interpretation. It does not replay all helper
scalar maps, native lowering, all 126,432 helper occurrences, every physical
family, the complete interleaved caller, the all-size compiler, hosting at
all scales, precision/tape, analytic transfer, or the multiplication
theorem. It does not change the selected certificate or κ. Extending the
same exact operator check to all 444 mixed-child families per replica is a
separate next step.

## Credit and disclosure

Credit DreamingOfClouds and eumemic for PR589/PR555 and the retained bit
supplier lineage; credit commdata2338 for PR1307's source-bound geometric
census; and credit the retained nine-stage recipe and idle-axis hosting
authors named in the source notices. Prepared by Cinna Davis
(@1337isnot1337) with substantial OpenAI Codex assistance for research,
implementation, verification, and writing. No subagents or independent
human review are claimed. New material is Apache-2.0.

## Open next questions

1. Does the same typed matrix check pass for all 444 mixed-child families per
   replica? A full census would test whether this exact one-family mechanism
   generalizes across the selected allocation. First step: reuse the pinned
   selector and stream exact basis checks over each distinct `(pair, copy)`
   family. Blocked by the deliberate one-family stop rule and the increased
   exact matrix replay cost.
2. Can the finite per-family identities be joined to a complete native replay
   of the emitted PR589 caller? That would cover interaction with the full
   call chronology. First step: bind these projectors to the source caller's
   emitted owner records and replay the complete nine-stage word. Blocked by
   native, precision/tape, and all-size obligations outside this package.
