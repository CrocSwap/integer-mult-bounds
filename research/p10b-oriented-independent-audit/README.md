# Independent checks of the oriented-source literal word

The independently checked word is
`44659632417fb37d7f66f775db6c9348df668bdee3ae7b484f0bf88bc846e35a`.
These separately implemented audits supplement the full source-bound verifier.
Prepared with OpenAI Codex assistance; Apache-2.0 applies.

After completing `research/p10b-oriented-constructed42/verify.py` into `/tmp/oriented42-proof`:

```sh
mkdir -p /tmp/oriented42-independent/stages
python3 -B research/p10b-oriented-independent-audit/retile.py --proof /tmp/oriented42-proof --output /tmp/oriented42-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-oriented-constructed42/vendor/native research/p10b-oriented-independent-audit/audit.cpp -o /tmp/oriented42-independent/audit
/tmp/oriented42-independent/audit /tmp/oriented42-proof/candidate /tmp/oriented42-independent /tmp/oriented42-independent 31
python3 -B research/p10b-oriented-independent-audit/minor-audit.py --proof /tmp/oriented42-proof --output /tmp/oriented42-independent
python3 -B research/p10b-oriented-independent-audit/assembly-audit.py /tmp/oriented42-proof /tmp/oriented42-independent/ASSEMBLY-AUDIT.json
```

The C++ checker verifies the complete F2 forward/inverse operators, every dirty
input, COPY immutability, chronological common frames, both reflected ledgers,
and a distinct exact tiling reconstructed from the actual endpoints. Omitting
kernel restoration corrupts 966 formal rows. The tiling has 423,138 banks per
stage and preserves the complete residual inventory.

The minor checker uses modular elimination and exact Hadamard lifting to
independently verify all 27,782 nonzero basis and annihilator witnesses. The
assembly audit uses the closed-form finite recurrence to recompute eight
bootstrap levels, cutoff inequalities, the strict complex cap, seven margins
and the final rational grid. The complete verifier supplies both moment
engines, the full operational complex transfer and all structural invoices.

Saved receipts record local executions and are never inputs to the construction
verifier. These checks retain the inherited all-size theorem assumptions.
