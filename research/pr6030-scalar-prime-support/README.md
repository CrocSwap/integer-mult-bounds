# Scalar prime support on the selected PR6030 word

**Scoped census; no new κ.** Every `ADD`, `SCALE` and `COPY` coefficient of the selected PR6030 word is a nonzero rational whose numerator and denominator use only the primes 2, 3, 5 and 7. In the form `σ · 2^v · m`, the odd part `m` lies in `{1, 3, 5, 7, 9}` and the valuation `v` lies in `[-4, 4]`. Clearing by 16 produces an integer, 16 is sharp, and `|16q| ≤ 256` is sharp at `q = -16`.

The proof is [PROOF.md](PROOF.md). Selected κ stays `781451/250000000`. Assumption ID: `analytic_recovery`. This does not prove that assumption.

## Scope and evidence

Original card: `uniform-transfer-audit`, refined to one finite implication of `analytic_recovery` on the selected PR6030 scalar tape. The actual question, the refinement and the stop rule are in [TASK.json](TASK.json). Pins are in [SOURCES.json](SOURCES.json). Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.

This is session r105, item 8 of the ordered eligible list built on 2026-11-08. Open handoffs whose posts are completed, whose canonical artifact is an open pull request, or which say that no target was taken, are dropped, as are the delivered 19 October index, the H25 chain, and the 2 November review artifacts. The two seven-call notes are one updated request. Three open handoffs remain, then the revision-8 next-decision rows, then unnamed catalogue cards:

1. Three signed added frames at seven calls (discussion comment 19377832, updating 19377345).
2. Eight-source singleton connector at length 30 (comment 19377982).
3. Six-source depth-two block at `c = 7` (comment 19384981).
4. Complex helpers (`p104-side-correction`, `coverage-law-change`).
5. BIT (`bit-helper-contract`).
6. New decoders and interfaces.
7. Supplier audit (`supplier-boundary-audit`).
8. **This package.** All-size audit (`uniform-transfer-audit`): the scalar prime support of assumption `analytic_recovery`.
9. Verification tooling (`replay-runtime`).
10. `bit-new-register-model`.

Inside this row, #5837, #6293, #6522 and #6635 are different implications and are not repeated. No open upstream PR states this coefficient census. #6513 prices tape routes for width-64 scalar templates; it does not factor these rationals.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3 -B research/pr6030-scalar-prime-support/verify.py
python3 -O -B research/pr6030-scalar-prime-support/verify.py
python3 -B scripts/research_package.py --package research/pr6030-scalar-prime-support --check-only
python3 -B scripts/research_package.py --package research/pr6030-scalar-prime-support
```

Expected direct marker:

```text
PASS_PR6030_SCALAR_PRIME_SUPPORT events=19288 distinct=31 adds=18404 scales=861 copies=23 denom_lcm=16 max_abs_16q=256 odd_primes=3,5,7 valuation=-4..4 no_new_kappa=true
```

The checker raises `ValueError` on a bad coefficient, so `-O` does not disable it. Controls reject `0`, `11`, `1/3`, `1/32`, `32`, `15`, `27` and `1/48`.

Not run: `make frontier6030-verify`, the primary native replay, Lean, and any proof of `analytic_recovery`.

## Open next questions

1. Do the non-scalar payloads of this word, including Gaussian integer entries and `MOVE` chart matrices, stay inside the primes `{2, 3, 5, 7}`? The first step is one rank-r Gaussian row from the primary native payload. That payload is not an input here.
2. Does the retained analytic-recovery modulus already allow denominator 16 and odd primes `{3, 5, 7}`, or does the outer framework demand a larger avoided-prime set? The first step is to compare this support with the retained fine-prime padding bound. This note does not vendor that argument, and the census does not discharge `analytic_recovery`.

## Credit

The selected word is DreamingOfClouds' PR #6030. The selected review is `docs/research/pr-intake-evidence/pr6030-audit/PROOF-REVIEW.md`. #6635 (unpaidmoon) is the scalar chart lift on this word. #6293 (unpaidmoon) is the `MOVE` phase factor. #6522 (unpaidmoon) is the coordinate-envelope exponent. #5837 (unpaidmoon) is the scalar lift on the older #5599 word.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
