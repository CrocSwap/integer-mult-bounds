κ = 6.83190455036641e-4

Add a fourth **finite** stopped-leaf bootstrap level to PR207's verified supplier. PR207 claims κ = 6.831904550365e-4; this raises it by 1.41e-16. This is a very small arithmetic refinement, not a new scalar word, frame optimization, or bank construction. The public PR list was checked immediately before submission.

The branch is stacked on PR207 at `cd14825023b75af4f5919a30e5e6d548b6ade5bc`. Its actual bit word, 302 frame overrides, completed entrance banks, complex supplier, paid profiles, and all-size assumptions are retained. The new change uses four applications of the acyclic recurrence `a[j+1] = (1-c)c + c*a[j]`, with the exact paid ordinary saving as its initial value. Every level calls its predecessor; no infinite-depth limit is substituted. The resulting rational claim is `683190455036641/10^18`.

Validation: the full immutable offline verifier passed locally. This includes bit F2/defining-integer dirty restoration and both reflected signs, actual frame and bank/router checks, the inherited exact complex local-lift/contract replay, two independent paid-moment enclosures, all 47 strict assembly inequalities, and rejection of the next final grid point. The retained complex scope does not include a newly flattened global scalar transcript.

```sh
python3 -B research/coordinated-crossover-pr200/verify.py --temp-root /tmp
```

The consequence remains conditional on the inherited all-size Clifford/tensor, weighted compiler, restored selector, routing, precision/recovery, prime supply and analytic-transfer interfaces. Finite replay is not a proof of those interfaces or of an unconditional multiplication theorem.

Provenance: PR207's coordinated frames/banks and source pins are retained, including PR200 (`a1175449f34d39ff933d9d8ab23ced1f32b290ec`), PR202 (`8d8d67bcf69c5ea67d3a29dbc64ba588156d6e8d`), and the finite-bootstrap arguments of PR185/197. Original licenses and all upstream AI disclosures are preserved. The fourth-level refinement and its replay were prepared with substantial OpenAI Codex assistance.
