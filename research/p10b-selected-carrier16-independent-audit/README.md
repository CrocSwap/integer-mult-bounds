# Independent checks of the selected-carrier16 literal word

The independently checked word is
`065ef05861ad3cb87ce0275eaee1b65ce75c15fefdb0a1cff29d51bfe038e106`.
These separately implemented audits supplement the full source-bound verifier.
Prepared with OpenAI Codex assistance; Apache-2.0 applies.

After completing `research/p10b-selected-carrier16/verify.py` into `/tmp/selected-carrier16-proof`:

```sh
mkdir -p /tmp/selected-carrier16-independent/stages
python3 -B research/p10b-selected-carrier16-independent-audit/retile.py --proof /tmp/selected-carrier16-proof --output /tmp/selected-carrier16-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-selected-carrier16/vendor/native research/p10b-selected-carrier16-independent-audit/audit.cpp -o /tmp/selected-carrier16-independent/audit
/tmp/selected-carrier16-independent/audit /tmp/selected-carrier16-proof/candidate /tmp/selected-carrier16-independent /tmp/selected-carrier16-independent 31
python3 -B research/p10b-selected-carrier16-independent-audit/minor-audit.py --proof /tmp/selected-carrier16-proof --output /tmp/selected-carrier16-independent
python3 -B research/p10b-selected-carrier16-independent-audit/assembly-audit.py /tmp/selected-carrier16-proof /tmp/selected-carrier16-independent/ASSEMBLY-AUDIT.json
```

The C++ checker verifies the complete F2 forward/inverse operators, every dirty
input, COPY immutability, chronological common frames, both reflected ledgers,
and a distinct exact tiling reconstructed from the actual endpoints. Omitting
kernel restoration corrupts 955 formal rows. The tiling has 422,988 banks per
stage and preserves the complete residual inventory.

The minor checker uses modular elimination and exact Hadamard lifting to
independently verify all 27,814 nonzero basis and annihilator witnesses. The
assembly audit uses the closed-form finite recurrence to recompute eight
bootstrap levels, cutoff inequalities, the strict complex cap, seven margins
and the final rational grid. The complete verifier supplies both moment
engines, the full operational complex transfer and all structural invoices.

The fresh numerical operator replay is over F2. Integer inverse semantics
follow the actual elementary signed shears; signed decoder and recovery
interfaces remain inherited assumptions.

Saved receipts record local executions and are never inputs to the construction
verifier. These checks retain the inherited all-size theorem assumptions.
