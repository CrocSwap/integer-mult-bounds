κ = 6.8386028917304e-4

Improve PR211's cascade frame witness with paired-component enlargements followed by seeded raise/lower cascade search. Exact canonical comparison finds 274 changed operation subspaces relative to PR211. The resulting conditional bound exceeds PR211's `6.83847872495777e-4` by `1.2416677263e-8` (about **0.001816%**). This is a small verified frame refinement. The scalar word and bank endpoints remain those of PR200.

Starting from PR211 at `c63e50a5dde96fe1459d6b29e55e47f42f104347`, the search first moves connected equal-frame operations together, then explores seeded perturbations and exact forward/backward nesting closures. Only the best exactly admissible final frame assignment is retained. The complete paid histogram is rebuilt, including target, source, terminal and bank charges. The banked bit coarse saving is `6.84328274104459e-4`; four finite stopped-leaf levels and the unchanged 47-constraint assembly give the exact claim `8548253614663/12500000000000000`. The bit supplier binds.

The package contains the frozen PR211 input, the initial plateau delta, both search programs and exact canonical difference counts, and a fully pinned offline verifier. Validation covers the complete bit F2/defining-integer source/target/dirty columns, both reflected signs, every used frame basis, all 1,760 aliases and 34 terminals, explicit stage-private bank allocation and chart/router checks, the inherited exact complex local-lift and target contract, two independent rational moment enclosures, 47 strict assembly inequalities, and rejection of the adjacent final grid point. Complex numerical discovery is not rerun; its frozen witness is checked exactly.

```sh
python3 -B research/coordinated-crossover-pr200/verify.py --temp-root /tmp
```

The normalized bit profile remains `m=72`, `W=56402`, rank mass `4055136`, deficit `5808`, maximum child `22`. This remains conditional on the inherited all-size Clifford/tensor, weighted compiler, restored selector, routing, precision/recovery, prime supply and analytic-transfer interfaces. Finite replay is not a proof of an unconditional multiplication theorem; the complex scope does not include a newly flattened global scalar transcript.

**Provenance:** PR211's cascade witness is Rohan Arun's work with Anthropic Claude assistance. PR207 (Dugongue, `cd14825023b75af4f5919a30e5e6d548b6ade5bc`) supplies the offline package and admission/bank route. Chafik Boukhalfa's PR200 supplies the actual bit word/checkers; PR202/193 supply the complex witness; Evan McKinney's PR197 supplies completed-bank machinery; PR185/197 supply finite leaf composition. Original licenses and all upstream AI disclosures are retained. The additional plateau/cascade search, fourth finite level, integration and verification were prepared by eumemic with substantial OpenAI Codex assistance.
