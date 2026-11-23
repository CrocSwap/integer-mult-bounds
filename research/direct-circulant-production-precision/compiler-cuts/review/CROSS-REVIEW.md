# Independent review: complete-gate compiler cuts

**Decision:** accept the scoped mathematical result in the frozen author proof. No mathematical repair is required. Publication should include the overlap clarification below and preserve the stated source, conditioning, rank, phase-service and per-atom error premises. This is an independent model-assisted review, not independent human acceptance or a formal kernel proof.

Reviewed proof SHA256: `162dd4bb7a020dfb72dd3c80cb9a1de37212cc7f812f36fd4365d487d49b341b`.

Canonical source commit: `e54523517d0f03e58352e647c403a5af3e525a57`. The independent checker authenticates all 18 files in the author's `ORIGINS.json`, including their byte lengths, SHA256 values and Git blob identifiers, before execution. The proof is authenticated again after execution. The old author-proof status and interrupted receipt are historical; this dated separate review supplies the new review outcome without rewriting the frozen proof.

## 1. Accepted theorem and its boundary

For the literal pinned `Builder`, `Triangle`, `Program` and `Full` words, the existing sufficient four-way envelopes extend to cuts after any subset of **complete** one- or two-wire gates in a matching layer. The four operators are the prefix, suffix, inverse prefix and inverse suffix. The accepted envelopes are

\[
K_\triangle=3200m^3,
\qquad
H_G=\max(3200m^3,2+2k_G)(10+4\alpha+2k_G),
\]

and

\[
K_{\rm Full}=2L_0\mathcal B\mathcal H,
\quad \mathcal B=256N^3(\lambda Q)^{12}.
\]

The statement concerns the exact linear program with the stored coefficients. A Full interval has the conservative bound `K_Full^2`. It does not say that a partial cut is bounded by the measured maximum of its two neighboring whole-layer cuts. It does not cover an intermediate assignment of only one output of a two-wire gate, arbitrary alternative implementations having the same endpoint, or the internal states of an unexamined recursive replacement service.

This supplies a source-specific supplement to the same Full word used in #8093. The finite-carrier construction in #8092 is a different implementation and receives no compiler, tape, ownership or analytic discharge from this result. The selected canonical constant remains `.00363005817`; no selected assumption is removed by this review.

## 2. Why the primitive claim is sound

I inspected the pinned coefficient factory and elementary-gate construction. Every non-crossing elementary gate acts within one bank and is exactly unitary: swaps, rational unit-modulus phases, and the stored butterfly with `a^2+b^2=1`. Its inverse is the inverse of those same stored coefficients. The cyclic and negacyclic diagonal shears both have the same source-to-target direction; their intervening transforms and twists preserve the two banks.

Writing an arbitrary resulting fragment as

\[
A=\begin{pmatrix}U&0\\X&V\end{pmatrix},
\]

the diagonal blocks are unitary. A bank-local unitary preserves the norm of `X`; a shear updates it to `X+DU`, increasing its norm by at most `||D||`. Selecting complete gates from one matching changes a diagonal shear multiplier to a coordinate restriction and never increases its norm. A partial unitary matching remains unitary. Every chronological primitive interval encounters at most the two original shear matchings, so

\[
\|X\|\le M_g+M_h+2v,
\qquad
\|A\|,\|A^{-1}\|\le1+M_g+M_h+2v.
\]

The inverse off-diagonal block is `-V^{-1}XU^{-1}` and has the same norm. This proves all four fragment bounds directly, without interpolation. Order is essential: no overlapping bank transformations are commuted. The exact checker verifies the bank blocks, orthogonality and inverse formula separately; it does not infer them merely from a correct final endpoint.

Two adversarial cases explain the assumptions. Opposite-direction shears of coefficient two produce `[[5,2],[2,1]]`, whose first-column squared norm is 29, exceeding the square of the false additive cap 5. Compensated nonunitary scaling also permits intermediate amplification even when all whole-layer operators and inverses have a common cap. Neither case belongs to the pinned primitive alphabet.

## 3. Triangle and generator composition

`Triangle.parallel` checks the equality of sibling macro-boundary partitions, and siblings occupy disjoint supports. Therefore the active fragment is a direct sum of primitive fragments, rather than a product of arbitrarily staggered recursive subwords. The source near-identity admission and ideal-prefix bound `B=100m^3` remain hypotheses/results of the retained compiler proof. The fragment extension adds the local cap 7, or the scalar cap 4, to that existing argument.

The perturbation algebra is correct in its stated order. With ideal prefixes `Q_j`, normalized errors `G_j=Q_j^{-1}E_j Q_{j-1}` and stored prefixes, a suffix is exactly

\[
Q_q\bigl((I+G_q)\cdots(I+G_{j+1})\bigr)Q_j^{-1}.
\]

Only one consecutive product occurs. When the sum of error norms is at most one quarter, every consecutive product and its inverse have norm less than two. Using two separately bounded perturbation prefixes here would obscure the cancellation and unnecessarily enlarge the constant. The resulting completed-prefix and suffix caps, combined with the active primitive/scalar cap, fit inside the existing `32B` allowance. The literal inverse word exchanges prefixes with inverse suffixes; it must not be replaced with independently rounded forward macros or adjoints of nonunitary scalar leaves.

The generator chronology `p; S(h); p^{-1}; S(-h)` is also correct. `p^{-1}` is the paired stored inverse, and compensation negates the same stored multipliers. The endpoint is `S(h(p-I))`. I rederived all four checkpoint prefixes, suffixes and inverse formulas in the proof. In particular, the second suffix is `L(p^{-1},Cp^{-1}-h)`, whose product with `L(p,A+hp)` cancels the intermediate `hp` term in the required order. The common cap `4+4a+2k=10+4alpha+2k_G` follows without multiplying a separate amplification for every generator term. The primitive allowance `2+2k_G` retains its source hypotheses `k_G>=2` and `v<=1/2`.

## 4. Full downsets and actual cut chronology

The source domain includes **`lambda>=1` and `Q>=1` individually**, as enforced by `full.allocation` and the clamped return of `admission`. The weaker condition `lambda*Q>=1` alone would not justify the retained pivot and completed-downset estimates. A scalar `1/1024` with unclamped `lambda=1/1024,Q=1024` has product one but inverse norm 1024, exceeding `B=256`. This is outside the source domain. Integration should preserve the individual lower bounds explicitly when summarizing the theorem.

For the admitted domain, I checked the original downset derivation and source recursion. An internal node executes its upper shear, then both disjoint child programs, then its lower shear. An ideal downset has factorization `L(I)D(I)U(I)`; its lower factor is a direct sum over maximal completed subtrees, and its upper factor is `U_F^{-1}u_root` for the unvisited-upper frontier. Inverse factors occur in reverse order. The existing `W=3N chi^2`, `V=6N chi^4` and partial-pivot bound give `216N^3 chi^12 < B`. These estimates are inherited from the retained conditioning proof, not a new improvement to the predecessor's downset constant.

Actual timestamps classify a zero-duration atom as complete at its source position. At an interior matching cut, the complete and active sets satisfy the legal downset requirements; active atoms are incomparable and disjoint. A selected complete last gate may already finish its active atom's fragment without changing the validity of the conservative timestamp classification. Unequal sibling durations preserve the disjoint-support argument. The prefix is `F Qhat(I)`, while the suffix is `Rhat T`, and inverse formulas preserve reversed multiplication order. Only disjoint incomparable atom work can be reordered.

For the remaining whole-atom suffix, take a legal order `I,A,remaining`. The same normalized consecutive-product identity bounds the suffix after `I union A`; using the independent cap on active tails then gives `2L0 B H`. No factor proportional to the number of active atoms occurs because their direct sum takes the maximum norm. The root-scalar case and empty rank-zero identity atoms are included. An arbitrary interval is `P_b P_a^{-1}`, so its bound is `K_Full^2`, not the primitive interval cap and not an endpoint condition number.

## 5. Independent executed checks

`check_independent.py` was written for this review and never imports or executes the author's `audit.py`. It imports the authenticated retained `engine`/`exact` coefficient factory to obtain actual elementary gates. All reviewed gate multiplication, realification, inverse elimination, block checks and downset calculations use a separate standard-library Fraction implementation. Complex rational gates are realified into twice as many real coordinates; inverses use a separate last-available-pivot elimination. The downset fixtures are independently generated exact non-Hermitian Toeplitz LDU trees, not the author's instrumented Full traces.

The normal and optimized receipts record these checks:

- 760 primitive cuts at bank widths 1, 2 and 4, including 700 proper partial-matching selections and 3,040 four-way structural certificates. Every matching subset is enumerated in each fixture.
- 90 source gates independently classified by bank support and exact orthogonality or same-direction shear form. The two spectral layers and their multiplier bounds are checked explicitly.
- 726 source cut witnesses distinguish suffix-times-prefix order from its reversal.
- Additional chronological primitive intervals check the bank invariant, inverse formula and `P_b P_a^{-1}` identity. Exact counts are in the receipts.
- All 46 abstract downsets for three independent LDU trees: 2 at size one, 6 at size two and 38 at size four. These check factorization, unvisited frontier, inverse order and a rational Frobenius consequence of the old `B` envelope.
- Four generator checkpoints check prefix, suffix and both inverse identities. Missing the paired inverse, changing one compensation coefficient and reversing noncommuting chronology are rejected.
- Five normalized suffixes and five inverse suffixes check the single consecutive-product formula; three distinguish reversal of the normalized factors.
- The nonunitary-scale control has common whole-layer and inverse cap 10 but intermediate first-column squared norm 128; the opposite-direction shear control has squared column norm 29 against false cap squared 25; the split swap coordinate-write matrix is singular.
- The unclamped-conditioning scalar control has `lambda Q=1` but inverse norm 1024, violating the claimed completed-prefix cap 256 if the individual source bounds are improperly dropped.

The primitive certificates are exact algebraic certificates of the bank invariant and coefficient bounds. They are not an independent numerical spectral optimization or a PSD-eigenvalue test. The universal norm inequality is the written argument in section 2; bounded enumeration corroborates its source binding. Similarly, the 46 independent LDU downsets are not the author's larger source-timestamp sweep. The author reports separate execution evidence in its own receipt; those counts are not claimed as independent reviewer executions.

Run from this review directory, with `SOURCE` denoting the directory containing the frozen proof and `retained`:

```sh
python3 -W error -I -B check_independent.py --source "$SOURCE" --output EVIDENCE.json
python3 -W error -I -O -B check_independent.py --source "$SOURCE" --output EVIDENCE-OPTIMIZED.json
```

All logical checks use explicit exceptions and remain active under `-O`. Proof-relevant receipt fields match after removing only the elapsed `seconds` field. These bounded checks do not independently establish all-size rank, phase or analytic hypotheses.

## 6. Required overlap and credit clarification

Brian/JoyboyBrian's [#4976](https://github.com/CrocSwap/integer-mult-bounds/pull/4976) provides the unrestricted sharp `sqrt(2)` matching interpolation and asks about compiler alphabets. It should not be described as wholly untouched until this work: Nick Petalas's merged [#5940](https://github.com/CrocSwap/integer-mult-bounds/pull/5940), head `b709a6adb6a9543247260900b108166a4d469f6f`, proves the sharp conditioned factor

\[
\sqrt{\frac{2K^2}{1+K^2}}
\]

when a gate and its inverse have norm at most `K`, including no loss for a unitary layer. Its shear specialization has squared factor `1+u/sqrt(u^2+4)`. This author proof is different: it uses the structure of the **whole stored source word**, including both same-direction shear matchings, to retain a stated sufficient envelope. It does not improve the sharp generic conditioned interpolation formula, prove measured-adjacent no-loss, or claim the four-way coupled sharpness that #5940 itself leaves open.

Armin Pourshafeie/apoursh's merged [#5240](https://github.com/CrocSwap/integer-mult-bounds/pull/5240), head `6d0a6043120880c696d0850e9242a16e6fb980a5`, already audits the actual `exact.py:apply` rounded-output semantics, one residual vector per layer, stored-coordinate splice and unchanged component-width implication. It also supplies the singular partial-write swap warning. The swap in this independent checker is an inherited boundary rejection control, not a new discovery. The present source-fragment result does not claim its rounded-event or component-width theorem as new work, and does not supply the outstanding local arithmetic temporary-width proof.

The two preceding scope comparisons use the full downloaded PR bodies supplied by the coordinating reviewer. Their mathematical proofs were not independently audited here and are not inputs to the new bank-invariant proof. Exact PR heads identify the compared contributions; merge status was checked by the coordinating reviewer. Parent package integration should carry these credits in its README/overlap appendix without altering the reviewed proof bytes.

Further inherited results are Brian/JoyboyBrian's #4755 source-timed trace and #4977 allocation adapter, Nick Petalas's #4852 sharper completed-downset bound, and Jose Manuel/jmbarrancoml's rational compiler, conditioning and allocation results. This proof deliberately retains the older `B=256N^3 chi^12` source allocation rather than importing #4852's smaller bound. Vlado Vojdanovski's recursive matching schedule, Chafik Boukhalfa's phase service and the retained exact Stein producer remain credited premises.

## 7. Integration decision and remaining obligations

Accept the complete-gate fragment extension and its propagation through the unchanged factories. Preserve the proof hash, attach this separate review and both independent receipts, and state the individual conditioning lower bounds in the integration appendix. No selected frontier update or new kappa is justified by this result. The author proof's historic “separate review pending” line should be explained by the current completion record, rather than treated as a missing execution.

All-size conditioning and component guards, exact rank/displacement contracts, phase certificates and per-atom operator error must still be supplied by the caller. Physical arithmetic, scratch-register states, coefficient preparation and delivery, tape realization, temporary widths and analytic recovery remain outside this lemma. Any altered recursive gate implementation needs its own fragment and inverse bounds. The source-specific whole-word theorem should be published as that scoped addition, with the existing interpolation and rounding work credited distinctly.

Review completed 2026-11-23 UTC by a separate OpenAI agent for Jerry Chen / @CubeJerry. No author checker was imported as independent evidence.
