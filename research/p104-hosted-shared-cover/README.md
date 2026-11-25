# Conditional κ = 0.00341603 from a tighter shared cover of the hosted native, on the BIT pin of #6726

**Result.** κ = **0.00341603288178402** (exact-kernel crossing of the complete signed invoice), up from 0.00339993013239573 of #6883 by **+0.4736%** and from 0.00337180047549672 of #6833 by +1.3118%.
The claim for the outer statement is κ = 0.00341603 with tested price 0.0034160307 (grid 10⁻¹⁰); the raw crossing lies in (0.003416032881784, 0.003416032881785).
The package builds on #6883 (hosted pair at every call of the chain-nested root, fork commit 3652e9191) and keeps its root, caller and hosted pair (α, β) = (−1, 1/2), t = −1/2; only the native word and the BIT pin change.

**Conditional statement.** The result holds under the five framework assumptions of #6833, under assumption A6 (owned ascent) exactly as declared in #6883, and **under the BIT pin 0.00376669 taken from the open #6726**; it depends on all three.
This κ is above the pin 0.0034 of main, so without a higher admitted BIT saving the outer statement does not cover it. #6726 and #6883 are open pull requests; the BIT admission is read from the pinned file `retained/bit/FRAGMENT-BIT-ADMISSION.json` (git blob 482f9525…, sha256 86955dcd…, #6726 head 435bbe91) and is not re-derived here.

## The BIT pin
The ordinary BIT saving 0.00343635 (`research/query-thinned-controllers/RESULT.json`, `ordinary_saving`; `docs/research/pr-intake-evidence/pr4470/PROOF-REVIEW.md:175-177`, "above the admitted .0034") is the stock above main's admitted 0.0034. It is above this κ, but it is not an admitted saving, so using it instead of #6726 (it is admitted conservatively as 0.0034, `docs/research/bottleneck-brief.md:17-18`; the ledger lines pass at 0.00343, the BIT verifiers not re-run) would itself need an admission; it is not used.
The pin used is `ordinary_admitted` = 376669/10⁸ of the #6726 two-fragment BIT admission (status `PASS_TWO_FRAGMENTS_BIT_ORDINARY_00376669`, raw BIT crossing above the BIT tested saving 0.0037667). The ledger takes it as `bit_saving`; the margin from the tested price is 3.5e-4. A control with a saving just under κ + 4·gap is rejected.
The second hidden 0.0034, the cap of the input-lift saving lemma of #6833 (pricing.py:128-156), is moved to the pin and checked (its crude bound holds up to about 0.0037765). The logarithm power 2100 is a free compiler parameter; it follows the existing `p`-form used at `research/balanced-query-tree/pricing.py:95-107` (the integer-`q` form of `LOG-MAJORANT.md:110-122` does not apply literally here), and its minimum at this price is 2073 (η 6.65e-15 > (63/64)²¹⁰⁰ = 4.34e-15).

## What changed against the #6883 word (counts measured on the two words by `cover_check.py`)
The forward network is no longer the #6824 word verbatim, so correctness does not rest on a black-box argument: the whole word is replayed exactly.
* 342 ADD events of the core (first to last MOVE) are deleted; the core loses exactly 342 ADDs and no other event kind but MOVEs. These deletions are not no-ops: none of the 342 leaves T unchanged on its own, and the changes fall in blocks the rebuilt gates correct, so their correctness rests only on the exact replay. They hold jointly under the exact endpoint test; controls show that removing the first core ADD, duplicating an ADD (a wrongly restored one), and removing sampled ADDs are all rejected.
* Silent helpers (no ADD, COPY or SCALE) are dropped: the #6883 word has 22, this word none; each is one MOVE whose rank equals its target rank, so targets and paid lose the same job. Public registers 1403 → 1385, MOVEs 6734 → 6679.
* The search reports 26 silent helpers removed from its intermediate word and 2 cross shares (a mirror helper placed on a different forward helper's register). Neither count is recoverable from the shipped words alone (a cross share is not distinguishable from a self share when two helpers have equal stop frames); the replay checks that the endpoint is exact with whatever sharing is present.
* Gates are rebuilt per word. Events 172166 → 222128; peak owned fields 13 → 25; owned lifetimes 54. Owned ascent is unchanged: 23 events, rank mass 56, and the same lifetime shapes as in #6883 (19 lifetimes with rises, 3 read before the rise, 3 with contacts between rises, none both rising and falling, same start frames), so the list of what goes beyond the P112 precedent is unchanged.
* Targets: 38×104 diagonal fields plus 1177 helpers per call (#6883: 1195); 6679 paid moves per call. S = 656 + 48·18 = 1520, already net of 56 per hosted call. New = 2 × base + 29759.8 (hosted word) − 29740.0 (36 whole H8 idles per port) = net +19.80 at the crossing.

## Inherited from #6883, stated here
**A6, owned ascent (load-bearing: no ascent, no word):** an owned nested rise costs one paid H_r plus rank-0 adapters, no credit, on arbitrary contents, factorwise at every width, with CLEAR at any frame under owned_erasure. The one-line rule change, both verifiers (the strict one rejects this word at exactly the 23 events), the direction-free cost argument and the evidence read at the base commit (the compiler text FP:258-268, pr4416 PROOF-REVIEW:115-117, `05-layers.tex:83`, the P112 backward word with its accumulate-first lifetimes, #2479) are in `PROOF-OWNED-ASCENT.md`. What this word does beyond P112 and no sentence decides: lifetimes read before the rise, contacts between rises, nonzero start frames, both directions in one word and gauge. Direction-based lower bounds (#6315 Lemma S, #6229, #6257, #6831, and the c ≥ 56 input of #6881) are scoped to words whose owned registers only descend.

| class | departure (as in #6883; counts recomputed by `check.py`) |
|---|---|
| convention (A6) | owned ascent, native.py:55 / local.py:126: 23 events, rank mass 56 |
| verifier | endpoint literal native.py:75-77 / local.py:168: the hosted target replaces `X = x, Y = x + y` on the 104 main pairs |
| verifier | events 222128, public 1385, owned roles 51, 54 lifetimes, peak 25 (local.py:52,54,103; pricing.py:84-87) |
| verifier | per-call scalar work 12,788,136 against the displayed 10⁷ (pricing.py:93) |
| verifier | caller coefficient height 9 and 8 bits against 8 and 7 (pricing.py:96-97) |
| convention | LAMBDA: 82 caller events, a two-term scalar pass at width ≥ 2, inherited from the open callers #6726 and #6763; no compiler list names it and it is not on main; the text does not decide whether it is a scalar or a routing pass. Verified algebraically by the composition replay, counted in ordinary work, no physical contact check |
| convention | root family N = n + 2, two units per stage (chain_root.py:79,82,83,98; check_root.py:26,133,141-145) |
| convention | one-site idles: a rank-8 one-field idle is a whole job by the compiler definition (FP:23-26); IDLE_ONE comes from the open #6716 and #6726. The 36×104 are paid whole H8 idles in P[8]; targets get nothing for them. Priced as eight rank-1 jobs each, κ would be 0.002995 |
| assumption | dirty owned erasure (the existing owned_erasure assumption) |

## Raw bound (parameters; the constant substitution of FP:278-283 is written by `check.py`)
Literal definition (18 × 10⁷ + caller, thin, output and adapter terms): 948,952,288 < 10⁹. With the actual per-call work (18 × 12,788,136 + the same terms): **999,138,736 < 10⁹, margin 0.1% (861,264)**. With the review's more conservative per-call count (reviewed scalar upper 5,860,168 + routes 9,873,000, 18 × 15,733,168): **1,052,149,312, which exceeds 10⁹ by 5.2%**, more than #6883's 1,019,551,024.
The substitution: events 222128; scalar allowance 2,915,136 or reviewed upper 5,860,168; routes 9,873,000; caller envelope 258,618,880; coefficient denominator height 14 bits. No term of the outer ledger reads the 10⁹ (`check.py` verifies that the ledger source has none); it is a finite parameter of the precision and tape contract, which is not re-examined here.

## Outer statement
Cutoff 11, floor 12, offset 1/7, power 1920 hold unchanged: α = 0.99999999723, γ = 0.9458, δ = 0.8595 (< 31/32); the composite bound 1/(1+power·reserve) + 4·decay^power < 1 holds; η > (63/64)²¹⁰⁰ at maximum target rank 145; the 54 strict and 4 functional outer inequalities are positive (their smallest value is the chosen parameter r0 = gap/10, not a measured margin). Both interval engines bracket the crossing.

## Check
`check.py` (about 55 s): exact event replay; strict and relaxed verifiers with the rejection control; root checker; composition at four central characters with the pair read from the root and controls; invoice rebuilt from word, root and caller, with the #6883 word (comparison control) and #6833 rebuilt by the same code; raw bound; interval engines; pin, input-lift lemma, logarithm power, strictification, compiler and outer ledger; departures.
`cover_check.py` (about 15 s): the counts above and the ADD controls. `physical.py` (about 35 s): all 222128 events as 512-component streams over F_p[i] (p = 10⁹+9), chart predictions for helpers and both main outputs, the raw main-pair identities by tableau and phase on all 104 ports, with controls. `caller_physical.py` (about 15 s): the caller's physical replay through the retained independent physical audit (one declared line changed for A6): 7488 contact phases, reverse cross term, main targets, whole idles on every owner and port, field map and alias control, complete invoice, adapters, controls.

## Not claimed, and not independently examined
No frontier change; no claim without A6; no claim above the pin 0.00376669; the #6726 BIT admission is not re-derived; the inherited precision-tape and compiler assumptions are not discharged. Not independently examined: the adjoint (transpose) replay of this word; the tensor-width-3 (Q = −i) sector, where only widths 1 and 2 were run; the compiler texts beyond the parts quoted in `PROOF-OWNED-ASCENT.md` (the Lean development only in part, the PR1673 notes by search). The physical replay uses one prime and one random input per run.

## Open next questions
1. Is owned ascent (A6) accepted for the native verifier, as it is in the P112 native?
2. Is the BIT pin 0.00376669 of the open #6726 admission accepted for the outer statement above the retained 0.0034?
3. Are the single-field idle (IDLE_ONE) and the two-term LAMBDA pass of the open callers admitted to the compiler's job list?

## Credit
Builds on #6883 (hosted pair at every call of the chain-nested root; its word, root, caller and checks are the base of this package), #6833 (chain-nested root, invoice and outer ledger), #6726 (zxv, two-pair root caller; the BIT admission used for the pin), #6716 (thu-nmrc, common idle fusion), the #6702 native source by DreamingOfClouds with the helper-basis mechanism of Ali Romman and the retiming and helper-retirement extension of Jerry Chen / @CubeJerry (#6805, #6824), the retained interval engines and Clifford compiler of their authors.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
