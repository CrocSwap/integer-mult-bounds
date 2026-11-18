# CongestionNative.lean (+ CongestionNativeTab.lean, PathCut.lean): the native-covering ceiling kappa <= .0136564
Copy of the own56 half of CongestionI3Dual*.lean (shipped files untouched), with the HC1-HC4 / AUD / AUD2 edits. Kernel only: no sorry, no native_decide; `#print axioms` of every theorem = [propext, Classical.choice, Quot.sound]. Builds (runlean.sh, one at a time): CongestionNativeTab 10 s / 1.3 GB, PathCut 4 s / 1.4 GB, CongestionNative 11 s / 3.0 GB.

## What changed against `ceiling_C2` (all done)
- hcong* has the owned surplus on the right: `Omega ks mr s = dprice ks s + mr - (6*9^s+10)`; ks = 24 descents + 13 non-unit rises (sum 102), mr = 10 unit rises (AUD FIX-1; the literal split gives Omega 16.1 < 24.8 and is out of class); stated only for s in [.9, 1 - tC0].
- `hE` generalised to `Lj <= E + Omega` (`E_lower_cap_om`, `branchC_om`). Omega cancels, so tC0 = .0136564 is unchanged. `branchC_om` needs no ks-hypotheses; hk/hmass/hmd/hmr are used only in the t >= .1 branch (own56_floor, 88c).
- ONE J: a single `J : Finset (ℕ × ℕ)` in hcong, hdist, hJ. It is J^arr (the arrival residual) by interpretation; Lean cannot see that, it is a name for the set the data hypotheses are about.
- FIX C: `Rank8C56`, `Prov`, `PlaneSep`, `MV` are gone. No bare `Prop` stands in for a condition. `ell`, `corr`, `cap` are concrete: `ellC spF s = min (spF (1-s)) (capC s)`, `capC s = (9^s-8^s)/48`, `corrC cstF s = 8 * cstF (1-s)`.
- `LcTabC` is no longer a hypothesis: it is DERIVED (`tab_piece`, `unit_mono` proved) from the rational tables of CongestionNativeTab (outward-rounded, emitted from hc9's 80-digit Decimals; the arithmetic `lcp_j + 8 cH_j <= 1936 min(spFlo_j, unitLo_j/48)` is norm_num-proved) and the hypotheses 11-13 below.
- PathCut.lean: `path_cut` PROVED (abstract: preorder of charts, monotone `Hold`, public edges ascend, owned edges NESTED (FIX A), confinement to G; conclusion: legal path, or a first owned strict descent dropping u_s with all earlier charts holding u_s and c_i <= G). `nested_needed`: Lean counterexample (lateral owned move {0} -> {1}) showing the nestedness premise cannot be dropped. `transported_card_le`: |Jt| <= 48 |V| from the 48-law and "every transported cell lies in cells(visit)".
- `hcong_of_capclass` PROVED: legal cells (charge `Pub + cst*Rm`) + transported cells (`<= 48 Nf`, cap U/48) + Cap class `cst (Rm-8) + U Nf <= Omega` give hcong*. It is the accounting of HC1 sec. 2, not used inside `ceiling_native` (which takes hcong* itself).
No paper statement was found false as written. Known and already encoded: hcong* fails for the natives at t > ~.507 (hence the s-range); the literal ks/mr split is out of class (hence FIX-1).

## `ceiling_native`: EVERY hypothesis (status for st1 / #7637 / x1t2a; "Lean" = what the kernel checked)
Lean treats R, n, ks, mr, st, E, J, distF, spF, cstF as abstract data. The statement is: IF the listed facts hold for these objects THEN F(1-t, invoice (caller 6 7) n 17) < 0 for t in [tC0, 1]. **That st1, #7637 and x1t2a satisfy the hypotheses (class membership) rests on the computed facts below, not on Lean.** One owned layer is shared by all three words (one data point, not three).
1. hmono, hd9 (public registers ascend, end <= 9): natives: computed fact (0 non-ascending public moves; WHOLEFLOOR/hcong/audit/au2.py, audit2/aud2a.py).
2. hmix (<= 5 mixed registers): natives: computed fact (hmix = 5, aud2a.py).
3. hk, hmass, hmd, hmr (ks/mr split, ranks <= 6 in [1,9], sum 102 >= 56, length 37 >= 8, mr 10 >= 8): natives: computed fact (au1.py, aud2a.py).
4. hF (F-currency identity, equality up to float noise): natives: computed fact (hc6.py, aud2a.py; needs all 400 mains to span 8).
5. hY (104 <= st + 47, st = 1266): natives: computed fact (aud2a.py).
6. hst (slack >= 158 on the grid; 0 only at s = 1): natives: computed fact (hc6.py, aud2a.py).
7. hEex (E >= sum of register excesses; identity): proved as an identity on the natives (hc6.py); open as a general lemma outside the natives.
8. **hcong\*** (sum_J min(dist,cap) - 8 cst <= sum_pub c2 + Omega, s in [.9, 1-tC0]): paper-proved on the Cap class from Path-Cut + I3 + rise charge (PV1 sec. 3, HC1 sec. 2); in Lean only `path_cut`, `transported_card_le`, `hcong_of_capclass` (the combinatorial/arithmetic parts) are proved; the register-machine facts (SP span law, D_t-confined ADD path, I3 distance bound) are NOT formalised. Natives: computed fact: Cap margin Omega - cst(Rm-8) - U Nf >= 19.356 on [.9, 1-tC0] (Omega 47.995, Nf 24, Rm 56); 6124 public moves nested strict ascents, 47 owned moves nested (23 up, 24 down), 207,881 ADDs same chart; all 4962 cells have a legal owned-descent-free path (WHOLEFLOOR/hcong/audit/au1.py, audit2/aud2a.py, prov/pv1-pv4.py). 48-law: computed exhaustively (aud2d.py, max n*m = 48 over all 1,398,491 port-spanned subspaces of dim <= 4; natives max 24, hc8.py).
9. hdist (spF(1-s) <= distF s p for p in J): paper-proved (I3 path bound, ID1, audited); Lean: hypothesis. Natives: covered by the same computed census as 8.
10. **hJ (1936 <= |J^arr|)**: HYPOTHESIS, and for the general Desc56 class a CONJECTURE (AUD2 FIX B: rigidity is numerical, span-form L1-L3 and shared carriers open). Natives: computed fact: |J^arr| = 4962 (aud2b.py exact mod 2^61-1; hc11.py; 2536 forced cells on route flags).
11. hspMono, hcstMono (spF, cst nondecreasing in t on [tC0, 1/10]): paper-proved (HC3: psi = x^s ln x convex, superadditive, so c2 nondecreasing in t); Lean: NOT proved (spF is a min over a 230+dual shape DAG, not defined in Lean); kept as named hypotheses.
12. hspTab, hcstTab (spFlo_j <= spF(tC_j); cst(t_{j+1}) <= cH_j): computed fact, outward-rounded (hc9.py / hc9.log "ALL TABLE ENTRIES CERTIFIED", relative slack ~1e-9); Lean: hypotheses over certified rationals, arithmetic proved (CongestionNativeTab).
13. hunitTab (unitLo_j <= 9^s - 8^s at s = 1 - t_{j+1}): computed fact (hc9.py unit_lo, Decimal 80 digits, outward); Lean: hypothesis (rpow numerics not kernel-checked).
Proved inside Lean (not hypotheses): sigma certificates sigC0..3, F_base point enclosures ptC0..2, tail cfC_neg/cfC88_neg, own56_floor, two-sided I3 (`E_lower_cap_om`), branches, table derivation.

## Not covered / open
- Class extension (Desc56 in general, >= 9-row and network decoders, non-Desc56 words): open; Rank8C56 rigidity [Q] enters only through hJ.
- Hypotheses 8, 9, 11 are the formalisation gaps (statements about the register machine and the shape DAG); 10 is a conjecture beyond the natives; 12-13 are certified numerics outside the kernel.
