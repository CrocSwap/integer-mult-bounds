# A mixed-cutoff BIT supplier for conditional integer multiplication

The full application replay gives **conditional κ ≥ 0.00387992803556**. The gain is **0.00000000000955** over #7835 and **0.00000000001050** over #7831. The admitted ordinary BIT saving is **0.003879928035646**. The application uses 36 binary calls and 48 rational calls with their original signed invoices. [PR #7835](https://github.com/CrocSwap/integer-mult-bounds/pull/7835) · [PR #7831](https://github.com/CrocSwap/integer-mult-bounds/pull/7831)

The BIT supplier takes 480 chronological tensor factors. A paid tuple whose first job has rank 1 through 4 is split at $10^{480}$. A tuple whose first job has rank above 4 is split at $11^{480}$. Each complete independent productive tuple below $16^{480}$ becomes an owned zero at its endpoints. Its intervening work stays in the schedule. The working ambient is $134^{480}$.

The two classes contain 99,624 and 7,836 possible first jobs. For the product rank $4^{182}14^{134}21^{164}$, the first factor can be a literal rank-4 job or a literal rank-14 job. The same rank takes two disjoint calls in the first order and one in the second. The receipt also records two larger literal tuples, their original caller and native event labels, and their exact full-block and residual sizes. Its controls reject an omitted tuple, a duplicate, and a substitution between distinct occurrences of the same rank. [BIT.json](BIT.json) · [Proof and accounting](PROOF.md)

| Schedule | Tensor factors | Paid cutoff bases | Uniform loss | Delayed-cover loss | $\log_2 N$ | Conditional κ lower |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| #7831 | 416 | 10 | $10^{-11}$ | $10^{-11}$ | 209,400,000,000,000 | 0.00387992802506 |
| #7835 | 832 | 14 | $10^{-11}$ | $10^{-11}$ | 1,642,800,000,000,000 | 0.00387992802601 |
| Mixed cutoff | 480 | 10 and 11 | $2.5 \times 10^{-12}$ | $8 \times 10^{-12}$ | 1,285,200,000,000,000 | **0.00387992803556** |

The mixed schedule reduces $\log_2 N$ by 21.8% relative to #7835. Its normalized separation surplus exceeds $1.2309863319385 \times 10^{-12}$. The uniform majorant uses $\theta=13/15$ and logarithmic power 64. The same moment proof permits a uniform loss of $10^{-15}$ at $\log_2 N=3{,}954{,}000{,}000{,}000{,}000{,}000$. The qualified application uses the smaller carrier in the table.

The binary word and its adjoint pass all $680^2$ native coefficients and all $38^2$ caller coefficients in each orientation, including the omitted-CLEAR control. The complete binary account has 934,182,831,504 ordinary records and 6,998,544 owned backing fields before tensoring. The rational application checks 1,289 source columns, addressed retirement, exact basis products, the lowered scalar and division plans and the common width and depth guards. It charges 1,315,098,624 scalar services and 151,912,932,864 elementary ordinary records. The outer check passes 54 strict and four functional conditions, with minimum margin $10^{-15}$. The 480-factor and uniform schedules are specified by finite generation rules. [AUDIT.json](AUDIT.json) · [RESULT.json](RESULT.json)

The five inherited premises are native_all_columns, owned_erasure, compiler, precision_tape, and analytic_recovery. The signed binary crossing lies in $[0.003879928046154, 0.003879928046155]$. Its upper endpoint also bounds this fixed-profile joint application. The enrolled target **0.003889928046155** remains **0.000010000010595** above the qualified lower bound. [Selected framework review](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)

## Reproduce

Use CPython 3.12 and a fresh output directory. The first command verifies 21 direct source pins and 127 inherited pins. It writes the complete application receipt as well as the three checked-in certificates. With a populated authenticated cache, omit the fetch flag.

~~~sh
python3.12 -IB verify.py --work inputs --out replay --fetch
cmp BIT.json replay/BIT.json
cmp AUDIT.json replay/AUDIT.json
cmp RESULT.json replay/RESULT.json
python3.12 -IB review/independent.py --work inputs --out independent-replay --producer replay
~~~

Add the fetch flag to the independent command if its review cache is missing a pinned input. The separate review rebuilds the directed arithmetic and checks the application and matching bills. [Independent review](review/REVIEW.md)

Please review the paid partition at the two block ceilings, especially the same-rank first-factor swap. Also check the two exponent losses independently. The uniform loss pays for the logarithmic carrier majorant. The delayed-cover loss pays for the charged fallback under the actual prime bound.

## Open next questions

The two complete invoices have signed shortfalls at the enrolled target. A substantially larger bound requires stronger signed profiles. A first step on the BIT side is to replay a cheaper multi-coordinate helper projection across both orientations with every bridge and cleanup operation charged. The rational profile also has a separate shortfall. Candidate rational donor repairs need complete arbitrary-input restoration and full caller pricing.

## Credit

Prepared for Clear1nsight with substantial OpenAI Codex assistance. Dugongue supplied the cutoff rebalance and finite replay in #7831. Rohan Arun supplied the grade-14 successor in #7835. This package adapts those verifiers and reuses Clear1nsight’s #7786 and #7830 words and Ali Romman’s complete dual-supplier caller. The retained NOTICE records the compiler, physical, and analytic contributors. [PR #7835](https://github.com/CrocSwap/integer-mult-bounds/pull/7835) · [PR #7831](https://github.com/CrocSwap/integer-mult-bounds/pull/7831) · [PR #7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830) · [PR #7786](https://github.com/CrocSwap/integer-mult-bounds/pull/7786) · [PR #7776](https://github.com/CrocSwap/integer-mult-bounds/pull/7776)
