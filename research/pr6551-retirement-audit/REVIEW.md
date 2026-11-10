# Independent review of the PR6551 retirement cut

**Verdict:** no mathematical objection was found to carrying PR6545's independent retirement through the changed PR6551 tree allocation. The finite retirement cut has an independent exact check described below. This review is not admission of the complete supplier, a new kappa claim, a replay of native operators or outer inequalities, a human review, or a formal-kernel proof.

Frozen construction inputs are Ali Romman's PR6551 at `11ca568cd1a16776ade02b4df09ea04a784cc674` and PR6545 at `775722aa94a5e85b05d1d704d7dca10cbf016f0c`. Their exact `CONTROLLER.json`, `WITNESS.json` and proof hashes are recorded in `evidence/review-input-hashes.json`. The supplied reviewer script does not authenticate these pins by itself; the integrated package must bind its two data inputs before replay. No source or primary checking routine is imported or executed.

## A different exact check

`cut_four_fibers.py` treats the stage variables as formal multivariate monomials with Gaussian rational coefficients. It evaluates the central variable q at all four values `1,-1,i,-i`. It independently propagates a column forward and a row backward through each literal 345-event prefix. This is the input basis inverse, the complete 329-event original prefix through zero-based event 328, and the 11-event middle basis. Every one of the 35 pivot-column and 35 pivot-row positions is checked in each fiber, for both old and new callers. Both are exactly the scalar `S=lambda*q^(-1)` on coordinate 4 and zero elsewhere. The pivot scalar in these four fibers is respectively `1,-1,1,-1`.

This four-point check is exact for the claimed ring, rather than testing a few random numerical inputs. Put `A=Q(i)[D_0,...,D_18]`, or its Laurent localization when discussing inverses. Over A the four linear factors of `q^4-1` are pairwise comaximal, since their differences are nonzero elements of Q(i), hence units. Therefore

`A[q]/(q^4-1) -> A x A x A x A`

by evaluation at the four fourth roots is injective (indeed an isomorphism). The checker retains the D variables symbolically. It never specializes them, substitutes `q^2=1`, or approximates a coefficient. Thus vanishing in all four fibers establishes the pivot identities in the full stated q quotient ring. This is a written algebraic justification of the finite checker, not a formalization of that justification.

The script independently implements all used opcodes from the declared linear interfaces. The shared semantic premise is the source contract: `LOCAL(j,s,d)` maps `(s,d)` to `(D_j*s,D_j*d+q^-1*D_j*s)`, QUERY and ADD are translations, IDLE multiplies by its stage monomial, and LAMBDA multiplies by `(1+sign*i)/2+(1-sign*i)*q^2/2`. These same mathematical meanings are necessarily shared with the construction. The separate code representation and CRT argument reduce implementation dependence; they do not independently prove that physical native programs realize those meanings.

## Input independence and boundary argument

The old and new 345-event prefixes are literally equal. Their `WITNESS.json` records are also equal. The fresh coordinate 34 is never accessed before the handoff. Coordinate 4 is never accessed afterward except for its final scalar normalization. The script checks the two access facts against opcode-specific role slots, so stage numbers are not mistaken for register names.

Consequently the isolated output at the cut depends only on arbitrary initial coordinate 4, while the suffix receives independent arbitrary initial coordinate 34. There is no copying of a single input into two productive targets. The final inverse-lambda normalizer sends the retired `S` output to `q^-1`. The literal caller has 35 independent input coordinates from the start; lifetime language does not supply extra algebraic independence beyond this explicit input model.

For the conceptual unretired construction, the input basis G only mixes fields 4,20,21, whose normalized complete targets are all `S*C`. The changed child product is `C=D_10*D_11*D_12*D_13*D_14`; the equality of all three targets is the relevant property. G therefore commutes with the full normalized target F. All its elementary factors are invertible: ADD is a shear, each SCALE is a nonzero dyadic unit, and lambda is invertible because `lambda^2=q^2` and `q^4=1`. The same holds for J.

One implicit step in the source prose deserves being made explicit in an audit: if `J*P*G^-1=S direct_sum K`, proving that the matching suffix is block diagonal uses invertibility of K. This follows in the Laurent stage ring because the full prefix is a product of invertible gates. The same polynomial identities then descend to the polynomial subring by its injective localization. There is no gap from this step under the stated invertible stage contract. With that observation, source endpoint `F`, equal-target commutation, and `S^2=1` give suffix pivot block C. A full independently checked endpoint is still needed to bind the argument to the remaining 34-field word; that is the lead caller check, not this cut-only reviewer script.

The source all-width convention is also necessary: the ordinary coefficients in lambda and the basis gates remain outside tensor powers. Tensoring scalar coefficients separately would change the construction. This review accepts the factorwise substitution convention and does not discharge physical all-width realization, precision, erasure, movement or compiler hypotheses.

## Invoice and ordinary costs

For the claimed delta `208*(H41-H40-H57+H56)`, strict positivity at every `H_r=r^t`, `0<t<1`, follows directly from

`(41^t-40^t)-(57^t-56^t) = integral_0^1 t*((40+x)^(t-1)-(56+x)^(t-1)) dx > 0`.

The inequalities are strict throughout the integration interval. At t=0 or t=1 the delta is zero, so the open interval restriction is material. This establishes a favorable signed-invoice difference only after the complete histograms have been independently reconstructed; it neither determines a numerical crossing nor certifies a whole supplier budget.

A direct literal event count gives 609 versus 611 events and 17 versus 19 Q_POWER operations. The source ordinary upper-bound expression evaluates to `254699248` and `254932208`, respectively; their difference `232960=32*35*104*2` includes the two added events. This checks the arithmetic of the declared bound, not the physical proof of its per-event rate or all retained local route allowances. The body of `pricing.py` was read to assess that limitation; it was not imported or executed. In particular no claim of freshly verified raw root, tail decay, compiler threshold, BIT admission or 58 outer predicates follows from this review.

## Actual runs and controls

Commands, interpreter path, elapsed seconds, exit status and peak child RSS are in `evidence/review-runs.json`. Normal and optimized modes passed with byte-identical output receipts:

```sh
python -I -B cut_four_fibers.py OLD_CONTROLLER.json NEW_CONTROLLER.json
python -I -O -B cut_four_fibers.py OLD_CONTROLLER.json NEW_CONTROLLER.json
```

The runs took approximately 0.087 s and 0.170 s, with peak child RSS at most 13,608 KiB, on the activated CPython 3.12 environment. A canceling ADD pair is a positive operator-preservation control. Four deliberately invalid controls reject: input-basis sign change, middle-basis sign change, a fresh-input read before handoff, and retired-input reuse after handoff. The first two fail the exact pivot-row identity; the last two fail the corresponding input-lifetime condition. No assertion is used for scientific acceptance inside the checker, so the optimized run exercises the same checks.

Timing was recorded with Python's `time.monotonic` and `resource.getrusage`. The final two receipts and `evidence/review-runs.json` describe the final checker bytes.

## Resolved findings and remaining obligations

There are no unresolved blocking findings for this scoped cut argument. The implicit invertibility step is supplied above, the `0<t<1` restriction is retained, and the distinction between arbitrary independent caller inputs and retained-state physical execution is explicit. The unmodified native source, complete paid inventory, full endpoint, physical phase/rank interpretation, numerical moments and five framework assumptions remain separate dependencies. No universal optimality statement is supported.

The useful next review step is to combine this cut certificate with the independent complete endpoint and literal invoice derivation, then retain the exact source pins when assessing supplier admission. This review does not reserve a continuation or recommend a wider tree search merely from the positive local result.

Prepared for DLamdata with substantial OpenAI Codex assistance in a separate native AI review role. The construction and retirement identity remain Ali Romman's contribution, with the predecessor credit and Apache-2.0 notices in the frozen packages. Separate AI implementations are not independent human review or maintainer acceptance.

## Review of the integrated primary checker

After sealing the independent cut verdict, I read the lead's `caller.py`. It represents complete transfer rows by keys `(input_coordinate, q_exponent_mod_4, eighteen_stage_exponents)` and checks all 1,225 coefficient positions for both callers. The opcode updates, lambda arithmetic and LOCAL update order agree with the declared linear contract. The expected-output reader explicitly requires the serialized unused D0 coordinate to be zero before omitting it; native stages and idle-stage sets are restricted to 1..18. No loss of a live stage variable was found.

The primary cut test checks both isolated pivot/fresh rows and the absence of their input columns in all other rows. It also enforces the access lifetime independently of the final endpoint. In particular, its endpoint-preserving ADD/negative-ADD use of the retired field is correctly rejected by the lifetime check. The input-pin layer remains outside `caller.py`; it must run before interpreting these frozen files. This is a deliberately fixed-source checker, not a general untrusted-program validator. No blocking implementation finding was found.

The primary and this review share opcode semantics, frozen source data, Python Fraction arithmetic and the same physical hypotheses. Their polynomial representations and acceptance routes differ (complete sparse transfer versus exact CRT fibers at the cut), so their agreement is corroborating evidence with those dependencies disclosed, not two independent physical proofs.
