# MASKK13 (Nov 20, Sonnet; exact finite check). Code: mk1 (SPARSE on controls + k13 placements), mk2/mk2b/mk2c (stage-level CEGAR), mk3 (family IP), mk4/mk4b (type-level counts), t2 (k13 type-level enumeration).
## Result
- [P] SPARSE law (dimension count): for every stage set U, #{roles with mask inside U} <= 2|U|-2. (ah_r, r in roles, are a basis of Z; those with supp inside U are independent zero-block-sum vectors on U, dim 2|U|-2.) LOCAL-PIECEFIX contains it; Lemma A refines it: |S| <= sum_t min(2,c_t(S)) - max_t min(2,c_t(S)).
- [P] The Turan-tight k13 face is dead in EVERY piece/main assignment and EVERY call order. Equality in Mantel allows two placements of G = K6 u K7:
  P1 (IC.md): R = 6-side, 21 deg-2 roles = all pairs of the 7-set W: 21 roles inside W > 2*7-2 = 12.
  P2 (missed in IC.md): R = a 6-subset of the 7-side, deg-2 roles = K6 on the other side + the 6 edges at the leftover vertex: 15 roles inside the 6-side > 2*6-2 = 10.
  [C mk1] both placements violate SPARSE (232 / 50 violating sets); controls C1, c33 pass.
- [C t2/mk4] type-level members (2 hubs D=13, R D=6, 21 D=2; all IC rows incl. MAINS; invoice > 128.891): 21155. Each has only these two placements. Killed by SPARSE: 21155/21155. Per-stage MAINS, RELAY-HALL, STAR-PURE, CELL-RANK, flatness are never reached (SPARSE needs no pieces, mains or order).
## Other k (profile: 2 full hubs + third role degree d + (2k-5) degree-2 roles; TRIPLE per-triple + SPARSE, exact CP-SAT CEGAR on all 2^k sets)
- [C mk2, k=9..20] stage-level INFEASIBLE iff d <= k-7. IC argmax d: k9..12 d=k-6 (alive); k13..20 d=k-7,..,k-9 (DEAD): k13 6, k14 7, k15 8, k16 9, k17 9, k18 10, k19 11, k20 11.
  With the Turan floor on d the dead range is k13..16: d = k-7 only; k17: 9,10; k18: 10,11; k19: 11,12; k20: 11..13. For k9..12 nothing is dead.
  Analytic form: Y = stages outside the third mask, y = k-d; every m in M3 needs N(m)∩Y to cover the complement of E[Y] (triangle-free); edges 2k-5 >= e(Y) + d*tau; with sparsity this fails for y >= 7.
- [C mk3] value of the surviving family: best invoice with d = k-6: k9 142.19(d3), k10 142.69, k11 143.01, k12 143.15, k13 143.18, k14 143.10 (d8), k15 142.98.. all >> bar. Removing the Turan-minimal d costs <= 0.02. NOT LOUD.
- [C mk4] type-level members by d (rows+MAINS+invoice>bar, Turan ok), k13: d6 21155, d7 31969, d8 51440, ... d12 159250. d >= k-6 survivors: k9 27631, k10 68521, k11 141274, k12 295292, k13 542677, k14 1003525.
- At d = k-6 the placement is FORCED (tight edge count 2k-5 = 2d+7): Y = K4 u K2 (K2 = {p,q}), every stage of M3 joined to both p and q, plus pq. Sparsity is tight on Q (6 pairs inside 4 stages) and on M3+{p,q}.
  [P] Lemma A on S = roles inside M3+{p,q} (and S = K4 roles) forces rank A_t|S = 2 at every stage of those sets; STAR-PURE (3 pure pair roles at a stage, relays only the hubs => rank 1) then gives: <=2 pure pairs at p, at q, at each K4 stage => chords >= 2d-1.
  [C mk4b] cuts the d=k-6 type-level members: k9 821->691, k10 2890->2278, k11 6336->4596, k12 16828->10903, k13 31969->17672, k14 69631->33328, k15 121180->44155. Survivors NOT killed here.
## Open / next
- Survivors (d >= k-6): d = k-6 has the forced placement above; piece/main enumeration with RELAY-HALL, CELL-RANK, PC3, flatness on it is the next finite job (orbit count not run; labelled space is huge, enumerate by orbit under S_M3 x S_2 x S_4).
- A placement-free type row from SPARSE+TRIPLE (every third role must have d >= k-6) would cut the Turan-minimal face at k13..20 but costs <= 0.02 in the LP: not the 10% needed.
