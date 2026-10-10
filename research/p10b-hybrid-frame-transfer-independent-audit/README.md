# Independent checks of the hybrid-frame-transfer literal word

The independently checked word is
`9c99e3e6ac6058132bec486425ecf078489edb23f018e395831358111f501297`.
These separately implemented audits supplement the full source-bound verifier.
Prepared with OpenAI Codex assistance; Apache-2.0 applies.

After completing `research/p10b-hybrid-frame-transfer/verify.py` into `/tmp/hybrid-frame-transfer-proof`:

```sh
mkdir -p /tmp/hybrid-frame-transfer-independent/stages
python3 -B research/p10b-hybrid-frame-transfer-independent-audit/retile.py --proof /tmp/hybrid-frame-transfer-proof --output /tmp/hybrid-frame-transfer-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-hybrid-frame-transfer/vendor/native research/p10b-hybrid-frame-transfer-independent-audit/audit.cpp -o /tmp/hybrid-frame-transfer-independent/audit
/tmp/hybrid-frame-transfer-independent/audit /tmp/hybrid-frame-transfer-proof/candidate /tmp/hybrid-frame-transfer-independent /tmp/hybrid-frame-transfer-independent 31
python3 -B research/p10b-hybrid-frame-transfer-independent-audit/minor-audit.py --proof /tmp/hybrid-frame-transfer-proof --output /tmp/hybrid-frame-transfer-independent
python3 -B research/p10b-hybrid-frame-transfer-independent-audit/assembly-audit.py /tmp/hybrid-frame-transfer-proof /tmp/hybrid-frame-transfer-independent/ASSEMBLY-AUDIT.json
```

The C++ checker verifies the complete F2 forward/inverse operators, every dirty
input, COPY immutability, chronological common frames, both reflected ledgers,
and a distinct exact tiling reconstructed from the actual endpoints. Omitting
kernel restoration corrupts 951 formal rows. The tiling has 422,532 banks per
stage and preserves the complete residual inventory.

The minor checker uses modular elimination and exact Hadamard lifting to
independently verify all 27,868 nonzero basis and annihilator witnesses. The
assembly audit uses the closed-form finite recurrence to recompute eight
bootstrap levels, cutoff inequalities, the strict complex cap, seven margins
and the final rational grid. The complete verifier supplies both moment
engines, the full operational complex transfer and all structural invoices.

The fresh numerical operator replay is over F2. Integer inverse semantics
follow the actual elementary signed shears; signed decoder and recovery
interfaces remain inherited assumptions.

Saved receipts record local executions and are never inputs to the construction
verifier. These checks retain the inherited all-size theorem assumptions.
