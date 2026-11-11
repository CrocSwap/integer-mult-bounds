# A paid-volume bound for paired BIT reflections

**NO VERIFIED GAIN.** On the retained #7001 BIT interface, two independent full-fibre rank-one address reflections cannot be made cheaper by packing them into reflection children with normalized linear adapters. This applies at κ = 0.0040075385047236 and throughout 0 ≤ κ ≤ 1/2.

## Literal address maps

The [#7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001) provider uses the #6726 native word. A nested chart move from F to G uses the reflection $I-2P_D$ of the orthogonal difference D, specialized at a suitable odd prime. The resulting address permutation acts linearly on binary data. The move rank is the dimension of D. This is the paired-address interpretation used in the [chain-root proof](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/bit-chain-root-g20/PROOF.md).

The rational orthogonal reframe $A=I-2nn^{\mathsf T}/4$, with $n=(0,1,0,-1,1,0,1,0)$, permutes all 111 port head lines and their paired body hyperplanes. Of 1,386 rank-one MOVE occurrences, 660 have independent original and rotated paid directions, all with absolute cosine 1/2. Exactly 264 share their source span and 396 change it. The first common-source pair is zero-based event 19152, role 0, charts 2→125. Its directions are $d=e_3$ and $u=(0,1,0,1,1,0,1,0)/2$. In the plane basis $(d,u)$ the exact maps are

$$R_d=\begin{pmatrix}-1&-1\\0&1\end{pmatrix},\qquad R_u=\begin{pmatrix}1&0\\-1&-1\end{pmatrix}.$$

Both fix the perpendicular complement, are self-inverse and fail to commute. The rank-two reflection of the plane is $-I$ on that plane. The first changed-source pair is event 19167, role 225, charts 3→213. [REFLECTION.json](REFLECTION.json) gives the exact ambient matrices. The two fields are independent in the all-column contract. Their normalized target is the direct sum of the two address permutations.

## Rank of the binary data operator

Put $s=q^f$, with q an admissible odd prime and f≥1. A full-fibre bank of volume V contains all combinations of the active digit coordinates and an unchanged spectator set. A rank-r reflection has $V/s^r$ fixed positions, since all $rf$ flipped digits must be zero. Every other position is paired into a transposition. On binary data a transposition contributes one to $\operatorname{rank}_{\mathbb F_2}(K-I)$. The defect of this child is $V(1-s^{-r})/2$. Spectator multiplicity is included in V.

Let the original rank-one fields have volumes $V_1,V_2$ and direct-sum target T. Then $\operatorname{rank}(T-I)=(V_1+V_2)(1-s^{-1})/2$. Allow any sequence of linear adapters, workspace initialization, child banks and linear readout. Each child acts as identity away from its bank. Use the same preparation and readout when replacing all children by identity, and require that the resulting external map be identity. Only the external map on the required input space is normalized.

Telescope the difference between the two external maps, changing one child at a time. Each term factors through $K_i-I$ and has rank at most $V_i'(1-s^{-r_i})/2$, where $V_i'$ is the complete child volume. This permits overlapping banks, rectangular adapters and clean padding. Consequently

$$ (V_1+V_2)(1-s^{-1})\le\sum_i V_i'(1-s^{-r_i}). $$

For a single rank-two child of two equal original volumes V this requires $V'\ge 2sV/(s+1)\ge3V/2$. A volume-V child is too small. Charging the larger volume at $V'(2f)^{1-\kappa}$ costs strictly more than the two original calls at $2Vf^{1-\kappa}$ for the stated κ range.

For r=1 the quotient $(1-s^{-r})/(1-s^{-1})$ is one, for r=2 it is at most 4/3, and for r≥3 it is less than 3/2. Hence it is at most $\sqrt r\le r^{1-\kappa}$, strictly at r≥2. The summed volume-weighted tariff is at least $(V_1+V_2)f^{1-\kappa}$, with a strict surcharge if any positive-volume child has rank ≥2. This calculation grants free setup, routing, linear mixing and restoration inside the stated scope. Charging those operations cannot yield a saving there.

If replacing the children by identity produces a nonidentity map H, the same argument bounds $\operatorname{rank}(T-H)$ by child capacity. In particular, $\operatorname{rank}(H-I)\ge\operatorname{rank}(T-I)-\sum_i V_i'(1-s^{-r_i})/2$. The cost of implementing H needs its own proof. Incomplete fibres, changed external contracts, other paid primitives, and adapters that perform nonidentity address work are outside the normalized tariff result.

## Verification and credit

The replay checks all 111 port correspondences, all 1,386 rank-one sites and the common-source and changed-source examples over the rationals. It enumerates all plane addresses at primes 5, 7 and 11. At q=5 the two independent fields have combined defect rank 20 and the one-plane rank-two permutation has rank 12. Replacing the second field by a literal identity spectator reduces the target rank to 10 and removes the obstruction. The checker also tests 28 exact finite tariff comparisons. The general inequalities prove the result for all admissible widths and ranks.

[Androo Lloyd's #673](https://github.com/androolloyd/integer-mult-bounds/blob/0b4f514c60d9bc7786415d7cbc24754f24d6dc3b/research/bit-role-sharing-budget/PROOF.md) supplies the rank-defect argument for one fixed address permutation. This contribution evaluates different literal rank-one directions and higher-rank reflection children with distinct bank volumes and charges. [#1920](https://github.com/CrocSwap/integer-mult-bounds/pull/1920) and [#1924](https://github.com/CrocSwap/integer-mult-bounds/pull/1924) study complex reciprocal and clean-selector encodings. Credit zxv and the #6726 lineage for the word, DreamingOfClouds and CubeJerry for the #6834/#6980/#7001 paired construction, and the Round 8 projective search for the candidate reflection. [#7162](https://github.com/CrocSwap/integer-mult-bounds/pull/7162) covers a separate change to the caller schedule with the native bill fixed. OpenAI Codex and subagents materially assisted the derivation and independent audit.

## Open next questions

Can an already-required nonidentity address map supply H without exceeding the price saved by removing a reflection? Begin at event 19167 and compute H on both retained source charts. Charge every address change and require the full binary action on arbitrary complete fields. All-width realization, ordinary adapter costs, larger BIT atom admission and the fixed-tape proof remain open.
