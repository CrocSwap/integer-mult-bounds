# Independent V45 frame and ledger audit

Status: scoped independent audit of PR #2979, source head
`be191346391661f4d35fc0d1508d0a6029572576`. The worktree base is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6. This package
does not change the selected frontier or claim a new κ.

The live overlap check found PR #3823, which records the V45 triple
intersection, and PR #3841, which records the printed V45 margin ladder and
the five stage-one group prices. This audit keeps those finite facts as
cross-checks. Its separate coverage is an independent implementation of frame
application and both provider child-rank reports, all 15 endpoint subsets,
the owner schedule/fill checks, and the complete physical invoice. It does not
claim that the archived search-time pricing witness is independently derived.

## Question and method

For PR #2979's V45 group, do the four shared rank-seven end frames fit the
recorded gates, does a one-helper control lose under the stated local pricing
model, and do the resulting child-rank and physical totals reconcile through
both provider words?

`verify.py` is a Python standard-library-only implementation. It hashes every
file in the pinned #2979 source package, rebuilds the F2 frame walk from the
compressed parent/final words, applies the declared frame edits, and checks the
rank histogram and width inventory. It independently reconstructs source
windows and checks each serialized owner role for chronology, same-call family
collisions, bin capacity and overlapping offsets. It imports no code from the
source package and does not run that package's registered verifier or owner
engine.

Run:

```sh
python3 -B research/independent-v45-ledger-audit/verify.py
```

Expected status: `PASS_INDEPENDENT_V45_FRAME_COST_AND_PHYSICAL_LEDGER`.

## Findings

The shared space is
`W = <256,128,64,35,16,11,5> = E_7 ∩ E_42 ∩ E_45`. It has rank 7 because
`7 xor 42 = 45`, so the three normals impose two independent conditions. Each
of helpers 249, 251, 265 and 267 has an eight-dimensional parent end frame
containing W. The four endpoints become W, and 29 of the 139 recorded gate
frame edits touch this group. Recomputed parent and complete stage-one reports
agree with both provider word records. The gate/operator/scalar entries and
cleanup arrays stay fixed during stage one. Five semantic controls reject a
wrong W, a missing partner refit, a changed gate signature, a duplicate helper
role and an over-capacity role.

The independently recounted stage-one profile is `{1:2430, 2:722, 3:236,
4:102, 5:18, 8:8}`. Its exact weighted delta is `-46,150,994` units; with 22
freed width units at break-even `2,091,300`, the complete stage-one margin is
`+142,394`. The five source group prices sum exactly to this independently
recounted total.

The pinned V45 group price is `-8,388,172`, with margin `+22,972`. Holding
the complete stage-one gate edits fixed, independently toggling its four
endpoint frames changes the child-profile cost by `-8,466,684`, exactly four
times the rank-one tariff `2,116,671`. The difference implies a shared
partner-refit charge of `+78,512` in the source price decomposition. The audit
rebuilds all 15 nonempty endpoint-subset profiles in the complete stage-one
word; the single-helper control is a direct profile variant, but its group
margin uses that source-derived shared refit charge. The subset formula is
then

```text
margin(k) = k * (2,116,671 - 2,091,300) - 78,512
          = k * 25,371 - 78,512
```

It gives margins `-53,141`, `-27,770`, `-2,399` and `+22,972` for one through
four lowered endpoints. The audit checks the profile variants and all 15
rows against the pinned source table. An attempted V45-only gate refit on the
parent is not a valid independent decomposition: its frame walk becomes
nonmonotone at register 169. The archive does not include the frame-search
optimizer, so this audit does not independently derive the V45 group price or
establish that the chosen refit is globally optimal.

The final child-rank ledger independently agrees for both providers
(`gauge44` and `extra`):

| Rank | Per-provider local children | Full 666-call profile, including idle children |
|---:|---:|---:|
| 1 | 2,445 | 1,645,680 |
| 2 | 706 | 470,196 |
| 3 | 232 | 159,468 |
| 4 | 108 | 71,928 |
| 5 | 18 | 13,716 |
| 8 | 8 | 5,328 |
| 48 | 0 | 28,190 |

The final width inventory for each provider is `{4:26, 5:2, 6:16, 7:52,
8:99, 9:213}`. Relative to the PR2942 parent, the complete local-profile cost
delta is `-56,726,747`, rank mass falls by 27, and the recorded total margin
reconciles to `+261,647`.

The serialized owner ledger has 666 calls and 271,728 helper roles, with 416
calls dispatched to `extra` and 250 to `gauge44`. The independent schedule and
family check finds 54,200 distinct assigned family IDs within the 66,304
reserved live-family stock (`74 * 896`). The full physical invoice is:

```text
66,304 live-family stock
+   408 helpers
+     8 centres
+    91 private cleanup buffers
+     2 guards (residual in the pinned owner invoice)
= 66,813 physical families
```

The two provider records have the same independently rebuilt profile and
width inventory. The source-selected bit/complex bounds, the numerical cap
root and the outer release are not recalculated here.

## Open next questions

Can the V45 group price and single-helper control be rederived without the
search-time group price row while preserving a valid monotone frame walk?
First find a valid decomposition of the V45 edits from the complete 139-edit
stage-one word, then compare its child-profile costs with the source table.
The straightforward isolated V45 gate-edit subset fails monotonicity at
register 169, and the archive does not include the optimizer witness.

## Scope limits

The archived group-price table is search-time evidence from a frame solver
that is not present in the package. The audit does not independently derive
the V45 group price or the `78,512` shared refit charge. It confirms the
complete stage-one profile, constructs valid endpoint-subset profiles under
the complete gate refit, and checks their listed margins against the pinned
price table. An isolated gate-edit decomposition is nonmonotone, and optimizer
completeness remains open.

This is not a fresh two-sided algebra replay, native-provider replay, outer
proof, supplier admission or multiplication theorem. Do not treat the finite
frame and ledger result as a new κ.

Credit and predecessor attribution remain with Marius-Paul Dumitrean/PR #2979,
Mason Hale/PR #2917, Jeremy Kothe/PR #2957, PR #2942 and their cited source
lineage. This scoped audit was prepared with model assistance; no independent
human or formal-kernel review is claimed.
