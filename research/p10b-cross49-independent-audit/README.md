# Independent checks of the cross49 literal word

The independently checked word is
`ad45a7f132ea4bdd8e37a228d4d52673d17c224c9fa9a4a9c70f2e79271da82d`.
These separately implemented audits supplement the full source-bound verifier.
Prepared with OpenAI Codex assistance; Apache-2.0 applies.

After completing `research/p10b-cross49-pr327/verify.py` into `/tmp/cross49-proof`:

```sh
mkdir -p /tmp/cross49-independent/stages
python3 -B research/p10b-cross49-independent-audit/retile.py --proof /tmp/cross49-proof --output /tmp/cross49-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-cross49-pr327/vendor/native research/p10b-cross49-independent-audit/audit.cpp -o /tmp/cross49-independent/audit
/tmp/cross49-independent/audit /tmp/cross49-proof/candidate /tmp/cross49-independent /tmp/cross49-independent 31
python3 -B research/p10b-cross49-independent-audit/minor-audit.py --proof /tmp/cross49-proof --output /tmp/cross49-independent
python3 -B research/p10b-cross49-independent-audit/assembly-audit.py /tmp/cross49-proof /tmp/cross49-independent/ASSEMBLY-AUDIT.json
```

The C++ checker verifies the complete F2 forward/inverse operators, every dirty
input, COPY immutability, chronological common frames, both reflected ledgers,
and a distinct exact tiling reconstructed from the actual endpoints. Omitting
kernel restoration corrupts 1,130 formal rows. The tiling has 422,739 banks per
stage and preserves the complete residual inventory.

The minor checker uses modular elimination and exact Hadamard lifting to
independently verify all 27,834 nonzero basis and annihilator witnesses. The
assembly audit uses the closed-form finite recurrence to recompute eight
bootstrap levels, cutoff inequalities, the strict complex cap, seven margins
and the final rational grid. The complete verifier supplies both moment
engines, the full operational complex transfer and all structural invoices.

Saved receipts record local executions and are never inputs to the construction
verifier. These checks retain the inherited all-size theorem assumptions.
