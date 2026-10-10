# Independent checks of the terminal-caches10 literal word

The independently checked word is
`f99a64ba36393aa9d0dd04f10dcab19d688782137d89bc27711bf654dd4711f2`.
These separately implemented audits supplement the full source-bound verifier.
Prepared with OpenAI Codex assistance; Apache-2.0 applies.

After completing `research/p10b-terminal-caches10/verify.py` into `/tmp/terminal-caches10-proof`:

```sh
mkdir -p /tmp/terminal-caches10-independent/stages
python3 -B research/p10b-terminal-caches10-independent-audit/retile.py --proof /tmp/terminal-caches10-proof --output /tmp/terminal-caches10-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-terminal-caches10/vendor/native research/p10b-terminal-caches10-independent-audit/audit.cpp -o /tmp/terminal-caches10-independent/audit
/tmp/terminal-caches10-independent/audit /tmp/terminal-caches10-proof/candidate /tmp/terminal-caches10-independent /tmp/terminal-caches10-independent 31
python3 -B research/p10b-terminal-caches10-independent-audit/minor-audit.py --proof /tmp/terminal-caches10-proof --output /tmp/terminal-caches10-independent
python3 -B research/p10b-terminal-caches10-independent-audit/assembly-audit.py /tmp/terminal-caches10-proof /tmp/terminal-caches10-independent/ASSEMBLY-AUDIT.json
```

The C++ checker verifies the complete F2 forward/inverse operators, every dirty
input, COPY immutability, chronological common frames, both reflected ledgers,
and a distinct exact tiling reconstructed from the actual endpoints. Omitting
kernel restoration corrupts 951 formal rows. The tiling has 422,622 banks per
stage and preserves the complete residual inventory.

The minor checker uses modular elimination and exact Hadamard lifting to
independently verify all 27,836 nonzero basis and annihilator witnesses. The
assembly audit uses the closed-form finite recurrence to recompute eight
bootstrap levels, cutoff inequalities, the strict complex cap, seven margins
and the final rational grid. The complete verifier supplies both moment
engines, the full operational complex transfer and all structural invoices.

The fresh numerical operator replay is over F2. Integer inverse semantics
follow the actual elementary signed shears; signed decoder and recovery
interfaces remain inherited assumptions.

Saved receipts record local executions and are never inputs to the construction
verifier. These checks retain the inherited all-size theorem assumptions.
