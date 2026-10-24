# Validation

Scientific bytes committed at e429af48b2af768cd084b1178b64246d71a8bb28.
CPython 3.12.7, standard library only:

- Registered `scripts/research_package.py --package research/unequal-cycle-fit-rigidity-boundary`: PASS.
- Direct `python3.12 -B .../verify.py` and `python3.12 -O -B .../verify.py`: PASS.
- `scripts/check_research_commit.py --package ... --check-source-history`: PASS, 13 files, pinned base ancestor ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c.
- Official committed export and integrity check: PASS, 13 payload files.
- Fresh Git-free extracted export, empty PATH, isolated optimized Python (`-I -O -B`): PASS, 0.046 seconds.
- Actual cold mutations: missing RESULT, missing SOURCES, changed source byte, float-for-int receipt, boolean-for-int receipt, wrong witness vector, and wrong optimum claim all rejected. Restored bytes compared exactly against every original export member; restored replay PASS.

The final documentation-only commit adds this record. The cold run binds the
unchanged scientific bytes of the preceding commit, not an unrun full replay
of a newer archive. Exact local transport receipts and independent peer reports
are handed to the director separately. Finite runs corroborate the handwritten
universal proof; they do not exhaust all fields or all widths.
