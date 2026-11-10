# Conditional κ = 0.00362702 (+0.087% over #6934): seven main contacts on shared wires

**Result.** The exact-kernel crossing of the complete signed invoice is **0.0036270188295951444**, which is **+0.0872% over #6934** (crossing 0.0036238597350766513; ratio − 1 = 0.00087175). This package makes no other comparison.
The claim for the outer statement is **κ = 0.00362701882** with tested price **0.00362701882007** (grid 10⁻¹⁴; the whole ledger, 54 strict and 4 functional inequalities, is run at that price), both strictly below the raw crossing, which lies in (0.003627018829595, 0.003627018829596).
**This is the declared framework change of #6932 and #6934, unchanged in kind and in clause.** The word uses gate scalars 1/3 and 1/5, outside the dyadic scalar alphabet of the native verifiers, with the certificate S = 1125 = 3² 5³. Maintainers must accept the clause; acceptance is not claimed and the result depends on it. Everything else that #6934 assumes is assumed here too.
**Credit first.** The odd-denominator grid is merged **#104 by icekylinx**. The type A caller blocks are **CubeJerry (#6912)**, taken as data; the owned-rise argument in `check_a6.py` is **CubeJerry (#6914)**; the width-2 phase test is **unpaidmoon (#6930)**; the helper-split lemma is **Ali Romman** (#5599) and its application to the shared native word is **CubeJerry** (#6916). The word is #6934's word with the moves below.

## The move, in plain language

Seven direct main-to-main contacts are moved onto one new shared public helper wire each, with F and R reading the same wire, after a legal reorder of commuting events that lets their rests overlap at a stage frame. Two of the seven wires are then each split in two plain helpers (the second starts at the frame where the first ends). 7 wires and 2 split tails are added (public registers 1,461 against 1,452), 70 events are removed (56 MOVEs of mains and 14 contact ADDs) and 145 are added (88 ADD, 49 MOVE, 8 SCALE); 70,999 events are common. D is lower by 362.43 over the 18 calls (422,589.15 to 422,226.72) and S = 1520 is unchanged. The invoice reads each paid job by its rank (per MOVE) and each helper by its credit; it does not read a count of stops.

`check.py` recomputes each of these statements from the two words (step 1c): the multiset difference after renumbering; that every added ADD touches a new register; that each removed ADD joins two mains; that the new registers ascend and the two split pairs are plain (credits 7 + 1 and 7 + 1 against the unsplit credit 8); that for the 70,999 common events each of 1,503 registers sees the same ordered sequence of access classes (0 differ), so every read sees the value it saw in #6934's word; and that the 28 partner registers' MOVE chains are endpoint-preserving subsequences of their old chains with equal rank change.

## What changed against #6934

- **The word.** 71,144 events, 1,461 public registers, 1,061 helpers. The frame table, live set, hosted pairs, ports, initial and final frames of the old 1,452 public registers, the 54 owned lifetimes (as a multiset), the 47 owned MOVEs (as a multiset), the 51 owned fields, the 23 owned rises (mass 56) and the 16 owned reads of mains are identical to #6934's. T gains per call two rank-1, four rank-7, two rank-8 and one rank-9 fields; P changes as printed by `check.py`; both rank masses rise by 55 per call.
- **The owned peak.** The peak of concurrent owned fields is **43** against 40 in #6934: nine owned INITs are hoisted earlier, a retiming of exclusive accesses with nothing else changed on the owned side. The A6 declaration is for 23 rises of mass 56, 51 owned fields and a peak of 43.
- **The certificate.** S = 1125; 375 and 225 are rejected at events 36997 and 1103. Odd divisions per call: 4,143 (64 SCALE, 4,079 ADD), 8,286 scans. Width per unfinished context is unchanged: 2-adic height 24 bits, magnitude 36.54 bits, so 80 t < d (placeholder caller mass) and 362 t < d (quoted majorants, not recomputed on this caller).
- **The caller** is #6934's (the #6912 type A blocks; saving 159,498,240 at 96 A ports in every raw reading).
- **The opening-gauge clause.** The clause of the dyadic words' joint check "the first 8 SCALEs are the 8 hosted-port gauge SCALEs" is no longer literally true: seven of the eight gauge SCALEs are events 5 to 11 and the eighth (register 30) is event 29089. It is replaced by "each hosted-port main X has its first SCALE by 1/2 before its first use", asserted by `check.py`. The gauge is covered by the exact endpoint in any case.

## Statements of #6934 that this package changes

1. "71,069 events, 1,452 public registers, a full rebuild, one more public helper register": 71,144 events, 1,461 public registers; the word is #6934's plus the moves above, and the gain is the sum of seven contact moves and two splits, recomputed in `check.py`; it is measured against #6934 only.
2. "The peak of concurrent owned fields is 40": 43.
3. "375 and 225 rejected at events 36915 and 1101": 36997 and 1103. "4,125 odd divisions (60 SCALE, 4,065 ADD), 8,250 scans": 4,143 (64, 4,079) and 8,286.
4. The literal first-8-SCALEs gauge clause: replaced, as above.
5. "Logarithm power minimum 2223, written 2224": minimum **2225** (2224 and 2223 fail), written **2226**. BIT pin margin: .00376669 − .00362701882007 = 1.397e-4; the ledger passes all 54 + 4 inequalities there and fails at every other listed saving.
6. Raw figures: literal 802,809,952; actual 815,970,652; reviewed scalar upper 832,255,648; 844,815,648 with the second LAMBDA count; 834,990,640 and 847,550,640 with a conversion on every call (104 per input × 1,461 × 18). All below 10⁹, least margin 152,449,360. With #6932's caller the recharge readings would exceed 10⁹, so the new caller is still needed.
7. 61,053 ADD mutants with seven uncaught (see Disclosures); 3,234 native chart maps; 148,332 divisions in the integer run (F = 33; F = 32 and F = 31 fail at event 61461); largest numerator 14,729,531 first at event 252; K_star log2 14,072.3 at the written H = 14,161,600,000,000,000,000.

Every other statement of #6934 stands unchanged, including the clause and its corrections of #6932.

## Conditional statement

The result holds under the five framework assumptions of #6833; under assumption A6 (owned ascent) as declared in #6883 (23 owned rises, rank mass 56, 51 owned fields, peak 43, 16 owned reads of mains); under the BIT saving of the open #6726 (necessary); under the forms declared in #6919 and #6931 (splits, sinks, valves, flips, the per-port root, the reducible type A root and its three family lines, the per-port root pair, the joint contact, HOST2, same-label second mains, LAMBDA, IDLE_ONE, the shared-helper accounting); under the type A caller blocks of #6912 as data; **and under the clause: odd gate scalars with a prefix certificate, exact only for exact child returns.**
**Premise declared here, which #6934's body does not state (no change to the claim).** Each chain root has one empty-mask field E (type A roles 19 and 39: **192 productive targets of rank 1** over the 96 two-chain ports; `check.py` recomputes the count from the invoice). It is credited by the same rule as every root field (rank 1 + 8 |mask|) and fed by the caller as an independent array (9 ADD and 6 SWAP events, and it enters the three thin queries). The hosted type B root has no such field. The same applies to #6919, #6931, #6932 and #6934.
- If these 192 credits are refused with the paid jobs unchanged, κ here is **.00316585** (−12.71%), computed by `check.py` from the invoice (#6934's word: .00316310, −12.71%).
- E is a size count of a real output: a rank-1 job on an arbitrary independent array, resting on the `compiler` and `native_all_columns` premises already listed. No merged or selected invoice has an empty root field, so maintainer acceptance of one as a productive credit is not claimed.

## Checks

Eight commands within the 1,200 s limit (`VERIFY.json`): `check.py` (exact replay with the S certificate, endpoint, invoice, the move against #6934's word, controls, raw figures, outer ledger), `controls.py` (28 odd-verifier controls), `physical.py` (512-component streams), `physical_exact.py` (the integer run of one column), `caller_physical.py` (the joint caller), `native_maps.py` (3,234 chart maps), `mutants.py` (the second engine with all ADD and SCALE mutants) and `small_checks.py` (second engine, division pass, caller blocks with 12 failing controls, `check_a6.py`, raw recount). Validator: `python3.12 -B scripts/research_package.py --package research/p104-main-wire-native`.

## Disclosures and not claimed

- **Second-reader model replay only, no human review.** An independent model-run reader replayed the word, its diff against #6934's word, the mutants and the chain. No human has reviewed the word or the package.
- **7 of 61,053 ADD mutants are not caught** (events 33201, 37661, 39201, 40052, 40053, 40076, 42666): each leaves the exact endpoint unchanged under both doubling and negation. Six are dead stores into owned registers cleared before any read; event 42666 (ADD 1485 += −769, then ADD 769 += 1485) is a temporary pair that cancels downstream. They are equivalent mutants, shown by exact replay; none touches a helper wire or any added ADD.
- **The truncated-child control is weak below 14 bits.** At F = 33 it rejects truncations of 14 and 24 low bits per MOVE and does not see 13. The integer run is one column with generic commuting frames, not true Clifford frames and not width 2.
- **Quoted, not recomputed:** the caller majorants behind 362 t < d, on #6934's caller (this package's caller is the same).
- **Rounded child returns** are outside this package.
- **Not claimed:** maintainer acceptance of the clause, of A6 (peak 43), of the per-port root, of LAMBDA priced as ordinary work, of the BIT admission (#6726); the type B caller rewrite; joint width 3 or more.
- **The E credit (192 rank-1 targets) is declared, not shown acceptable.** A root with no E and one thin query fewer per chain would leave T[1] and P[1] dropping together, so κ and S unchanged; that root is argued by hand and not replayed, and it is not claimed here.

## Raw bound, logarithm power (recomputed by `check.py`, `check_caller_blocks.py`, `small_checks.py`)

Raw: literal 802,809,952; actual 815,970,652; reviewed upper 832,255,648 (margins 197.2M, 184.0M, 167.7M). Logarithm power: minimum 2225, written 2226 (carrier 153). Growth: events 71,144 (ADD 61,052, COPY 1, SCALE 3,660, MOVE 6,323, INIT and CLEAR 54 each); largest |q| 227445/8 = 28,430.6 (|q|+1 < 2^16); sum of log2(1+|q|) 82,828 against the retained 416,000 line.

## Open next questions
1. Do maintainers accept odd gate scalars (alphabet A = Z[1/2, 1/3, 1/5] with a declared prefix certificate S), exact on exact child returns, for complex native words?
2. What are the caller majorants for this package's caller, and does 362 t < d hold with them?
3. Is the declared owned ascent (A6: 23 rises of mass 56, peak 43, 16 owned reads of mains) accepted for the native verifier, and does the width-2 phase test extend to joint width 3 and to all maps?
4. Is the BIT saving .00376669 of the open #6726 accepted for the outer statement?
5. Are a per-port root, a reducible type A root, LAMBDA and IDLE_ONE priced as ordinary work admitted forms?
6. Can the remaining main-to-main contacts that this reorder could not free be moved by a retime of the main chains? (Not tried here.)
7. Is the empty-mask root field E (192 productive rank-1 targets, κ .00316585 without them) accepted as a productive credit? Is a root with no E and one thin query fewer per chain admissible, and does it leave κ and S unchanged as argued?

## Data

The word is `data/word.json.gz`. `data/prior_word_6934.json.gz` is the word of #6934 (comparison); `data/prior_word_6932.json.gz`, `_6931`, `_6919`, `_6917`, `_6911` are controls of the invoice code. `data/caller.json` is #6934's caller; `data/caller_old.json` the caller before the #6912 blocks; `data/caller_6912_before.json` and `_after.json` are #6912's source and result, read as data.

## Credit

**icekylinx** (#104, the odd-denominator grid); **CubeJerry** (#6912, #6914, #6916, #6805, #6824); **unpaidmoon** (#6930); **Ali Romman** (#5599). Builds on #6934 (the word this one is compared with), #6932, #6931, #6919, #6917, #6911, #6902, #6889, #6833, #6726, #6716, the #6702 native source by DreamingOfClouds with the helper-basis mechanism of Ali Romman and the retiming and helper-retirement extension of Jerry Chen / @CubeJerry, and the retained interval engines, native verifier and Clifford compiler of their authors.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
