# Independent verification of the four-bin relay

This check attains **k=939** in the pinned T37 face. It independently verifies
the complete literal geometry and preserves the complete paid rank histogram.
It supplies no new kappa. The source is Dumitrean's PR2979 at
`be191346391661f4d35fc0d1508d0a6029572576`; the attained k=940 predecessor is
PR3010 at `87ca15cf005ab232ca0104ec5137014ac754f487`. All 16 frozen exports in
`SOURCES.json` are byte/hash checked. Their separate notices and contributor
credits remain governing attribution.

`independent.py` uses only the Python standard library. It does not import or
execute the constructor or a predecessor verifier. Its inputs are the exact
frozen source JSON and the candidate's declarative artifacts. Reproduce with:

```sh
python3 research/rank7-multibin-face-relay/independent.py --check-result research/rank7-multibin-face-relay/INDEPENDENT-RESULT.json
```

The check-result mode recomputes and compares every deterministic receipt field,
including the checker and candidate input hashes; it preserves the recorded
generation time. Running without that option writes a fresh receipt.

## Source chronology and family identities

For the supplied call order let `a(s,r)` be the time of stage s in replica r,
and put `a(-1,r)=-1`. The TEMPLATE recipe fixes the active pairs at stages
0 through 8 to `(0,0,0,1,1,2,2,3,3)`. Its call owner addresses independently
check the active data family formula

```text
family(r,q,side,p) = 896*r + 224*q + 112*side + p,
0 <= p < 112,  side in {0,1}.
```

The TEMPLATE execution schedule's idle sweep `(q,from,to,[j0,j1])` supplies one
child for each side with capacity `8*(to-from)`. A source event occurs after
the completed local call. Its pending interval is therefore
`a(from,r) < t <= a(to,r)`: the previous event is excluded and the call before
the receiving source event is included. The nonzero children are exactly:

| Children by side 0/1 | Pair | from | to | Capacity |
| --- | ---: | ---: | ---: | ---: |
| 0 / 2 | 1 | -1 | 1 | 16 |
| 1 / 3 | 1 | 1 | 2 | 8 |
| 4 / 6 | 2 | -1 | 3 | 32 |
| 5 / 7 | 2 | 3 | 4 | 8 |
| 8 / 10 | 3 | -1 | 5 | 48 |
| 9 / 11 | 3 | 5 | 6 | 8 |
| 12 / 13 | 0 | 2 | 8 | 48 |
| 14 / 15 | 1 | 4 | 8 | 32 |
| 16 / 17 | 2 | 6 | 8 | 16 |

The last pair-3 terminal sweep has zero gap and supplies no nonzero child.
The checker derives these entries from TEMPLATE, then cross-checks every
pair, side, rank and permitted call against PLAN. This covers **666 T37
windows** and **74,592 bins** (37 replicas times 18 children times 112 ports).
PLAN's old 480-helper widths and old local profiles are not reused. The pinned
actual `PROVIDERS.json` supplies the ordered **408** widths and local paid
profiles; its native arithmetic and endpoint-width derivation remain premises.
The provider identity at every call is cross-checked against PLAN's stage and
replica registry, and candidate ORDER/DISPATCH must equal the predecessor's.

For every source family, the legal call sets of its different nonzero child
windows are disjoint. No such set contains a call with that replica's pair
active. The checker establishes both properties from the complete order.
Consequently, for this source, received roles with distinct call times in a bin
cannot collide with another child bin of the same family. This sufficiency
statement depends on these checked source invariants; separate coordinates or
different child names alone never justify sharing a physical family.

## Exact witness and sequential replay

The starting fill is independently reconstructed by projecting source T74
copy zero and replaying all 123 predecessor journal entries, including their
actual ordered widths and deterministic compact repacking. This verifies the
attained starting fill; it does not recensus or reprove PR3010's matching graph
or its restricted optimality theorem.

The new endpoint witness changes six owner assignments in these four bins:

| Name | (replica,child,port) | Window | Before | After |
| --- | --- | --- | --- | --- |
| C | (23,16,0) | (265,306] | [8,8] | [7,9] |
| D | (17,14,0) | (158,281] | [7,7,9,9] | [7,8,8,9] |
| R7 | (16,17,111) | (221,276] | [7,9] | [7,9] |
| R9 | (21,15,111) | (190,298] | [4,9,9,9] | [4,9,9,9] |

The six roles, with their unchanged `(call,helper)` identities, are:

| Role | Width | From | To |
| --- | ---: | --- | --- |
| (224,337) | 7 | D | R7 |
| (259,166) | 9 | D | R9 |
| (266,64) | 9 | R9 | C |
| (268,399) | 8 | C | D |
| (269,87) | 8 | C | D |
| (271,342) | 7 | R7 | C |

The construction can also be replayed as three valid complete allocations:
exchange the two width-7 roles between D and R7; exchange the two width-9
roles between D and R9; then perform the inverse C/D face swap. The last
stage moves four roles, including the relayed roles that temporarily occupied
D. Thus there are eight staged transfers but six endpoint owner changes.
These are offline choices of the owner allocation; physical execution continues
to depend on the inherited hosting contract.
The checker reconstructs every intermediate offset, verifies every declared
offset-only change and bin-state field, and checks full T37 geometry and invoice
after each stage (k=940,940,939). No capacity-48 bin changes.

Every final fill check covers all **135,864** call/helper identities, actual
provider-indexed widths, integral contiguous masks, capacities, disjointness,
compact prefixes, strict source windows, active families and the one-helper
per-call physical-family rule. It compares the entire pattern multiset, rather
than inferring the face parameter only from a few changing bins. At k=939 the
changing multiplicities are 1,262 copies of `[8,8]` at capacity 16, 15,314
copies of `[7,9]` at capacity 16, 939 copies of `[7,7,9,9]` at capacity 32,
and 124 copies of `[7,8,8,9]` at capacity 32. All other face patterns remain
unchanged.

The exact two-copy embedding sends each role time to `2*t+b` and its owner
replica to `r+37*b`, for b=0,1. Both embedded ORDER and DISPATCH equal the frozen
source T74 files. The source literal fill equals this embedding as well. The
checker fully verifies the embedded source, starting and candidate fills:
**271,728 roles, 149,184 bins and 1,332 windows** each. It uses the actual T74
source intervals, with entrance endpoint -1, rather than assuming all endpoint
integers transform identically under the embedding.

## Complete paid cost and tariff identity

Both providers have the pinned local profile
`{1:2445,2:706,3:232,4:108,5:18,8:8}`. Summing over all 333 calls and adding
every bin's nonzero residual gives

```text
native = {1:814185,2:235098,3:77256,4:35964,5:5994,8:2664}
idle   = {1:8655,3:2478,5:864,48:14095}
total  = {1:822840,2:235098,3:79734,4:35964,5:6858,8:2664,48:14095}.
```

The total paid rank mass is 2,408,256. T74 doubles every count and this mass.
The source paid-profile file and the candidate PROFILE, PATTERNS and all
numeric/boolean/pin META assertions are independently checked against the full
fill. META's mode, search and proof-level prose is descriptive; the checker
does not certify a historical search duration or trial count.

Here is a written equality proof for every rank tariff. A same-width exchange
preserves the occupied rank of both receiving bins. In the last inverse swap,
C and D both remain full, with loads 16 and 32; R7 and R9 retain loads 16 and
31. Every other bin is unchanged. Hence each individual residual rank, and
therefore every residual-rank multiplicity, is unchanged at every stage.
Every native provider invocation and its source paid profile is also unchanged.
For an arbitrary function tau on positive integer ranks the complete conditional
recursive bill is therefore exactly

```text
822840*tau(1) + 235098*tau(2) + 79734*tau(3) + 35964*tau(4)
+ 6858*tau(5) + 2664*tau(8) + 14095*tau(48),
```

with zero delta; T74 has twice this bill. No monotonicity, concavity, or power
assumption on tau is needed. The literal full-fill computation additionally
checks equality of every per-bin load with source and predecessor.

The 408 helper names, eight centres, **91 private buffers** and two guards are
the unchanged inherited interface. The conditional namespace is
`896*T+408+8+91+2` (33,661 at T37 and 66,813 at T74). This work does not derive
the private-buffer count from native execution or certify physical stock.

## Controls, covered domain and remaining obligations

Eight deterministic rejecting controls remove a role; exchange equal-width roles
into wrong windows while preserving aggregate widths; cause a same-call physical
family collision with disjoint masks; overlap offsets; move a role onto an
excluded lower endpoint by an equal-width exchange; request the wrong face k;
lie about a journal width; and corrupt an intermediate offset. Every control
must fail the intended semantic assertion. Their mutations and the exact check
outputs are reproducible in the independent checker and result receipt.

The geometry and journal claims are **finite exact computations** on these
specific T37/T74 files. The family-window sufficiency argument and equality for
all rank tariffs are written proofs under the pinned source interface. They are
not formal-kernel proofs or all-size allocation theorems. The new witness leaves
the frozen-source, disjoint, direct inverse-swap model by relaying concrete roles
through other bins; it does not contradict the predecessor's bound in that model.

Native arbitrary-dirty-input arithmetic, phase and literal restoration, endpoint
width derivation, physical stock and movement, precision and reachable prefixes,
consumer/outer admission and all-size or machine/compiler transfer remain
separate inherited obligations. General feasibility below k=939, face optimality,
an improved fully charged histogram and any larger kappa remain unresolved.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0. Credit
Dumitrean's PR2979 construction/face, PR3010's attained predecessor, Lu and the
owner flow/colouring lineage, and all contributors retained in the frozen notices.
