# Independent all-coefficient two-image boundary audit

**Result:** PR4991's nonsingular dirty-helper volume obstruction is corroborated with literal original/repaired source phases and all-width quantifiers. Its singular coefficient cases need a rank argument in addition to noting singularity; [PROOF.md](PROOF.md#4-the-singular-coefficient-cases-require-rank-not-volume) supplies that missing step. The exclusion holds for every fixed alpha*beta!=0 in the stated fixed finite bank/word model, including eventual width tails. This is an independent written scoped proof, not a formalization or new multiplication exponent.

For q arbitrary-input banks of dimension d, the singular cases have target rank `(q-1)d+rank(F)>(q-1)d`; any singular register-mixing factor has rank at most `(q-1)d`. For nonsingular coefficients, the source-specific normalized determinant contains independent `2^-f` and `4^-f` terms, incompatible with the allowed affine profile. Fixed arbitrary invertible address letters are included. Exactly one zero coefficient remains an allowed single-image case.

PR4998's `diag(F,F^-1)` is a required positive boundary control: the inverse partner transforms an independent input and compensates the volume. It is not returned dirty state. No clean-input or width-dependent nonunitary-word exclusion is inferred.

## Reproduction

```sh
python3.12 -B research/two-image-volume-independent-audit/verify.py --check research/two-image-volume-independent-audit/RESULT.json
python3.12 -O -B research/two-image-volume-independent-audit/verify.py --check research/two-image-volume-independent-audit/RESULT.json
python3.12 -B scripts/research_package.py --package research/two-image-volume-independent-audit
```

Executed on Python 3.12.14, Darwin 27.0.0 arm64: the direct normal replay took 0.17 seconds and the optimized replay 0.23 seconds; registered normal/optimized replay and metadata/pins checks passed. Standard library only. Exact character/determinant checks are bounded to widths one/two; the full-width and all-complex claims follow from the written proof. The retained compensated program is checked on all 16 and 128 independent columns over F17, solely as a finite boundary control. No predecessor verifier is imported/executed, and PR4991/4998 verifiers are absent. [RETAINED-SOURCES.json](RETAINED-SOURCES.json) binds original paths/commits/SHA256/Git blobs; all necessary pending-source bytes are committed here. [NOTICE.md](NOTICE.md) preserves predecessor credit and AI disclosure.

This audit changes no predecessor package or selected record. It does not establish a continuation, Gaussian consumer, full native/tape/precision implementation, new paid-call bound or kappa.

## Open next questions

Can the compensated inverse partner be consumed as an independently priced Gaussian target? Name one actual consumer and retain both arbitrary independent outputs, precision, denominator-15 scalar arithmetic and tape charges. PR4998's exact local construction and this completed-boundary audit supply no such consumer. The structured dependency is in TASK.json; a new construction round is not justified by the isolation obstruction alone.
