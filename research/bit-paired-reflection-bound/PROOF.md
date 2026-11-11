# A paid-volume bound for paired BIT reflections

**NO VERIFIED GAIN.** On the retained #7001 BIT interface, two independent full-fibre rank-one address reflections cannot be made cheaper by packing them into reflection children with normalized linear adapters. This applies at κ = 0.0040075385047236 and throughout 0 ≤ κ ≤ 1/2.

## Literal address maps

The [#7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001) provider uses the #6726 native word. A nested chart move uses the split involution $D_P$ for the projector P of the orthogonal difference. Write its address variables as $(x,y)=(H,C_nD)$, with $C_n$ reversing atom positions. In these coordinates $D_P(x,y)=((I-P)x+Py,Px+(I-P)y)$. In the sum and difference variables $(x+y,x-y)$ this is $\operatorname{diag}(I,I-2P)$. The change is invertible at every admissible odd prime and every power of it. Hence the exact rational reflection $I-2P$ acts on the difference coordinates, with the sum coordinates as spectators. The resulting permutation acts linearly on binary data. The move rank is $\operatorname{rank}P$. [Physical split involution and cover](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md#2-native-projector-jobs-before-canonical-lowering)

The rational orthogonal reframe $A=I-2nn^{\mathsf T}/4$, with $n=(0,1,0,-1,1,0,1,0)$, permutes all 111 port head lines and their paired body hyperplanes. Of 1,386 rank-one MOVE occurrences, 660 have independent original and rotated paid directions, all with absolute cosine 1/2. Exactly 264 share their source span and 396 change it. The first common-source pair is zero-based event 19152, role 0, charts 2→125. Its directions are $d=e_3$ and $u=(0,1,0,1,1,0,1,0)/2$. In the plane basis $(d,u)$ the exact maps are

$$R_d=\begin{pmatrix}-1&-1\\0&1\end{pmatrix},\qquad R_u=\begin{pmatrix}1&0\\-1&-1\end{pmatrix}.$$

Both fix the perpendicular complement, are self-inverse and fail to commute. The rank-two reflection of the plane is $-I$ on that plane. The first changed-source pair is event 19167, role 225, charts 3→213. [REFLECTION.json](REFLECTION.json) gives the exact ambient matrices. The two fields are independent in the all-column contract. Their normalized target is the direct sum of the two address permutations.

## Rank of the binary data operator

Put $s=q^f$, with q an admissible odd prime and f≥1 the digit width of one active rank axis, including its atom width. A full-fibre bank of volume V contains all combinations of the active digit coordinates and an unchanged spectator set. A rank-r reflection has $V/s^r$ fixed positions, since all $rf$ flipped digits must be zero. Every other position is paired into a transposition. On binary data a transposition contributes one to $\operatorname{rank}_{\mathbb F_2}(K-I)$. The defect of this child is $V(1-s^{-r})/2$. Spectator multiplicity is included in V.

Let the original rank-one fields have volumes $V_1,V_2$ and direct-sum target T. Then $\operatorname{rank}(T-I)=(V_1+V_2)(1-s^{-1})/2$. Allow any sequence of linear adapters, workspace initialization, child banks and linear readout. Each child acts as identity away from its bank. Use the same preparation and readout when replacing all children by identity, and require that the resulting external map be identity. Only the external map on the required input space is normalized.

Telescope the difference between the two external maps, changing one child at a time. Each term factors through $K_i-I$ and has rank at most $V_i'(1-s^{-r_i})/2$, where $V_i'$ is the complete child volume. This permits overlapping banks, rectangular adapters and clean padding. Consequently

$$ (V_1+V_2)(1-s^{-1})\le\sum_i V_i'(1-s^{-r_i}). $$

For a single rank-two child of two equal original volumes V this requires $V'\ge 2sV/(s+1)\ge3V/2$. A volume-V child is too small. Charging the larger volume at $V'(2f)^{1-\kappa}$ costs strictly more than the two original calls at $2Vf^{1-\kappa}$ for the stated κ range.

For r=1 the quotient $(1-s^{-r})/(1-s^{-1})$ is one, for r=2 it is at most 4/3, and for r≥3 it is less than 3/2. Hence it is at most $\sqrt r\le r^{1-\kappa}$, strictly at r≥2. The summed volume-weighted tariff is at least $(V_1+V_2)f^{1-\kappa}$, with a strict surcharge if any positive-volume child has rank ≥2. This calculation grants free setup, routing, linear mixing and restoration inside the stated scope. Charging those operations cannot yield a saving there.

## Cover routes alone cannot pay the missing rank

If replacing the children by identity produces a map H, telescoping bounds $\operatorname{rank}(T-H)$ by the same child capacity. The retained matchers route complete cover rows by $g\mapsto gS$. This changes the cover index and preserves the ambient address z in every moved row. Pointwise scalar operations and zero preparation preserve the same address grading. Any no-child map composed of these operations is block diagonal by z, even if it mixes all rows and roles at each address.

Let m be the number of transpositions in T. Every one changes the ambient address, with the cover index and role fixed. Fix a total order on z and orient each transposition from lower address $a_i$ to higher address $b_i$. Take the rows of the lower endpoints and the columns of the corresponding higher endpoints, ordered by $a_i$. T gives the identity on this minor. The H entry $(i,j)$ can be nonzero only if $a_i=b_j>a_j$. Thus H is strictly lower triangular on this minor and $\operatorname{rank}(T-H)\ge m=\operatorname{rank}(T-I)$. The same paid-volume bound applies to any address-preserving no-child map. In particular, existing cover right routes can conjugate a retained child but cannot supply one of these two address reflections alone.

For a general H the weaker necessary inequality is $\operatorname{rank}(H-I)\ge\operatorname{rank}(T-I)-\sum_i V_i'(1-s^{-r_i})/2$. A genuinely address-changing H, incomplete fibres, changed external contracts and other paid primitives remain separate questions.

## Verification and credit

The replay checks all 111 port correspondences, all 1,386 rank-one sites and the common-source and changed-source examples over the rationals. It enumerates all plane addresses at primes 5, 7 and 11 and checks all 53,001 input cases of the corresponding doubled split involutions. At q=5 the two independent fields have combined defect rank 20 per sum-coordinate spectator, and the one-plane rank-two permutation has rank 12. Replacing the second field by a literal identity spectator reduces the target rank to 10 and removes the obstruction. The checker also tests 28 exact finite tariff comparisons. For event 19167 an exact control across all 480 GL₂(F₅) rows retains all 9,600 triangular pivots under a nonidentity cover route with 2,240 strict-lower entries. A true address-changing no-child map equal to T cancels those pivots. The general inequalities prove the result for all admissible widths and ranks.

[Androo Lloyd's #673](https://github.com/androolloyd/integer-mult-bounds/blob/0b4f514c60d9bc7786415d7cbc24754f24d6dc3b/research/bit-role-sharing-budget/PROOF.md) supplies the rank-defect argument for one fixed address permutation. This contribution evaluates different literal rank-one directions and higher-rank reflection children with distinct bank volumes and charges. [#1920](https://github.com/CrocSwap/integer-mult-bounds/pull/1920) and [#1924](https://github.com/CrocSwap/integer-mult-bounds/pull/1924) study complex reciprocal and clean-selector encodings. Credit zxv and the #6726 lineage for the word, DreamingOfClouds and CubeJerry for the #6834/#6980/#7001 paired construction, and the Round 8 projective search for the candidate reflection. [#7162](https://github.com/CrocSwap/integer-mult-bounds/pull/7162) covers a separate change to the caller schedule with the native bill fixed. OpenAI Codex and subagents materially assisted the derivation and independent audit.

## Open next questions

Can an already-required address-changing map supply H without exceeding the price saved by removing a reflection? Begin at event 19167 and compute H on both retained source charts. The cover right routes alone cannot supply it. Charge every address change and require the full binary action on arbitrary complete fields. All-width realization, ordinary adapter costs, larger BIT atom admission and the fixed-tape proof remain open.
