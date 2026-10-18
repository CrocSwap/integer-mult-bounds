# Independent audit of the four compensation-kernel lifts

This checks the changed local words against the two immutable PR2833 words at commit `e9307b48d7d1b690939935ecef0f8e524e6d92f4`. It imports no construction, inherited audit, or repository modules. Credit for the base word and dirt-entry mechanism remains with Jeremy Kothe / PR2833 and the lineage credited there. The four-group construction is the separate producer's work; this audit independently checks its algebra, frames and cleanup.

Both providers pass 68 named checks, including the original 65 checks and additional source geometry, key-set and input-immutability checks. Python `-O`/`-OO` is explicitly rejected before input access because the frame ledger also uses assertions. `OPTIMIZATION-REJECTION.json` records that test. Earlier executed single-group and four-group checker files and receipts were retained outside this portable directory.

## Algebra and orientation of the compensation equation

For a group ordered as `(q0,q1,q2,q3)`, let `z` be the column vector of its four independent original dirty helper values. The inserted A gates produce the same A output as the original A word started with `S z`, where

```
S = [[ 1, 0, 0, 0],
     [ 1, 1, 0, 0],
     [-1, 0, 1, 0],
     [-1, 0, 1, 1]].
```

Thus the transformed dirty inputs are `(z0, z1+z0, z2-z0, z3+z2-z0)`. The checker establishes `A_new = A_old S` for every one of the 704 formal output rows, using exact rational coefficients and independent noncommuting symbols for the warp operators. Of these slots, 632 are live independent inputs and 72 removed slots remain untouched identities. No dirty input is assumed zero. The source partners that reconstruct raw dirt are also independent inputs.

`S` is lower triangular with diagonal entries1, so it is invertible. Let `C` map original helper dirt to the initial target compensation. Its four columns obey `C*(1,1,-1,-1)^T=0`. The required new compensation is **`C_new=C S`**, not `C S^-1`: the changed A word consumes the transformed dirty inputs `S z`, so its target dirt response is transformed by the same right multiplication. The first column of `C S` is zero; the third is old column3 plus old column4; the other two remain their old columns. This is exactly the producer's removal of compensation reads from q0 and addition of old q3 compensation to q2. The checker verifies this equation across all112 target rows, not just the displayed nonzero supports, then independently replays the complete program.

| Group order | Raised entrance | Partner frame intersection |
| --- | --- | --- |
| 478,479,490,491 | 478 | span(25) |
| 460,461,468,469 | 460 | span(7) |
| 462,463,470,471 | 462 | span(7) |
| 480,481,492,493 | 480 | span(25) |

Each compensation block has exact rational rank3 and the stated one-dimensional kernel. Both the four operand supports and the four compensation target supports are pairwise disjoint. The combined compensation matrix has rank12 and nullity4. These facts justify composition for these groups; they do not establish optimality over other rewrites or boundary changes.

## Cleanup and frame cost

The audit independently reconstructs cleanup by reversing and inverting the changed non-target forward word, excluding the inherited84-event prelude and target writes. It independently checks the private-buffer remapping against the unchanged72 restored helpers. Forward and dual free-operator replay both yield the required endpoint on every formal register, with every private buffer zero. This proves arbitrary-dirty linear/operator endpoint behavior; it does not itself prove Clifford phase or Gaussian-product identities.

The exact GF(2) frame ledger checks monotonicity, warp endpoints, target and centre cut pins, final frames and ordered helper widths. Only eight helper climb profiles change: each q0 contributes `H1-H2`, and each q2 contributes `2H1-H2`. Therefore

`local profile delta = 12 H1 - 8 H2`.

Only ordered helper widths460,462,478,480 change, each from9 to8. The resulting local profile is `{1:2394,2:642,3:266,4:128,5:26,8:8}`. The complete width histogram is `{4:26,5:2,7:62,8:84,9:234}`. The reconstruction adds20 A primitives and20 inverse-cleanup primitives. Compensation removes28 primitives and adds28, so its count is unchanged. No helper, warp, private buffer or port assignment is added. Cleanup is at the same FULL frame; the extra scalar gates do not create additional climb charges in this ledger, but their native phase behavior still needs verification.

The four freed width units must be priced by the actual owner fill and idle profile. This audit does not count them as free, assign each a standalone H1 cost, or claim that a fractional packing witness is a realizable order/dispatch.

## Remaining admission conditions

A bound improvement remains conditional on the fresh declared source stage and its rejection controls; whole-package strict source release; native phase/Gaussian replay of all new primitives and cleanup; actual owner fill, order and dispatch using the changed ordered width list; and both exact outer checks plus selected-parent admission and inherited rejection controls. The local audit found no algebraic or frame blocker. It does not substitute for those gates or alter the selected frontier.

## Portable reproduction

The checker accepts only the two pinned original PR2833 compressed source words, then checks the supplied candidate structurally and algebraically. Run once for each provider:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B check_four_kernels.py \
  --source-word PATH/TO/BORROW-WORD-43base.json.gz \
  --candidate-word PATH/TO/WORD-base.json.gz \
  --out RESULT-base.json
```

For the second run use `43extra`, `WORD-extra.json.gz` and `RESULT-extra.json`. The checker reads its two inputs and writes only the requested JSON receipt; it does not import or execute the candidate.

| Object | SHA256 |
| --- | --- |
| Pinned source base compressed | dda9878455b3a3bec64ca16b1ac7789bbf5ffb603d5713b8df8644485e85b1b7 |
| Pinned source extra compressed | bbe6bcba59e45e827a8e932ee4b23650d56ed4a0b8e0875c14f23c36b9e47eac |
| Candidate base compressed | 001b14314d8db873d4d80826d4af9c40a3e5a1fecde743e5a26391bdf673f458 |
| Candidate base decompressed | fd073806137fdd0b2e74f7075c7079304797227011c30147341328b928a8840c |
| Candidate extra compressed | bc5bfe51178f0c3312d28318412ec490463c896ceed0660b9c443fcb76496546 |
| Candidate extra decompressed | d61a8077a8bb60b5e36b742fca6c04df21a701b09ef432600ec62462caaa8f6d |
| Historical prototype producer inspected | 90aa848c2fc4c4c79d18a792417d73ab3683440d79ca89d9efd348a430e0f91f |
| Current production producer, separately checked to reconstruct both identical decoded words | b3241527e6c136dc4b54975ef401c49d452bd6159fb99030accaf095c8fbd3ed |
| Portable checker executed | 34ded7db6524ca4e7229c887c24ad7a5ce2531007f7c1ebfc4dd9af952406614 |
