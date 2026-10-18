# Shared-core fan-in with simultaneous rank-one deviations

This package gives an exact local connector construction for three distinct source maps that share one rank-48 core and differ from it by rank-one maps. It preserves arbitrary dirty source, target, and scratch rows. The code checks every F2 basis column of the full five-row interface and an integer-valued mixed-state fixture.

The construction is

    B_j = B + D_j
    z += B_1*x_1 + B_2*x_2 + B_3*x_3

with B = diag(I_48,0) on 49 coordinates and D_j = e_49*v_j^T. Each v_j is distinct and has final coordinate 1, so each B_j has rank 49.

Let d be the arbitrary starting value of scratch t and S=x_1+x_2+x_3. The paid sequence is

    z -= B*d
    t += x_1+x_2+x_3
    z += B*t
    t -= x_1+x_2+x_3
    z += D_1*x_1
    z += D_2*x_2
    z += D_3*x_3

The signed core outputs add to -B*d+B*(d+S)=B*S. Over F2 the minus sign is the same as plus; over integer-valued rows the exact inverse sign cancels the arbitrary dirty term. The scratch returns to d; every source is unchanged. The three deviations contribute their own outputs. This establishes the requested map on arbitrary dirty rows without a clean vector. The local rank tariff prices both orientations of B at their larger complete-call cost; any orientation asymmetry in an actual supplier belongs in the remaining overhead budget.

## Complete local cost

The direct plan uses three complete rank-49 calls. The shared-core plan uses two rank-48 calls, three rank-one deviation calls, and six rank-one gather/restore calls. Every one of its 11 calls is charged one extra rank-one-equivalent dispatch unit; the direct plan's 3 calls are charged the same way. Thus the compared profiles are

| Plan | Paid profile including dispatch |
| --- | --- |
| Direct | 3 rank-49 calls, 3 rank-one dispatch units |
| Shared core | 2 rank-48 calls, 20 rank-one units (9 complete rank-one operations and 11 dispatch units) |

For q=1-a at the selected a=836330098538459/500000000000000000, the local moment difference is

    direct - shared = 3*49^q - 2*48^q - 17 > 28.

The strict inequality is certified without floating point: a<1/100, 49^0.99>47 because 49^99>47^100, and 48^q<48. The construction therefore has a 28-unit budget for any remaining parent program, interface, hosting, or precision overhead measured in the same normalized units.

The interface requires one 49-coordinate dirty scratch row. Summing three integer-valued sources can require two extra guard bits; these resources are stated explicitly and must fit the remaining overhead and live supplier stock. The F2 construction has no rounding or precision error. It changes no frame and hides no source map, recursive child, gather, correction, dispatch, or restoration call.

This is a local construction under an explicit rank-class call tariff. It has not been matched to actual maps in the selected supplier. It does not establish a new supplier, new selected profile, or new kappa. Its direct relevance is conditional: an actual three-map seam must expose one common rank-48 core and three rank-one residuals, and its added dirty-row and guard-bit charges must fit the 28-unit budget.

## Reproduce

From the repository root:

    python3 -I -O -B research/common-core-fanin-seed93550f9f/verify.py

Expected status: PASS_COMMON_CORE_FANIN_DIRTY_BOUNDARY. The verifier checks ranks 48/1/49, all 245 basis columns, an exact integer-valued fixture, four negative controls, the selected exponent pin, and the rational cost bound.

## Source and predecessor pins

The accepted selected record is pinned by its SHA-256 in SOURCES.json, alongside the maintainer review, integration receipt, selected source manifest, assembly certificate, current task catalogue, current autoresearch instructions, and universal connector model. Nearest open predecessors and exact heads are listed in TASK.json and SOURCES.json.

## Open next questions

- Does any live selected-supplier interface contain three simultaneous source maps with one shared high-rank core and rank-one residuals? This determines whether the local mechanism can change a paid profile. First step: extract one exact multi-source seam from the source manifest and compare its three map matrices over F2. Blocker: the selected construction has not yet been mapped to this multi-source interface.
- Can the required dirty 49-coordinate row and two guard bits be hosted within the 28-unit overhead cap? This decides whether the local cost screen survives supplier admission. First step: bind the scratch and precision requirements to one named selected call. Blocker: no such call has been identified.
