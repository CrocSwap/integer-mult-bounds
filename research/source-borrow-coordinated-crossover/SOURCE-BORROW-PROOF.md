Packaging note: the original verifier filenames passive-boundary.cpp and passive-bank.cpp are shipped here as native/source-boundary.cpp and native/joint-banks.cpp. Run the root verify.ps1 or verify.sh for the complete frozen candidate.

# Passive source copying: sufficient physical construction

Pinned upstream PR210 source: 39905c6e0081fc6a0feec5e91c0651fd1e2d8356. Native input is `extracted inputs/combined`. These checks use actual source lines, all 67 donor aliases, current-bases.json and every remaining branch endpoint. They introduce no zero-dirty assumption. The earlier bank9 checkpoint remains unchanged.

## Sufficient substitution lemma

Consider a restored linear auxiliary tape with exact chronological dirty compensation and original external sources X. A later branch s first receives `s += q_n`, where the retained injected source q_n has clean value X_n at that event. Suppose s has no earlier touch, is neither an entrance-gauge role, retained injection role, recipient alias nor terminal redirect, and n is a passive member of a disjoint external partner pair (a,n). The retained original source injections occur before this tape. Assume the physical continuation of s, including any later donor-to-recipient gauge splice, accepts the original source line and the proposed early mixing frame; all chronological frame inclusions are checked on this complete continuation. Before the early event s is never a physical destination.

Replace the physical s slot with the original X_n array, omit its first copy, and omit its independent initial-dirty compensation. At the early event execute `X_a += X_n`. Continue the auxiliary tape on the borrowed physical X_n slot. At the old partner delivery anchor deliver X_a without a second mix. Use the exact reverse adjoint of the tape with the first copy omitted for every remaining dirty compensation. Reverse precisely the executed auxiliary gates. Then undo `X_a += X_n`, and finally undo the retained original source injections. This is a sufficient physical substitution, with no new scratch slot.

Proof of the clean signal: before the removed copy the old s has zero clean contribution and no touch. At that copy its clean value becomes X_n. The new s already contains X_n and has no touch before the omitted event. Thereafter every surviving auxiliary operation has identical clean input, inductively. The retained q_n clean value is indeed X_n because no auxiliary destination touches it before the omitted copy. At the early event X_n is still its original value: all preceding surviving s events are controls. Thus X_a stores exactly the original pair sum. Partner pairs are disjoint and no passive source is a carrier; external carriers are isolated from the auxiliary tape after the retained injections. Saving all pair sums therefore does not change any auxiliary clean signal, even when later gates modify the borrowed passive sources.

Proof of arbitrary dirty response: removing a copy changes only the linear auxiliary tape, not the definition of compensation. For any surviving dirty input its output coefficient is the exact reverse-adjoint coefficient of that new tape. Subtracting that coefficient times its entrance value cancels its complete response. At an internal donor-to-recipient gauge the compensation reads the CURRENT shared physical value, using the unchanged complete recipient response; it does not initialize or erase that value. This is precisely the chronological compensation invariant of the inherited construction. The 440 independent old s-dirty inputs cease to exist, so their old compensation is also omitted. Remaining dirty values may be arbitrarily correlated. The separate full scalar-column audit checks this invariant and the exact terminal redirects on the emitted word, over F2 and the defining integer decoder in both signs.

Proof of restoration: borrowed source arrays are among the operands of the executed auxiliary tape. Running its exact inverse restores each borrowed X_n and every other auxiliary slot to the tape entrance state. External carriers were not auxiliary operands, so the saved X_a values remain intact. Subtracting the NOW RESTORED X_n undoes each early mix exactly. Retained injection cleanup then uses original external sources and restores its original dirty slots. Undoing the early mix before the passive source is restored would subtract its changed value; this order is essential.

## Checked physical implementation and payment

`passive-boundary.cpp` independently reconstructs all 440 physical histories from literal operations, source endpoints, roots and current frames. It verifies the exact omitted original-source copies; retained source no-write prefixes; pair disjointness; borrowed no-write windows; source/carrier inclusion in the early frame; all source path nesting; 67 donor histories ending before their actual recipient reads; the recipient gauge and entire continuation on the SAME physical array; and the full-space terminal endpoint. It checks 3,042 old/new path steps. Complementing and reversing each path preserves every positive rank increment, so the reflected construction has the same paid path histogram.

The exact local recount is ΔH2=−440, ΔH22=−440. Three stages give ΔH2=ΔH22=−1320, rank mass −31680, physical stock −440, and deficit change zero. These are actual path deltas, not inferred scalar-operation savings. Scalar copies and reverse copies decrease by 880; early mix and inverse mix counts stay unchanged. Positive recomputed adjoint coefficients do not increase (separate emitter/replay audit). No extra auxiliary copy or delivery chain is hidden in this substitution.

## Complete reduced physical banks

`passive-bank.cpp` reconstructs the entrance gauges directly from the final literal word and excludes all and only the 440 selected physical roles. Every excluded role is ungauged and is checked by the source-boundary audit to be neither a recipient nor a terminal. The remaining 16,674 physical roles have residual ranks:

| rank | physical roles |
| --- | ---: |
| 4 | 2200 |
| 5 | 3 |
| 6 | 13 |
| 11 | 48 |
| 12 | 18 |
| 24 | 14392 |

All 234 actual canonical entrance charts are reconstructed, and both inverse identities, exact elementary factor replay and residual/gauge orthogonality are checked with unbounded integer/rational arithmetic. The native canonical factorization maximum is 310 factors, numerator 13, denominator 72. All numerator/denominator factors are units for retained primes greater than 2^80. The upstream 200-factor convention is not used in this invoice.

For each of three stages the 72-replica bank patterns are 54(4×5 + 13×4), 864(4×11 + 7×4), 8425(18×4), 78(12×6), 216(6×12), and 345408(3×24). Every pattern covers exactly 72 coordinates. The checker allocates every physical role/replica once at each stage; checks all normalizer permutations and the distinct scaled outside columns; replays each whole bank swap and inverse on arbitrary labeled correlated contents; and rejects omitted/repeated blocks. This gives 355,045 banks per stage, 1,065,135 total banks, 3,601,584 assignments and literal stock 1,318,575.

The paid native selector invoice is

`K = 2*3*72 * ((1318575-1) + 16674*72*(310+71+72)) = 235508151456 < 2^40`.

The all-size selector/compiler/routing and analytic assembly remain inherited conditional interfaces. This document proves and checks the finite sufficient substitution and complete reduced-bank invoice; the root exponent requires the parent's unchanged full frame, scalar, prime/value and analytic audits. No new exponent is claimed here.

## Native replay

Compile each owned source with `g++ -std=c++20 -O2 -Iextracted deps/include passive-boundary.cpp -o passive-boundary.exe` (and correspondingly passive-bank.cpp). Both include the frozen `new-frame-algebra.hpp`.

Run `passive-boundary.exe extracted inputs/combined passive-boundary.json` and `passive-bank.exe extracted inputs/combined passive-bank.json`. The receipt includes every borrowed source, carrier, omitted-copy/early index, donor alias and individual paid histogram. Input/output/source hashes are recorded in PASSIVE-COPY-HASHES.json.

## Additional butterfly candidate, separately admitted

The direct source440+440-butterfly composition is not covered by the baseline certificate: reassociation changes physical branch touches and can make the rank2 partner mix incomparable with the branch's current frame. A chronological mix cut must be inserted even when its reference operation no longer touches the borrowed role. The checker handles operation, recipient-gauge, root and full endpoints at their actual chronological cuts. Enlarging a later mix by the preceding branch frame can escape its retained carrier delivery cap; such a change is rejected rather than assumed harmless.

A concrete sufficient candidate instead retimes all440 mixes to their omitted initial-copy operations. Retained original source injections already precede those operations. Borrowed passive sources have no prior auxiliary touch, so all early reads remain original values. Carrier pairs are disjoint; retained dirty source heads remain separate physical operands. Nevertheless a fresh full scalar-column audit is required because the actual word chronology changed.

Keep every original rank2 mix and carrier delivery frame. Join each later borrowed physical operation frame with its preceding source/mix ancestry. `passive-frame-repair-early.cpp` generates 440 G-nondegenerate operation joins and 7337 total frame entries, with no mix-frame changes. All440 complete local physical histories and all67 recipient splices pass. `passive-early-emitter.cpp` stages `source440-butterfly-early-inputs`, updating BORROW.json early/windows, word.borrowed_sources and word.retimed_partner_mixes together; original public inputs remain unchanged. The complete source-boundary checker passes on this literal staged candidate. Its comparison against the same repaired physical auxiliary histories still gives ΔH2=ΔH22=−1320 shared and deficit change zero. The frame joins themselves have their own paid global effect and cannot be treated as free butterfly gains.

Candidate receipts: `passive-butterfly-early-final-boundary.json` and `passive-butterfly-early-bank.json`. Bank geometry is unchanged: all234 charts, 3,601,584 assignments, literal stock1,318,575 and K235508151456 pass again. The parent's fresh whole-graph/frame/prime audit and quantum lane's fresh source440 scalar executor establish whether this retiming is globally admissible. Local path admission is not claimed to establish a root exponent or global frame admission.
