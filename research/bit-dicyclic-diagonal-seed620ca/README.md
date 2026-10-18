# A bounded non-sharing result for three diagonal outputs over `F2[Dic_3]`

**Status: scoped finite negative; no new `kappa` or supplier.** The exact census finds no paid-call saving in either of two stated endpoint layers of a three-register dicyclic address model. It does not prove a lower bound for other groups, generators, endpoints, or word depths.

The work uses accepted seed `620ca5cd76dec930418c29abde328dc6` on selector base `fcea6916f3af98346ff13581ac7626718b7e55a2`, track `bit-mechanisms`, task `bit-new-register-model`, priority revision 3. The selected-record SHA-256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`; the catalogue SHA-256 is `6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075`. The claim and pivot update are on [the research coordination discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931125) and [the depth-five scope update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931245).

## Exact model and charged baseline

Use the dicyclic group of order 12

\[
\mathrm{Dic}_3=\langle u,v\mid u^6=e,\ v^2=u^3,\ vuv^{-1}=u^{-1}\rangle
\]

in its group algebra over `F2`. A paid operation is

\[
D_N([g])=I+([g]+[e])N,
\]

on exactly three registers, with `g` one of the two charged letters `u` or `v` and `N=xy^T` one of the 28 rank-one idempotents over `F2^3` (`x,y` binary and `y^T x=1`). Each generator call costs one. Inverses, register changes, helpers, and endpoint translations are not free operations in this model. The inverse of a paid factor is used only algebraically for the meet-in-the-middle lookup; it is never counted as an available call unless its label has a positive `{u,v}` spelling.

For a target `diag([w0],[w1],[w2])`, the fully charged separate construction applies the coordinate idempotent `E_ii` once per letter in a shortest **positive** `{u,v}` spelling of `wi`. The table of shortest distances is included in `EXPECTED.json`; its maximum coordinate cost is four, so the maximum three-coordinate bill is twelve. Every endpoint comparison is coefficientwise in `F2[Dic_3]`, not a finite column smoke test.

## Result

The endpoint universe is all `12^3 = 1,728` ordered monomial triples. The two tested layers cover every triple for which their stated saving threshold can apply:

| Search layer | Direct coordinate bill | Paid-word cap | Endpoints checked | Exact words found |
|---|---:|---:|---:|---:|
| First bounded stage | at least 5 | 4 | 1,482 | 0 |
| One evidence-driven pivot | at least 6 | 5 | 1,230 | 0 |

The first stage tests every depth-four-or-less word for any endpoint where it could save at least one call. After it found no hit, the single pivot raised the word cap by one and retained a one-call improvement threshold. The pivot found no hit in its larger direct-cost layer. The canonical coverage SHA-256 values are `a1398353921f55628c8329852554a6538f2a075eccc51ae127e25bfc791727f3` and `816765d363f764fdaf4b3cbe4f1bc10ed235fc664924ea11a4112046d2157a1b`.

The exact meet-in-the-middle census keeps one shortest representative for each distinct product matrix. There are 2,409 distinct products through depth two and 92,318 new products first appearing at depth three (94,727 total through depth three). For every target `T` and every prefix product `P` through depth two, it checks whether `P^{-1}T` is in the appropriate suffix table. Every word through four calls splits into two pieces of length at most two; every word through five splits into a prefix of length at most two and a suffix of length at most three. Equal product matrices can share one representative because multiplication by any later factor depends only on the current product, and the retained representative has minimum length.

This is a scoped obstruction to shallow cross-output call sharing in this exact alphabet. It is not a theorem about unrestricted nonabelian groups or arbitrary generator sets, and it does not modify the selected result or establish any change in the conditional integer-multiplication bound.

## Reproduce and controls

From the repository root, run:

```sh
python3.12 research/bit-dicyclic-diagonal-seed620ca/verify.py
python3.12 scripts/research_package.py --package research/bit-dicyclic-diagonal-seed620ca --check-only
python3.12 scripts/research_package.py --package research/bit-dicyclic-diagonal-seed620ca
```

The verifier checks the complete group table, presentation, all 28 rank-one idempotents, one-call and separately routed positive fixtures, the noncommutative `uv` versus `vu` ordering control, a mutated endpoint control, and a raw enumeration of all zero-, one-, and two-call products against the quotient-state pair table. It then recomputes both complete bounded searches and requires exact equality with `EXPECTED.json`.

## Relation to prior work and limits

The changed premise is the address algebra and the paid alphabet. The abelian three-register theorem of PR720, head `a942c0ae1b463710ca535c1fba1b07b6431b5a86`, establishes nine calls for its stated rational-frame model and arbitrary invertible targets. Recent exact finite-group scopes include `SL2(F3)` in PR2010, the order-21 Frobenius group in PR2011, `S3` in Discussion #2012, `A4` in Discussion #1999, `D10` in PR1953, and `D16` in Discussion #1818. The current object is the order-12 dicyclic presentation with **only** `{u,v}` charged; the direct baseline is shortest positive generator length. The overlap searches found no exact dicyclic scope in the available PR/Discussion snapshot.

The result is an abstract finite-word classification only. It has no physical multiplier routing, compiler lemma, child/hosting invoice, recursive moment, or `kappa` claim. Substantial OpenAI Codex assistance was used for formalization, search implementation, exact controls, and packaging. The mathematical framework and predecessor work are credited to PR720 and its cited lineage; no predecessor result is claimed here.

## Open next questions

The next finite layer is whether any diagonal triple with direct cost at least seven has a word of at most six calls in this same alphabet. A feasible first step is a depth-three by depth-three exact product join over the 94,727 products already classified through length three. A positive word would locate the first sharing layer in this toy model; the remaining blocker is the lack of a route from such a finite identity to the selected bit-supplier interface.
