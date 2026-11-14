# P104 decoder wall: row price, partial-replacement bounds, half-wall for h ≤ 6 (no κ)

This package gives lower bounds on the owned mass of the P104 decoder, the 56 owned units per plane that every P104 word pays (8 rows of climb 7). It makes **no κ claim** and ships no word. It does not repeat the owned deletion bound or the contract classes; those are in #7555.

Tags: **[P]** proved in `PROOF.md`; **[C]** exact finite check, re-run by a checker here; **[C-pin]** exact finite run done by our lane code, pinned summary only, not repeated in CI; **[N]** search evidence, not a proof; **[open]**.

## Model

- **Ports and labels.** There are n ports. Port p has an odd label q_p ∈ F2^h, and Q = [q_t·q_s] is the 0/1 matrix of odd cells. Q includes the diagonal; on P104, h = 9 and n = 104.
- **Decoder.** A decoder is M = Σ_k w_k u_kᵀ with M_pp = 1 and M_ts = 0 on every odd cell t ≠ s. Even cells are junk and are left free.
- **Rows.** Each rank-1 term (row) is one owned chain. It deposits into D_k = supp w_k and gathers from S_k = supp u_k.
- **Frame rules.** A gather of s needs f ⊆ q_s^⊥. A deposit into t needs q_t ∈ f. The climb is dim f_end − dim f_start.
- **Scope.** This is the row model.
  - A network that shares one ascent among several rows is not covered.
  - Frame legality (nondegeneracy) can only raise prices, so every floor below holds a fortiori.

## 1. Row price and the E8 decoder (`rows.py`)

**Lemma 1 (row price) [P].** A row's climb is at least r(D,S) = rank_F2 Q[D,S] = dim B − dim(B ∩ A^⊥), where B and A are the label spans of D and S. Equality holds for the chain B ∩ A^⊥ → B, which gathers at the bottom and deposits at the top.
- **Lemma 2 [P].** On odd cells and the diagonal, any chain is exactly rank 1: every gather of s comes before every deposit into t whenever q_t·q_s = 1.
- **Not the form rank.** The price is not the rank of the dot form on A + B. On P104 rows the form rank is 9 and the price is 7 [C].

**The P104 decoder [C].** It has 8 rows. Each row has w_j = G[·,d_j] and u_j = G[·,d′_j]/(2G[d_j,d′_j]), where (d_j, d′_j) are pairs of the 16 non-port E8 lines.
- Σ_j w_j u_jᵀ = G/2 holds exactly.
- Every row has |D| = |S| = 52, dim B = dim A = 8 and price 7, for a total of **56 = 7/13 per port**.
- The G here is the PR968 Gram, via the vendored map, on every entry.

**Rigidity [C].**
- **Zero freedom.** Fix the 8 gather vectors and leave all 8 coordinates free. Each port's deposit vector is then the unique solution of its 55 odd equations plus the diagonal equation (nullity 1 at all 104 ports), and it equals the E8 deposit vector.
- **Real flats.**
  - Exactly 16 label hyperplanes have outside ports of real rank ≤ 7. They are the kernel hyperplanes, with 52 ports outside each.
  - No codim-2 label subspace has this property: all 43,435 were checked, and the check also holds after deleting any one port.
  - **Consequence.** Every E8-world row (Xa)(Yb)ᵀ has dim B, dim A ≥ 8, so its price is ≥ 7, even when one port is left free. A rank-8 decoder on P104 labels therefore costs exactly 56, and any gain needs ≥ 9 rows.

## 2. Partial replacement (`partial.py`, `fiverow.py`)

Keep the E8 rows outside R and replace the rows in R by new rank-1 rows. The new rows must equal 2T_R = Σ_{j∈R} w_j(2u_j)ᵀ on every odd cell and on the diagonal.

| replaced rows | replacement | result | tag |
|---|---|---|---|
| 4 (any of 70 R) | ≤ 3 rows, any climbs, any char-0 field | impossible (a rank-4 all-odd-cell rectangle exists for every R) | [P + C] |
| 4 (any of 70 R) | exactly 4 rows | cost ≥ 28. Propagation forces all 104 ports for 62 R, and all but one common port for 8 R, so the rows are E8-world rows of price ≥ 7 | [P + C] |
| 4, R = (0,1,2,3) and (0,1,3,5) | exactly 5 rows | cost ≥ 28 | [P + C-pin + C spot-check] |
| any R, half-integer entries | any number of rows | cost ≥ \|R\|(8 − \|R\|): 7, 12, 15, 16 for \|R\| = 1..4 | [P + C] |
| 4 | ≥ 6 rows | **open** (§4) | [open] |

**Five rows [P + C-pin].**
- **Cheap row.** A 5-row design with total < 28 has a row of price ≤ 5. That row lies in one closure D̄(B) × S̄(F) of codim exactly 5.
- **Rigidity outside it.** Outside that closure, the other 4 rows alone equal 2T_R. Propagation from a rank-4 start block shows they are E8-world rows on the forced ports, with one GL4 gauge shared by all blocks.
- **Finite check.** Our C++ enumerator (`lane/prop2.cpp`, inputs from `lane/prep.py`) found a start block with β ≥ 7 for every codim-5 closure.
  - It used a monotone cover of 27,423,618 closures over both R.
  - Every coarse failure was refined to all of its codim-5 sub-closures (R0123: 756, R0135: 133,308), with 0 failures.
  - The pinned summary is `data/fiverow-coarse.txt`.
- **What CI runs.** That run is **not** repeated in CI. `fiverow.py` re-implements the method independently. It:
  - re-derives the flats exactly;
  - validates every start rectangle;
  - checks 80 seeded random codim-5 closures (all β = 7);
  - reproduces 30 codim-7 failures exactly (teeth: the argument is tight to codim 5).
- **Orbits.** We take R = (0,1,2,3) and (0,1,3,5) to represent the two orbits of 4-subsets. That orbit claim comes from our lane notes and is not re-checked here.

**Cross-pair identity [P + C].** Put x_j = 2u_j mod 2 and y_j = w_j mod 2. Then (2T_R ∘ Q) mod 2 = Σ_{j∈R, i∉R} (x_i x_j)(y_i y_j)ᵀ. Its F2 rank is exactly |R|(8 − |R|), checked for all 255 R.
- Half-integer rows (w integral, 2u integral, after 2-adic rescaling) reduce mod 2 to rank ≤ price. So any half-integer replacement of R costs ≥ |R|(8 − |R|).
- For |R| = 1 this gives 7: no single E8 row can be replaced more cheaply.

**Graded 2-adic rank bound [P].** Suppose row k has denominators dividing 2^{e_k}. Then n ≤ Σ_k s_k, where s_k is the rank of Q[D_k,S_k] over Z/2^{e_k+1}.
- e = 0 (odd denominators) gives C ≥ n.
- e = 1 gives s_k ≤ r_k(r_k+1)/2, so C ≥ 2n/(h+1) (21 on P104).
- P104's own rows have mod-4 rank 27 against price 7, so this bound cannot reach 56: plain Smith-rank counting is exhausted.

## 3. Rank certificates and the half wall (`halfwall.py`)

**Certificate lemma [P].** Let Z live on the odd cells and the diagonal, with a nonzero diagonal. Then every decoder satisfies n ≤ Σ_k rank Z[D_k, S_k].
- The lemma holds over any field, with any denominators, any row count and repeated labels allowed.
- **Mixtures.** If a mixture of such Z satisfies E rank Z[D,S] ≤ λ·r(D,S) on every closure, then C ≥ n/λ.
- **Closures suffice.** It is enough to check the flags F ⊊ B of F2^h.

**Theorems [P + C].**

| label rank h | certificate | bound |
|---|---|---|
| ≤ 3 | Z = Q | C ≥ 3n/4 |
| ≤ 4 | Z = Q (353 closures, max ratio 3/2) | C ≥ 2n/3 |
| ≤ 5 | S_5-symmetric mixture of functional splits, λ5 = 5291/2845 | C ≥ 0.5377·n |
| ≤ 6 | S_6-symmetric mixture, λ6 = 1395/697 = 2.00143… | C ≥ 0.49964·n, and **C ≥ ⌈n/2⌉ for distinct labels** (integrality, n ≤ 32) |

**The functional-split family cannot reach h = 9 [P + C].**
- Take the full flag at h = 7 (D = S = all 64 labels, price 7). Over all 29,212 subspaces A, the block-rank sum is ≥ 15, and 15 is attained.
- So every functional-split mixture has λ7 ≥ 15/7.
- The family is closed under restriction, so λ9 ≥ 15/7 > 2·255/254. Split certificates therefore cannot prove the h = 9 wall. Any h = 9 certificate must be non-split.
- **Pure clique partitions also fail [P].** Every 16-clique of odd(F2^9) contains the all-ones label. A clique partition therefore needs ≥ 31 blocks, against a budget of 18.

**The wall depends on h [P, quoted from our lane].** Decoders multiply under the tensor product of label sets. P104 ⊗ P104 reaches 0.290 per port at h = 81. So "C ≥ n/2 on any label set" is false as worded, and the target is h = 9.

## 4. Open

- **≥ 6 replacement rows [open].**
  - **Reduction [P; profile table from a lane exact run, not re-checked here].** The case follows from one union-rigidity lemma (URL): for each of the 252 dangerous cheap-row profiles C (all with max cheap climb ≤ 5), propagation outside the union of the cheap closures still certifies β ≥ need(C). The needs are 2–7; need 7 arises only for (1,1), (2,1) and (1,1,1).
  - **Evidence [N].** Adversarial hill-climbs over unions (both R, profiles (1,1) up to 23 patches) and 400 random unions all gave β = 7. That is evidence, not proof.
  - **Why the finite method stops.** Codim-1 closures alone have ≥ 58M distinct port traces, so pairs number about 10^15. A proof needs a structured robust closure (per-port covering number plus a start lemma that uses subspace structure).
- **The h = 9 wall [open].** Is C ≥ n/2 for distinct labels of rank 9 (C ≥ 52 on P104)? It is open both ways at h = 9, and only non-split certificates remain. On the 120 E8 labels the numerical minimum full-flag certificate rank is about 18 = 2h [N], which leaves essentially no slack.
- **Junk trade-off [open, conjecture].** C ≥ 104 − 48·J/4,992 for every decoder on P104 labels, where J is the number of nonzero junk cells. This is the chord from E8 (56, 4,992) to M = I (104, 0). Every block design we built lies on or above it [N].

## Method notes

- **Rank direction.** Rank mod p = 2^31 − 1 lower-bounds the rank over Q. We use it only where the claim needs "rank ≥". Every "rank ≤" is exact: Fractions, or a prime above the Hadamard bound.
- **Exact flats.** Flats of a rank-4 configuration are computed exactly from integer normals of independent triples.
- **Propagation** (FATROWS lemma). A port whose forced partners on allowed odd cells have rank 4 is itself forced. Starts are rank-4 rectangles: a 4-port coset of a 2-dim W times its common odd partners.
- **Cheap-row closures.** A row of price c lies in a closure of codim exactly c. Enlarge B, then shrink F; both only grow D̄ and S̄.
- **Symmetric certificates.** Average each column over its full S_h orbit. Then checking flag-orbit representatives is enough.

## Checks

| command | prints | runtime (one core) |
|---|---|---|
| `python -I -B rows.py` | `PASS_DECODER_ROWS` | ~20 s |
| `python -I -B partial.py` | `PASS_DECODER_PARTIAL` | ~50 s |
| `python -I -B fiverow.py [samples]` | `PASS_DECODER_FIVEROW` | ~17 s at 8 |
| `python -I -B halfwall.py` | `PASS_DECODER_HALFWALL` | ~1 s |

All checkers use the standard library only and our own code. Data is SHA256-pinned. The PR968 decoder file comes from the repository.

## Open next questions

1. Prove the union-rigidity lemma: it closes k ≥ 6 rows for 4-row replacement (§4).
2. Find a non-split certificate at h = 9 (full-flag rank ≤ 18 and ≤ 2·price on smaller flags), or a sub-1/2 decoder on 9-bit labels.
3. Prove or break C ≥ 104 − 48J/4,992 on P104 labels, e.g. with junk-weighted certificates.
