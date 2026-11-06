# Six calls for three rank-two targets with arbitrary dirty auxiliaries

**Scoped written lower bound.** Three invertible rational 2-by-2 targets need
at least six rank-one calls in the formal abelian BIT register model, for any
finite number of dirty auxiliary registers with arbitrary diagonal monomial
outputs. Six coordinate calls attain the bound and restore all auxiliaries.
This closes the five-call/span-three block left open by
`bit-span4-auxiliary-structure`. Its reduction then gives **nine calls for every
span-four word with three invertible 3-by-3 targets**, with the same arbitrary
diagonal auxiliary-output contract.

[PROOF.md](PROOF.md) is the argument. The new mechanism is a projective conic
split into three, four or five distinct rank-one directions. In the four-point
case, two-copy direction incidence forces three singleton scalar projectors to
be coordinate; the remaining two rank-one updates cannot supply a rank-three
endpoint difference. In the five-point case, the secant graph forces all but
at most one scalar image into the three active roles. The remaining factor
either restricts or acts identically there, enabling the inherited
three-register theorem. The reduction does not assume restored auxiliaries.

The low-span/one-relation theorems and the three-register six-call theorem are
explicit inherited dependencies, not independently re-proved here. Their source
text is byte-pinned. This is not a formal-kernel proof, new supplier, physical
cost improvement, complete multiplication theorem or selected-frontier change.
The selected conditional value remains PR5413's 0.003027288235.

## Verification

Standard-library Python 3.12; each direct check is under a second locally:

```sh
python3 -I -B research/bit-fivecall-dirty-block/verify.py
python3 -I -O -B research/bit-fivecall-dirty-block/verify.py
python3 -B scripts/research_package.py --package research/bit-fivecall-dirty-block
```

Expected: `PASS_FIVECALL_DIRTY_BLOCK`. The read-only replay authenticates source,
proof and checker bytes and compares [RESULT.json](RESULT.json). Explicit
`--write-result` regenerates the receipt. Two independently implemented exact
formal engines check the six-call arbitrary-input endpoint, all six deletions,
a changed address, and non-coordinate dirty cancellation. Exact rational conic
fixtures check all secant incidences; all 17,576 triples of five-vertex matchings
check the graph reduction. Singular-target and nine-bad-edge controls show why
its assumptions matter. A separate behavioral test runs a closed Git-free copy
and rejects changed proof, source, receipt and checker bytes in both modes. The finite checks corroborate the written universal
argument; they are not a five-call word enumeration or a new proof of inherited
lemmas. No 120^5 search, historical supplier replay, Lean or Docker was run.

## Sources, overlap and credit

Scientific base `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority 7.
Canonical investigation: [Discussion5473](https://github.com/CrocSwap/integer-mult-bounds/discussions/5473).
The root checked 342 open PRs and 4,736 Discussion records before assignment;
local source checks include the span-four handoff, span-six flag/cyclic-line
successors, four-role pattern census and mixed-target compression. The latter
requires restored extras and is not used to justify this broader contract.
Arbitrary diffs and unpublished work are outside that overlap coverage.

Credit unpaidmoon for the span-four equality reduction and explicit remaining
five-call question; waynenilsen for arbitrary-register low-span and one-relation
bounds; David Govea for arbitrary-target three-register six-call reduction;
Ali Romman PR468 for the original algebraic/flag/finite-classification methods,
with eumemic PR288 and huxint PR203 retained. The geometric incidence and
rank-update tools are classical. New proof and diagnostics by JoyboyBrian,
with substantial OpenAI Codex assistance. Apache-2.0. No independent human
review is claimed.

## Open next questions

Spans five and six for eight rank-one calls and three rank-three targets remain
outside this result. Start with a named unresolved relation class and its exact
endpoint/auxiliary contract; check later successor results first. The conic
proof does not automatically extend to a larger rank-one determinantal variety.
A positive candidate would still require native address realization, all scalar
role changes, owned/dirty restoration, hosting and a full recursive invoice.
[TASK.json](TASK.json) records the same scoped handoff and stop gate.
