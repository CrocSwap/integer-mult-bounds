# One-buffer sequential CRT tail switches

This contribution was produced by Nick Petalas. A new sequential staging
construction uses one suffix-slice buffer and at most `19V/2` payload actions
for the complete-fiber controlled switch. Its exact bill is `6V+7SB`, where
`S=2^H R` is a slice and `B` is the number of switched prefixes. The input is
preserved, the buffer is erased, and all payload heads return to their origins.
There is exactly one control preparation per prefix.

The cited two-buffer construction in ToikY's
[PR4187](https://github.com/CrocSwap/integer-mult-bounds/pull/4187), head
`45fc0750436ae5cc14b95fba81c030a3d7df3412`, uses `13V` payload actions and
`2S` staging cells. The new policy saves at least `7V/2` such actions and
uses `S` staging cells. On a switched prefix, buffer the first slice, send
its second slice directly to output, then drain and erase the buffer.
Unswitched prefixes copy directly. No optimality claim is made.

Claim type: scoped written all-size construction with exact finite
corroboration. [PROOF.md](PROOF.md) gives the endpoint, complete payload
invoice, transported-target contract and uniform overhead. This is a
physical traffic improvement under stated caller premises, with no new
kappa or selected-frontier change. The predecessor's construction and costs
are cited premises, not audit or replay targets.

## Reproduce

From the repository root, with the available CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/crt-tail-single-buffer/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/crt-tail-single-buffer/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/crt-tail-single-buffer
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/crt-tail-single-buffer --check-source-history
```

Other hosts can substitute their CPython 3.12 path. Standard library only.
Expected marker: `PASS_CRT_TAIL_SINGLE_BUFFER`. Verification writes no files
and generates a JSON receipt bound to every package-file hash.

The finite checks cover 23,786 cases, 787,968 forward payload-bit instances
and 6,099,591 forward physical actions. Each case also executes the inverse.
Every Boolean control table is included when the fiber count is at most
eight. All payloads are included through volume eight; basis payloads cover
all coordinates through volume 32. Other cases use specified patterns.
Larger cases reach `L=12`, `R=16`, with suffix widths zero and ten.
This is not an exhaustive census at those larger dimensions.

A separate sparse interpreter replays every forward read, write and unit
move against an address-wise endpoint oracle. Checks include source
preservation, blank scratch, returned heads, preparations and exact counts.
Fifteen negative controls reject invalid domains and incomplete inputs,
unreturned heads, omitted erasure, source writes, false read transcripts and
stale controls. No predecessor executable or scientific suite is imported.
The written proof covers all positive `L,R` and `0<=H<L` independently of
these finite tests.

## Limits

The exact bill counts payload reads, writes and unit moves. Marker visits,
encoded counters and uniform control preparation are separately charged in
the written bound. The Python payload interpreter does not execute their
finite-state lowering. The ordinary coordinate exchange is also a cited
paid contract. The new policy reduces middle-stage scratch, not the complete
caller's total asymptotic workspace.

The actual uniform numerical evaluator, full reservoir placement, ordinary
callee, complete CRT invoice, numerical precision and outer multiplication
join remain unrun obligations. Incomplete sparse fibers are outside scope.
All five selected framework assumptions remain. No complete rounded
multiplier, formal-kernel proof, independent human review, selected cold
replay, Lean or Docker run is claimed.

## Open next questions

- Replace the remaining buffer with a source-retreat schedule and derive its
  complete head-travel and encoded-control bill. This package supplies no
  optimum over schedules.
- Join the changed staging policy to one actual transported CRT layer,
  including its evaluator, coordinate exchanges and intermediate erasure.
  Those caller implementations remain external premises.

[TASK.json](TASK.json) gives the scope change, blockers and first steps.
Research stopped at this first verified strict improvement.

## Credit and overlap

Credit ToikY / PR4187 for the explicit two-slice lowering and complete-fiber
interface; Cinna Davis / PR4100 for the original last-K construction and
amortization; Hiroki KUMAZAKI / PR4174 for reservoir/split-coordinate context;
Vlado Vojdanovski, Jose Manuel and the retained physical/compiler lineage.
Buffering and sequential copying are classical. No worldwide priority claim
is made. No predecessor code or credit line is changed. New files are
Apache-2.0.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19373391)
records the changed contract. Canonical main at intake is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected
PR6030. Live handoffs, active Discussions, open/account PRs, main README and
merged object/formula searches and local reservations were checked. The
cached helper reports 555 open PRs and 6,596 Discussion records with complete
remote pagination, but only 139 of 8,917 local notes searched. Main searches
supplement that sparse coverage; arbitrary diffs and unpublished work remain
unknown. No lack of matches is treated as a novelty certificate.

Related open work includes PR4187 itself, PR4192's encoded Beneš compiler
and PR6592's matched-record stack parking. The already merged PR6185 supplies
an arbitrary-bit Sandwich wrapper. Only PR4187 studies this complete-fiber
payload stage. The others compute different quantities, and no extra
computation compared their numbers.

## Local validation

Both warning-strict CPython 3.12.15 modes pass with identical generated
receipts. Separately timed commands took 3.31 and 3.25 seconds against
120-second limits; these are local check durations, not a runtime comparison.
The registered package runner and metadata/source-pin checks pass. Hosted
CI and committed-byte/source-history/export evidence are recorded in the PR.
