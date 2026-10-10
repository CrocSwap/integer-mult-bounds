# Independent checks of the donor-flow literal word

The independently checked word is
`7c7b1cf9baf45b63855597c9e1f8ebfd400f0958f2f40f09347c6176482587ef`.
These separately implemented audits supplement the full source-bound verifier.
Prepared with OpenAI Codex assistance; Apache-2.0 applies.

After completing `research/p10b-donor-flow52/verify.py` into `/tmp/donor-flow52-proof`:

```sh
mkdir -p /tmp/donor-flow52-independent/stages
python3 -B research/p10b-donor-flow-independent-audit/retile.py --proof /tmp/donor-flow52-proof --output /tmp/donor-flow52-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-donor-flow52/vendor/native research/p10b-donor-flow-independent-audit/audit.cpp -o /tmp/donor-flow52-independent/audit
/tmp/donor-flow52-independent/audit /tmp/donor-flow52-proof/candidate /tmp/donor-flow52-independent /tmp/donor-flow52-independent 31
python3 -B research/p10b-donor-flow-independent-audit/minor-audit.py --proof /tmp/donor-flow52-proof --output /tmp/donor-flow52-independent
python3 -B research/p10b-donor-flow-independent-audit/assembly-audit.py /tmp/donor-flow52-proof /tmp/donor-flow52-independent/ASSEMBLY-AUDIT.json
```

The C++ checker verifies the complete F2 forward/inverse operators, every dirty
input, COPY immutability, chronological common frames, both reflected ledgers,
and a distinct exact tiling reconstructed from the actual endpoints. Omitting
kernel restoration corrupts 959 formal rows. The tiling has 423,036 banks per
stage and preserves the complete residual inventory.

The minor checker uses modular elimination and exact Hadamard lifting to
independently verify all 27,808 nonzero basis and annihilator witnesses. The
assembly audit uses the closed-form finite recurrence to recompute eight
bootstrap levels, cutoff inequalities, the strict complex cap, seven margins
and the final rational grid. The complete verifier supplies both moment
engines, the full operational complex transfer and all structural invoices.

Saved receipts record local executions and are never inputs to the construction
verifier. These checks retain the inherited all-size theorem assumptions.
