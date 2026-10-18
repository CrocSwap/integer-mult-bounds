# Selected cross-call cycles cannot coalesce idle ranks 0,1,7 into 0,0,8

**Complete exclusion for one fixed-map rank transition; no new supplier or κ.**

On the selected PR1094 owner map, 21,886 simultaneous directed three-role
cycles have the proposed remainder change. Every one violates a strict
source-event window. This remains true if active-pair and per-call family
restrictions are relaxed. It does not exclude other remainder changes,
longer paths, changed call orders, or a global packing improvement.

## Domain and exact obstruction

Keep the selected scalar word, all helper widths, 144 calls, call order,
actual source-event windows and occupied-prefix hosting model fixed. Three
existing whole-helper roles rotate among three distinct occupied bins
A→B→C→A. At least two invocation times must be represented. The old free-rank
multiset is `{0,1,7}` and the new one must be `{0,0,8}`. Anchor A at the unique
old-slack-7 bin; both directed orientations are included, cyclic rotations
counted once. “Slack 7” means seven unused coordinates, not an empty bin.

For old slacks `(a,b,c)` and outgoing widths `(x,y,z)`, the new slacks are
`(a+x-z, b+y-x, c+z-y)`. The source map supports exactly two type patterns
with the required target, where a type is `(own-bin slack, outgoing width)`:

| A,B,C types | Cycles | Constant forbidden landing |
|---|---:|---|
| `(7,8), (0,8), (1,7)` | 17,567 | C→A: event 181 is outside `(255,430)` |
| `(7,8), (1,7), (0,7)` | 4,319 | A→B: event 417 is outside `(-1,208)` |

There is exactly one role of type `(7,8)`: `(stage,replica,helper)=(7,14,296)`,
owner bin `(13,15,14)`, event position 417. There is exactly one role of
type `(1,7)`: `(1,15,226)`, bin `(11,8,103)`, event position 181. The other
members are the 17,567 type `(0,8)` or 4,319 type `(0,7)` roles. The fixed
forbidden landing therefore rejects each entire row independently of the
third role. The two fixed roles belong to different calls, so none of these
arithmetic candidates is removed by the same-call scope restriction.

The unused coordinates could reduce cost if the change were legal:
with `p=1-a` in `(0,1)`, strict concavity gives `8^p < 1^p+7^p`.
All local charges stay fixed, so the complete modeled moment delta would be
`(8^p-1^p-7^p)/(14336*73^p)`. This census realizes none of that potential
gain because the landings are illegal. It is not a new general 3-cycle method.

## Evidence, independence and controls

[RESULT.json](RESULT.json) includes the two supported class rows, the
constant-leg proof objects, baseline owner recount, source hashes and complete
supplier pricing. Two enumeration methods agree:

- The primary implementation exhausts actual width/slack types, counts all
  role multiplicities, then performs an indexed strict-window join. A
  simultaneous family update removes all vacated families at each call
  before inserting the incoming roles; it never substitutes sequential
  relocation legality for a cycle.
- A separately written role-first enumeration tries all three possible
  placements of the target rank 8. It solves the incoming-width equation,
  materializes every supported triple, and compares each literal event
  position directly to its destination window. It calls neither the primary
  transfer/classification helper nor its landing predicate. Its complete
  candidate-ID list has SHA256
  `65b6437819f57f90f1d2d076bc96638b1d44302ef431462056fc136d497cf1dd`.
  All three windows pass on zero candidates. The digest is a compact receipt;
  acceptance depends on the regenerated exact census and inequalities.

Both methods share source decoding and Josie Elliston's PR1091 geometry and
baseline audit. This is algorithmically different enumeration, not a
code-disjoint reimplementation of the entire source geometry or independent
human review. Windows are rebuilt from actual source events and checked
against PLAN by the unchanged inherited auditor. All eleven inherited owner
mutation controls run.

Six local synthetic controls cover an admitted `{7,1,0}->{8,0,0}` toy cycle,
a same-call vacated family, an unvacated-family collision, the same-call scope
restriction, a blocked last-leg window, and an indexed/direct toy-triple
comparison with two possible third roles. The toy gain is not a physical
source witness. CLI tests also reject an omitted-candidate receipt and an
integer/float count alias. Receipts use type-preserving canonical JSON.
Deadline regressions reject an over-budget census even when every first
landing is blocked or the role set is empty. The deadline covers setup,
skipped branches and final return; timeout is never recorded as an exclusion.

## Both supplier budgets and the packing cap

The complete source profiles are unchanged. The pinned exact rational
calculator checks strict moment acceptance at both retained endpoints and
strict rejection at the next `10^-24` tick:

| Supplier | Endpoint | Rank mass / deficit |
|---|---|---|
| Complex | `67018507072324140917/40000000000000000000000` | 1,041,408 / 5,120 |
| Bit | `1733427039589844234749/10^24` | 1,808,352 / 10,272 |

Bit pricing includes the inherited `10^-16` bad-residue envelope of
`32*m^2` rank-one fallback calls per paid child. Neither this surcharge nor
any physical bill is reduced. Complex remains the binding side. These are
pricing checks of the pinned profile model, not supplier or full cold replays.

The required `ceiling(local,73,896,9,64)` call on local profile
`{1:2412,2:418,3:432,4:142,5:82,8:8}` gives
`a < 0.001690054109089`, balanced planning cap `κ < 0.001687202646`.
The fraction of remaining packing headroom realized by this domain is **0**.
The newer [fixed-route indivisibility bound](../fixed-route-indivisible-idle-mass/README.md)
is stronger for this unchanged-route model (`a < 0.001681977435447`,
planning κ about 0.00167915314); it is credited, not newly replayed or claimed
sharp here. Zero gain also realizes zero of that tighter headroom.

## Reproduce and assignment

Python 3.12, standard library, repository root:

```sh
python3 -I -O -B research/selected-crosscall-rank8-cycle/verify.py
python3 -I -O -B research/selected-crosscall-rank8-cycle/test_verify.py
python3.12 -B scripts/research_package.py --package research/selected-crosscall-rank8-cycle --check-only
python3.12 -B scripts/research_package.py --package research/selected-crosscall-rank8-cycle
```

Expected primary status:

```text
PASS_SELECTED_CROSSCALL_RANK8_CYCLE_OBSTRUCTION candidates=21886 all_window_blocked direct_crosscheck=PASS owner_controls=11 new_kappa=NO
```

Default replay is read-only. `--write NEW_PATH` refuses an existing path;
`--probe` runs the primary census without pricing, the direct cross-check or
receipt validation. Test scratch directories are scoped to the package and
removed automatically. No dependencies or native builds are needed.

Track `incumbent-optimization`, card `selected-packing`, nonce
`3474c3e21150f5db2b291dfc2989aac6`, catalogue key `2eb6f6918b10e182033b`,
priority revision4, base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
Scope was refined to this precise cross-call transition, approved before
implementation, recorded locally before computation, and claimed at
https://github.com/CrocSwap/integer-mult-bounds/discussions/1332#discussioncomment-18933588.
The prescribed baseline binding check passed. Source Git blobs and SHA256
pins are in [SOURCES.json](SOURCES.json); detailed scope/overlap is in
[TASK.json](TASK.json). The five-minute first-probe budget was not exhausted;
there was no scope pivot or randomized optimizer search.

## Overlap and limits

This takes the cross-call handoff of
https://github.com/CrocSwap/integer-mult-bounds/pull/1873 (same-call 3-cycles),
closing only one rank-transition slice. It is distinct from
https://github.com/CrocSwap/integer-mult-bounds/pull/1790 (2-swaps),
https://github.com/CrocSwap/integer-mult-bounds/pull/1617 (complete
neutral-then-strict 2-relocations), and
https://github.com/CrocSwap/integer-mult-bounds/pull/1407 (longer sequential
paths). https://github.com/CrocSwap/integer-mult-bounds/pull/1154 has a positive
3-cycle on a different word and owner map. Fresh text-based overlap plus
live owning heads found no matching cross-call census; no-match does not
prove novelty.

## Open next questions

Can a different supported rank transition admit a
legal cross-call 3-cycle on the original map? Enumerate the remaining
capacity-feasible type patterns touching a slack-7 bin (for example old
slacks involving rank3), classify exact moment differences, and only then
join windows/families. The blocker is that 3-component transitions need not
be ordered by majorization; the simple two-component concavity sign rule
does not decide every case. This package supplies no such larger census.

There is no global optimum claim, modified source map, native/controller
rebuild, physical invoice, supplier adoption, full selected cold replay,
outer assembly, Lean proof or κ change. All inherited all-size/compiler,
realization, hosting, precision/tape, analytic and bit H1–H5 obligations remain.
No attaining source witness exists in this domain, so no modified-map
admission is claimed. Frozen inputs and the selected record are untouched.

## Credit

Rohan Arun's PR1094 supplies the selected packing, retaining Jeremy Kothe's
mutable-leaver and Hao Yan's controller lineage. Josie Elliston's PR1091
supplies the unchanged independent owner/event audit. The PR1790 swap
fixture and PR1873 same-call census supply the immediate extension context;
Arham Tahir's one-relocation work, PR1617, PR1819, PR1407 and the other cited
predecessors keep their separate contributions. Douglas Colkitt's PR1240
supplies the ceiling engine; PR1012 supplies the coverage law; PR1847
supplies the stronger fixed-route context. The bit source retains the
PR589/PR555 and earlier attribution. No predecessor files are copied or edited.

Prepared by **Aaron Wang / navinor, with help from chatgpt**, including
research, code, writing and separate read-only AI review. New work Apache-2.0;
no independent human or formal-kernel review claimed.
