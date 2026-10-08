# Draft: cost-aware selection with compatible live anchors

Candidate κ = 51033776497467/10^18 = 5.1033776497467e-5.
Bit saving = 25518190538443/(5*10^17).
This is 3978313/(250000000000000000) above PR #67 at b3745601.

Compose Rohan Arun's PR #67 cost-aware retired-slot selection with Dominik
Scholz's PR #68 compatible pending live anchors at h=23. Keep PR #67's h=25
word unchanged. Every used carrier satisfies F ⊆ E ⊆ G and emits paid literal
XORs. The scalar graph, role counts and complete physical width are unchanged.

Passed in the research lane: h23 compiler containment/scatter assertions,
paid event reconstruction, actual fixed-basis C++ profiles with zero CRT
disagreements, exact adjacent moment bracket and all 47 constraints/seven
margins. PR #67's baseline was independently replayed in both orientations.
**Pending: independent full dirty-state replay of the new h23 word, parent
reproduction, dedicated CI integration and broad validation.** This draft
publishes the concrete candidate promptly, not a fully verified new record.

Reproduce the selected mixed-axis candidate with:

```sh
python3 research/cost-live-composition/experiment.py --h 23 --full-replay
```

The portable source manifest binds consumed files rather than unrelated local
research logs. Build outputs are ignored. `candidate.json` records exact
arithmetic and pending verification; `frame-compiler.json` binds axis words.
The preceding fully replayed live-anchor result remains in
`research/global-anchor-screen/`.

Attribution: Rohan Arun (#67 cost selection, profile oracle and refined exact
arithmetic), Dominik Scholz (#68 live anchors and this composition), Chafik
Boukhalfa (#60 rank-first reclamation), eumemic (#57 joint compiler), Avi
Eisenberg (#62 graph, with Claude assistance), and all inherited contributors.
Prepared with substantial OpenAI GPT-6 Astra / Codex assistance. Apache-2.0;
original notices retained. All analytic, all-size compiler, routing/recovery
and fixed finite-alphabet multitape hypotheses remain conditional. No full
formal theorem or practical speedup is claimed.
