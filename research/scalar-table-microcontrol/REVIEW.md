# Complementary review evidence

Both reviewers and the lead approved the unchanged construction and proof.
The final model receipt pins `lower.py` SHA256
`f378d44b7a208ac9b876549a28afe0b6905d74ba109194b83bd2e3becbe5b671`
and `PROOF.md` SHA256
`fa06bcf3660f871a972915a32942f20cc76187f449086d97e957a1bf83445b89`.

The model reviewer independently checked 253 generated graphs, 11,666
state instances, 1,226,848 explicit full-P transition instances, 17
negative controls and a 257-step nontermination prefix. Its graph checker
and transition expansion do not use the author's checker or simulator.
It also reviewed the complete source/model/setup/storage qualifications.

The operational reviewer independently derived original primitive/table
semantics, then checked 2,827 admitted generated executions and 30,375
microsteps against its own oracle. Ordered raw traces, final cells/heads,
rejection labels and C=A+U matched. Its additional source-oracle checks
cover 2,806 primitive cases and 2,843 table cases; 12 negative controls
were detected. The lead read the source, construction and full proof,
and independently derived a slightly tighter state bound, confirming the
advertised bound without requiring unreachable-state pruning.

All review scripts, receipts and notes are copied unchanged under `review/`.
From the repository root their portable commands are:

```bash
python3 -I -B research/scalar-table-microcontrol/review/micro-model-review/check_model.py research/scalar-table-microcontrol
python3 -I -B research/scalar-table-microcontrol/review/micro-operations-review/check_operations.py research/scalar-table-microcontrol
```

They print JSON results and return zero on success. Normal and optimized
runs agree. The author's own checker and both independent scripts are
registered for normal/optimized replay. The source/proof, not finite
enumeration alone, establishes the universal fixed-program claim.

These are separate OpenAI-assisted checks using shared immutable source,
not human or proof-kernel acceptance. No complete caller, readonly-context
interface, tariff converter, global assumption discharge or kappa claim
is inferred. `review/LEAD-REVIEW.md` records the lead's final qualification.
