# P104 cross-group collectors: 90 helpers for three corrected targets

Cross-incidence mixing removes two extra collectors without adding scalar
operations. Combined with the exact Y2-exclusive component of
[CubeJerry's PR2504](https://github.com/CrocSwap/integer-mult-bounds/pull/2504),
the full word uses **90 new dirty helper lifetimes, 517 ADDs and 810 ZERO-to-FULL
boundary rank units**. It corrects Y0/Y1/Y2 and restores every arbitrary dirty
input. No unrestricted minimum, complete supplier or new kappa is claimed.

This answers the cross-group-mixing handoff in
[PR2460](https://github.com/CrocSwap/integer-mult-bounds/pull/2460), whose sharp
94-helper bound assumes incidence-separated gathering. The new construction
changes that assumption. PR2504's late acquisition is retained and credited.
The separate 92-helper cross-only control isolates the new saving.

## Contract and sources

The original 4,058-event G/2 channel, original source/target paths, 72 arbitrary
dirty helpers and eight owned private-copy lifetimes are fixed. New helpers
start as independent arbitrary dirty inputs in ZERO, climb monotonically through
nested frames, and finish with their initial logical values in FULL. Correction
ADDs read new helpers and immutable original X values; no original G/Q/D/private
or target values are read. Targets receive only additive updates. The original
private-copy contract still includes nonzero discard and is not replaced here.

Let C=I-G/2 on the 104 ordered roots. Partition the first three correction rows'
source columns by incidence set S. PR2460 gathers each group's captured source
contributions in J_S=intersection(t in S) H_t. Groups {0,2}, {1,2} and {0,1,2}
have identical rows within each group, and use one, one and two extra dirty
collectors respectively. Source sets, rational coefficients and frame
intersections are independently reconstructed from the pinned root fixture.

Exact predecessors are PR2460 `a0030819c6d0e89e133cd3e52cc748035d58e3c7` and
PR2504 `9db4192bf3fd7f43c5f41ae040649067191682e0`. Their circuits and explanatory
READMEs are retained with Git blob/SHA256 pins in [PREDECESSORS.json](PREDECESSORS.json).
The original word and fixture are declared live inputs in [SOURCES.json](SOURCES.json).
Default replay imports no predecessor executable or builder.

## Cross-group construction and proof

Write T for the normalized source total of group {0,1,2}, B for {0,2}, and D for
{1,2}. Keep the two extra dirty helpers in J_012. The existing sum and fanout
produce three carriers whose source projection is T, with independent dirty
rows. Send one to J_02, one to J_12, and retain the third for Y2. The routes are
monotone: dim J_012=6, dim J_02=dim J_12=7, and each meeting frame is contained
in both corresponding dimension-eight target endpoints.

At J_02 gather B into its ordinary acquisition collector. On its complete
logical value b and the incoming carrier value t execute:

```
b += t
t -= b
```

This maps (b,t) to (b+t,-b), has determinant one, and has inverse
(u,v) -> (-v,u+v). Deliver b+t to Y0 and -t to Y2: the source projections are
B+T and B. At J_12 the analogous shear delivers D+T to Y1 and D to Y2.
Deliver the third T carrier to Y2. These groups therefore contribute
`(B+T, D+T, B+D+T)` to the three targets, exactly as required.

The T carriers are not free copies: their two extra independent dirty coordinates
remain charged and restored. Their independence also serves the pair-group
shears, eliminating the separate E02_2 and E12_2 collectors. The separated-group
lower bound is not contradicted because these groups now mix with the triple
group. No claim that this is a normal form or a global minimum is made.

Propagate all independent dirty basis rows through the actual gather/shear word.
At original cut 0 subtract each future delivered dirty row from its target, while
both have ZERO frames. The original channel never reads targets, so these offsets
reach the target endpoints unchanged. Cross-group helpers capture original X
values at cut 0, when their initial lines are available; X logical values remain
immutable throughout the original program.

After the original channel, deliver the collectors at the target frames and move
all new helpers to FULL. Reverse every gather/fanout/shear ADD at FULL, then
subtract every captured X contribution using original X values at FULL. This
restores all arbitrary dirty inputs. Transport changes the chart but not the
logical row, so reversing ADDs at the common final frame is the inverse logical
transformation. This proves arbitrary-input correctness of the finite framed
word; it does not rely on sampled initial states.

## Composition with the exact late-exclusive component

PR2504's actual exclusive sources are `{0,1,3,6,8,11,16,19,25,28,97,99}`. They
differ from the twelve sources whose first expanded X frames stay inside H2.
The verifier reconstructs both sets and checks the distinction. It does not
substitute PR2496's three Y2-only chains into this exclusive group.

Remove the twelve original exclusive helpers and all events touching them from
the cross-only word. Insert PR2504's ten helpers and every event touching them,
literally unchanged. Its shared helper reads X6 at cut 0, X1 at cut 669 and X0 at
cut 842; cuts count completed original events. Its other nine helpers capture
once. The helpers are disjoint from the cross-group roles. Initial Y2 dirty
compensation, endpoint delivery and FULL cleanup compose additively. Original X
values remain available at their exact pinned cuts.

The checker compares the entire retained component, boundary frames and route
metadata with PR2504. It separately compares the entire complement with the
cross-only word after exclusive-group removal. Full chronological replay checks
every frame and coefficient. No general assumption that separate local savings
always compose is used.

## Complete finite invoice

| Added quantity | PR2460 | PR2504 | Cross-only control | Combined word |
| --- | ---: | ---: | ---: | ---: |
| Dirty helper lifetimes | 94 | 92 | 92 | **90** |
| Scalar ADDs | 532 | 517 | 532 | **517** |
| Source reads, including cleanup | 180 | 180 | 180 | 180 |
| Nested transports | 287 | 283 | 283 | **279** |
| ZERO-to-FULL rank mass | 846 | 828 | 828 | **810** |

The new cross-group step saves exactly `2 H2 + 2 H7` against either corresponding
baseline: four transports and 18 rank units, with no extra ADDs. The combined
added profile is `146 H1 + 36 H2 + 7 H3 + H4 + 8 H5 + 40 H6 + 41 H7`.
The full word has rank mass 3,178 and 4,854 events. Its 370 independent inputs are
208 original data, 72 original dirty helpers and 90 new dirty helpers. All
136,900 endpoint coefficients check. Y0/Y1/Y2 become yt+xt; the other 101 targets
retain yt+(Gx)t/2. All source and dirty helper logical values restore.

These are common-chart transport ranks, **not hosted recursive excess costs or
a favorable completed moment**. Lifetimes are not simultaneous physical registers.
The ideal logical row-l1 maximum 106 and denominator bound 4 are not physical
precision results. Native phases/scalar-address work, backward orientation,
global owners/idle/residual children, physical precision/tape, all-size admission
and the remaining 101 corrections are open. No selected or frozen source changes.

## Evidence and reproduction

The sparse Fraction replay is adapted from PR2460. The separate dense dyadic
integer/binary-echelon interpreter is adapted from CubeJerry's PR2504; its
independent arithmetic is credited, not newly claimed. Both check every endpoint
coefficient. Eight primary semantic faults and two separate branch-sign faults
reject; equivalent frame bases pass. Regeneration compares both complete
artifacts. Export tests cover missing/corrupted evidence, source drift and
overwrite refusal.

Standard-library Python 3.12. Default replay is read-only, Git-free and
network-free; `--out` only writes a new caller-selected file.

```sh
python3.12 -I -O -B research/p104-cross-group-collectors/verify.py --regenerate
python3.12 -I -O -B research/p104-cross-group-collectors/independent.py
python3.12 scripts/research_package.py --package research/p104-cross-group-collectors
```

Local author validation uses CPython 3.12.7 on Windows AMD64. Hosted CI, a proof
assistant, human independent review and selected-frontier cold replay are not
claimed. Current review status and commands are in [TASK.json](TASK.json).

## Open next questions

Can a broader cross-incidence network reduce this 90-helper construction further?
First state allowed source acquisitions/frame contacts and test one concrete
network. Neither the separated 94 theorem nor the isolated exclusive 10 theorem
proves a global 90 minimum.

Can these exact 279 new transports receive phase-correct native recipes and paid
scalar/address operations? Compile this literal word first; a native certificate
of a different P104 word does not automatically admit it. A completed 104-target
construction and global owner/moment budget remain later gates.

## Credit

Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
PR2460/ywz65 supplies the three-target construction and cross-group handoff;
CubeJerry/PR2504 supplies the exact late-exclusive component, corrected source-set
distinction and dense interpreter. Credit Ross Richardson/PR2445's two-target
shear and dirty compensation; commdata2338/PR2393, Hiroki Kumazaki/PR2353,
Philippe Van Velzen, Rohan Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940,
Josie Elliston/PR1071, Ali Romman/PR1125 and the retained geometry/native/compiler
lineage. Predecessor READMEs and frozen notices remain unchanged.
