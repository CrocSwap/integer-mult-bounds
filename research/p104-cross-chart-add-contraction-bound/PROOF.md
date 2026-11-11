# Exact scope and exclusion

Let the original word be #7314 at `9d0119eb12fbd9fa534b48cd37b68e7099757b91`.
An ADD is `d += a*s` on its declared chart. Normalize the word by omitting
MOVE events only. Consider every consecutive triple of ADDs in that
normalization with at least two distinct literal charts and exactly three
roles. Exclude any triple touching roles 863, 1355 or 1568. The permitted
rewrite requires a chain through an owned middle role.

On distinct roles `i,j,k`, write the chain and correction as
`X = I + a E_ij`, `Y = I + b E_jk`, and `Z = I + c E_ik`.
The correction commutes with both chain factors. If the old chronological
order of the chain is X followed by Y, reversing it and dropping Z requires
`c = ab`. If the old order is Y followed by X, it requires `c = -ab`.
These statements follow from `E_ij E_jk = E_ik` and
`E_jk E_ij = 0`. Testing all three basis inputs over the rationals checks
the exact normalized forward product, which also determines its adjoint.
The normalized test alone does not establish a native realization.

The window entry is immediately before the first original ADD, and its exit
is immediately after the third original ADD. The two retained ADDs keep
their literal charts and factors in the reversed order. For each touched
role, the direct route visits each chart demanded by these ADDs in order
and returns to the original exit chart. It must visit a scalar operand's
chart whether the role is a source or destination. Public roles can only
move by strict span ascent. Owned roles may ascend or descend along nested
spans. Both walks check the original literal MOVE histogram. The reverse
walk reconstructs entry and exit charts independently and records the
two public-middle triangles as a diagnostic outside the owned scope.

| ADD clocks | ADD charts | Middle role | Required descent | Before scalar slot |
| --- | --- | --- | --- | --- |
| 35646, 35648, 35650 | 3, 1031, 1031 | public 699 | 1031 → 3 | 35650 |
| 36496, 36498, 36500 | 3, 595, 595 | public 581 | 595 → 3 | 36498 |

The two descents are illegal under the unchanged public-role contract. The
owned-middle stock is empty. Neither a changed physical tape nor a changed
compiler, caller, precision or recovery claim is needed for this exclusion.

## Complete directed price

The full caller has 17 native copies, 110,536 paid positions and 22,461
productive targets. Its rank surplus is 1,424. The complete invoice uses
the #7298 directed tariff on `T-P` at the exact upper crossing endpoint
`36462214364462343366888845568981/10000000000000000000000000000000000`.
For a legal proposed edit, `T` stays fixed, while `P` changes by 17
times the new-minus-old touched-role MOVE histogram. New direct routes and
restoration to the exit are charged before the identity test. Unrelated
MOVEs stay charged. The maximum whole compatible saving is zero because
the eligible stock is empty.

A hypothetical histogram control removes two rank-one paid calls per copy
and adds one rank-two call per copy. It clears the directed comparison
before one additional rank-one paid position, which reverses the result.
This is a tariff control. No literal #7314 case realizes that hypothetical
delta in the tested scope.
