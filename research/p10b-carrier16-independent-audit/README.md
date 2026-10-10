# Independent checks of the carrier16 literal word

The independently checked word is
`be44db315647bf12789b1efdcad87a0980c063159587e9de565a134a0b493d15`.
These separately implemented audits supplement the full source-bound verifier.
Prepared with OpenAI Codex assistance; Apache-2.0 applies.

After completing `research/p10b-carrier16/verify.py` into `/tmp/carrier16-proof`:

```sh
mkdir -p /tmp/carrier16-independent/stages
python3 -B research/p10b-carrier16-independent-audit/retile.py --proof /tmp/carrier16-proof --output /tmp/carrier16-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-carrier16/vendor/native research/p10b-carrier16-independent-audit/audit.cpp -o /tmp/carrier16-independent/audit
/tmp/carrier16-independent/audit /tmp/carrier16-proof/candidate /tmp/carrier16-independent /tmp/carrier16-independent 31
python3 -B research/p10b-carrier16-independent-audit/minor-audit.py --proof /tmp/carrier16-proof --output /tmp/carrier16-independent
python3 -B research/p10b-carrier16-independent-audit/assembly-audit.py /tmp/carrier16-proof /tmp/carrier16-independent/ASSEMBLY-AUDIT.json
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
