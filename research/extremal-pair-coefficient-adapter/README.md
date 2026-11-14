# Produce the two extremal source tables through four existing encoded scalar calls

**Source-specific coefficient adapter; no new kappa.** [A12](https://github.com/CubeJerry/integer-mult-bounds/commit/702c7616667c5f4e583eb73687944d148b7a1ccf) proves a uniform rank margin for two deterministic extremal Gaussian source pairs, but leaves coefficient production as an explicit premise. This package supplies that local production interface using the unchanged scalar primitive audited in [#6085](https://github.com/CrocSwap/integer-mult-bounds/pull/6085). It introduces no new exponential algorithm.

The adapter borrows six canonical binary Count values `(p,alpha,s1,t1,s2,t2)` with heads at 1. For `p,alpha>=1`, `1<s_l<t_l<2s_l` and `alpha^2<=4p`, it constructs

    P=p+8, F=2alpha^2,
    f_(l,+)=alpha^2(2(t_l-s_l)+1)/s_l,
    f_(l,-)=alpha^2(2s_l-1)/s_l.

All four rational arguments lie strictly between 0 and F. One shared encoded Exponentials setup and four decay calls return the two row-major tables `[[1,U_l],[V_l,1]]` on the `2^-P` grid. The off-diagonal absolute errors are less than `2^(-p-7)`; diagonals are exact. The actual calls use unreduced owned rational copies through the predecessor's `reduce=False` ABI, so no gcd is omitted from the bill.

## Source binding and complete local cost

For A12's retained fine-prime family with `p>=4096`, `s_l>=p^4` and `alpha=ceil(sqrt((4/pi)ln(16p)))`, the selected centered phase is `s_l beta_i=-(s_l-1)/2`. Its literal directed coefficients are exactly those supplied by this adapter. Phase and chirp remain in the already column-normalized source matrix. Primality, the exact alpha choice and source admission are caller premises; the adapter does not silently certify them.

Writing `a=pi alpha^2` and `w=exp(-2a)`, each scalar error is less than `2^-37 w^2`. The omitted aliases of the matched exact periodization contribute at most `2^-37 w^2` per selected entry. Thus the emitted factors approximate the selected periodic principal sections with absolute error **less than `2^-36 w^2`**, meeting A12's table-error premise including aliases. Their tensor and its own exact inverse consequently have full ordinary Stein displacement rank in all 24 orders, with the inherited A12 margins. This is not an inverse section of the full source matrix.

Let B be the maximum input integer bit length. With fresh private scratch grants, or a stated O(p+B) entry-history bound on each of the fixed private roles, the complete local bit tariff is

    time O(p^3+(p+B)^2), storage O(p+B).

The proof binds the predecessor precision policy to `R<=257p`, keeps rational input lengths, and pays argument products, comparisons, copying, four diagonal outputs, scalar setup, all four calls and complete owner retirement. An additional source bound `B=O(p)` permits the simpler `O(p^3)` specialization; A12's lower bound on s alone does not imply it. For arbitrary reused blank roles, retained storage keeps `sum_tau max(H_tau,C(p+B))`; a required full-history sweep or transport also pays the actual history length. Earlier blank capacity is not erased from the bill. The retained encoded Count/Rational arithmetic model is explicit. This is not a newly compiled native ROM or a complete multiplication bill.

Successful return preserves all borrowed input bytes and restores every head to 1. Nine distinct output owners remain live: the copied precision and eight numerator records. Private setup is retired; output history is paid when the caller later invokes `Tables.close()`. That retires these nine outputs only: `pool.empty()` additionally requires every other lease in the pool to have been released by its own owner. Borrowed inputs may belong to the same pool and remain live and unchanged. Normal guard rejections restore the valid borrowed inputs. Arbitrary malformed tapes, allocation-fault rollback and asynchronous interruption are outside the interface.

## Reproduction and evidence

From a checkout containing the declared canonical runtime inputs, with Python 3.12 and its standard library:

```sh
python3 -I -W error -B research/extremal-pair-coefficient-adapter/verify.py
python3 -I -O -W error -B research/extremal-pair-coefficient-adapter/verify.py
python3 -B scripts/research_package.py --package research/extremal-pair-coefficient-adapter
```

The direct commands are read-only and print `PASS_EXTREMAL_PAIR_COEFFICIENT_ADAPTER`. [VERIFY.json](VERIFY.json) declares six existing runtime inputs, including the predecessor's original source archives; those archives are not duplicated in this new package. `--source-root PATH` supports a separate read-only input cache. [RUNTIME-PINS.json](RUNTIME-PINS.json) authenticates every declared input, and the unchanged predecessor loaders authenticate their nested sources.

[RESULT.json](RESULT.json) records identical normal and optimized receipts for one complete actual encoded packet: four calls under sealed constructors and no-decode protection, P=9/F=8/R=251, all nine returned owners, borrowed-byte/head restoration, full post-retirement history cleanup and seven guarded invalid inputs. The independent-algorithm predecessor oracle encloses the answer using arcsine pi and alternating decay; its complete interval must lie inside each actual source interval. Argument, precision, sign, normalization and output-order checks bind the source execution. Returning table-swap and omitted-alpha checks are bounded controls, not a claim to have executed every mutant program.

The small packet deliberately lies outside A12's `p>=4096` rank domain: two coefficients correctly round to zero. It corroborates producer semantics, not asymptotic rank. The universal source/error/cost result rests on [PROOF.md](PROOF.md) and the inherited scalar theorem. No large-p execution, full supplier replay, human/formal-kernel acceptance or hosted CI is claimed.

## Novelty, limits and credit

[OVERLAP.json](OVERLAP.json) records bounded overlap checks. #6085 already proves the scalar algorithm and its tariff. A12 already proves the quantitative source margin. The new step is their exact source-specific four-call join, including argument admission, matching alias/error budget, owned output lifecycle and complete local cost. The named #6099 ProductionPlan domain is unnecessary for these isolated calls; its global admission is not repaired.

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`. [SOURCES.json](SOURCES.json) and [DEPENDENCIES.json](DEPENDENCIES.json) pin exact provenance and retained proofs. Credit JoyboyBrian for [#6085](https://github.com/CrocSwap/integer-mult-bounds/pull/6085) and [#6099](https://github.com/CrocSwap/integer-mult-bounds/pull/6099), Chafik Boukhalfa / [#1786](https://github.com/CrocSwap/integer-mult-bounds/pull/1786), Vlado Vojdanovski / [#1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673), Jeremy Kothe and the bilateral source lineage, and the retained encoded arithmetic/framework contributors. Original notices and Apache-2.0 terms are preserved.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. The worker identified and reused the scalar predecessor and derived the adapter proof; the lead proposed closing the production premise; a separate worker independently audited admission, ownership and proof. All five foundational assumptions, selected #7000 and the complete multiplication bound remain unchanged.

## Open next questions

1. Bind the A12 index selector, these owned tables, tensor formation and transport to one actual Gaussian caller with a complete physical bill.
2. Establish a new source-specific margin before extending production to arbitrary phases or more than two axes; A12's three-axis whole-box nonextension remains relevant.
