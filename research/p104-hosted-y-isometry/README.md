# Conditional κ = 0.003429289 from the hosted native with 24 Y pads removed

**Result.** The exact-kernel crossing of the complete signed invoice is **0.00342928953721633**, up from 0.00339993013239573 of #6883 (the base) by **+0.8635%**, from 0.00341603288178402 of #6884 by **+0.3881%**, and from 0.00337180047549672 of #6833 by +1.7050%.
The claim for the outer statement is **κ = 0.003429289** with tested price 0.00342928907 (grid 10⁻¹¹), both below the raw crossing, which lies in (0.003429289537216, 0.003429289537217). The rounding 0.00342929 is above the crossing and is not claimed.
The package keeps the root, caller and hosted pair (α, β) = (−1, 1/2), t = −1/2 of #6883 and the 342 deletions and shared cover of #6884; only the native word changes (`data/word.json.gz`, a single input; its gate blocks were compacted with the gate matrices asserted identical, and the invoice, the endpoint and the physical identities are unchanged).

**Conditional statement.** The result holds under the five framework assumptions of #6833; under assumption A6 (owned ascent) exactly as declared in #6883; and under the BIT pin 0.00376669 of the open #6726 (the pin of #6884, below). #6726, #6883 and #6884 are open pull requests; the BIT admission is read from the pinned file `retained/bit/FRAGMENT-BIT-ADMISSION.json` (git blob 482f9525…, sha256 86955dcd…, #6726 head 435bbe91) and is not re-derived.

## What changed against the #6884 word (counted by `check.py` and `cover_check.py`)
Correctness rests only on the exact replay of the final word (and the physical and caller replays below). It does not use a black-box argument about the forward network, Law H, the weight rule or any isometry claim.
* **24 Y pads removed.** Exactly 24 ports have no Y pad and no pad-to-Y transfer; on those ports the mirror reads the Y register of the forward network itself with diagonal weights: 91 more direct reads of Y by mirror helpers (119 → 210 in the core), spread over exactly those 24 ports; all other ports are unchanged. Public registers 1385 → 1371 (24 pads fewer, 10 fewer shares), MOVEs 6679 → 6634, core ADDs 6767 → 6719, core SCALEs 742 → 730; owned lifetimes, COPY and the 342 deletions unchanged.
* **Two owned registers now read a main Y register** (events 77753 and 78775 of this word: `ADD 1402 134 -2` at frame id 595 and `ADD 1401 213 2` at frame id 594). They replace pad reads, are declared together with A6, and exist in no earlier word. Peak owned fields 25, as in #6884.
* Controls on the direct reads: a wrong weight (×2), a missing read and a read taken twice, each on 8 sampled reads of the 24 ports, are all rejected by the replay, as is removing the first core ADD and removing any of 12 sampled core ADDs.
* The reason the removal can be exact is a hand argument of the builders (a diagonal weight replaces the pad where the forward gates on Y are two-by-two isometries between diagonal forms). It is not used and not examined here. Law H, the builders' statement of which cover the unweighted mirror only, is not cited as a lower bound.
* Owned ascent is unchanged: 23 events, rank mass 56, 19 lifetimes with rises (3 read before the rise, 3 with contacts between rises, none both rising and falling, same start frames), so the list of what goes beyond the P112 precedent does not change. The hosted pair is unchanged: T[Y,X] = 1/2, Tinv[X,Y] = 1, block determinant 1, helpers identity, and XX = YY = D, YX = Q⁻¹D, XY = QD on all 104 ports.
* Targets: 38×104 diagonal fields plus 1163 helpers per call (#6884: 1177); 6634 paid moves per call; dD per hosted call 7451.30 (#6884: 7546.61); S = 656 + 48·18 = 1520, net of 56 per hosted call. New = 2 × base + 29764.9 − 29739.2 = +25.74 at the crossing.

## Raw bound
* Literal definition (18 × 10⁷ + caller, thin, output and adapter terms): 948,952,288 < 10⁹.
* With the actual per-call work (18 × 11,477,894 + the same terms): **975,554,380 < 10⁹**, margin 24,445,620 (2.4%).
* With the review's conservative count (reviewed scalar upper 3,377,444 + routes 9,800,000, 18 × 13,177,444): **1,006,146,280, which exceeds 10⁹ by 0.61%.** The same formula on #6883 and #6884 gives 983,664,136 / 1,019,551,024 and 999,138,736 / 1,052,149,312, so the conservative line was already over 10⁹ at #6883.
* Substitution (FP:278-283): events 123,860; scalar allowance 1,677,894 or reviewed upper 3,377,444; routes 9,800,000; per call 11,477,894 or 13,177,444 (both above the displayed 10⁷ of pricing.py:93); caller envelope 258,618,880. The growth bound written for the precision contract is 2^(1,006,146,280 + 348,500·f) on the conservative count (2^(975,554,380 + 348,500·f) on actual work), with R = 348,500 the paid rank mass, as in FP:278-283 and `OUTER-TRANSFER-AUDIT.md:382,390`.
* No term of the outer ledger reads this number (`check.py` verifies that the ledger source has none). That it is not load-bearing is a reading of the texts, not a proof; the precision and tape contract (`research/p104-productive-controller/PROOF.md` section 5, "parameters for the retained precision/tape contract") is inherited and not examined; the only packages above 10⁹ on any count are the open #6883 and #6884, on the conservative line.

## Growth of the scalar updates (PROOF.md section 5 of the productive controller: fewer than 26,000 events, |q|+1 < 2¹⁶, local growth bound 2^(16·26000) = 2^416000)
* Events: 123,860 here, 222,128 in #6884, 172,166 in #6883: all above 26,000 (read literally the bound is 2^(16·events)).
* Sum of log2(1+|q|) over the ADD coefficients, the actual local growth exponent per call: 171,846 here, 309,379 in #6884, 196,440 in #6883, against 416,000; below it in all three.
* This word: peak |row entry| on any prefix 2^15.5, peak row denominator 2^17, coefficient bits at most 18 (numerator) and 14 (denominator), largest |q| 5208, far below 2¹⁶. (An earlier version of the same invoice with unsolved gate blocks, 331,219 events, reached 2^25.9, 2^21, 27/18 bits and |q| = 523541/8, 93 under 2¹⁶; it is not the shipped word.)
* `check.py` computes all of these on the word it is given.

## The BIT pin
The pin is the ordinary BIT saving 0.00376669 (`ordinary_admitted` of the pinned #6726 admission, status `PASS_TWO_FRAGMENTS_BIT_ORDINARY_00376669`), as in #6884; the margin from the tested price is 3.4e-4. The ledger passes at the tested price 0.00342928907 (all 54 strict and 4 functional inequalities positive). The claim is above main's admitted 0.0034 and below main's ordinary BIT stock 0.00343635 (`research/query-thinned-controllers/RESULT.json`, `ordinary_saving`; `docs/research/pr-intake-evidence/pr4470/PROOF-REVIEW.md:175-177`); the ledger also holds at the savings 0.00343 (margin 7.1e-7) and 0.00343635, which would not need an open pull request, but those are not admitted savings and are not used. A control with a saving just under κ + 4·gap is rejected. The input-lift saving lemma of #6833 (pricing.py:128-156) has its cap moved to the pin and passes. The logarithm power 2100 is a free parameter (minimum 2081 at this price, valid up to a tested price of about 0.00346); its theorem in `research/higher-moment-strictification/vendor/LOG-MAJORANT.md:110-122` is stated with an integer q, its literal conditions (3) and (4) fail for the real exponent used, and the code uses the same argument with 1/q replaced by a real p (conditions theta_bar^p < eta, m^(1-t) < 2^p, (1+H)^p < 2^((z−t)H)); a reviewer of #6884 re-walked that replacement, I did not.

## Inherited, stated here
**A6, owned ascent (load-bearing: no ascent, no word):** an owned nested rise costs one paid H_r plus rank-0 adapters, no credit, on arbitrary contents, factorwise at every width, with CLEAR at any frame under owned_erasure. The one-line rule change, both verifiers (the strict one rejects this word at exactly the 23 events), the direction-free cost argument and the evidence read at the base commit (FP:258-268, pr4416 PROOF-REVIEW:115-117, `05-layers.tex:83`, the P112 backward word, #2479) are in `PROOF-OWNED-ASCENT.md`. Direction-based lower bounds (#6315 Lemma S, #6229, #6257, #6831, and the c ≥ 56 input of #6881) are scoped to words whose owned registers only descend.

| class | departure (recomputed by `check.py`) |
|---|---|
| convention (A6) | owned ascent, native.py:55 / local.py:126: 23 events, rank mass 56; two owned reads of a main Y register (above) |
| verifier | endpoint literal native.py:75-77 / local.py:168: the hosted target replaces `X = x, Y = x + y` on the 104 main pairs |
| verifier | events 123,860, public 1371, owned roles 51, 54 lifetimes, peak 25 (local.py:52,54,103; pricing.py:84-87) |
| verifier | per-call scalar work 11,477,894 against the displayed 10⁷ (pricing.py:93) |
| verifier | caller coefficient height 9 and 8 bits against 8 and 7 (pricing.py:96-97) |
| convention | LAMBDA: 82 caller events, a two-term scalar pass at width ≥ 2, inherited from the open callers #6726 and #6763; no compiler list names it and it is not on main; the text does not decide whether it is a scalar or a routing pass. Verified algebraically by the composition replay, counted in ordinary work, no physical contact check |
| convention | root family N = n + 2, two units per stage (chain_root.py:79,82,83,98; check_root.py:26,133,141-145) |
| convention | one-site idles: a rank-8 one-field idle is a whole job by the compiler definition (FP:23-26); IDLE_ONE comes from the open #6716 and #6726. The 36×104 are paid whole H8 idles in P[8]; targets get nothing for them. Priced as eight rank-1 jobs each, κ would be 0.003006 |
| assumption | dirty owned erasure (the existing owned_erasure assumption) |

## Outer statement
Cutoff 11, floor 12, offset 1/7, power 1920 hold unchanged: α = 0.9999999994, γ = 0.9465, δ = 0.8553 (< 31/32); the composite bound 1/(1+power·reserve) + 4·decay^power < 1 holds; η > (63/64)²¹⁰⁰ at maximum target rank 145; the 54 strict and 4 functional outer inequalities are positive (their smallest value is the chosen parameter r0 = gap/10, not a measured margin). Both interval engines bracket the crossing.

## Check
`check.py` (about 55 s): exact event replay; strict and relaxed verifiers with the rejection control; root checker; composition at four central characters with the pair read from the root and controls; invoice rebuilt from word, root and caller, with the #6884, #6883 and #6833 words as comparison controls; the three raw figures; the growth figures; the two owned reads of Y; interval engines; pin, input-lift lemma, logarithm power, strictification, compiler and outer ledger; departures.
`ordinary.py` (a few seconds): the raw figures. `cover_check.py` (about 25 s): the counts and controls above. `physical.py` (about 30 s): all events as 512-component streams over F_p[i] (p = 10⁹+9), chart predictions, raw main-pair identities by tableau and phase on all 104 ports, with controls. `caller_physical.py` (about 15 s): the caller's physical replay through the retained independent physical audit (one declared line changed for A6): 7488 contact phases, reverse cross term, main targets, whole idles on every owner and port, field map and alias control, invoice, adapters, controls.

## Not claimed, and not independently examined
No frontier change; no claim without A6 and the pin of #6726; the precision-tape and compiler assumptions are not discharged. Not independently examined: the adjoint (transpose) physical replay of this word; streams at tensor width 2 or more (only width 1 and the ring replay were run; width 3, Q = −i, not run); the BIT verifiers (the ledger passes at the pins 0.00343 and 0.00343635, but no BIT admission was re-run); the builders' derivation of the weights; the compiler texts beyond the parts quoted in `PROOF-OWNED-ASCENT.md`. The physical replay uses one prime and one random input per run. `data/word.json.gz` is the only word input; a word with the same invoice can replace it, and the constants asserted in `check.py` and `cover_check.py` (counts, event numbers, raw figures) are the ones to update.

## Open next questions
1. Is owned ascent (A6), with the two owned reads of a main Y register, accepted for the native verifier, as it is in the P112 native?
2. Is the BIT pin 0.00376669 of the open #6726 admission accepted above the retained 0.0034, or can the pin of the merged ordinary stock be admitted instead?
3. Does the conservative raw count 1,006,146,280 matter for the precision and tape contract, or can the gates be rebuilt a little smaller so that it falls under 10⁹?
4. Are the single-field idle (IDLE_ONE) and the two-term LAMBDA pass of the open callers admitted to the compiler's job list?

## Credit
Builds on #6883 (hosted pair at every call of the chain-nested root; the base of this package: its root, caller and checks), #6884 (the shared cover, deletions and BIT pin), #6833 (chain-nested root, invoice and outer ledger), #6726 (zxv, two-pair root caller; the BIT admission used for the pin), #6716 (thu-nmrc, common idle fusion), the #6702 native source by DreamingOfClouds with the helper-basis mechanism of Ali Romman and the retiming and helper-retirement extension of Jerry Chen / @CubeJerry (#6805, #6824), the retained interval engines and Clifford compiler of their authors.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
