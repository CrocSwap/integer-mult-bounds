# Independent review of the P104 guidance follow-up

At #7869 head `06c207a9feb3994a4b987dc3010657b6e85b7956`, the requested Q = 0 dual data is present. A separate standard-library implementation of its rows and partition optimization gives the following exact rational enclosures of the specified dual envelope. The displayed decimal endpoints are rounded outward.

| k | Lower endpoint | Upper endpoint |
| --- | --- | --- |
| 71 | 129.037259547105063 | 129.037259547105064 |
| 72 | 128.850071932566732 | 128.850071932566733 |
| 73 | 128.681325145969644 | 128.681325145969645 |

The upper endpoints certify the named LPs conditionally on their rows. The k = 71 dual remains above 128.891. These are bounds on the stated role-partition models. The paper derivations of the additional rows, the frame-to-configuration bridge, and the appropriate application premises remain obligations. No new achievable κ follows.

## Independent arithmetic

`independent_q0.py` imports none of the author's verifier or solver. It reconstructs the 357, 362, and 367 row functions, checks nonnegative inequality multipliers, and optimizes over all partitions of every admitted D with pieces at most min(D,k−2). Its dynamic program carries whether a singleton has appeared as an explicit state. The two main-role flag choices are checked. All supplied main and constant multipliers are zero.

Each positive power x^(99/100) has an exact integer enclosure at scale 10^20. The floor a is certified by `a^100 <= x^99 * 10^2000 < (a+1)^100`. Lower and upper dynamic programs round every rational contribution in the corresponding direction. The output retains rational endpoints and verifies an interval width less than 10^-14. The author uses Decimal-60 evaluations with a safety increment. This independent result supplies direct integer inequalities for the numerical enclosures.

The original standalone package replay passed in 66.47 seconds and 24,712 KiB, checking 1,159 file pins, its 11 Lean token scans, both certificate families, 15 symbolic-D words at all four fourth roots, and its other listed witnesses. Lean was unavailable and was not built. The first independent Q0 run took 53.33 seconds and 13,204 KiB. These times describe local observed runs. The registered wrapper also passed from the pinned sparse checkout after its exact canonical base was materialized, with `PASS_REGISTERED_RESEARCH_PACKAGE research/p104-lowerbound-guidance outcome=completed` retained in `registered-replay.log`. The final portable independent check took 51.63 seconds and 17,788 KiB.

## What excludes the earlier witness

The #7856 witness has two roles of type `(D=k, P=(1,...,1))` and `2k−4` roles of type `(D=2, P=(2))`. This gives a legitimate comparison with the new type rows even though that event-data example fails the signed product equation.

Every named row outside `DYADIC_2` through `DYADIC_7` is satisfied. The first failing row is `DYADIC_2`.

| k | Left side | Right side | Exact residual |
| --- | --- | --- | --- |
| 71 | 152 | 210 | −58 |
| 72 | 154 | 216 | −62 |
| 73 | 156 | 216 | −60 |

All residuals are retained in `INDEPENDENT-Q0.json`. The dyadic rows are the paper consequences of the signed-Gram CROSS law in #7869 `notes/scherk.md`. Thus the extra inequality identifies a specific missing signed-product consequence. The earlier result about the smaller event relaxation remains valid.

## Two-hub mask consequence

Let there be k chronologically ordered two-column host blocks over a field of characteristic different from two. Write G_st=B_s^T A_t, K_ss=2I+G_ss, K_st=G_st for s<t, and K_st=−G_st for s>t. Assume K has rank at most two and each diagonal host block is invertible. Let the host entries of each role have support contained in its declared mask M_r, with n=2k−2 roles and every |M_r| at least two. Assume two distinguished masks cover all stages. The remaining 2k−4 roles are called nonhubs, even if another one also covers every stage.

For these hypotheses, the number of nonhubs with |M_r| at least three is at least 10 for k=71, 11 for k=72, and 10 for k=73. The argument depends only on masks and the signed block factorization. It does not use the assignment of events to role partitions.

Because K has rank two and invertible diagonal blocks, it factors as K_st=P_s Q_t with every P_s and Q_t invertible. At different stages, the ordinary Gram block G_st equals K_st or its negative according to the chronological order. For disjoint alternating stage sets X,Y, invertible block scalings therefore turn G_XY into E_XY tensor I_2. With c stages in the smaller alternating set, E_XY has a c-by-c submatrix with +1 on and above the diagonal and −1 below. Its determinant is 2^(c−1), so rank G_XY=2c. A role contributes at most rank one and only if its mask meets both X and Y. At least 2c role masks must cross this cut.

Apply those cuts to each residue class modulo 2^l, split into its two children modulo 2^(l+1), for l=0,1,2. A role crossing the induced binary tree contributes at most min(|M_r|,8)−1. The summed cut rank is 210,216,216 at k=71,72,73. The two full masks contribute 14, and the nonhub size-two baseline contributes 2k−4. Hence

`sum_nonhub (min(|M_r|,8)−2) >= 58, 62, 60`

respectively. Each enlarged mask contributes at most six. Taking ceilings proves the stated 10,11,10 counts. This is a corollary of the upstream dyadic argument with a direct proof specialized to the relevant signed frames.

In particular, the campaign's k=73 family with two full hubs and at most one enlarged nonhub is excluded at the frame level by these hypotheses. Its independent common-kernel price calculation remains a separate derivation, with a conditional 128.881499938303 upper bound under its stated event model. The newly supplied dyadic law gives a stronger structural conclusion for the shared signed-frame assumptions.

## Other overlap

The #7869 thin LP gives k=76 above the bar and k>=77 below for its model, with the actual nonempty IDLE_ODD correction remaining explicit in `OPEN-PROBLEMS.md`. The campaign's k=76 split two-hub result includes that actual correction and additional global event-partition and fragmentation hypotheses, so its scoped 128.879425704223 ceiling addresses a distinct case.

The 15 supplied Q0 words pass independent recomputation of all their degree-only dyadic rows. A changed HOST coefficient in the k=4 word preserves syntactic host conditions and fails the exact operator check. The portable positive/control replay passed in 53.84 seconds and 18,816 KiB. These examples support finite positive and negative controls. They do not derive every full-LP row from every legal word.

## Hosted status and source credit

At review time #7869 is open and Ready at the head above. Run 44862688701 has failed `plan` and skipped `replay`. Job 136719385631 fails `test_current_ci_section_matches_selected_record` because the CI guide names `make frontier6030-verify` while the selected record names `make frontier7000-verify`. This hosted result did not run the package's mathematical replay.

Original guidance, certificates, words, CROSS and DYADIC are by DreamingOfClouds with Claude Opus 5.5. The independent arithmetic, row comparison, and two-hub corollary here were prepared with OpenAI Codex assistance. Source files are copied at their exact pinned bytes and retain attribution. The repository license applies.

## Reproduce and remaining questions

Run `python3 -B verify.py` and `python3 -B positive_controls.py` in this directory. The standalone public packet checks its source hashes, independently recomputes the Q0 intervals and witness residuals, and checks the finite dyadic corollary arithmetic and controls. Its inputs include the three original duals, source notes, and the 15 original word files and operator checker. The positive-control runner independently checks all mask-degree dyadic rows and invokes that original operator checker for the symbolic-D identities and the altered-HOST control. The complete 1,159-file author replay is documented separately in `author-replay.log` and is reproduced from #7869.

Open work includes a full frame-to-type proof with role-piece assignment, formal verification of the additional LP rows, k=71 and smaller Q0 caller bounds, actual odd-idle invoice qualification, and constructive supplier changes with complete application evidence.
