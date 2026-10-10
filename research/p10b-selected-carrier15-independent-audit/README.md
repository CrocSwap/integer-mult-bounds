# Independent checks of the selected-carrier15 literal word

The independently checked word is
`420b66079b610fe66ecd4683c505d13d07101eb5ffc27e5407e8a68c5312460d`.
These separately implemented audits supplement the full source-bound verifier.
Prepared with OpenAI Codex assistance; Apache-2.0 applies.

After completing `research/p10b-selected-carrier15/verify.py` into `/tmp/selected-carrier15-proof`:

```sh
mkdir -p /tmp/selected-carrier15-independent/stages
python3 -B research/p10b-selected-carrier15-independent-audit/retile.py --proof /tmp/selected-carrier15-proof --output /tmp/selected-carrier15-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-selected-carrier15/vendor/native research/p10b-selected-carrier15-independent-audit/audit.cpp -o /tmp/selected-carrier15-independent/audit
/tmp/selected-carrier15-independent/audit /tmp/selected-carrier15-proof/candidate /tmp/selected-carrier15-independent /tmp/selected-carrier15-independent 31
python3 -B research/p10b-selected-carrier15-independent-audit/minor-audit.py --proof /tmp/selected-carrier15-proof --output /tmp/selected-carrier15-independent
python3 -B research/p10b-selected-carrier15-independent-audit/assembly-audit.py /tmp/selected-carrier15-proof /tmp/selected-carrier15-independent/ASSEMBLY-AUDIT.json
```

The C++ checker verifies the complete F2 forward/inverse operators, every dirty
input, COPY immutability, chronological common frames, both reflected ledgers,
and a distinct exact tiling reconstructed from the actual endpoints. Omitting
kernel restoration corrupts 956 formal rows. The tiling has 423,045 banks per
stage and preserves the complete residual inventory.

The minor checker uses modular elimination and exact Hadamard lifting to
independently verify all 27,810 nonzero basis and annihilator witnesses. The
assembly audit uses the closed-form finite recurrence to recompute eight
bootstrap levels, cutoff inequalities, the strict complex cap, seven margins
and the final rational grid. The complete verifier supplies both moment
engines, the full operational complex transfer and all structural invoices.

The fresh numerical operator replay is over F2. Integer inverse semantics follow
from the actual elementary signed shears; the signed decoder and recovery
interfaces remain inherited assumptions. See `AUDIT-CLOSEOUT.json` for scope.

Saved receipts record local executions and are never inputs to the construction
verifier. These checks retain the inherited all-size theorem assumptions.
