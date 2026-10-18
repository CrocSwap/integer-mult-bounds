# Four-way port borrowing:480 fewer exact leaf calls

This recursive-interface construction combines PR758's known higher-arity echo
with PR1057's exact additive borrowing contract. For the same 56 ordered factors,
the best arity2..4 tree needs 1088 calls instead of 1568 for the predecessor's
binary/ternary optimum. Every inverse is paid. Four dirty arrays suffice at
any depth, versus three for that predecessor. The written proof, emitted word,
all-input identity, precision bound and complete conditional dense invoice are
included. No new kappa or physical supplier admission is claimed.

Reproduce from the repository root with Python3.10+ and its standard library:

```sh
python -I -O -B research/quaternary-port-borrowing55/verify.py
python -I -O -B research/quaternary-port-borrowing55/test_package.py
```

Expected main marker:
`PASS_QUATERNARY_BORROW calls=1088_vs_1568 dirty=4_vs_3 controls=9`.
Ordinary replay writes nothing. `--write` explicitly regenerates EXPECTED.json.

The checker exhausts 396550 planner candidates, checks all 1099 ordered trees
through seven factors (173690 signed leaf events), and checks both complete
56-factor orientations on the free module and noncommuting dense2x2 matrices.
Nine controls cover missing/inverted operations, source writes, invalid pools,
bad tree/sign/precision and a nonlinear contract failure. Source and receipt
mutation checks are separate. The retained independent PR1057 interpreters and
invoice are unmodified, credited source, not a claim of new human review.

See PROOF.md for the full recurrence, norm argument and backend parameters.
At common 119-bit precision the new word reduces primitive commands 43904 to
30464 but increases data storage 1190 to 1428 bits. Startup, program, coefficients,
head travel and clean scalar workspace remain charged. This is a scoped space
and call-count tradeoff, not an arbitrary-program optimum or runtime benchmark.

Base ce7ad1b6ab09452c3478723a2e96ed5ff212dc08 selects PR1094 with conditional
kappa 836330098538459/500000000000000000; selected files are untouched. The
bit supplier remains PR589/PR555. Sources are pinned under SOURCES.json, with
the exact PR1057 commit and original notices. CLAIM.json records seed55,
rejected overlapping candidates, the finite domain and stopping rule.
