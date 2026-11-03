# Resident SCALE 2 without a whole-cache flush

This scoped circuit construction and written traffic proof was produced by
Nick Petalas. It answers Ali Romman's released same-ribbon question in
[PR6530](https://github.com/CrocSwap/integer-mult-bounds/pull/6530).

A resident width-64 complex field can be doubled on its existing ribbon for
exactly **3284D-2** reads, writes and unit head moves. The other resident field,
both zero owner slots, the owner head and the carry tape remain unchanged.
There is no additional payload workspace. Signed components must satisfy the
retained exact-doubling no-overflow condition.

The retained source local circuit costs 9840D before staging. A complete
comparison for fields 256/257, with identical entry and exit, reduces the best
of four explicit flush/scale/reacquire paths from 17776D-282 to 3284D-2.
The saving is **14492D-280** for every positive D. At D=1 it is 14212 operations.
This is an exact operation count under the predecessor's tape tariff, not a
wall-clock speedup or a new complete caller bill.

The new schedule rotates each record through neighboring CNOT swaps, then
clears the duplicated sign bit. Its inverse reverses the same gates.
[PROOF.md](PROOF.md) proves the bit map, ownership, all-D count and the precise
comparison class. [ribbon.py](ribbon.py) emits and executes the physical route.
The implementation bounds W at 64 and D at 64; the written construction holds
for arbitrary finite W >= 2 and positive D.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/resident-scale-ribbon/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/resident-scale-ribbon/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/resident-scale-ribbon
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/resident-scale-ribbon --check-source-history
```

Both registered commands are read-only. The optional `--receipt /absolute/path`
writes a generated result bound to all fifteen package-file hashes. No receipt
is handwritten. Expected final line: `PASS_RESIDENT_SCALE_RIBBON`.

The complete finite replay checks 129 source/new basis columns, 1364 exhaustive
legal small-width complex pairs with exact inverses, 252 arbitrary-bit
width/dimension roundtrips with exact traffic, and 24 full physical comparison
paths with all tape cells and heads checked. Seven invalid-domain/instruction
controls reject, and three semantic controls distinguish sign clearing,
rotation direction and the CNOT swap identity. The source's compiler is used
only to obtain this comparison circuit; its whole-word verifier and policy
optimizer are not run. No predecessor result is claimed as a new audit.

The selected word is a declared source-pinned input. The exact three-event
window at indices 10481..10483 needs the two fields on both sides of SCALE.
This establishes a relevant legal local contract, not a globally spliced
replacement for the source policy. ORIGINS.json binds the retained external
source bytes and their original Git blobs at PR6530's exact head. Those
committed copies make replay independent of the unmerged source branch's
ancestry; full predecessor history is not claimed.

## Limits

Only SCALE 2 is supplied. The complete caller policy is not reoptimized.
Initial allocation, native/reset implementation, uniform encoded-D control,
numerical admission, stock, full supplier funding and outer transfer remain
open. A component improvement does not raise kappa or change the selected
frontier. The five selected framework assumptions remain. Independent human
and formal proof-kernel review are unclaimed. Lean, Docker and a selected
supplier cold replay are outside scope.

## Open next questions

The structured questions in [TASK.json](TASK.json) concern integrating this
exact edge into a complete certified policy, then one different SCALE
coefficient with its full transition charged. Neither is reserved here.

## Credit

Ali Romman supplies PR6530's exclusive-owner contract, released question and
comparison policy, PR6527's staging and PR6513/6511's physical scalar lineage.
Credit Nick Petalas for the retained scalar circuits, Sagar Thakrar / PR3241,
DreamingOfClouds / PR6030 and the retained native, owner, precision and compiler
authors. Classical adjacent swaps, CNOT identities and two's-complement
arithmetic retain their usual credit. Original source credit lines are retained
unchanged in inputs. This contribution is under Apache-2.0.

The replay-runtime card is explicitly changed to physical operation count.
The first verified resident transition improvement ended the construction work.
