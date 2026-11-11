# Conditional κ = 0.003644267085400 from the chart-237/595 composition

The chart-237 temporal split from [#7147](https://github.com/CrocSwap/integer-mult-bounds/pull/7147)
also works on the completed chart-595 word from
[#7148](https://github.com/CrocSwap/integer-mult-bounds/pull/7148). The package
rebuilds the source word, finds the nine translated contact brackets, and
checks the two prefix and six suffix observations from scratch. One rank-nine
productive field becomes ranks four and five; one paid rank-six path becomes
ranks one and five. Both added buffers, every scalar and the unchanged literal
17-stage caller are included in the bill. [PROOF.md](PROOF.md) explains the
arbitrary-input identity, and [APPLICATION.md](APPLICATION.md) records the
complete comparison with both parents.

The candidate has 76,180 events, 1,497 public fields, and 59 owned labels with
62 lifetimes and peak 46. No new scalar-width repair is needed: all 69,779
ADD/COPY/SCALE numerators fit the retained 24-bit compiler contract.

The complete signed caller improves #7147 by **0.000000277745773** and #7148 by
**0.000000550917095**. Both parent invoices reject the new claim.

## Exact source and replay

Main base: `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8.
The archived #7148 package is complete at
`154ef929894225674df48df2d6ea3b7a7d1f39a0`; it contains its complete nested
closure and notices. The #7147 archive is the eight-file source subset at
`3b61d41d81a4bc8f78252240c8fb02473dd3d94f` needed to authenticate the
translation, independently reconstruct its caller invoice, and compare price
brackets. Neither upstream PR has to be merged to replay this package.
PR7148-INPUTS.json and PR7147-INPUTS.json bind exact paths, Git blob IDs and
SHA256 values checked before use. SOURCES.json pins the task catalogue and
selected baseline provenance on main.

Candidate native SHA256:
`8f0fe8e7b7180e4ee2bb74284e8946603f07ceb04b4ffcd96156f0e50c5d7667`.

```sh
python3.12 -B scripts/research_package.py --package research/p104-temporal-237-595-composition
```

The hook runs the certificate, full native replay and full caller replay
serially, comparing every field of the three frozen receipts. The three
`verify_certificate.py`, `verify_native.py` and `verify.py` entry points also
run directly with `python3.12 -I -B` in a Git-free export. No third-party
Python dependencies or network are needed. [VALIDATION.md](VALIDATION.md)
records actual executions and limits.

This is one exact conditional construction, under `native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape` and `analytic_recovery`.
The selected frontier remains #7000. This package does not establish
a global optimum, independent human or formal acceptance, or a compiled
top-level multiplier execution.

## Credit and coordination

Rohan Arun provided the chart-237 witness, dillona the chart-595 source
and width repair, Ali Romman the causal split identity, CubeJerry the
temporal/verification methods, Matarener the kernels, and ToikY the price
engines. The remaining retained authors and sources are listed in [NOTICE](NOTICE).
Prepared for Clear1nsight with substantial OpenAI Codex and ChatGPT Pro assistance.
[Canonical composition claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19532859).

## Open next questions

Independently replay the nine brackets and the guarded suffix, then review
the complete 17-stage physical/price binding, especially the peak-46
lifetime and 24-bit fixed-tape checks. Formal acceptance of the inherited
framework and compiled top-level execution are separate obligations.
