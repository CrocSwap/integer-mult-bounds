# Partial K/M face bypass: the missing consumer costs two copies

**Scoped negative result; no new κ.** Replacing two selected-source face
copies by raw leaver reads looks like a two-helper saving. In the mixed
K/M interface tested here, the remaining ordinary consumer forces four
private carriers of the other face packet. With other register roles fixed,
the two extra copies cancel that helper saving. A complete scalar/native control circuit attains four
carriers, restores arbitrary dirty inputs, and has a strictly worse paid
moment than its raw K492 baseline for every exponent `0 < s < 1`.

This is a result about a specified local replacement, not a lower bound on
all complex suppliers, all schedules, or the selected optimized providers.

## Reproduce

From the repository root, Python 3.11 or later, standard library only:

```sh
python3 -B research/partial-k-face-bypass/verify.py
```

Expected first line:
`PASS_PARTIAL_K_BYPASS_FLOOR_AND_UNFAVORABLE_PAID_CONTROL`.
The run takes roughly 12 seconds on the development machine. It checks source
pins, reconstructs 16 exact geometric certificates, completes the stated
scheduling searches, rebuilds the baseline and paid control, runs both native
orientations on all 716 columns, rejects four circuit mutations, and compares
all deterministic results with [EXPECTED.json](EXPECTED.json). Generated
words and logs go to a fresh temporary directory. Use `--work /new/path` to
retain them at a chosen location. Compression bytes are not compared;
receipts bind decompressed mathematical payloads.

[CLAIM.json](CLAIM.json) records OS assignment seed **24**, the three candidate
tasks, coordination/overlap checks, and completed scope. The exact base is
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. At this base the accepted conditional
κ is `51110230636731/31250000000000000`, from #626/#622/#623 with #543.
[Source pins](SOURCE-PINS.json) identify the actual construction and native
auditor used here. Pending PR titles are not treated as accepted results.

## The replacement being tested

The #531/#622 construction has three four-coordinate blocks incident to each
coordinate pair `p`. For eight pairs, two blocks use the selected K delivery
and the third uses ordinary M delivery. For either sign, there are four K
coordinates, two in each selected block. The seed chooses `(0,2)` from the
lexicographically sorted eight mixed pairs; both signs are checked.

For the negative sign, the selected blocks are `(0,2,4,6)` and `(0,2,5,7)`;
the ordinary block is `(0,1,2,3)`. The K target indices are `12,13,36,37` in
the restricted 112-port numbering. Each selected source produces a face
`a+b` from two rank-two leavers. The proposed replacement:

1. Omits that face's second copy in each selected block.
2. Gives each K coordinate its own token and both raw leavers of the other
   selected block, allowing **any order**, including a deferred own read.
3. Supplies the remaining contribution from pure copies of the ordinary
   block's rank-three face packet, retaining other register roles and
   allocating any extra carriers as ordinary copy helpers.
4. Still forms each selected-source face for the unchanged ordinary M
   consumer and retains its subsequent mixing and target delivery.

All frames are monotone; a scalar read joins the frames of both operands;
target frames remain inside their original hyperplanes. The packet/leaver
scalar decomposition, target basis and ordinary delivery are fixed. Extra
encoded mixtures, borrowed or recycled registers, changed factories,
different ordinary consumers, partial one-face bypasses and additional
helper trades are outside this claim.

This changes the search class relative to #651's own-read-first face/slot
sharing argument: it splits a face before assembly and permits own-read
movement. It also differs from #622/#646's full K triangles, which have no
ordinary M consumer for that pair. No previously closed search is reopened
merely with a larger compute budget.

## Why four remaining-packet carriers are necessary

Let `Q` be the intersection of the four ordinary consumers' target caps.
Each selected-source face must eventually be formed and feed those four
consumers through the unchanged M circuit. Every participating raw leaver
therefore must stay in `Q`: its frame is inherited by the formed face and
all its descendants. A monotone frame cannot later discard a forbidden
vector. The certificate checks that all four initial leaver frames lie in
`Q`, while the remaining packet frame `P` does not.

Consequently a K coordinate cannot read the remaining packet before any
of its three required leaver reads. Such a subsequent read would carry
`P` into that leaver and violate the ordinary consumer's cap. **This derives
packet-last; it does not assume own-first.**

For K coordinate `t`, let `V_t` be the span of its own token and the two
foreign leavers. At its packet read the frame contains `W_t = V_t + P`.
The exact certificate gives

```text
W_t is contained in cap(u)  if and only if  t = u,
```

for the four K coordinates. Thus a remaining-packet carrier that has served
one coordinate cannot serve another. Copying it afterward does not help:
the copy inherits its forbidden frame. At least four carriers are required.
The certificate contains a nonorthogonal vector for each of the 12 ordered
cross-target pairs and a vector witnessing `P` outside `Q`, for all **16**
mixed-pair/sign cases. These are exact F2 witnesses, independently derived
from the pinned packet data; no numerical rank tolerance or solver is used.
This is a finite geometric proof for those objects, not formal verification
of the full multiplication theorem.

## Bounded search and a diagnostic that catches the missing constraint

The search has four target registers, four fixed leavers and `c` pure packet
carriers. It executes exactly 16 reads, selecting a carrier for each packet
read and otherwise enumerating all orders. Its only symmetry reduction skips
identical adjacent packet-carrier states. Future-reader pruning rejects a
state only when monotonicity already makes a required read impossible.
The stopping rule is first witness or exhaustion, with a hard two-million
state cap; no reported run reaches that cap.

| Seed-selected sign | Two carriers | Three carriers | Four carriers |
| --- | ---: | ---: | ---: |
| −1 | exhausted, 63,383 states | exhausted, 156,085 states | first witness, 12,201 states |
| +1 | exhausted, 63,383 states | exhausted, 156,085 states | first witness, 12,201 states |

Removing the ordinary-consumer guard admits a two-carrier schedule after
12,555 states. Its first forbidden leaver frame is recorded in the receipt.
This is a concrete counterexample to treating that relaxed schedule as a
complete circuit, not a counterexample to an accepted theorem. The all-16
geometric argument supplies broader evidence than these two enumerated
instances. No enumeration of other circuits is claimed.

## Complete native cost of the attaining control

[RECIPE.json](RECIPE.json) gives the negative-sign four-carrier schedule.
[construct.py](construct.py) applies narrowly checked substitutions to the
pinned #622 constructor. It removes two old face-copy helpers, explicitly
allocates two new packet copies, defers the two selected face assemblies,
and leaves the constructor's clean scalar, monotone-frame, inverse cleanup
and rank-mass assertions in place. Its helper map distinguishes removed
historical helpers from the two genuinely new helpers.

The unchanged native auditor independently rebuilds arbitrary-dirt
compensation and checks forward and inverse-transpose endpoints on all
716 input columns. It recounts every source/helper/target frame climb,
center visit, terminal climb and residual width. The full reversed cleanup
is retained; no restoration or source-access operation is declared free.

| Quantity | Raw K492 baseline | Paid control |
| --- | ---: | ---: |
| Helpers / residual width | 492 / all width 9 | 492 / all width 9 |
| Native paid rank mass | 6,284 | 6,284 |
| Scalar operations including compensation and cleanup | 16,972 | 16,975 |
| Recomputed dirty compensation additions | 10,632 | 10,631 |
| Directed native frame edges | 3,110 | 3,112 |

The complete paid-profile difference is

```text
ΔH = +10 H1 − 6 H2 + 2 H3 + 2 H4 − 2 H6.
```

For `m=73`, the moment difference is
`2/73^s * (5 + 3^s + 4^s − 3*2^s − 6^s)`, strictly positive for
`0 < s < 1`. One exact concavity proof starts with
`[6,2,2,2,0,0,0]` and performs the following transfers:

```text
[6,2,2,2,0,0,0] → [5,3,2,2,0,0,0] → [4,3,2,2,1,0,0]
                  → [4,3,1,2,1,1,0] → [4,3,1,1,1,1,1].
```

Each transfer is from a strictly larger coordinate toward a smaller one,
so strict concavity of `x^s` increases the sum. The checker also verifies
every integer majorization prefix. The same helper-width inventory leaves
no extra hosting capacity; granting identical external charges and any
common owner assignment therefore cannot improve this circuit's moment.
This rejects this fully specified implementation. It does **not** prove
that every four-carrier schedule has this profile or that different
entrance kernels/cold ends could never help.

All source access and restoration are in the reconstructed scalar word;
all native recursive children and center charges are in `H`; the 492 width-9
residual demands are counted separately. A global owner certificate,
all-edge phase lowering, optimized entrance/cold-end transport, full finite
invoice and outer assembly are intentionally not supplied: the control
already loses under the favorable comparison above. No bit-side gain,
new conditional κ, or practical runtime speedup follows from this note.
Inherited uniform/compiler/common-label/mutable-basis/hosting/precision/tape
and analytic assumptions remain untouched.

## Controls, attribution and license

The replay rejects a wrong source coefficient, omitted dirty cleanup,
unpaid frame increment, and illegal read frame. It also rejects a corrupted
source pin and exhibits the false positive from dropping the ordinary
consumer. Verification details and limits are in [VALIDATION.json](VALIDATION.json).

The #531 factory and mutable-source construction are by **icekylinx**, with
its credited #514/#507/#425/#433 ancestry. The #622 leaver-read K-triangle
construction and schedule are by **Jeremy Kothe / jeremykothe2** and the
credited **AtomScout** research work. **Chafik Boukhalfa / chafreaky** supplied
the selected #626 allocation; **eumemic** supplied #543's bit provider.
The native auditor credits icekylinx, **DreamingOfClouds** and the preceding
112-port transport work. **Jeremy Diviney's #646** provides the signed-root
triangle comparison; **Sreekanth Nair / higherbeing's #651** identifies the
related fixed-delivery obstruction. **Dominik Scholz's #571** packet-plane
floor motivated checking replacement work. None is asserted to have
reviewed this contribution.

Prepared by **Douglas R. Colkitt (@Mister-Meeseeks)** with substantial
**OpenAI Codex assistance** in research, implementation, verification and
writing. New files are under the repository's Apache-2.0 license. Original
source files, notices, `upstream/`, and the selected record are unchanged.
