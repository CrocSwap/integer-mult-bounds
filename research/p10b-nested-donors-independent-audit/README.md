# Independent checks of the nested-donors literal word

The independently checked word is
`09c7011fb4ad0e910ff5fad89205533fb70c671ff2a12ca859f3329b2d5ceada`.
These separately implemented audits supplement the full source-bound verifier.
Prepared with OpenAI Codex assistance; Apache-2.0 applies.

After completing `research/p10b-nested-donors-pr327/verify.py` into `/tmp/nested-donors-proof`:

```sh
mkdir -p /tmp/nested-donors-independent/stages
python3 -B research/p10b-nested-donors-independent-audit/retile.py --proof /tmp/nested-donors-proof --output /tmp/nested-donors-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-nested-donors-pr327/vendor/native research/p10b-nested-donors-independent-audit/audit.cpp -o /tmp/nested-donors-independent/audit
/tmp/nested-donors-independent/audit /tmp/nested-donors-proof/candidate /tmp/nested-donors-independent /tmp/nested-donors-independent 31
python3 -B research/p10b-nested-donors-independent-audit/minor-audit.py --proof /tmp/nested-donors-proof --output /tmp/nested-donors-independent
python3 -B research/p10b-nested-donors-independent-audit/assembly-audit.py /tmp/nested-donors-proof /tmp/nested-donors-independent/ASSEMBLY-AUDIT.json
```

The C++ checker verifies the complete F2 forward/inverse operators, every dirty
input, COPY immutability, chronological common frames, both reflected ledgers,
and a distinct exact tiling reconstructed from the actual endpoints. Omitting
kernel restoration corrupts 1,130 formal rows. The tiling has 422,730 banks per
stage and preserves the complete residual inventory.

The minor checker uses modular elimination and exact Hadamard lifting to
independently verify all 27,834 nonzero basis and annihilator witnesses. The
assembly audit uses the closed-form finite recurrence to recompute eight
bootstrap levels, cutoff inequalities, the strict complex cap, seven margins
and the final rational grid. The complete verifier supplies both moment
engines, the full operational complex transfer and all structural invoices.

Saved receipts record local executions and are never inputs to the construction
verifier. These checks retain the inherited all-size theorem assumptions.
