# Independent review of the new signed local maps

All ten local words pass. The review covers the plain signed forward and
backward maps, their coded forms, and the oblique backward map on both
new provider words. The maps are

    F_S(x,y) = (x, y+Sx),
    B_S(x,y) = (x-Sy, y),
    coded F_S(x,y) = (x, S(x+y)),
    coded B_S(x,y) = (S^-1 x-y, y),
    oblique B_S(x,y) = ((S^-1+Pi)x-y, y-Pi x).

Here `S=I-KR-Pi`, `K=R^T/4`, and Pi selects ports
`[0,7,20,27,36,46,57,111]`. The checker derives S and its inverse from
the literal new R. It verifies both inverse orders, `RK=14I`,
`R Pi K=I`, `P^2=P`, and `P S^-1=-Pi`, where `P=Pi K R`.
The inverse uses dyadic coefficients only.

The complete local bills are:

| Map | Real scalar primitives | Native rank mass | Child count |
| --- | ---: | ---: | ---: |
| Plain signed F or B | 164626 | 5081 | 3515 |
| Coded signed F or B | 171938 | 5081 | 3515 |
| Oblique B | 172050 | 5089 | 3523 |

Each signed boundary has eight rank-one children and sixteen explicit
monomial wrappers. The oblique word has two such boundaries. The scalar
bill includes the common-bank code factors, owned copies, additions,
clears, and the complete retained core.

`check_new_signed.py` imports two pinned independent review engines. It
does not import the producer. It propagates output coefficients backward
through the complete literal word in the free algebra of invertible
warp symbols. This is distinct from the producer's forward row replay.
Every program uses the exact retained clean-J core. Every scalar and
boundary access has a checked frame. All 640 arbitrary live and private
input columns have the required response. All 408 borrowed helpers have
the identity logical response. Each of the 91 private zero-buffer output
rows is zero at release. C0 returns to zero; C1 through C7 remain unused
and retain their arbitrary input values.

The sixteen signed line recipes are checked on every spatial basis
input. For each recipe the checker independently applies the two affine
permutations around the coordinate rank-one kernel and compares both
Gaussian coefficients with the required signed C_q kernel. This gives
8192 exact spatial column checks per provider. It also binds each q to
the actual new port. The core's full phase-aware implementation and
proper-terminal wrapper contracts are proved in
`NEW-CORE-NATIVE-REVIEW.md`.

The run used:

    python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/check_new_signed.py --out work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/NEW-SIGNED-REVIEW.json

It returned `PASS_INDEPENDENT_NEW_SIGNED_EXTENSIONS`. Negative controls
reject an omitted oblique input return, the wrong return sign, a borrowed
helper clear, and the wrong signed-line kernel on every checked spatial
column. The checks remain active under `-O`.

This result makes these mechanisms available on the lower-cost new core.
It does not choose a complete caller. A caller must still prove that its
paired exterior phases permit the same-port boundary copies and adds.
Legal source access, owner assignment, decoding, query transport,
recursive child hosting, precision, and the complete supplier invoice
remain separate obligations. In particular, a uniform coded target can
leave holes and is not automatically the mixed retiring target used by
the earlier 448-decoder construction.

The producer's proof and predecessor credit are in
`../new-core-transfer-20261017/SIGNED-EXTENSIONS.md`. The source and
independent-engine pins are in the receipt and freeze file. OpenAI Codex
assisted this independent review. No PR, push, or publication commit was
made.
