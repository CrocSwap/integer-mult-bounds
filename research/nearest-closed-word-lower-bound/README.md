# Nearest coefficient rounding attains quadratic closed-word error

DONE — nearest coefficient rounding still requires quadratic closed-word guards. This answers a specified-policy case of Open next question 2 in Nick Petalas's [PR #5153](https://github.com/CrocSwap/integer-mult-bounds/pull/5153), with a [pinned statement of that question](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/closed-word-rounding-guard/README.md). Scoped written lower construction with exact finite checks; no new kappa or selected-frontier change. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202#discussioncomment-19149680) is complete.

**Policy and word.** Round every gate entry to the nearest multiple of h=2^(-P), P>=1. Any tie convention is allowed: none of the constructed coefficients is a tie. Apply the rounded matrices with exact arithmetic; this isolates coefficient rounding from arithmetic rounding.

For q,m>=1, set s=2^q and define

```text
S = diag(1/2,2),             U(a) = [[1,a],[0,1]].
Execution order:
q copies of S,
m copies of the three-gate loop U(a), U(a), U(-2a),
q copies of S^(-1).
```

The gate count is K=2q+3m. The exact endpoint is I. Every exact gate, its inverse, every rounded gate and its inverse have infinity norm at most 2 and determinant one. Two coefficient choices give the following exact formulas:

```text
Dyadic family: a=3h/8.
  exact prefix/inverse maximum B = s(1+3h/4),
  rounded endpoint = U(-m h s^2).

Fixed rational family: a=1/3, independent of P.
  exact prefix/inverse maximum B = 5s/3,
  rounded endpoint = U((-1)^(P+1) m h s^2).
```

In both families the endpoint operator error is exactly m h s^2. The input vector (0,1) attains this error. The fixed rational word therefore exhibits the amplification at every dyadic precision. The dyadic family shows the same obstruction within the class of dyadic exact coefficients, but depends on the selected grid; a single fixed dyadic word is eventually represented exactly.

**Proof.** Each exact loop has coefficient sum a+a-2a=0. Scale entries 1/2 and 2 are exact on every grid with P>=1. For a=3h/8, the three rounded coefficients are 0,0,-h. For a=1/3, 2^P has residue 1 or 2 modulo 3. Direct nearest rounding gives a coefficient sum of -h for even P and +h for odd P. These are not arbitrary error assignments.

All m rounded loops commute and sum to U(plus-or-minus m h). The scale blocks conjugate this to U(plus-or-minus m h s^2). This proves the exact endpoint and error formulas.

During a middle loop an exact prefix is U(t)diag(1/s,s), where t is 0,a,or 2a. Its inverse is diag(s,1/s)U(-t). Since s>=2 and 0<=t<=2/3, their largest infinity norm is s(1+t). The maximum occurs at t=2a. Earlier and later scale prefixes have norm and inverse norm at most s. This proves the displayed B. Local gate bounds and determinant statements follow directly from the displayed two-by-two matrices and their inverses.

**Guard consequence.** Taking m=q gives K=5q. For every fixed epsilon>0, the ratio of the actual error to K B^(2-epsilon) h tends to infinity as q grows. Thus nearest rounding cannot replace the quadratic B power by any smaller fixed power in a uniform closed-word bound of this form. More generally the same construction defeats a smaller power times any fixed polynomial in K. At fixed q, varying m proves linear growth in the number of repeated loops while B stays fixed. Choosing P>=2q+ceil(log2(m))+4 keeps the actual error at most 1/16; the obstruction is present in the small-error regime.

This does not establish an optimal numerical guard constant. The predecessor's arbitrary-error lower construction and endpoint upper theorem retain their credit. The new point is an explicit correlated error pattern produced by ordinary deterministic nearest rounding, with a fixed-rational version and a dyadic version.

**Evidence.** Both warning-strict normal and optimized CPython 3.12.14 checks pass 288 cases, 6,876 literal prefixes, 96 small-error cases, and four controls. The checker quantizes the actual matrix entries, multiplies the full gate lists, computes each inverse from its determinant, and checks all prefix, local-gate and endpoint identities. It also confirms that opposite shear pairs cancel under this policy, so an independently perturbed inverse-pair example cannot simply be reused.

Base: canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority revision 7. Main, the live Discussion/PR snapshot, the exact released question and pinned precision notes were checked. This changes the formal-interface card to a written precision side result. The source's production-caller question, rounded matching-layer audit, and active native work remain distinct.

**Limits and next question.** Coefficient rounding is the only error in the constructed execution. A compiler can remove these symbolic zero loops before rounding. The lower bound concerns unchanged emitted words, not every possible compilation method. This does not implement data rounding, prove a selected caller uses these words, price state widths or physical movement, or change a supplier/outer bill. A useful next step is to test whether a specific emitted word has exact algebraic coefficient relations that its storage format preserves; such structure could exclude this example. No predecessor scientific replay, selected cold replay, native replay, Lean or Docker build was run.

Credit Nick Petalas's PR5153 for the open deterministic-policy question and the retained sharp-power context, ywz65's [PR #2701](https://github.com/CrocSwap/integer-mult-bounds/pull/2701) for the simultaneous-error theorem, and Vlado Vojdanovski's [PR #1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673) for the Toeplitz precision interface. Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0. No independent human or proof-kernel acceptance is claimed.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/nearest-closed-word-lower-bound
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_DETERMINISTIC_CLOSED_WORD`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Test which exact coefficient relations a production storage policy preserves. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
