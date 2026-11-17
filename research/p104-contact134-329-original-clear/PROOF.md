# The 134/329 contact with the original 74 CLEAR rows

This is the proof for candidate canonical SHA-256 `dcd797e45b6d4b74411a8a73a9b6e8247bb2ea8744924332b0dd43db3e219f02`. Its comparator is exact [#7642](https://github.com/CrocSwap/integer-mult-bounds/pull/7642) at head `d7f82810689ed2cd649ec9aaaf3b1485b585c82e`, canonical SHA-256 `aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916`. The comparator's complete clean local replay certifies signed conditional κ `0.003650666180757`. Its conservative public value is `0.0036506661663`. This proof keeps the same original private interface and exact signed [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113), head `07a76c5e2738882c0cb322278e56f6cae3c9885d`, byte SHA-256 `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`.

## Literal contact and restored outputs

Use zero-based clocks in the #7642 word. Role 134 enters the window at chart 3 and first uses its returned row at ADD43528. Role 329 enters at chart 373 and first supplies its returned row at ADD41143. The complete incident clocks in between are `41049, 41051, 42086` on 134 and `41050, 41051, 41142` on 329.

| Old clock | #7642 | Candidate |
| --- | --- | --- |
| 41049 | MOVE 134 from 3 to 618 | MOVE 134 from 3 to 373 |
| 41050 | MOVE 329 from 373 to 618 | Delete |
| 41051 | `134 -= (1/2)·329` in chart 618 | Same signed scalar ADD in chart 373 |
| 41142 | MOVE 329 from 618 to 733 | MOVE 329 from 373 to 733 |
| 42086 | MOVE 134 from 618 to 913 | MOVE 134 from 373 to 913 |

Let $F_c$ be the exact canonical signed frame on chart $c$, including global phase. At the two entries write the arbitrary physical streams as $F_3x$ and $F_{373}y$. The old lifts make the two ADD operands $F_{618}x$ and $F_{618}y$, while the new lift and retained sender supply $F_{373}x$ and $F_{373}y$. Coframe scalar ADD is linear. In both words the physical exit pair is
$$
\bigl(F_{913}(x-y/2),\ F_{733}y\bigr).
$$
The entire comparison is on independent $x,y$. Both the receiver's signed contribution and the sender's independent value are restored in the required charts before their exterior reads. On the normalized pair the adjoint is $(u,v)\mapsto(u,v-u/2)$, with the same entrance and exit conjugations in reverse order.

Equivalently, the receiver's retained input follows $F_3\to F_{618}\to F_{913}$ or $F_3\to F_{373}\to F_{913}$. The sender's contribution follows $F_{373}\to F_{618}\to F_{913}$ or $F_{373}\to F_{913}$. The sender's independent exit follows $F_{373}\to F_{618}\to F_{733}$ or $F_{373}\to F_{733}$. Each equality uses cancellation of the same signed intermediate frame and its inverse. All seven changed old/new MOVE pairs and these three compositions passed 512 exact Gaussian forward and 512 adjoint columns each, signed Pauli comparison, and absolute phase. A quarter-turn absolute-phase fault on the new $373\to913$ map rejected. The new rank-two and rank-five catalogue pairs are `373→733` and `373→913`.

## Chart and private interface

The authenticated words have identical headers and the complete ledgers validate every chart transition and scalar operand. The new charged public ascents are proper nested inclusions. Their source dimensions are 0 for chart 3 and 2 for chart 373. The old contact chart 618 has dimension 3, and the return charts 733 and 913 have dimensions 4 and 7. The two basis vectors of 373 occur in 618, all basis vectors of 618 occur in 733, and in 913 the basis vectors of 618 are given by `30 = 6 xor 10 xor 18`, `42 = 10 xor 32`, and `321 = 65 xor 256`. Dropping MOVEs and reading scalar instructions in normalized chart coordinates leaves the same 70,377 non-MOVE operations, in order. Exactly one ADD changes chart annotation, and both operands are present together at its new chart. The exact owned-event subsequence includes every contact with an owned source as well as an owned destination. Its 74 INITs, 74 CLEARs, 47 owned MOVEs, peak 50 and 68 owned fields match #7642.

Thus normalized equality is inductive through all checkpoints, including 1,501 public endpoints, all owned reads and writes and the COPY-zero guard. Each owned interface also has the same declared frame, so its normalized row equality transfers through the identical canonical frame. All 74 actual erased values remain the original #7605/#7642 rows, including CLEAR44 in chart 595 on role 1557. This port uses no added owned field, changed erased value, earlier access from another bank, or strengthened whole-extent reset contract.

The retained all-positive-column premise lifts the width-one signed quotients to any positive column multiplicity, with the identity on spectators and the inherited rank-scaled child factorization. Equal signed factors cancel under the mixed-product law. Coframe rational scalars act coordinatewise through the retained exact service. The 17-stage signed caller therefore retains its original input/output ports and private obligations. The complete replay rebuilt the caller occurrence, physical binding and tape records for the changed paid itinerary.

## Directed signed price and all-size boundary

The replaced local paid ranks $(3,1,1,4)$ become $(2,2,5)$. The independent recount reconstructs every rank from the two literal words and every static operation of the unchanged caller. The signed paid histogram delta is `{1:-34,2:+34,3:-17,4:-17,5:+17}`. Paid counts fall from 110,349 to 110,332. The 22,461 productive positions and their ranks are unchanged. The paid rank mass is 296,156 and the productive rank mass is 297,580 in both words, giving rank surplus 1,424.

Write $p=1-C$ and $M(C)=\sum_r (T_r-P_r)r^p$. Padding the new rank tuple with zero gives the decreasing tuple $(5,2,2,0)$, which strictly majorizes $(4,3,1,1)$. Strict concavity of $r^p$ for $0<C<1$ gives a positive full signed improvement
$$
\Delta M(C)=17(2+3^p+4^p-2\cdot2^p-5^p)>0.
$$
The independent outward-rounded rational recount strengthens this to separation at exact $C=0.0036506761807577608622666732886142$, which is the comparator's certified raw upper endpoint plus $10^{-8}$. At that value, the old full signed moment has strictly negative upper bound and the new full signed moment has strictly positive lower bound. The interval engine uses binary range reduction, rational atanh-series logarithm bounds and odd/even alternating exponential bounds. The exact endpoints are stored in the recount receipt. This finite price test concerns the full declared signed rank invoice.

The normalized scalar charge is unchanged. The complete replay computes an ordinary saving of 17,000 units, from 782,685,204 to 782,668,204. All 3,041 signed catalogue maps and 104 boundaries pass. Context precision is 2,430, and the elementary tape bound is 25,445,676,576. The full replay recomputes the caller, exact-grid and pre-product divisibility, fixed tape, both directed price enclosures, the compiler gate and the 54 strict and four functional outer predicates. These verify conditional κ `0.003650982374396`, strictly above the complete #7642 raw upper bound and by exactly `0.000000316193639` over the certified #7642 value. The maintainer-selected record is separate.

The five premises remain `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`. The preserved exits retain the same recovery map and fixed deterministic multitape bit machine for every input size. The original decomposition, BIT witness and compiler closure are inherited. The finite changed-word checks and directed positive slack supply their part of the conditional all-size integer-multiplication argument.

## Provenance

Clear1nsight's [#7612](https://github.com/CrocSwap/integer-mult-bounds/pull/7612) at `e814828ee5b869c9468282d57ba28c364b07d130` supplies the literal contact repair and signed coefficient. SYLforge's [#7616](https://github.com/CrocSwap/integer-mult-bounds/pull/7616) at `22b310ba50a554b6111804824782793beb41073f` reused the same port in a broader composition with 39 additional stationary owned lifetimes. The present scope is the port on exact #7642 with its original 74-CLEAR contract. DreamingOfClouds's [#7610](https://github.com/CrocSwap/integer-mult-bounds/pull/7610) supplies the main-46 edit in the comparator. [#7605](https://github.com/CrocSwap/integer-mult-bounds/pull/7605) supplies the underlying original interface and retained verification lineage. Rohan Arun's #7113 supplies the signed caller. OpenAI Codex and subagents materially assisted the transplant, exact replays and proof.
