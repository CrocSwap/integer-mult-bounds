# Fine-theta admission obstruction in the retained recovery caller

**Scoped source-bound negative result. No new kappa.** The actual old
`Catalogue -> TensorPlan -> Sandwich.admit` chain cannot admit the eventual
fine-theta family. Its spacing is literally D+1, so its strict lower ratio
already fails. That old-band mismatch is credited to predecessors.

The additional useful results are stronger:

- Even if spacing is freed from D, retaining the fine family's
  `alpha=ceil(sqrt((4/pi)ln(16p0)))` and the old concentration/similarity
  guards admits **no external precision q** for p0>=2^200.
- If alpha is also retuned, those necessary guards force
  `q>(p0^2/4)(1+2log2(p0))`. The literal two input ingresses write exactly
  `4S(q+2)` payload cells. Any hypothetical successful relaxed port retaining
  this ABI therefore incurs `Omega(n log n log log n)` ingress work on the
  fine family, beyond the target multiplication budget.
- Passing the existing numerical recovery inequality cannot waive this
  catalogue admission. The package binds the actual gamma and both source
  S factors and specifies the remaining complete-transform interface.

The universal argument and scope distinctions are in [PROOF.md](PROOF.md).
[OVERLAP.md](OVERLAP.md) separates the contribution from #4142, the prior
fine-prime audit, #3861, #5095, #5325 and #6185. No claim is made against
the new analytic construction, the selected conditional theorem, other
callers, packing schemes or replacement admission policies.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python -B research/fine-recovery-catalogue-obstruction/verify.py
python -O -B research/fine-recovery-catalogue-obstruction/verify.py
python -B scripts/research_package.py --package research/fine-recovery-catalogue-obstruction
python -B scripts/check_research_commit.py --package research/fine-recovery-catalogue-obstruction --check-modes
```

Expected markers are `PASS_FINE_RECOVERY_CATALOGUE_OBSTRUCTION`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The deterministic receipt is in [evidence/REPLAY.json](evidence/REPLAY.json).
The replay authenticates 16 canonical files and two public proofs, inspects
the actual AST sites, checks an explicit finite integer domain, and uses
independent rational CRT/convolution/rounding controls. It executes no
physical Tensor/CRT runtime or predecessor verifier. The finite checks do
not establish the universal theorem by extrapolation.

## Exact dependencies

Canonical main: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The public production-gap proof is frozen at
`9a07c08c014259bb23c0a2b5844a1b67d91892f6`; the public Reference/ideal
compression join is frozen at `4509310a9a58d4c41c74029f899cbf36be1af9a1`.
The latter remains a compression result with explicit caller obligations.
No new implementation or selected-result change is made here.

## Open next questions

1. Which actual encoded fine-family catalogue replaces the old ratio,
   concentration and similarity policy while preserving O(p0) external
   records? Start from its precise header, original axes, source producer
   and full coefficient/setup/ownership bill.
2. Can the actual expansion/chirp prefix and opposite transform satisfy the
   public compression radius and error interface? Bind the total existing
   Gamma, prefix errors, codecs and both S factors before invoking nearest
   integer recovery. A complete source-transform error is still required.

## Credit

Prepared for @CubeJerry with substantial OpenAI assistance in source audit,
mathematics, exact checks and packaging. Prior mathematics and software
remain credited to Jose Manuel / jmbarrancoml (#3851/#3935), JoyboyBrian
(#5095 and compression/recovery lineage), Tekalign / tekuuu (CRT), ToikY
(#4029), unpaidmoon (#4142), Nick Petalas (#5149/#6185), Ali Romman and
Hiroki KUMAZAKI / kumagi (#5325/#5295), Chafik Boukhalfa / chafreaky and
the fine-prime lineage, JosieElliston's independent fine-prime audit, and
the retained source08/word/Count/Gaussian contributors. Details and license
scope are in [NOTICE.md](NOTICE.md). Shared-source lead review, if included,
is separately recorded; independent human or proof-kernel acceptance is
not claimed.
