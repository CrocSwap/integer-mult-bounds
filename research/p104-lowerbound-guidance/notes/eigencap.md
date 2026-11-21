# EIGENCAP EC (Nov 20, Opus; theory + exact checks). Own code: ec1.py (exact law checker on rebuilt ML words), ec2.py (type LP + IDLE row, float),
ec3.py (numeric probe, KILLED: its feasible control failed). Logs ec1.log, ec2.log, ec3.log. 1 proc, threads = 1.
Why this differs: QZBUILD saw the 2(t-1) eigenspace cap only in chain frames and left start/end pieces open. Here the cap is proved for EVERY
legal tight Q=0 word (QZB section-0 word model: n = 2k-2, every host ab != 0,-1, contacts right after their host), in any frame and order.

Notation: hosts in time order h_1..h_k, P_j = V_{h_j}...V_{h_1}, K_j = ker(P_j+I), W_j = sum of the contact planes Pi_{h_1..h_j}.
An event is INVARIANT if pi^-_e = pi_e. Every event before the first host (L = I) or after the last host (L = -I) is invariant.
For stage t, nu_t = number of non-invariant, non-contact stage-t events.

## 1. Structure of the prefix products [P]
- (E1) dim K_j = 2(j-1) for j >= 1. Proof: rank(P_{j+1}+I) - rank(P_j+I) is at most 2 in size (since (V-I)P_j has rank 2); K_1 = 0 (lambda != -1); K_k = everything (n = 2k-2).
- (E2) Im(P_j - I) = W_j, and dim W_j = 2j for j <= k-1. So the contact planes of the first k-1 hosts are a direct sum = K^n.
  The only deficiency is at the LAST host: Pi_last lies in W_{k-1}.
  Proof: for x in K_{j+1}, (P_j - I)x = -(V^{-1}+I)x, and V^{-1}+I is invertible. So Im(P_j - I) contains a 2j-dim space, and it lies in W_j (telescoping).
  Dually ker(P_j - I) = (W*_j)^perp has dim n - 2j.
- (E3) MIDDLE host t = h_{j+1}, 1 <= j <= k-2: P_j has NO fixed vector in Pi_t, and P_j^{-1} Pi_t meets Pi_t only in 0.
  Proof: write blocks over W_j + Pi_t + Z. Requiring dim K_{j+1} = 2j forces A + I = -B(T+I)^{-1}alpha. Since rank(A+I) = 2 (from E1), rank B = 2.
## 2. IDLE LAW [P]: every middle stage has nu_t >= 2
- Let H_t be the span of the contacts and the non-invariant stage-t events. H_t is the SAME space in both frames (it is the biorthogonal complement of the invariant events).
- H_t contains Pi_t and also the minus-frame contacts P_j^{-1} Pi_t.
- So (P_j^{-1} - I)Pi_t, which has dim 2 by E3, lies in H_t and in W_j. Also Pi_t meets W_j only in 0 (E2). Hence dim H_t >= 4, i.e. nu_t >= 2.
- If nu_t = 2, then H_t = Pi_t + P_j^{-1} Pi_t, and the + frame idle span is (I - J_t)P_j^{-1} Pi_t (fixed by the frame).
- Corollary CLEAN: only the first and the last host stage can have nu = 0.
- Total non-invariant non-contact INCIDENCES >= 2(k-2).
## 3. COVER-CAP [P, order-free; event dual of SPARSE]
For S a nonempty set of stages: #{non-contact events e with S contained in S_e} <= 2 max(k-|S|-1, 0).
Proof: those v_e are biorthogonal and fixed by V_t for every t in S. A vector fixed by every twist but one would be a -1 eigenvector of that twist.
Corollary: no event covers k-1 stages.
## 4. Task (1): ESCAPE SETTLED, it is DEAD
- Start and end pieces (and every invariant mid piece) never count toward nu_t.
- Replacing the forced middle idles by frame-free pieces leaves nu_t = 0 at the middle stages, which contradicts the IDLE LAW at every k.
- So the 126.11 (k5) and ~130 (k6) escape charts are not realisable. This works for every order and every placement, and it proves QZB's numeric stalls.
- ML already uses both allowed CLEAN stages (first and last) and is tight on COVER-CAP.
- Count correction: ML has 4k-2 singletons, not 4k-4. That is 2k contacts + 2(k-2) middle idles + 2 invariant last-stage singletons. The values are unchanged.
## 5. Exact checks [C exact, ec1.log]
ML k3..k9 (rebuilt exactly):
- E1, E2 and E3 hold.
- nu_t = 2 and core dim 4 at every middle stage.
- COVER-CAP holds with min slack 0.
- Half of the non-contact events are invariant (the level pieces).
## 6. Task (2): bound on c-hat [C float LP, ec2.log]. NOT LOUD
- The IDLE LAW becomes a type row only under [CONJ] SINGLE: non-invariant non-contact events are singletons. This is open.
  The proof gives incidences only. The ec3 numeric probe was invalid (its control failed).
- KASYM reduced LP (n, MAINS, SEP, RC2, parts <= k-2, mixed main/idle) + row "#idle singletons >= 2(k-2)":
  k4 124.65, k5 130.07, k6 133.06, k7 134.75, k8 135.71, k9 136.20, k10 136.40, k11 136.41 (peak), k12 136.29, k13 136.08.
- Worth 2.7-7.2 against HP. The window k5..13 stays open. Built ML words sit at 113.8-115.4, so the remaining gap of ~15-21 is mask/frame structure.
  The LP optimum moves to many degree-2 roles with two singletons.
## Next
(a) Prove or kill CONJ SINGLE. A non-invariant f covering two middle stages s, u must have v_f in H_s and in H_u.
    In the minimal case: v_f in Omega_u intersected with C_u, and v_f in W_{j_s+1}. The second-order D-cross condition (sum over a<b of [pi_b, pi_a] = 0) is unused so far.
(b) Feed E2 (contact planes are a direct-sum basis), COVER-CAP and SPARSE into the mask-level CEGAR (MASKK13/RESCUEBUILD).

## 7. Round 2 (coordinator follow-up): SINGLE
- [C numeric, VALID control] ec4.py/ec4.log. Control = exact replica of QZB climb4 STEP-1 (ML k4, same piece order, placements, seed, try_design): solved, res 1.4e-13.
  Probe = same chart with {1}x2,{2}x2 merged into {1,2}x2 (value 119.47), all 6 mid placements, 12 tries each: every one stalls (res 5.9e-4 .. 1.3).
  Start/end placements are already dead by the IDLE LAW [P]. Scope: ML k4 masks, host order 0123 only. Earlier ec3/first ec4 runs had failing controls; they were discarded.
- [P] k4 RIGIDITY (minimal case: hosts a,s,u,z; f1,f2 non-invariant on {s,u}; nu_s = nu_u = 2). Steps:
  - Y := span v_f lies in C_s and C_u. Minimality gives Y = Omega_u, and V_a^{-1}Y = N^-_u, which lies in H_u and W_2, so in Omega_u. Hence V_a Y = Y.
  - VEC-FIX rules out a V_a-fixed vector in Y, so Y = Pi_a.
  - The trajectory gives V_z = -V_a^{-1} on Y, so Pi_z = Pi_a.
  So a counterexample needs the first and last contact planes to coincide and to equal the idle span, i.e. to be supported on full-mask roles.
  The second-order D condition sum_{a<b, u in a, t in b} [pi_b, pi_a] = 0 [P] is derived but not yet used to finish the kill.
- STATUS: SINGLE = [CONJ], supported by a valid-control numeric negative at k4 and the rigidity reduction. Not killed, so there is no counterexample word.
- LP with E2 + COVER-CAP + SPARSE + SINGLE: E2/COVER-CAP/SPARSE are mask-level. Their type images are only MAINS, parts <= k-2, and the averaged SPARSE that DYADRELAY found inert.
  So the reduced LP equals ec2 LP+IDLE: k5 130.07 ... k11 136.41 ... k13 136.08. No k in 5..13 closes.
## 8. Q >= 1 (thin) branch [P sketch, conditional]
- If LIFT extends to thin columns (QUERY/IDLE_ODD) so that the word model holds with prod V = diag((-1)^ex), then:
  - E1 holds on the odd part: d_j <= 2(j-1) still, and d_k = #odd roles, so #odd roles <= 2k-2. With n = 2k-2+Q and Q even (thin) roles this is tight.
  - E2 holds with W_{k-1} = the odd-role span.
  - COVER-CAP holds verbatim for events supported on odd roles (only P_k = -I on Y is used).
- Thin roles are fixed by every twist, which matches THINQ's width-1 blocks. The IDLE LAW also needs the minus-frame stage law for thins: open (LIFT is proved only for HOST + q-free events).
