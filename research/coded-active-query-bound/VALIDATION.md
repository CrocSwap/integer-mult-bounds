# Validation and evidence limits

Executed on 2026-10-23, macOS 27.0.1 arm64, with CPython 3.12.15 for the final registered and portable replays. Standard library only. The separate initial binary audit also passed on CPython 3.14.7. No network service, native build, solver or historical full-source replay is required by these commands.

## Completed checks

The following registered replay passed with the final mathematical checker and its four source-condition mutations:

```sh
python3.12 -B scripts/research_package.py --package research/coded-active-query-bound
```

It ran the source checker in isolated normal and optimized modes and the separately derived binary checker in isolated optimized mode. Every command used warnings-as-errors. Results were `PASS_CODED_ACTIVE_QUERY_BOUND`, `PASS_INDEPENDENT_RIGHT_COSET_CENSUS`, and `PASS_REGISTERED_RESEARCH_PACKAGE`. All mathematical checks use explicit exceptions; disabling assertions does not disable them. The retained exact Clifford implementation was executed from authenticated source bytes, bypassing any preexisting bytecode cache.

The registered checker authenticates CODE.json, NORMALIZERS.json and clifford_exact.py; metadata also authenticates the declared PHYSICAL.md interface and frozen Git proof provenance. It verifies all 12,544 ordered right-coset tests by both a new binary formula and the retained Clifford tableaus, all 12,544 left-coset tests, all 12,544 one-sided grade-one tests, the 5,824 supported code terms, 52-entry column support, and 112 distinct source directions. It checks all 12,544 code-factor entries, all 64 mode-Gram entries and four mode contacts per owner. Four mutation controls reject a duplicate direction, empty source column, nonzero diagonal and altered mode factor. Coincident directions give the expected grade-zero positive exception.

The independent binary checker authenticates its two inputs and reconstructs the complete right-coset census without importing the retained Clifford code. Its scope is that binary/source census; it does not independently replay the mode matrix or a native producer.

A separate temporary directory received only this package and the four live inputs declared in VERIFY.json, with no Git directory. Both direct optimized checkers passed there. The main checker took approximately 2.46 seconds and the independent check 1.06 seconds on this machine. The source package bytes were unchanged by that read-only replay. The process made no network requests; operating-system network isolation was not imposed. This establishes portable direct replay of the declared executable inputs, not an official committed package export.

## Mathematical review and remaining obligations

[INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) records a separate AI-agent derivation and binary audit. [EXTENSION-REVIEW.md](EXTENSION-REVIEW.md) audits finite projective H, nonunitary normalization, rectangular modes, free retraction rebasing, homogeneous direct sums and the isolated-patch tariff. It distinguishes its initial executable snapshot from later algebraic review. The final package replay above includes the subsequently added mode checks. These are AI-agent reviews, not independent human or formal-kernel acceptance.

The all-width implications are written proofs using a finite-coset tensor Gram argument and input/output dimension cuts. The checker does not enumerate H, calculate a universal width threshold, search all circuits or verify those proofs in a kernel. It supplies the exact physical-source facts used in them. The eight rank-eight calls removed by the producer are inherited from the pinned source invoice; this package does not recount the native word.

No complete coded caller endpoint, native internal-prefix schedule, changed compiler, finite-precision realization, stock protocol, full multiplication algorithm, selected cold replay or new κ is supplied. The nonfree-history, width-one, per-column-alphabet and same-field restrictions in PROOF.md remain material.

The submitting agent repeated the registered normal/optimized/independent replay in an isolated publication worktree; it passed. The final upstream refresh advanced that worktree to `20a1e31bc6009b9b3f4d084bbaadc6350e34fcba`; all live scientific inputs and relevant guidance were byte-identical to the preceding checkpoint. Publication-byte/source-history preflight, official committed export and hosted CI results are recorded in the contribution PR against its publication commit. No selected record or predecessor file was changed.
