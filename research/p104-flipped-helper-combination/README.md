# Combine the flipped mixed-port word with causal helper splits

**Conditional candidate: κ = 0.00357906.** The raw crossing is in
`(0.003579065166491, 0.003579065166492)`, with tested saving
`0.00357906007`. This combines the exact word of
[PR #6917](https://github.com/CrocSwap/integer-mult-bounds/pull/6917)
with 58 newly constructed applications of the helper-split method in
[PR #6916](https://github.com/CrocSwap/integer-mult-bounds/pull/6916).

| Construction | Proposed conditional κ |
|---|---:|
| #6917, flipped mixed-port word | 0.003530104 |
| #6916, shared-native helper splits | 0.00357027 |
| This combination | **0.00357906** |

The headline improves on #6916 by about **0.2462%**, and on #6917 by about
**1.3868%**. These compare candidate savings, not accepted theorem frontiers.
The selected canonical result remains unchanged.

The 58 cuts consist of 21 rank-4/5, 30 rank-3/6, two rank-2/7 and five
rank-1/8 splits. The new word retains all 6,379 paid native operations with
their exact chart pairs and multiplicities. It has 1,020 independent helpers,
400 mixed-port mains and 67,514 events. Full forward and reverse rational
checks cover all 2,016,400 public endpoint coefficients. The mixed caller has
78 formal roles, with 96 type-A ports and eight type-B ports.

The full ordinary charge, including every global LAMBDA translation, is
**996,089,112** using the original caller. The type-A constant-block
compression already retained by #6916 transfers exactly, reducing that charge
to **836,590,872**. Both are below the inherited billion-unit allowance.
The compression preserves the recursive invoice and creates no extra κ by
itself. These are finite source-accounting units, not machine-step counts.

## What actually combines

#6917 changes the word's helper relations, so #6916's old list of 68 cuts is
not transplanted. This package recomputes valid cuts on the exact flipped
word and composes them sequentially, verifying every intermediate source and
output hash. The old root pair, joint boundaries, owned lifetimes and every
paid native operator remain. Thirty-two cuts move 60 existing public MOVEs
within separately checked contact-free windows.

The caller compression transfers because #6917's type-A stream is exactly
the original caller used by #6916, including every joint boundary. Type-A
and type-B caller operations between joints act on disjoint fields. The
38 replacement blocks are proved by 60,800 exact scalar equalities, while
all type-B events and every joint are retained verbatim and in order.

## Sources and claim scope

- Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
- #6917 source: DreamingOfClouds at `07e81202470957555569d0c1077b2d6915e897fe`.
- #6916 method and caller source: CubeJerry at `ed359c115fa713395da380dcc602761196f5df4a`.
- [Construction and composition proof](PROOF.md), [validation](VALIDATION.md),
  [precision prescription](PRECISION.md), [exact result](RESULT.json), and
  [complete retained-file pins](SOURCE-PINS.json), and
  [dependencies and companion packages](DEPENDENCIES.md).

This remains conditional on the five framework assumptions, the open
BIT saving **0.00376669**, and the inherited owned-storage/erasure and
mixed-port physical admission contracts. The exact finite algebra and
complete numerical checks do not discharge those contracts. The compiler
uses the actual 153-axis ambient cap and fresh logarithm power 2300;
productive maximum 145 is not substituted for physical ambient dimension.

The retained ambient-cap proof is instantiated for the new invoice under
its general whole-job hypotheses. Its source's four-main specialization
does not itself admit this mixed-port word. The additional application
conditions are stated in [PROOF.md](PROOF.md).

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/p104-flipped-helper-combination
```

Six registered commands use Python 3.12 and the standard library, with a
total declared timeout of 1,200 seconds. They reconstruct the word, check
all physical chart maps and both caller views, certify the complete price,
and reject targeted corruptions. **All six passed on 2026-11-09.**
[SEARCH.json](SEARCH.json) records the
bounded search scope; the frozen witnesses, rather than search output alone,
are the verification input. No global optimality is claimed.

## Open next questions

1. Can the remaining compatible helper cuts improve this exact word while
   retaining full ordinary and physical accounting? The time-bounded search
   did not exhaust all candidates or bases.
2. Can the 23 owned rises, 53 dirty clears and mixed-port joint construction
   receive complete admission under the existing physical contracts?
3. Can the external BIT supplier and completed compiler dependencies receive
   full independent mathematical review?

Contribution by @CubeJerry with substantial OpenAI assistance. The flipped
word and mixed-port construction are DreamingOfClouds' work; the helper-basis
mechanism originates with Ali Romman. Full lineage is in [NOTICE.md](NOTICE.md).
