# Finite paired temporal-gauge certificate

## Predecessor word and domain

The verifier pins and replays PR1369's zero-static temporal census on base
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, then recovers the exact PR1263
static word in both orientations. The eligible zero-static helpers are

`[272,288,348,359,381,440,444,446,447,469,478,479,491,503,507,514,515,519,542]`.

For each helper and orientation, the attributed exact integer DP optimizes its
incident ADD sequence over the certified finite breakpoint interval. The
verifier checks each new DP result against PR1369's frozen census. It then
enumerates all 171 helper pairs, retaining pairs whose single-coordinate
minima improve and are both nonzero at a shared ADD. The identical candidate
list in both orientations is `[(348,359),(479,515)]`; seed 28 chooses its first
pair.

This search optimizes one coordinate at a time. It does not claim a joint
minimum for the two-coordinate objective.

In the final overlap refresh, PR #1376 covered a disjoint-support L248/L253
composition. The concurrent PR #1380 covered 16 shared-ADD pairs, all with
L225, including L225/L348 but not L348/L359. This certificate prices the
distinct L348/L359 pair from the PR1369 zero-static domain; it does not
duplicate PR #1380's joint-optimum claim.

## Simultaneous composition

At each original ADD, the composed coefficient is scaled by the product of
the two selected dyadic gauge factors. Entry and transition scales, with a
terminal restoration when the final gauge is nonzero, are emitted on their
own helper lines at the original ADD frame. The full exact invoice prices
every inserted scale and every changed coefficient;
the complete replay checks both orientations on all 712 formal columns.

For any shared ADD with original coefficient c, helper signs s1 and s2, and
chosen exponents e1 and e2, its combined price change is

`price(c * 2^(s1*e1+s2*e2)) - price(c)`.

At event 24336 the exact data are:

| Orientation | signs (L348,L359) | exponents | c | separate ADD deltas | combined delta | correction |
|---|---|---|---:|---:|---:|---:|
| Forward | (+1,-1) | (-1,3) | -8 | -1,-4 | -2 | +3 real |
| Backward | (-1,+1) | (1,-3) | 8 | -1,-4 | -2 | +3 real |

All other incident ADDs are disjoint between the two helpers. Therefore the
joint invoice delta is `-161 - 242 + 3 = -400` real primitives, or 800 complex
primitives. Literal lowerer invoices independently confirm 136002 to 135202
forward and 136018 to 135218 backward.

The candidate's paid profile and all non-scalar events equal the static word.
The scale entry, transition, and any necessary terminal restoration work is
included. Prefix ceilings remain 52 and 68
bits under the existing 192-bit local charge. The selected exponent and
supplier certificate do not change.

## Controls and limits

The verifier checks an all-zero schedule identity, rejects a candidate with a
missing L348 transition scale, and rejects a shared-ADD coefficient mutation
that omits the L359 exponent. These controls and the 712-column replay test the
finite scalar map, not all-size hosting or supplier admission.

The claim depends on the pinned PR1263 source word, PR1369 single-coordinate
DP and PR1161 invoice/replay implementation. It does not show that this pair
is optimal among all two-coordinate temporal schedules, that three or more
gauges compose profitably, or that the operation saving changes the recursive
profile or kappa.
