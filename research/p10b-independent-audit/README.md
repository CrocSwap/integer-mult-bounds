# Independent checks of the p10b final literal word

These supplementary audits were implemented separately from the portable package's native checkers, with OpenAI Codex assistance. Apache-2.0 applies.

The final word SHA256 is `688d4706d9b083fc43951a47a9b95d31c51b1283d5b1e14a20671d2b652186ed`. The independently checked frame file SHA256 is `f7f249c363cb5edfb69e63b7fc74d583555061c8f5c0f479bd542e3765ca1b8f`. The saved JSON files record completed local checks; the complete construction is admitted by the separate portable verifier.

After completing `research/p10b-complex-retiming/verify.py` into `/tmp/p10b-proof`, run from the repository root:

```sh
mkdir -p /tmp/p10b-independent/stages
cp research/p10b-independent-audit/independent-tiling.json /tmp/p10b-independent/stages/bank-tiling.json
c++ -O2 -std=c++17 -I research/p10b-complex-retiming/vendor/native research/p10b-independent-audit/audit.cpp -o /tmp/p10b-independent/audit
/tmp/p10b-independent/audit /tmp/p10b-proof/candidate /tmp/p10b-independent /tmp/p10b-independent 31
python3 -B research/p10b-independent-audit/minor-audit.py --proof /tmp/p10b-proof --output /tmp/p10b-independent
```

Category 31 is `kernel_restore` in this exact word. Its omission corrupts 999 formal rows. The C++ audit independently checks the complete F2 forward and inverse operators, arbitrary dirty restoration, COPY immutability, chronological common frames, both reflected required ledgers and an independently chosen exact bank tiling. This tiling has different patterns from the native package and the same residual inventory and 423,192 banks per stage.

The determinant audit uses modular Gaussian elimination over the independently certified prime `2^127-1`. Exact Hadamard bounds prove that equality modulo this prime uniquely lifts to equality of integer determinants. All 27,802 witnesses pass; none is zero. This checks the package's Bareiss witnesses with a different determinant algorithm.

The independent assembly check also recomputed the strict complex cap, all eight finite recurrence levels and the outer κ grid by rational arithmetic, and compared two completed complex supplier replays after removing exactly their two elapsed-time fields. The full portable package remains the reproducible source for complete supplier and outer assembly admission. These checks do not establish the inherited all-size theorem interfaces.
