# A four-bin relay crosses the frozen direct-swap boundary

A source-legal six-role relay takes PR3010's literal T37 allocation from
**k=940 to k=939** in PR2979's saturated-swap face. Two same-width exchanges
prepare one inverse swap. The complete local-plus-idle rank histogram is
unchanged, conditional on the source's ordered native widths and local costs.
This tests the chronological feasibility of the changed joint rank-seven helper
inventory. It claims no new kappa or supplier admission.

Scientific base: `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
Construction source PR2979: `be191346391661f4d35fc0d1508d0a6029572576`.
Starting witness and restricted bound PR3010:
`87ca15cf005ab232ca0104ec5137014ac754f487`.
PR2987's necessary boundary `k>=473` is not a sufficiency theorem.
Frozen source files and exact Git/SHA256 pins are in [SOURCES.json](SOURCES.json).

Registered replay resolves its Git provenance against the identical frozen
exports in this PR's first commit
`64af5a56c7e3aba128161ec215cd909dcfa0fe11`, an ancestor available in a full
checkout of this branch. `SOURCES.json` retains every original source commit,
path, Git blob and SHA256 in `exports` and the provenance rows' origin fields.
The runner verifies the same blob identities and bytes without requiring an
unrelated open-PR head in local Git history. The direct Git-free checks verify
the frozen export hashes as before; mathematical inputs and claims are unchanged.

## The smallest decisive exchange

Bin keys are `(owner_replica, child, port)`; windows use `L < time <= U`.

| Bin | Capacity | Window | Pattern before | Pattern after |
|---|---:|---|---|---|
| C=(23,16,0) | 16 | (265,306] | [8,8] | [7,9] |
| D=(17,14,0) | 32 | (158,281] | [7,7,9,9] | [7,8,8,9] |
| R7=(16,17,111) | 16 | (221,276] | [7,9] | [7,9] |
| R9=(21,15,111) | 32 | (190,298] | [4,9,9,9] | [4,9,9,9] |

First exchange D's width-7 role `(224,337)` with R7's `(271,342)`.
Then exchange D's width-9 role `(259,166)` with R9's `(266,64)`.
Finally put C's width-8 roles `(268,399)` and `(269,87)` in D, and put
D's newly acquired `(271,342)` and `(266,64)` in C. Each pair is `(time,helper)`.
There are eight staged transfers of six distinct roles, over four bins.
Coordinate offsets are repacked into integer compact prefixes after each stage.
No capacity-48 bin changes.

The original D has width-seven times 224 and 227, both outside C's window;
its width-nine times 259 and 265 are also outside, including the excluded lower
endpoint 265. The relay supplies times 271 and 266, both legal in C.
Consequently this is outside PR3010's frozen-source, pairwise-disjoint direct
swap graph. Its sharp k940 result remains valid under its original premises.

Every bin keeps its individual occupied width. Every local word, source call,
provider dispatch, helper width and 91-private-buffer count stays the same.
Thus the complete rank histogram is equal for **every rank tariff**, not merely
for rank mass or one approximate exponent:

```
T37: {1:822840, 2:235098, 3:79734, 4:35964, 5:6858, 8:2664, 48:14095}
T74: twice the T37 counts
```

This is a feasibility bridge, not an extra recursive-cost improvement. It neither
constructs every `473<=k<=939` member nor proves any new optimality statement.
The only new attained face member is k939. The prior journal supplies its own
separately proved k940..1063 family.

Concurrent PR3018 at
`ca7113157d7c959fdfa9d7cd17ef92d3877070d0` reports a strict moment improvement
by changing the exceptional capacity-48 bin patterns. Its native and admission
obligations remain explicit. Our fixed-face construction keeps those bins
unchanged; no composition of the two witnesses is asserted.

## Verification and reproduction

Final exact checks and receipts are recorded in `RESULT.json` and
`INDEPENDENT-RESULT.json`. `verify.py` credits and adapts PR3010's forward-event
geometry checker; `independent.py` independently reconstructs the source model
without importing the constructor or predecessor Python. The constructive
argument is a written proof of this finite witness; literal enumeration checks
all actual roles, families, windows, masks and the T74 embedding. It is neither
an all-parameter allocation theorem nor a formal-kernel proof.

Run the registered verification with:

```sh
python3.12 -B scripts/research_package.py --package research/rank7-multibin-face-relay
```

The standard-library verification commands are declared in `VERIFY.json`.
The optional constructor deterministically rebuilds the witness from `start/`;
its bounded discovery is distinct from verification. No large search, root
recalculation, native replay or hosted workflow rerun is needed.

The conditional namespace `896*T + 408 + 8 + 91 + 2` is not an implementation of
physical movement, backing, tape or precision. Native phases, arbitrary dirty
restoration, complete physical hosting/storage, precision, the outer transfer,
uniform all-size compilation and the bit supplier remain inherited obligations.
No selected result is changed. Hosted CI is separate from local verification.

## Open next questions

Can one source-legal all-width flow realize the necessary k473 boundary?
The earlier 600-second MILP timeout proves no infeasibility. A useful next step
must preserve actual roles, windows, families and complete costs; another small
neutral relay is not by itself evidence of a larger kappa. Join the unresolved
native/physical/precision obligations before interpreting the parent proposal's
profile as an admitted supplier. Structured questions are in `TASK.json`.

## Credit and license

Marius-Paul Dumitrean/PR2979 owns the changed joint frame/helper construction and
original face relation. Ross Richardson/PR2987/3010 supplied the necessary-cut
and frozen-direct-pair checks and starting witness. Retain Yiyang Lu's
flow/coloring and the Tekalign, Kothe, Dugongue, Hale, Diviney, themilkman216,
icekylinx and full source lineage; see `NOTICE` and preserved source notices.
This contribution is Ross Richardson with substantial OpenAI Codex GPT-6.1 Sol
Max assistance, including mathematical owner-allocation specialists. No
independent human review is claimed. Apache-2.0.
