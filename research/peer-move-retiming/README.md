# Peer MOVE retiming at conditional κ = 0.00363206219

Delaying a public MOVE allows one existing ADD to execute at an earlier
common chart and removes one paid MOVE per LOCAL in the complete #7003
construction. The new conditional exponent is `363206219/100000000000`,
up `39227/100000000000` from #7003 under the same contracts.

## Literal change and proof

The source is #7003 at `ec30476096b2f9aed718152a2fa3712d1c4e884d`, Git tree
`89a8336b6ebf8186f75dbe1da6476c364a3e2338`, with canonical native word SHA-256
`d0de7804e56b2c8fe6db9d323560e53041810fd0377b91680cbed19b5176ebc0`.
The generated successor canonical word hashes to
`311069e5faeef999a0b3f2fd8ae9c256b67b40a368998c5c31cd38a500f385e3`.
All source indices are zero-based.

| Index | Source event | Edit |
|---:|---|---|
| 29706 | `MOVE(972,3,105)` | Delay to immediately after the relocated ADD at cut 30463. |
| 30463 | `MOVE(1317,3,105)` | Replace with `MOVE(1317,3,1048)` at the same cut. |
| 33688 | `ADD(1317,972,+1,105)` | Execute `ADD(1317,972,+1,3)` first at cut 30463. |
| 33689 | `MOVE(1317,105,1048)` | Fuse into the replacement at 30463. |

Role 972 has no intervening contacts while its MOVE is delayed. Role
1317's sole chart-105 contact is the moved ADD. With chart operator
`C_f`, use normalized coordinates `C_f^-1 v`. Each MOVE then preserves
the normalized vector, and a same-chart ADD has matrix `I + q E_dest,src`.
The moved ADD crosses one scalar event with an overlapping operand.
That event is `ADD(544,972,−1/2,105)` at index 33687. Both operations read
972 and have different destinations, so their elementary off-diagonal
matrices multiply to zero in both orders. Other reversed pairs involve
disjoint operands or chart-only transports. This proves the same linear
map on arbitrary inputs. The full grid replay also compares both ADD
source rows, all 1,480 public output rows, 54 CLEAR rows, COPY, and all
owned lifetimes and moves.

The three spaces strictly nest with dimensions 0, 1 and 5. The middle
chart cancels in `C_1048 C_105^-1 C_105 C_3^-1`. The direct pair 3→1048
already occurs in #7003 on role 671. Exact signed Pauli, phase and all
512 Gaussian columns are checked again. The all-column justification
uses the retained native contract.

## Complete price and verification

For `p = 1−κ` in `(0,1)`, strict subadditivity gives the margin gain
`18(1 + 4^p − 5^p) > 0`. The full caller changes its paid profile by
`{1:−18, 4:−18, 5:+18}`. Paid requests fall from 117,522 to 117,504.
The 23,392 target requests, rank-mass surplus 1,520, and E-free paired
BIT source stay fixed. The conservative ordinary bill falls by 18,000
to 826,682,496 under the retained tariff.

Independent rational enclosures place the raw crossings in

- #7003: `(0.00363166992015115785886325297974980, 0.00363166992015115785886325297974981)`.
- Successor: `(0.00363206219577303624414255882815714, 0.00363206219577303624414255882815715)`.

The tested price is `0.00363206219007` and the compiler gap is `10^-14`.
The checker recomputes the literal native and caller invoices, verifies
strictification, the input lift and 54+4 outer conditions, reruns the
source-bound grid and precision engines, and runs the width-512 physical
control on all main and helper outputs. The receipt records rejection of
a scalar mutation, a wrong phase, a smaller grid and the new claim at
the old invoice.

Run with Python 3.12 from the replay bundle or from the exact predecessor
checkout after applying the patch.

```sh
python3.12 -I -B research/peer-move-retiming/verify.py
```

Expected final line: `PASS_PEER_MOVE_RETIMING 0.00363206219 3.9227E-7`.
The checker compares the complete computed receipt to `RESULT.json`.
`BASELINE-EXPORT.json` binds all inherited live input bytes to the exact
source tree. The two independently implemented interval engines use the
recomputed invoice, with source-engine reuse for precision and physical
checks. The physical replay is finite.

The result inherits #7003's original five framework assumptions plus the
exact odd-scalar child returns, owned ascent, per-port and one-field-idle
caller, LAMBDA/ordinary tariff, and paired BIT contracts. The full fixed-tape
provider, rounded admission, and #6998 tariff conversion remain open.

## Open next questions

- Seek simultaneous retimings outside the single contracted stop and peer
  MOVE scope. The deterministic search found one candidate among 4,778
  public two-hop chains after allowing peer MOVE slack. The predecessor's
  fixed-cut screen had zero nominations on #7003.
- Resolve the physical provider and tariff bridge against a common tape
  model before asserting full admission.

Credit DreamingOfClouds for related #6932 retiming and the earlier words,
CubeJerry for #7000/#7001, and all contributors in the predecessor notices.
The four authenticated #6932 words checked for overlap retain this specific
role-1317 two-hop stop. The final #6932 sequence has the original MOVE,
ADD and MOVE at indices 29789, 32406 and 32407. Prepared for ToikY with
substantial OpenAI Codex assistance. Apache-2.0.
