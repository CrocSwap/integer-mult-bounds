# Independent checks of the sinkaware-combo15 literal word

The independently checked word is
`ff143af7459bdc2f21ef633f897b1dd2b0b76cda15c1bf926b89960cea37055d`.
These separately implemented audits supplement the full source-bound verifier.
Prepared with OpenAI Codex assistance; Apache-2.0 applies.

After completing `research/p10b-sinkaware-combo15/verify.py` into `/tmp/sinkaware-combo15-proof`:

```sh
mkdir -p /tmp/sinkaware-combo15-independent/stages
python3 -B research/p10b-sinkaware-combo15-independent-audit/retile.py --proof /tmp/sinkaware-combo15-proof --output /tmp/sinkaware-combo15-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-sinkaware-combo15/vendor/native research/p10b-sinkaware-combo15-independent-audit/audit.cpp -o /tmp/sinkaware-combo15-independent/audit
/tmp/sinkaware-combo15-independent/audit /tmp/sinkaware-combo15-proof/candidate /tmp/sinkaware-combo15-independent /tmp/sinkaware-combo15-independent 31
python3 -B research/p10b-sinkaware-combo15-independent-audit/minor-audit.py --proof /tmp/sinkaware-combo15-proof --output /tmp/sinkaware-combo15-independent
python3 -B research/p10b-sinkaware-combo15-independent-audit/assembly-audit.py /tmp/sinkaware-combo15-proof /tmp/sinkaware-combo15-independent/ASSEMBLY-AUDIT.json
```

The C++ checker verifies the complete F2 forward/inverse operators, every dirty
input, COPY immutability, chronological common frames, both reflected ledgers,
and a distinct exact tiling reconstructed from the actual endpoints. Omitting
kernel restoration corrupts 956 formal rows. The tiling has 423,045 banks per
stage and preserves the complete residual inventory.

The minor checker uses modular elimination and exact Hadamard lifting to
independently verify all 27,840 nonzero basis and annihilator witnesses. The
assembly audit uses the closed-form finite recurrence to recompute nine
bootstrap levels, cutoff inequalities, the strict complex cap, seven margins
and the final rational grid. The complete verifier supplies both moment
engines, the full operational complex transfer and all structural invoices.

Saved receipts record local executions and are never inputs to the construction
verifier. These checks retain the inherited all-size theorem assumptions.
