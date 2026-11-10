# Common odd grid for a native word: clause change and proof

Status key. **Proved**: follows from the statements below. **Replayed**: checked by exact rational replay of the one stated word (`check.py`, all 67,079 events), not a proof for other words. **Assumed**: stated hypothesis, not shown here.

## 1. What changes

Changed clauses, by name:

1. The scalar alphabet of the native word. Until now ADD and COPY coefficients, and SCALE units, are dyadic (`local.py` lines 146 and 149, the verifier copies, and `native.py` line 65). They become elements and units of the ring A = Z[1/2, 1/3, 1/5].
2. The Gaussian dyadic text of `03-motifs.tex` (lines 57 and 556), for the internal arrays of one parent word only. Completed endpoints, and every public role, stay Gaussian dyadic.
3. The scalar-alphabet constants in the #6900 and #6901 proofs, which are specific to #6030.
4. One added operation in `05-layers.tex` (lines 510-513): multiply by an integer, check divisibility, divide.
5. The clause of the joint check of the dyadic words "the first 8 SCALEs are the 8 hosted-port gauge SCALE 1/2" is not used: it is false for this word (the gauge SCALEs sit at events 24,278 to 26,587), and the gauge is covered by the exact endpoint X = x - y, Y = (x + y)/2. `check.py` prints it as information.

Nothing else is changed. The sets T and P differ from the baseline word only as counted in `check.py` (ten more helper registers, 39 merged stops); the rank mass S = 1520, the peak of 36 owned fields, and the 51 owned fields are those of the baseline word (section 5).

Precedent. The method is the merged one-root-scale odd-denominator grid of #104 by **icekylinx** (`notes/stopped-product-complex.tex`, lines 75-106: the average G = (1/21) sum A_i, a single numerator scale 21^K at the outer boundary, exact division, exact unscaling; lines 93-98 state the same invariant), and the merged odd-grid reviews that accepted its scope: `research/centre-metric-encoders/frozen/lanes/independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID.md` lines 4-8, `.../reciprocal-centre-rank-review-20261018/ODD-GRID-COMPOSITION.md` lines 10-48, `.../bridge-review-20261017/odd-grid-a8-review-20261017/REVIEW.md` lines 3-13, and `research/centre-code-services/frozen/lanes/native-escape-20261017/rational-code-admission-20261020/CLIQUE-CODE-GRID.md` lines 165-197, which states that the code grid "does not require every local coefficient to be dyadic". The statement here is that grid with divisors 3 and 5 in place of 21, with one scale S applied to the root inputs as in #104. No merged word on the record line uses it for a P104 native, as far as was found.

Texts a reviewer may raise, none of them a prohibition: `research/p104-integer-error-replay/README.md` line 54 ("nondyadic needs a new representation contract", which this section is), the literal "dyadic scalar alphabet" and a rejected 2^20/3 control in the #6901 verifier, a rejected 1/3 word in the #6900 controls, and `02-streams.tex` lines 198-200, which list only power-of-two division as streaming and so permit rather than forbid the pass of section 5.

## 2. Replacement clause

A native word may use ADD and COPY coefficients q in A with |q| + 1 < 2^16 (this bound is kept exactly as before), and SCALE by units of A (numerator and denominator products of 2, 3, 5), with frames as before, provided it declares S = 3^e 5^g such that:

- (i) for every prefix of the program, S times every row has entries in Z[1/2];
- (ii) for every ADD or COPY, S times the product q times the source row, formed before the addition, has entries in Z[1/2];
- (iii) every public output row of the complete word has entries in Z[1/2].

Execution: multiply every input numerator by S once at the root; for a coefficient a/b with b = 2^x 3^y 5^z, multiply by a, check divisibility by 3^y 5^z, divide; at the root exit divide by S. Rows are formal (the vector of coefficients of the inputs), so (i) to (iii) are finite checks on the word, independent of the inputs and of the tensor width f. `verify_host3_odd.py` checks A-membership, the |q| bound, (i), (ii) and (iii) event by event; `controls.py` runs its rejections (S = 75, 45, 15, 25, 9 and 1; a coefficient 1/7; a SCALE by 1/7, 7 or 3/2; |q| + 1 >= 2^16; a non-dyadic public row; cancelling pairs of 1/7 and of 65536; and the dyadic baseline word as the S = 1 control).

## 3. Theorem and proof

**Theorem (proved, conditional on exact children).** Suppose the word satisfies (i) to (iii), the root inputs are Gaussian dyadic, and every completed child returns the exact Gaussian-dyadic value of its operator. Then every stored value lies on the dyadic grid, every checked division is exact, and the word's output equals its exact action on every Gaussian-dyadic input, at every f, including dirty and correlated spectators.

Proof.

1. Work over R = A[i]. It is commutative and contains Z[i, 1/2]. The frames are matrices over Z[i, 1/2], and scalars from R are central, so the common-frame identity of `03-motifs.tex` (lines 168-175) holds with coefficients in R. The same holds for the Clifford representatives (`general-clifford-frames.tex` line 62).
2. The stored array on register r after any prefix is D_v applied to (S times the sum over inputs k of R_{r,k} x_k), where R_{r,k} are the row entries and D_v is the frame matrix. By (i), S R_{r,k} is in Z[1/2], and D_v has Gaussian dyadic entries, so the stored values are Gaussian dyadic. This is an identity in the formal inputs x.
3. Division by a/b: before the division the stored value is a times S q R_s x with S q R_s in Z[1/2] by (ii). Hence it is divisible componentwise by the odd part of b on the grid (#6901 lines 276-278), and the quotient is again on the grid.
4. By (iii) the root exit division by S is exact, and the result is the logical output.
5. Scalars are not raised to tensor powers (FINITE-PRECOMPILATION lines 247-248), so S does not depend on f.
6. Composition. Each unfinished context multiplies numerators by at most S, so debts add along the active chain only. A completed child returns a Gaussian-dyadic row (by the premise), so it adds no odd factor at exit (the active-path argument of `ODD-GRID-COMPOSITION.md` lines 33-48).

The endpoint of the word is the same kind as the dyadic word's, so the caller, contact, host and controller identities are unchanged, and the word is one atom to its caller. Quantizers act on stored cuts, which lie on the grid; their identities need F and W recomputed, not their form. Magnitude contract: `05-layers.tex` line 875 binds only the outer proposition; the recursive child is in the common guarded format with no disk contract.

## 4. Width

The cost is width only, and it is per unfinished context, not per ordinary node.

- Live nesting is the number of unfinished raw contexts t = K_star * ell (#6901 PROOF lines 88 and 191), where K_star is the per-level constant of that proof (7,455 bits there). It is not the ordinary node count, and an estimate of "8 bits times the logarithm of the node count" is not used.
- Per unfinished context, on the stated word: the 2-adic denominator height is **15 bits** (the odd part of any denominator is at most 225, 7.8 bits), and the magnitude is **37.48 bits** (log2 of the largest l1 mass of S times a row or product, scale included) [replayed, `check.py`]. The scale S itself is 7.8 of the 37.48 bits; the rest is row mass.
- Temporaries need |a| <= 40,864, 16 coefficient bits (about 17 more bits than a small coefficient) [replayed]; the `W + 6` of #6901 is a #6030 figure and is not reused.
- Sufficiency (argued, following #6901 lines 296-316): W = p + h + 2D + 3 remains sufficient once 2 (log2 10 + 37.48) t < d, about 82 t < d, using the #6030 caller mass 10 as a placeholder. This follows from K_star * 82 < 2^H as at #6901 lines 299-304. **Assumed**: K_star and the caller mass are recomputed for this word before the inequality is claimed (FINITE-PRECOMPILATION lines 278-283); they are not recomputed here.

## 5. What is priced, and what is not changed

- T, P, S = 1520, the peak of 36 and the 51 owned fields come from the frames and the MOVE blocks alone. T and P are recounted from the word by `check.py` against the baseline word: T gains ten helper registers (rank 2 +2, 3 +7, 4 +1, 5 +2, 6 +7, 9 -9), P loses 78 paid jobs of rank 1 and gains 39 of rank 2; the rank mass of both is unchanged, so S = 1520. The scalar passes are in place on existing fields, so no job and no field is added by the clause.
- The odd divisions are priced separately, as the reviewed text does (`CLIQUE-CODE-GRID.md` lines 9-11, `REVIEW.md` lines 10-11, `ODD-GRID` lines 122-123). The word has 3,001 odd divisions per call (59 SCALE and 2,942 ADD events), that is 6,002 scans per call (one multiply-and-check and one division each). Each is one least-significant-bit-first finite-state pass of 4(w_g + 1) head steps (`CLIQUE-CODE-GRID.md` lines 199-223), fitting the order of `02-streams.tex` lines 202-208; `division_pass.py` tests the pass exhaustively on widths 1 to 12 for the divisors 3, 5, 9, 15, 25, 45, 75, 225 (65,520 cases, 59,020 non-divisible inputs, all flagged). The upper formula's bit-length term covers the scans [argued]; quote the upper figure and the scan count.
- Raw counts, recomputed by `check.py` from the word: literal 962,308,192; actual per-call work 972,123,664; reviewed upper 985,187,200; all below 10^9. Conservative recharge: the reviewed upper already contains every LAMBDA event of the caller, and the second check of #6913 counts the LAMBDA translations a second time on purpose (12,560 jobs at 1,000 each = 12,560,000); with the scale applied once at the root, as #104 does, with no per-call charge, the total is 997,747,200. If instead every one of the 1,451 public registers were scaled on each of the 18 calls (80 x 1,451 x 18 = 2,089,440, an upper reading), the upper is 987,276,640 and with the second LAMBDA count 999,836,640, below 10^9 by 163,360. The root conversion is charged to the entry and exit at O(V (t + 1)) (`notes/stopped-product-complex.tex` lines 101-106). Scaling only the registers that carry an odd coefficient is not used: it is unsound, since inputs outside those registers carry odd coefficients at some prefix.

## 6. Exactness premise and fallback

Exactness is conditional. The statement "odd debt resets at each word exit" holds only for completed children that return the exact Gaussian-dyadic value. This is a premise the odd word shares with the dyadic words, which also need exact children, and it is **declared**: it is the exact recursion of #6901 lines 92-97 and 290-292 and #6900 PROOF lines 56-58 (no child-return rounding), and the hypothesis named in `ODD-GRID-COMPOSITION.md` lines 55-56 and `REVIEW.md` lines 11-13.

If a child's return is truncated to a coarser grid, the odd word is rejected by its own divisibility check: `physical_exact.py` shows rejection at event 26,563 (a SCALE by -1/45, "not divisible by 45") for g = 44 dropped low bits, and at event 24,158 for g = 50, while the dyadic baseline word under the same g = 44 truncation runs to the end and returns a wrong answer on 830 of 1,441 public rows. So neither is exact on a truncating child, and the odd word notices.

Fallback if a rounded return is ever needed: replace the exact divisions by rounded division. Measured exit-error gain over the stored truncation unit, on one input, on the earlier stage word in `data/stage_before_stops.json.gz` (not re-measured on this word, not a bound): 2^14.65 at g = 44 and 2^14.64 at g = 50, against 2^14.76 and 2^16.18 for the dyadic parent. The rounded-return error budget is open for both words, as in #6900 line 8, and is not specific to this clause.

## 7. Proved, replayed, assumed

Proved: the theorem of section 3 on exact children; the independence of S from f; linearity of each scan.

Replayed (the one stated word): all stored rows and pre-ADD products, times S = 225, are dyadic at every one of 67,079 events; S = 225 is minimal (75, 45, 15, 25, 9, 1 are insufficient); 0 bad of 1,451 public rows; no odd final row; the 3-adic and 5-adic heights are 2 and 2 with no other prime; the exact integer run on one column with generic commuting frames performs 140,162 divisions (64,350 by a non-unit), all exact; the debts of section 4; a second engine mod 2^61 - 1; streams over F_p[i]; every native chart map (3,230); the joint caller; mutants: all but five of the 57,023 ADD doublings are caught, and the five are shown by exact replay to leave the endpoint unchanged (four dead stores into owned register 1459, one coefficient-neutral temporary).

Replayed only (not proved): the 120 events rewritten by the retiming and the 76 events removed by the final same-frame rewrite are validated by exact replay of the final word, not by pairwise commutation; the commutation test of `reorder_check.py` covers the 66,895 matched events.

Assumed or not shown: exact completed children on every column; all root inputs dyadic; recomputed K_star and caller mass for the inequality of section 4; the actual P_r, the physical CLEAR and the LAMBDA pricing, as for dyadic words; a rounded child return. The physical run is one column, not true Clifford frames and not tensor width 2.

## 8. Sentences for the PR

1. Changed: the scalar alphabet of the native word (`local.py` lines 146 and 149, the verifier copies, `native.py` line 65), the Gaussian dyadic text of `03-motifs.tex` (lines 57 and 556) for internal arrays only, and the #6030-specific constants in #6900 and #6901.
2. Replacement: a common odd grid following #104 (`notes/stopped-product-complex.tex` lines 75-106) and the odd-grid reviews; rational operations stay local to the parent word; completed endpoints stay Gaussian dyadic on all public roles.
3. Hypotheses: exact completed children on all columns; a prefix certificate S = 3^2 5^2; all inputs dyadic at the root.
4. Penalty: zero in S; T and P change only as counted. Width is +15 denominator bits and +37.48 magnitude bits per unfinished context, absorbed in W = p + h + 2D + 3 by the written inequality; the 6,002 odd scans per call are priced separately; the root conversion is charged to entry and exit.
5. Not shown: a rounded child return, the actual P_r, the physical CLEAR, the LAMBDA pricing (as for dyadic words), K_star and the caller mass for this word.

Credit: icekylinx (#104) and the odd-grid reviewers for the grid and its composition argument.
