# Independent cross-review: native models, phases and reconstruction

The root and algebra exact tests passed independent replay against their stored receipts with unchanged source bytes during each replay. Hashes are recorded in CROSS-CHECKS.json. This review did not edit those files and is an independent Codex-worker review, not human peer review or a Lean certificate.

## Root triangular-port, transpose and echo tests

For U = [[A, 0], [A L A, A]] over the Gaussian rationals, the tested inverse is [[A⁻¹, 0], [−L, A⁻¹]]. The implemented Hermitian adjoint sends (u,v) to (A* (u + L* A* v), A* v), which is the literal block adjoint because A is unitary. The inverse-adjoint sends (u,v) to (A u − L* v, A v). These expressions agree with the code, including monomial phase reversal and permutation inversion.

The dirty-baseline echo formula is also correct: applying U⁻¹ to U(x,y) + (δ,0) returns (x + A⁻¹δ, y − Lδ). It retains arbitrary y and costs the stated two forward plus two reverse paid calls. It does not silently treat a dirty target as owned zero. The finite cases at widths 1, 2 and 3 validate 27 port/adjoint identities, nine echoes and nine wrong-adjoint controls. The written algebra, rather than those finite widths alone, is the reason the formulas hold universally.

The matching-vector toy decoder uses a nontrivial order-three character over F₁₃. Its nine distinct encoded queries recover four arbitrary linear images exactly. The query union is paid: a rank-three call at every query would cost 27 calls, versus 12 direct calls. It correctly reports no supplier gain. The equality of two displayed paid profiles is a bookkeeping check, not a general theorem that constants inside a recursive recurrence cannot change its exponent. A per-level expansion constant can matter; an unchanged paid recurrence cannot improve merely by renaming the implementation.

## Algebra anchored encoding and conditional funding

The tested skew block matrix is

    M = [[0, I, A], [−I, 0, B], [−A, −B, 0]].

For involutions A² = B² = I with AB = −BA over a ring in which 2 is invertible, one recovers inputs from outputs (r,s,t) by

    z = AB (t − A s + B r) / 2,
    x = B z − s,
    y = r − A z.

Substitution proves all three output equations. Thus it is a constructive whole-input inverse, not just a full-rank computation. Anchoring A and B on one designated native address bit retains anticommutation at every tensor width. Using identical tensor powers instead gives AB = (−1)^f BA, so the unanchored even-width full-rank promotion is correctly rejected.

The anchored maps are cheap native signed permutations, but their grammar is broader than applying one fixed base letter identically in every tensor factor. They are not automatically an admitted homogeneous Gaussian supplier or an intertwiner to the required independent endpoint jobs. The code's `anchored_model` field explicitly records this distinction. Full rank is not a complete κ improvement.

The conditional five-rank-three-in-fourteen arithmetic is correct at the checked rational points: 5¹⁶ 3¹⁵ > 14¹⁶ and 5¹⁵ 3¹⁴ < 14¹⁵. All nine displayed native savings exceed the hypothetical target 1/20 for the chosen parameters. The output explicitly says `supplier_exhibited = false` and `new_kappa = false`. This licenses a sufficient numerical funding target once its *complete* antecedent is met; it does not exhibit that antecedent. In particular, the assumed provider, all independent jobs, address grammar, precision and nine-row analytic hypotheses must be supplied by the actual construction.

The fixed-coefficient error envelope grows geometrically in recursion depth L, hence needs O(L) guard bits. Calling this logarithmic in a recursive dimension requires the explicit relation L = O(log dimension). For a C log n-bit native contract, one must bound the final precision plus input magnitude, guards and addresses by O(log n) with fixed constants. A Laurent degeneration whose guard is proportional to P L may exceed that contract when P = Θ(log n) and L grows; no finite-depth numerical example removes that obligation. The current tests contrast these envelopes rather than claim a completed precision theorem for an unknown supplier.

The newly added local-precedent padding test reports a forward tensor-action example and explicitly disclaims the converse theorem and kernel checking. Its source-only status must remain in the final handoff.

## Modular and signed-recovery model checks

The RAM lane's modular theorem is deliberately a ring theorem. The homomorphism Z[i,1/2] → F_p, i ↦ r, is not a star homomorphism when F_p has the identity involution: −r differs from r. Accordingly polynomial words and literal inverse words transfer, whereas Euclidean conditioning, positive definiteness and Hermitian-adjoint labels do not. The root's adjoint proof is over the Gaussian rationals and must not be silently relabeled as a split-field adjoint theorem. A nonsplit quadratic field with Frobenius involution is a separate possible target.

The full triangular port needs only its diagonal A and D to be units. Its coupling L need not be a unit. The characteristic-5 tests demonstrate exactly this distinction, while the optional polynomial coupling inverse requires 15 invertible. No odd-denominator exception is needed for the forward/reverse dyadic schedules themselves.

For signed negacyclic recovery, |h_j| ≤ r B² and M > 2 r B² are sufficient. Strict inequality matters; a signed endpoint at M/2 is ambiguous. The RAM test uses a strict margin, retains negative wrap, and pays two modulus channels. CRT does not make convolutions, prime/root construction or multiword reconstruction free. If M or the exact numerators exceed a fixed number of native words, their multiword costs must be restored. In the cp22f precision examples the complete coordinates already use Θ(log n) bits, so a C log n-bit word packs only O(1) of them.

Harvey's lazy butterfly requires p < β/4, not merely p < β; quotient approximations and twiddles are precomputed inputs to that kernel. The test proves correctness and word-range safety for those inputs. A full-product/high-word primitive can alternatively be compiled from a fixed number of bounded subword products if the native instruction set only returns a truncated product; setup of the quotient tables is still charged. These local kernel checks do not modify the recursive Gaussian paid profile.

## Bibliography audit

All 18 bibliography entries refer to actually inspected primary author/publisher sources. Their read depths distinguish four abstract-only items from statement/mechanism or local-proof reading; no full-paper proof audit is claimed. Preprint versus journal years are kept separate where needed: Fürer STOC 2007/SIAM 2009; DKSS preprint 2008/journal 2013; HHL preprint 2014/read manuscript dated 2015/journal 2016; cache-oblivious FOCS 1999/read journal revision 2012; NTT preprint 2012/read revision 2013/journal 2014. The Vigna author PDF is updated 2023 although the work is WEA 2008. The pinned 2026 manuscript identifies its author as OpenAI.

The verified relevant DOI metadata include 10.1007/BF02242355 (SS71), 10.1137/070711761 (Fürer), 10.1137/100811167 (DKSS), 10.1016/j.jco.2016.03.001 (HHL), 10.4007/annals.2021.193.2.4 (HV21), 10.1145/2071379.2071383 (2012 cache-oblivious revision), and 10.1016/j.jsc.2013.09.002 (Harvey NTT). Some DOI redirects were unavailable to the browsing tool; their publisher or author-hosted primary alternatives supplied the relevant text. This is an access limitation, not evidence that a DOI is invalid.

The HV21 full PDF access failed here; only its published abstract was used. SS71 full text was subscription-limited; only the publisher's summary was read. The original TFT author page explicitly notes a corrected multivariate mistake, and the review avoids relying on that uncorrected claim. The FFT-prime paper's prime-distribution hypothesis remains explicit. arXiv:2610.08144 and the mistyped arXiv:1904.00931 were verified as unrelated papers and excluded rather than attributed to integer multiplication.

The local Lean source records and notes are hash-pinned source inspection. No fresh source-matched kernel receipt or typed-port match was obtained. The canonical source tree and authoritative DAG remain unchanged.
