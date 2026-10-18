# Fixed eight-array block decoders have no recursive moment headroom

**Definitive dead end for the declared block class. No new kappa is claimed.**

The twelve late helper blocks in the selected complex word already attain the
minimum recursive moment over every finite rational scalar program on their
eight arrays with the retained input frames, late output frames, and dirty
helper endpoint contract. The result permits arbitrary gate order and length,
repeated source reads, information splitting, and changed helper coordinates.
It includes fusion with all later work inside each block. The retained provider
uses one canonical word for both orientations; the backward program is its
same-order inverse-transpose dual with the same frame climbs.

For a block with four low helpers and common frame dimension u, the exact
minimum at every 0<s<1 is:

| Common dimension | Minimum complete helper moment | Native profile |
| --- | --- | --- |
| 4 | 24 + 8*2^s + 4*3^s | H1=24, H2=8, H3=4 |
| 5 | 32 + 4*4^s | H1=32, H4=4 |

[PROOF.md](PROOF.md) proves the bound without a program-length bound. Its input
barrier does not assume read-once access. Its retirement argument accounts for
outputs already written before a helper jumps directly to rank nine. The bound
covers the whole helper path, including completion to rank nine.

The complete complex supplier moment cannot decrease for any exponent in its
range. The copied centres, other local paths, array volumes, owner assembly,
endpoint law, and bit supplier stay fixed. Thus the feasible region of the
complete outer recipe cannot expand. This is stronger than a scalar gate count
or a bound on one compulsory visit to the common frame.

## Scope

Each block uses its existing eight physical arrays. All sixteen boundary values
(eight helpers and eight external inputs) are independent. The four output
ports retain their late entry frames and distinct final hyperplanes. Inputs
are read-only and outputs are write-only additive ports. Helpers use rational
scalar additions and nonzero scalings at common frames. Frames grow by
inclusion. Each rank-r transport is charged as a rank-r recursive child.

No extra array, target scratch, frame descent, changed centre, cross-block
coding, or output access before the retained late entry frame is included.
An independently redesigned backward supplier with a different interface is
also outside the class. This is a declared interface restriction, not a claim that those routes are
impossible. Phase conditions can only reduce the permitted program class; the
lower bound grants every monotone common frame.

The investigation considered product-transform fusion, a new support-masked
block decoder, and joint exact factorization across the existing correction
seam. The third route was selected because it had a concrete eight-array
interface and could change the full recursive bill. The declared class is
recorded in [TASK.json](TASK.json). It was not narrowed to a finite gate search.

## Source and finite evidence

Base commit: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
[INPUTS.json](INPUTS.json) pins the three native word files by source commit,
path, Git blob, compressed SHA256, and decompressed SHA256.

| Native word | Blocks with u=4 / u=5 | Total optimal helper profile |
| --- | --- | --- |
| Selected PR1094 local word | 7 / 5 | H1=328, H2=56, H3=28, H4=20 |
| PR1319 base provider | 10 / 2 | H1=304, H2=80, H3=40, H4=8 |
| PR1319 extra provider | 11 / 1 | H1=296, H2=88, H3=44, H4=4 |

The selected local word is the retained member of the PR1042 replay archive;
PR1094 changes its global assembly. The selected conditional outer kappa at the
base is 0.001672660197076918. The pending PR1319 source at
`603defe58aac018c6a8457840481390a15846fe4` reports 0.001676855229071321.
These values identify the applicable baselines. This package does not adopt a
pending frontier or rerun either full construction.

The retained orientation emitter is pinned in SOURCES.json. The selected
emitted program pair is pinned in INPUTS.json. The checker verifies all 3486
climb events agree, every non-centre scalar has the inverse-transpose form,
and the complete paid profiles agree. The controller corollary uses this
coupled orientation contract.

The verifier extracts every input frame, output entry frame, endpoint cap,
and rational output matrix from the emitted words. For each block it checks
all 255 nonempty input subsets. Rational elimination is checked by exact Gram
minors; binary pivot calculations are checked by enumerated spans. Each of the
36 interfaces has a nonzero 16-by-16 prefix minor, checked by backward pullback
and a separate forward replay. Each minor uses eight original source columns
and the same eight dirty helper columns; it does not require free targets.
The twelve failure controls reject a changed
helper correction, a duplicated external input, a missing full helper end, and
a corrupted input file in each source.

[CERTIFICATE.json](CERTIFICATE.json) contains the extracted premises, all
independence minors, and complete helper profiles. The finite checks establish
the source-specific hypotheses of the proof. They are not a formal proof of
the arbitrary-length theorem or the integer multiplication theorem.

## Reproduce

From the repository root, with Python 3.12 or later and no third-party packages:

```sh
python3 -I -B research/complex-block-rank-optimum/verify.py
```

Expected result:

```text
PASS_FIXED_BLOCK_MOMENT_PREMISES blocks=36 subsets=9180 minors=36 controls=12
```

The verifier checks the stored certificate without writing files. Use
`--write-certificate` only to regenerate this package's certificate.

The registered metadata check is:

```sh
python3 scripts/research_package.py --package research/complex-block-rank-optimum --check-only
```

The generic replay hook uses Python 3.12. Local verification used Python 3.14.7,
one process, and no native solver. No full selected-construction cold replay,
new all-size realization, or Lean proof is claimed.

## Failed attempt and stopping rule

An initial stronger claim, that no kernel can retire below rank eight, is
false. Some input supports span rank seven and have nonzero kernel. The final
proof retains those supports. A backward perturbation shows that a retiring
helper has no earlier or later output response. The exact frame condition
then forces a rank-six stop before retirement. Its full cost equals the
retained rank-eight route. The checker requires that this case is present.

The experiment was deterministic. Its finite domain was all input subsets in
all twelve blocks of each of three pinned words. No random seed or uncompleted
search is involved. Work stopped when the all-order proof covered this whole
class and the native profiles attained its complete moment bound.

## Open next questions

A block with earlier output access or communication between blocks is outside
this theorem. Such a change could escape the fixed interface. The first useful
step is to specify the changed physical arrays, exact port times, and complete
native bill before searching for a factorization. The unresolved requirement
is an admitted interface with better complete cost, not more scalar words in
the class proved optimal here. See the structured question in TASK.json.

## Credit

Thomas DiFiore's helper-basis screen in Discussion 1167, source commit
`3e476186e261a531dc12c64a21bb15ac2a0736f8` in `tomdif/integer-mult-bounds`,
identified the twelve correction blocks, the full dependency, and the open
question of fusion with later work. This proof closes that question for the
fixed late eight-array interface. It does not repackage the 10,428 permanent
and 6,544 temporary basis-change experiments as an exhaustive theorem.

Douglas Colkitt's PR1240 supplies the fixed-word packing ceiling and the
optimistic rank-eight mass screen. PR679's selector-volume obstruction and
PR717's fixed-order frame obstruction define different restrictions. This
result changes gate order and length inside one existing array block and uses
no selector or doubled volume. A final overlap refresh read the 60 most
recently updated open PR bodies, covering the full session delta. New PR1389
and PR1399 concern masked E-graph rigidity; PR1368 concerns R439 bit blocks.
They do not prove this complete complex block moment result. PR1407 keeps the
selected local word and changes only owner hosting.

The selected construction is due to Rohan Arun's PR1094, Jeremy Kothe's PR1087,
and the cumulative k8/slot/T16 lineage. PR1319 and its PR1297/PR1286 provider
words are due to Rohan Arun, with Jeremy Kothe's PR1274 helper-donor work,
Jeremy Diviney's mixed-provider work, and the other credits retained in
[notices](notices). The unchanged bit supplier is PR589 on PR555.

Prepared by Ali Romman with substantial OpenAI Codex assistance in the proof,
implementation, verification, and documentation. New work is Apache-2.0.
Inherited source notices and mathematical assumptions are retained.
