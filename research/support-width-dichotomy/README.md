# When width-dependent native controls must grow their operator support

A local written theorem sharpens the existing nonlinear weighted-monomial control obstruction: **the complete operator set need not remain fixed as width grows**. A pointwise support/rank bound suffices, even when operators, weights, coefficients and auxiliary coefficient spaces change with width. In the declared 112-owner four-control interface, this excludes every sublinear-support exact control family. A matching general example shows why growing support can escape, while a two-term example shows why approximate recovery needs a separate precision argument.

The complete statements and proofs are in [PROOF.md](PROOF.md). This is a local mathematical derivation with exact finite calibration, awaiting independent review. It establishes no new κ, paid-query minimum, unconditional multiplication theorem or change to the selected result.

## The theorem in usable form

At width f, consider an endpoint expansion

`P_f = Σ_i B_i(f) ⊗ A_i(f)^⊗f`.

After correctly combining proportional one-column maps, let m(f) be the number of nonzero projective classes and r(f) their linear span rank. If

`f >= m(f) − r(f) + 1`,

then the tensor terms are independent, including with matrix/operator coefficients B_i on a separate auxiliary space. Therefore P_f=0 forces every B_i=0. The simpler sufficient condition is **m(f)<=f+1** for m>=2. Equality of two implementations uses their **combined** support. A proportionality A_i=λA_j contributes λ^f to the coefficient.

The scalar independence bound is classical: [Anthony Chefles, Section II](https://arxiv.org/abs/quant-ph/0105016). The repository's earlier tensor-separation proofs also contain the m−1 sufficient bound. The contribution here is a source-specific **moving-support obstruction and escape boundary**, with explicit expansion counts and executable certificates. Global literature priority is not asserted.

There is no assumption that the complete products come from a fixed set, that their word lengths are bounded, or that their nonlinear monomial weights are Clifford phases. Formal word labels must still be interpreted as actual one-column maps before claiming distinct projective classes. A free-word exclusion does not automatically become a physical exclusion.

## Concrete source consequence

The released interface from [#4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933) uses four ostensibly free controls: T0, its central Q conjugate, its D conjugate T, and the terminal control `E=Q^-1 C3 T C1 Q^-1`. Its code A from [#4929](https://github.com/CrocSwap/integer-mult-bounds/pull/4929) is invertible with zero diagonal; the source's distinct normalized directions and the q/U/W coset geometry make every nonzero terminal source term nonmonomial.

Let s0,sQ,sD,sE bound the number of monomial tensor terms in each respective owner block. If A has maximum row support R and column support C, the written theorem proves

`f+1 >= max(s0+sQ, s0+sD, RC s0+sE)  =>  T0_f=0`.

The retained source has **112 owners and R=C=52**. These counts and its code factorization are freshly checked from authenticated excerpts. If every block in the four controls has at most s(f) terms, then

**`2705 s(f) <= f+1  =>  T0_f=0`.**

Thus a nonzero all-width family in this interface requires **s(f)>(f+1)/2705**. This excludes all sublinear-support families, including controls whose complete one-column words vary without bound with f. Auxiliary registers and feedback do not avoid the conclusion when their extracted endpoint blocks obey these counts. The factor 2705 is sufficient, not optimal.

The result does not exclude linearly growing expansions, changed observations, extra paid calls, different productive endpoints or noncolumnwise routing. It is not a scalar-operation or paid-Gaussian-call lower bound. A compact circuit can generate a large expanded support, so support size must not be silently identified with execution cost.

## Sharp escape and precision boundary

Take the fixed Gaussian-rational unitary `D=diag(1,(3+4i)/5)`. At width f its spectrum has exactly f+1 distinct eigenvalues. Its minimal polynomial gives

`Σ_{j=0}^{f+1} c_j(f) (D^j)^⊗f = 0`.

All **f+2** coefficients are nonzero. The maps are powers of one fixed generator, yet they have a real tensor relation exactly one term beyond the universal support threshold. The coefficients have O(f²) bit length and can be constructed in O(f²) exact arithmetic operations. This is an explicit growing-support algebraic escape, not a useful physical supplier or a construction in the selected free alphabet.

Exact rigidity also does not establish approximate rigidity. A changing two-dimensional unitary with angle O(1/f²) satisfies

`0 < ||U(f)^⊗f−I||_op <= 2/f`.

Two projectively distinct terms can therefore approach cancellation while remaining exactly independent. The proof supplies a quantitative Gram bound when the actual one-column overlaps are controlled. Conditioning, coefficient precision and exact recovery are necessary new obligations for an approximate route.

## Significance for researchers

The result answers a concrete unresolved scope question in the retained nonlinear-control proof: allowing the complete product set to change with width does not itself invalidate the exact obstruction. A sublinear number of endpoint terms is still insufficient. Researchers can stop searching that class, use a pointwise certificate to reflect sparse formal identities into physical semantics, or deliberately investigate the identified escapes: linear support growth, noncolumnwise maps, changed observations and controlled approximation. The source-specific coefficient and general sharp examples make those choices measurable.

## Independent follow-up problems

| Investigation | Useful outcome | First discriminating step / main obstacle |
|---|---|---|
| **Review moving-support reflection** | A reviewed theorem or a precise correction to its quantifiers. | Check projective merging, coefficient spaces and each support union in Proof Sections 1–3. The classical separation lemma is credited, not a new research target. |
| **Tighten the 2705 multiplier** | A stronger source-specific support lower bound. | Count actual terminal projective classes and their span ranks, preserving the full zero mask. Raw RC is conservative; a local cancellation is not a new caller. |
| **Extract certificates from emitted programs** | A reusable semantic checker for evolving native alphabets. | Produce a correct expansion for one actual control block, including phase powers, source versions and auxiliary returns. Unreduced word labels cannot stand in for physical operator classes. |
| **Price a growing-support escape** | A new admissible width-dependent contract or a complete-cost rejection. | Implement the f+2-term annihilator with all coefficient generation, precision and field passes charged. An identity alone computes no additional productive Gaussian job. |
| **Quantify approximate escape** | A robust obstruction or a recovery-safe approximate module. | Bound the actual Gram separation and consumer error together. Two-term near-cancellation defeats an unconditional approximation barrier. |
| **Change the columnwise interface** | A concrete mechanism outside the theorem with retained independent inputs. | Specify a cross-column or observation-carrying program and price its storage, transport and return. A new representation is not automatically a legal child ABI. |

## Evidence and reproduction

```sh
python3 -I -B research/support-width-dichotomy/verify.py
python3 -O -I -B research/support-width-dichotomy/verify.py
# Optional authentication against the pinned canonical checkout:
python3 -I -B research/support-width-dichotomy/verify.py --source-root .
```

Python standard library only. The checker verifies 60 rational vector sets, 330 explicit separating certificates and a separate compressed tensor-rank calculation; seven moving-support families; the sharp rank-refined example; a characteristic-two control; exact Gaussian-rational annihilators at f=1..8; and two-term approximate examples at f=1..12. Omitted annihilator terms, reuse at the next width and projective duplicates reject. Source calibration checks all 12,544 code entries, M^T M=56I, the zero diagonal, all row/column supports and 112 distinct binary port maps. These finite checks supplement the written proof.

[RESULT.json](RESULT.json) records the output. [VALIDATION.json](VALIDATION.json) records the actual environment and read-only portable/optimized checks. [SOURCES.json](SOURCES.json) pins the exact canonical sources; [FIXTURE.json](FIXTURE.json) contains literal code/mode/port excerpts. The original producer, full 17-axis phase engine, native tape/compiler, selected cold replay, Lean and Docker were not run. The package is not registered with the generic replay workflow; these commands are the scoped local reproduction.

## Predecessors and novelty boundary

The canonical source checkpoint is [`1a3ced60b2f7a46bc70280a04f2eeb8ca027c700`](https://github.com/CrocSwap/integer-mult-bounds/commit/1a3ced60b2f7a46bc70280a04f2eeb8ca027c700), selected conditional κ=.003027288235. The nearest predecessor is [#5210](https://github.com/CrocSwap/integer-mult-bounds/pull/5210)'s [nonlinear weighted-monomial control ceiling](https://github.com/CrocSwap/integer-mult-bounds/blob/1a3ced60b2f7a46bc70280a04f2eeb8ca027c700/research/nonlinear-monomial-control-ceiling/README.md), which explicitly retains a fixed finite set of complete products and excludes unbounded width-dependent products. Its support-partition argument is preserved and restated, with a pointwise cardinality hypothesis replacing that fixed-set condition.

Earlier finite-alphabet/projective tensor separation appears in [#4928](https://github.com/CrocSwap/integer-mult-bounds/pull/4928) and [#4978](https://github.com/CrocSwap/integer-mult-bounds/pull/4978); [#5160](https://github.com/CrocSwap/integer-mult-bounds/pull/5160) supplies the monomial-Clifford control predecessor. The [native tensor cutoff, #5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369), has a different fixed affine-quadratic language and constructive width bound. The robust terminal error floor in [#5111](https://github.com/CrocSwap/integer-mult-bounds/pull/5111) concerns a specified actual inverse-postdecoder target and permitted operations; the changing-operator near-cancellation here does not contradict it. Its source-specific analysis is a starting point for an approximate extension.

The standalone 112-paid-call optimum in [#5425](https://github.com/CrocSwap/integer-mult-bounds/pull/5425) uses a fixed ordinary-only fanout grammar. The present expanded-support theorem establishes no paid-call minimum and does not extend that bound to an observation-carrying caller.

Before submission, canonical [`32890bc5de034ab8fc93ac88ead7279a6a416d04`](https://github.com/CrocSwap/integer-mult-bounds/commit/32890bc5de034ab8fc93ac88ead7279a6a416d04) was checked on 2026-10-24 at 13:19 UTC. Priority revision 7, the selected result, applicable guidance and all eight pinned source files are unchanged. The existing scientific pins and calibrated result are retained; the [overlap snapshot](OVERLAP.json) records the submission refresh.

The cached [overlap snapshot](OVERLAP.json) covered 322 open PRs, 4,710 discussion records and 7,377 local notes. Nearby source bodies and their mathematical reviews were read. Arbitrary historical diffs and unpublished work remain outside this search. The new [owned-helper exclusion](https://github.com/CrocSwap/integer-mult-bounds/pull/5433) and [observation audit](https://github.com/CrocSwap/integer-mult-bounds/pull/5427) concern different contracts; this theorem does not independently validate or generalize their claims without checking their actual operator expansions.

Native/source credit remains with [Chris R](https://github.com/Clear1nsight), [Ali Romman](https://github.com/aliromman), [Dillon Amburgey](https://github.com/dillona), [David Ganz](https://github.com/Dugongue), [Cinna Davis](https://github.com/1337isnot1337), [Cao Yifan](https://github.com/intqwq), [zxv](https://github.com/zxv), [Jacob Alan Sussman](https://github.com/Mister-Meeseeks) and the full retained Clifford, geometry, compiler and verification lineage. New prose and code are Apache-2.0 with substantial OpenAI Codex assistance. No global literature-priority or independent human/formal acceptance claim is made.

## Open next questions

1. **Does the pointwise source corollary survive independent review?** Start with the three support inequalities and the q/U/W partition proof. The auxiliary coefficient-space interpretation and correspondence to actual four-control endpoints need particular scrutiny.
2. **How much can actual support geometry improve 2705?** Start with one terminal (i,j) block, merge actual projective products and compute span rank. Efficient representation of the moving operator set is the obstacle.
3. **Can the growing-support identity help a real caller?** Start with one paid consumer and its required output, then price coefficient generation and every pass. The present identity is an escape witness, not an implementation of that output.
4. **Can approximation evade the source obstruction while preserving recovery?** Start with the actual consumer norm and precision budget. Exact independence alone supplies no answer.
