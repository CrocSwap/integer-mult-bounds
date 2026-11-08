# Conditional κ = 0.00339993 from a hosted pair at every call of the chain-nested root

**Result.** κ = **0.00339993013239573** (exact-kernel crossing of the complete signed invoice), up from 0.00337180047549672 of
[#6833](https://github.com/CrocSwap/integer-mult-bounds/pull/6833) by **+0.834%**. The claim for the outer statement is κ = 0.00339993 with tested price 0.00339993007 (grid 10⁻¹¹);
the raw crossing lies in (0.0033999301323957, 0.0033999301323958).

**Conditional statement.** The result holds under the five framework assumptions of #6833 **and under assumption A6, owned ascent, which is load-bearing: no ascent, no word.**
A6: an owned nested rise costs one paid H_r plus rank-0 adapters, with no credit, on arbitrary contents, factorwise at every width, with CLEAR at any frame under owned_erasure.
The word has 23 owned rises (rank mass 56); the predecessor rule lets owned moves only descend. The one-line change, both verifiers, the rejection control and the direction-free cost argument are in `PROOF-OWNED-ASCENT.md`.
The nearest text, `notes/copied-centers-lemma.tex:58-62,71`, covers a copy started by COPY; this word accumulates by ADD first, so A6 goes further than that text. The compiler text #4268 is not available to us and was not checked.

## Departures (each classified; counts recomputed by `check.py`)
File and line citations without a directory (`native.py`, `pricing.py`, `chain_root.py`, `local.py`, `check_root.py`) refer to the #6833 package `research/p104-chain-nested-root`.
| class | departure |
|---|---|
| convention (A6) | owned ascent, native.py:55 / local.py:126: 23 events, rank mass 56 |
| verifier | endpoint literal native.py:75-77 / local.py:168: the hosted target replaces `X = x, Y = x + y` on the 104 main pairs |
| verifier | events 172166, public 1403, owned roles 51, 54 lifetimes, peak 13 (local.py:52,54,103; pricing.py:84-87); the predecessor word already exceeds these literals |
| verifier | per-call scalar work 11,928,436 fails the predecessor check `per_call < 10⁷` (pricing.py:93), and the reviewed upper count is 13,922,152; see Raw bound |
| verifier | caller coefficient height 9 and 8 bits against 8 and 7 (pricing.py:96-97) |
| convention | root family N = n + 2, two units per stage (chain_root.py:79,82,83,98; check_root.py:26,133,141-145); SPEC-level identities re-proved in `root_check.py` |
| convention | pricing: the 36×104 one-site idle jobs at the hosted stages are paid whole H8 idles in P[8]; targets get nothing for them. κ rests on pricing them as whole H8 idles (the line construction attains this exactly); priced as eight rank-1 jobs each, κ would be 0.00298 |
| assumption | dirty owned erasure, 53 events (predecessor 45), the existing owned_erasure assumption |

## What the gain is
Targets are the 38×104 diagonal fields plus 1195 helpers per call. New = 2 × base + 29753.6 (hosted word against twice the predecessor native, 18 calls) − 29741.0 (the 36 whole H8 idles per port) = net +12.59 at the crossing, so the +0.834% is the small difference of two large terms.
S = 656 + 48·18 = 1520, already net of 56 per hosted call; D is higher by 7663.4 per call.

## Raw bound
Literal definition (18 × 10⁷ + caller, thin, output and adapter terms): 948,952,288 < 10⁹. With the actual per-call work (18 × 11,928,436 + the same terms): 983,664,136 < 10⁹, margin 1.6%; this second total is the self-consistent one because the per-call work exceeds 10⁷.
**With the review's more conservative per-call count (reviewed upper + routes, 18 × 13,922,152) the total is 1,019,551,024, which exceeds 10⁹ by 2%.** The 10⁹ value is a finite parameter of the retained precision and tape contract; no term of the outer ledger reads it. So this does not change the κ arithmetic, but the budget would have to be raised for that count, and the inherited precision-tape contract is not re-examined here. `check.py` asserts the first two totals; `ordinary.py` prints all three.

## Outer statement and the BIT pin
Cutoff 11, floor 12, offset 1/7, power 1920 (the predecessor's constants) hold unchanged: α = 0.99999999992, γ = 0.9452, δ = 0.8653 (< 31/32); 12/13 also holds; 13/14 and 17/18 fail on δ.
η = 7.75e-15 > (63/64)²¹⁰⁰ = 4.34e-15 at maximum target rank 145; compiler threshold H = 1.1196e16; the 54 strict and 4 functional outer inequalities are positive (their smallest value, 10⁻¹², is the chosen parameter r0 = gap/10, not a measured margin).
The binding item is the retained BIT pin: the tested price 0.00339993007 is below 0.0034 by exactly **6.993e-8**. Any claim above 0.0034 needs a different pin.

## Check
`check.py` (about 45 s, standard library): exact event replay; strict and relaxed verifiers with the rejection control; root checker; caller composition at the four central characters with the pair read from the root, with controls (root in the other gauge, wrong α or β sign, swapped pair) rejected; invoice rebuilt from word, root and caller, with #6833 rebuilt by the same code; exact-kernel κ; raw bound; both interval engines; strictification, compiler and outer ledger; departures.
`physical.py` (about 35 s, standard library): all 172166 events as 512-component streams over F_p[i] (p = 10⁹+9, random inputs, every chart change gate by gate, owned rises included), chart predictions for helpers and both main outputs, and the raw main-pair identities XX = YY = D, YX = Q⁻¹D, XY = QD by tableau and phase on all 104 ports, with controls.

## Not claimed, and not independently examined
No frontier change; no claim without A6; no claim above the 0.0034 pin; the inherited precision-tape and compiler assumptions are not discharged. Direction-based lower bounds (#6315 Lemma S, #6229, #6257, #6831, and the c ≥ 56 input of #6881) are scoped to words whose owned registers only descend and are not cited as global.
Not independently examined: the compiler text #4268; the adjoint (transpose) replay of this word; the tensor-width-3 (Q = −i) sector, where only widths 1 and 2 were run and width 3 follows from the ring replay. The physical replay uses one prime and one random input per run.

## Open next questions
1. Is owned ascent (A6) accepted for the native verifier, as it is in the P112 native?
2. Is pricing the hosted-stage idles as whole H8 jobs accepted by the compiler contract?
3. Can the pin 0.0034 be moved, so that the margin of 6.993e-8 stops being binding?

## Credit
Builds on #6833 (chain-nested root, invoice and outer ledger), #6726 (zxv, two-pair root caller), #6716 (thu-nmrc, common idle fusion), the #6702 and #6824 native work by DreamingOfClouds, the independent-helper basis and native input lifting of Ali Romman (#6349, #6353, #6372), the retimed helper split of CubeJerry (#6805), the compiler of Jacob Alan Sussman, the retained interval engines and Clifford compiler of their authors.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
