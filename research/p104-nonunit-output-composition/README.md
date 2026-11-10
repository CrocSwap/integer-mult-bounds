# Conditional candidate κ = 0.003642408496869

This composes PR7130's nonunit-pivot split with the global output rechart
mechanism from PR7124. The exact arbitrary-input native adjoint, complete
paid/target recount and both directed complete-price engines passed at
κ=0.003642408496869, improving PR7130 by 0.000000189212232.

Full native and application verification, including the source's F25 grid
and increased precision cost, is pending. This is an early draft, not full
verification or admission. The five inherited framework assumptions remain.

The complete PR7130 source export and nested sources/notices are authenticated
by INPUTS.json. CHANGES.json and construct.py regenerate the entire word;
21 helper output charts and 129 scalar-contact charts change, while scalar
coefficients/order, main endpoints and owned inventory remain unchanged.

```sh
python3.12 -B research/p104-nonunit-output-composition/verify_early.py
```

Credit dillona/OpenAI Codex for PR7130's legal nonunit-pivot split and precision
accounting; Rohan Arun/OpenAI Codex for PR7124's output rechart, PR7122's input
rechart and PR7113's caller; 1337isnot1337/OpenAI Codex for alpha expansion;
Ali Romman, Jerry Chen/CubeJerry, ToikY, Matarener, DreamingOfClouds,
Douglas Colkitt/#7000 reviewers and all retained source authors and notices.
Rohan Arun with substantial OpenAI Codex assistance; no subagents. Apache-2.0.

## Open next questions

- Complete source-specific native/application verification and registered replay.
- Obtain independent review of the composed construction and all charges.
