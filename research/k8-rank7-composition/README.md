# Conditional kappa from smaller ends on the k8 word

This finite construction certifies

**κ = 0.001672404744903063**,

or `1672404744903063 / 10^18`. The conservative calculation gives
`0.001672404742051193`. It improves the pinned PR1031 construction
`0.001672167430672016` by exactly `237314231047 / 10^18`. The base selected
certificate records PR942's `0.001661960547713947`; that selection is unchanged.

This is a distinct construction, pending review. The last overlap scan found
PR1082 claiming a larger `0.001672653061493085` using the preceding k8 terminal
interface. This package claims a new smaller-end interface with a complete
paid packing, without claiming the highest pending or accepted frontier.

## What changes

Alexander Schwartzman's PR1030 helpers 588/589 map to **574/575** in the k8
word. Their final frames become the dimension-seven space
`span_GF(2){256,128,96,17,9,5,3}`. Eight B frames and two early tails change.
The scalar program, gate order, all entrances and the center interface are
preserved. All twelve literal edits and both endpoint hashes are frozen in
`data/END-RECIPE.json` and `construct.py`.

The local profile changes from
`{1:2412,2:418,3:432,4:142,5:82,8:8}` to
`{1:2406,2:432,3:424,4:142,5:82,8:8}`. Width per call decreases **3730 -> 3728**;
local rank mass decreases **5586 -> 5584**. Keeping the previous owners fails
the improvement screen: every newly exposed residual is priced. The new
69,120-role map in `data/OWNERS.json.gz` pays those residuals, whole helpers,
copies, spectators, source windows, restores, frame and coefficient work,
physical routing, and every recursive child through the unchanged full invoice.

The final global profile is
`{1:348779,2:62233,3:61410,4:20459,5:11808,7:7,8:1156,16:16,32:1,48:4864}`.
It has 144 complete invocations, rank mass 1,041,408 and deficit 5,120. The
prefix is **397 < 512** bits and the physical row coefficient is
**16469 < 20161**. The complex supplier binds; PR589 is cited unchanged and
its complete bad-residue bit profile is repriced.

## Reproduce

Base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`. PR1031:
`e900534f0beda892c726723524203b97471fb9a3`. PR1030:
`d71857cd0ae7824e935aac17327e4ec27f66322b`. All retained source archives and
348 main files are SHA-256 pinned in `SOURCES.json`. No solver or GitHub fetch
is required for replay; Python 3.12+ with assertions enabled is sufficient.

From the repository root, with a new output directory:

```sh
python3 -I -B research/k8-rank7-composition/reproduce.py --work /tmp/k8-rank7-replay
python3 -I -B research/k8-rank7-composition/check_controls.py --replay /tmp/k8-rank7-replay
```

Expected markers:

```text
PASS_K8_RANK7_COMPLETE_REPRODUCTION 0.001672404744903063
PASS_K8_RANK7_SEMANTIC_CONTROLS 10
```

The command explicitly reuses the frozen parent ancestry in `evidence/ANCESTRY.json`
and `sources/SLOT-NATIVE.tar.gz`. That ancestry was freshly built before
publication: all 21 k8 chain stages, five cold-end control batches, native
programs/wrappers/phases, and all 34 new-slot controls passed. The portable
command checks its receipt and source identities, freshly constructs the
new word and native code, checks every exact scalar column in both
orientations, all frames and wrapper cones, and freshly verifies all phases.
It then replays both the preceding and new T16 controller, source geometry,
full invoice, both exact moment engines and all 47 outer conditions.
It does not rerun the inherited scalar constructors during every replay.

Both full admissions include 69 admission controls, 12 bit controls, 15
controller mutations and six independent owner controls. Ten additional
controls reject incomplete tails, invalid read frames/end spaces, false
profiles/widths, duplicate or split helpers, bad slices, restoration of the
preceding larger ends on the new map, and the next outer grid point.

## Search and mathematical scope

The changed width inventory is outside PR942's fixed-U8 all-replica theorem.
Searches used seed 32 and stopped at explicit budgets: six greedy epochs,
80 restricted MILPs (three seconds each), two global MILPs (120 seconds
each), one global CP-SAT run (120 seconds), and 12 window searches (18
seconds each). The global MILPs found no integer witness. The final map is
feasible; neither failed searches nor restricted solver optimality establish
a global packing optimum. Exact domains, completed attempts, accepted moves,
software versions and stopping rules are in `evidence/SEARCH.json.gz`.
Reproduction consumes frozen data and performs independent admission.

The inherited all-size/compiler, common-label and mutable-source realization,
whole-call hosting, physical implementation, precision/tape, exact recovery,
analytic transfer and bit H1-H5 obligations remain. This is a finite conditional
certificate, not an unconditional theorem or a full Lean proof. Contributor
credit, inherited licenses and substantial AI assistance are recorded in
`NOTICE.md` and the preserved source notices.
