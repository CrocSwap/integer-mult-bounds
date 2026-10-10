# Independent checks of the donor-refresh literal word

The independently checked word is
`1f8aa335c7c6e725eac22c9c8ff1c9b679cef8e6aa76a2cf75344157afefe605`.
These separately implemented audits supplement the full source-bound verifier.
Prepared with OpenAI Codex assistance; Apache-2.0 applies.

After completing `research/p10b-donor-refresh54/verify.py` into `/tmp/donor-refresh54-proof`:

```sh
mkdir -p /tmp/donor-refresh54-independent/stages
python3 -B research/p10b-donor-refresh-independent-audit/retile.py --proof /tmp/donor-refresh54-proof --output /tmp/donor-refresh54-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-donor-refresh54/vendor/native research/p10b-donor-refresh-independent-audit/audit.cpp -o /tmp/donor-refresh54-independent/audit
/tmp/donor-refresh54-independent/audit /tmp/donor-refresh54-proof/candidate /tmp/donor-refresh54-independent /tmp/donor-refresh54-independent 31
python3 -B research/p10b-donor-refresh-independent-audit/minor-audit.py --proof /tmp/donor-refresh54-proof --output /tmp/donor-refresh54-independent
python3 -B research/p10b-donor-refresh-independent-audit/assembly-audit.py /tmp/donor-refresh54-proof /tmp/donor-refresh54-independent/ASSEMBLY-AUDIT.json
```

The C++ checker verifies the complete F2 forward/inverse operators, every dirty
input, COPY immutability, chronological common frames, both reflected ledgers,
and a distinct exact tiling reconstructed from the actual endpoints. Omitting
kernel restoration corrupts 953 formal rows. The tiling has 423,102 banks per
stage and preserves the complete residual inventory.

The minor checker uses modular elimination and exact Hadamard lifting to
independently verify all 27,814 nonzero basis and annihilator witnesses. The
assembly audit uses the closed-form finite recurrence to recompute eight
bootstrap levels, cutoff inequalities, the strict complex cap, seven margins
and the final rational grid. The complete verifier supplies both moment
engines, the full operational complex transfer and all structural invoices.

Saved receipts record local executions and are never inputs to the construction
verifier. These checks retain the inherited all-size theorem assumptions.
