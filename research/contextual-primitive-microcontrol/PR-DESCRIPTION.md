## Change and mathematical scope

The retained `Controller.primitive` wrapper still used Python-level control
around its native tables, while #6999's explicit microcontrol theorem
excluded readonly contexts and scratch retirement. This package closes
that specific entry/return interface: a fixed finite-state graph executes
the actual wrapper on the same tapes and seven-symbol alphabet, including
old dirty-work retirement, raw protected descriptor ports, successful head
returns and success-only final cleanup.

For every admitted execution it preserves the exact source tape/head/
rejection trace and has serialized TM clock **C=A+U**, now counting raw
actions across the entire wrapper. For `N` source rows, `L` participating
ports and `K` work ports, the graph has at most `52N+3L+18K+9` states.
Retirement of an old physical body of length `B` from head `h` costs exactly
`2h+5B+7`; displaced entry travel, old longer dirty bodies and unused context-head
returns are included. Finite precompilation and installation remain paid
separately. Tables and scalar coefficients are fixed before runtime widths
vary; neither the target alphabet nor control grows with the field width.

**No new kappa.** The selected `0.00363005817` remains conditional on all
five assumptions. This does not lower the full recursive Controller, admit
the selected provider registry, validate production headers or convert
machine steps into the ordinary-work tariff.

## Sources and novelty

Canonical base is [`e5452351`](https://github.com/CrocSwap/integer-mult-bounds/commit/e54523517d0f03e58352e647c403a5af3e525a57).
The exact executor is Git blob `acf475e4fccaff2fb64bd5b0b3f3fc0d246dc592`.
The package retains and authenticates six small predecessor files.

This reuses #6999's coded-port construction unchanged. The new proof is
the mixed coded/raw context protocol and actual pre/post-retirement
composition, including source failures. The arithmetic provider fixtures
come from #6968 and #6988; their tables do not inspect context values, so
read-dependent context tests are separately labelled protocol controls.
The current #7000 application motivates the complete dispatcher question
but is not replayed wholesale.

Package: [proof, source pins and replay](https://github.com/CubeJerry/integer-mult-bounds/tree/research/continuous-20261110-dispatcher/research/contextual-primitive-microcontrol).

## Reproduction and checks

```sh
python3 -I -B research/contextual-primitive-microcontrol/verify.py
python3 -I -O -B research/contextual-primitive-microcontrol/verify.py
python3 -B scripts/research_package.py --package research/contextual-primitive-microcontrol
```

Expected `PASS_CONTEXTUAL_PRIMITIVE_MICROCONTROL 28 372 6`. The unchanged
source executor and generated graph agree on full traces, cells, heads,
history, terminal labels and clock for 28 protocol cases and 372 real
exact/rounded provider cases. An independent equation is checked on 660
retirement length/head pairs. Six graph mutants and five invalid layouts
are rejected. The universal claim follows from the written bisimulation,
not extrapolation of those cases. A separate lead review adds 38 target-only
probes against hand-derived wrapper equations, without importing the source
executor; see `LEAD-REVIEW.md`. No Lean or full multiplier replay.

## Remaining obligations and credit

Next lower the actual continuation/row boundary, bind the selected event
registry to its production headers and numerical providers, and establish
a complete common-volume tariff. Failure remains partial exactly as in
the source; no rollback or automatic failure cleanup is added.

Prepared for **@CubeJerry** with substantial **OpenAI assistance**. Credit
the lifecycle, exact/rounded scalar and #6999 microcontrol predecessors and
the canonical stream-model authors. This is model-assisted research,
without a claim of independent human or proof-kernel acceptance.
