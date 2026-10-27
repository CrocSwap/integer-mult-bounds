# Conditional finite arithmetic refinement on PR1800

This additive refinement with 500-digit slacks preserves the complete PR1800 package byte for byte under
`parent/` (commit `46d865ab92e58098538b8c5348b6a131c99abf45`, manifest SHA256
`b8dba5524f8603e1848c73a8dd675404a0d3d9eed3b0285e9f0cfccde38fd15f`).
It changes the explicit outer witness and moment-enclosure precision only.
The proposed final saving is recorded exactly in
`refinement/outer/OUTER-CLAIM.json`; its exact current-frontier gain is checked separately.
The construction, paid profile, native scalar words, owner maps and physical
invoice remain unchanged. This is a very small arithmetic gain.

The rational endpoint operand is copied verbatim from PR1789 commit
`2f5f9dbb8b8ce9f9a5f90b234e4b03ca3f4ba87b`,
`research/capped-fusion-t74-k554/new/SPEC.json` (SHA256
`7ab2a4e7ad8d7296cb9c920014daec8b47ae7c7ae6a4f8c70e878965c57a71cb`).
The package does not trust a claim that all 600 digits are certified. It backs off
by 1e-500 and independently encloses the native moment of the actual admitted
profile using two separately written exact-series implementations. A point
above the root must reject. The 600-digit source profile must equal PR1800's and
the actual freshly admitted profile exactly.

The explicit parameters are in `refinement/PARAMETERS.json`. Positive slacks
are 1e-500, epsilon=1-2e-500, beta=1-6e-500, and the final floor is 10^600 with
backoff 1e-550. Epsilon remains strictly below one. The exact main-row bound
still forces kappa below the unchanged complex supplier's moment root.

The higher-precision producer uses a directed fixed-point exponential
recurrence with 200 Taylor terms on the 10^650 grid, and 700 positive atanh-log
terms with a proven geometric tail. Integer rounding encloses every term;
its width and above-root rejection are checked independently. No floating
score accepts a bound. The printed rational and decimal kappa agree exactly.

The coordinator supplies a strict, immutable source-bound wrapper for reuse of
the completed cold replay of the 105 precision parent, actual admitted profile binding,
both newly computed moment engines, all 57 outer inequalities and 17 controls and the
symbolic guard. No full native replay or valid reuse is inferred from this
producer directory alone. Assertions are required for inherited scripts.
Dependencies and full-run bounds are specified by that wrapper.

The independent broad check corrects an inherited sign in the displayed
constant: the shifted exponent has d^2-d^2/L, whereas an inherited `or True`
guard admitted d^2+d^2/L. The parent bytes are retained as historical input;
the added exact rational-function guard requires the corrected identity.
This does not establish numerical stability or the all-size accretive circuit
lemma.

All inherited all-size compiler, common-label/mutable-source, whole-call
hosting, precision/tape, exact-recovery, analytic-transfer, bit H1-H5,
fine-prime-padding, gauge-free circuit and union-schedule assumptions remain.
Finite checks do not prove the complete multiplication theorem, a practical
cutoff, linear time, or an unconditional record. Source acquisition and cheap
arithmetic runs are separate from full release acceptance. A full result is
claimed only by a fresh source-bound successful `RESULT.json`.

Credits and licenses from PR1800 and all vendored predecessors are retained.
Fine-prime padding: Chafik Boukhalfa/PR1786 and Tim Trudgian. Capped phase-cell
fusion: Vlado Vojdanovski/PR1673. Gauge-free interiors and schedule lineage:
PR1758, Jeremy Kothe and contributors. Matching-profile endpoint refinement:
PR1789 and its contributors. Supplier lineage and substantial original AI
assistance are recorded in `parent/README.md` and preserved notices. This
additive package and its independent AI-agent checks were prepared with
substantial OpenAI Codex assistance; no independent human review is claimed.

## Open next questions

1. **Improve the paid supplier rather than its numerical slack.** Relevance:
   the main outer row limits kappa to the unchanged supplier moment root, so
   further arithmetic refinement has diminishing returns. First step: nominate
   one concrete helper-donor or paid-profile change and price its complete
   inventory before a full native replay. Blocker: any new scalar identity must
   also admit the native frames, phases, ownership and physical invoice.
2. **Independently review the uniform fine-prime and accretive circuit proofs.**
   Relevance: finite arithmetic does not establish the all-size source-prime,
   conditioning or circuit claims behind this conditional outer. First step:
   audit the PR1786 prime/precision lemmas and the gauge-free accretive extension
   together, tracking every parameter dependence. Blocker: a uniform analytic
   proof with explicit precision and tape costs remains outside these finite
   certificates.
3. **Find a scalable outer family and understand the linear-time barriers.**
   Relevance: epsilon strictly below one and the fixed supplier ceiling prevent
   this witness refinement from proving linear time. First step: derive a
   uniform family with all supplier, routing, precision and setup costs charged
   jointly as its parameters grow. Blocker: finite examples or a convergent
   sequence of exponents alone do not provide a uniform linear-time algorithm
   or control the growing constants and cutoffs.


## Exact finite-proof reuse

The default full command runs the original complete cold release. For the
local continuation of an already reviewed run, additionally pass both
`--reuse-baseline-source /path/to/frozen105/package` and
`--reuse-baseline-run /path/to/completed/full-001`. This mode authenticates all
397 baseline source files and all1199 execution files against the hard-pinned
reviewed seal, including native word/frame/phase outputs, every nested log and
STAGES/STEPS receipt, controller declaration and terminal, and the independent
actual-result review. It requires the current native parent to be byte-identical
to the admitted parent and repeats the full evidence authentication after new
arithmetic. New outer constraints, two exact actual-profile moment enclosures
and the exact broad-shift check are always rerun. Changed or incomplete baseline
evidence rejects. The resulting receipt explicitly records reuse. This is
source-specific finite evidence transfer, not a new native replay or all-size
proof. Fresh independent CI uses no reuse flags.


## Portable generated-artifact line endings

The frozen parent remains byte-for-byte unchanged. Its two committed generated
files `outer/LEDGER.json` and `outer/INDEPENDENT.json` use CRLF. The original
outer regeneration compares full bytes; Linux emits LF, so otherwise identical
arithmetic artifacts fail that comparison. This is a format portability repair,
with no change to kappa, slacks, formulas, native code or independent checkers.

For a fresh cold run, `portable_parent.py` authenticates every frozen parent
file against the pinned manifest. If the two artifacts already match the host
newline convention, it returns the original parent. Otherwise it makes an
execution copy strictly inside the new work directory, converts only CRLF/LF
bytes in those two files, and replaces only their two digest values in the
derived manifest. It rejects lone carriage returns. All other source bytes,
including the unchanged original release verifier, CLAIM and SPEC, stay exact.
The unchanged full parent release runs on that authenticated execution copy;
its original strict full-byte regeneration comparisons still run. Adaptation
alone is not scientific verification or a successful release.

The result records the original and execution manifests, permitted file
transformations, complete source inventories, and observed source-tree hashes
before and after execution. Both trees are reauthenticated after the new
arithmetic. The original frozen parent is never edited. Explicit baseline-reuse
mode continues to authenticate the unchanged original complete proof seal and
does not use this adapter or claim a new native replay.

For the two new refinement artifacts, equality compares every byte after only
CRLF-to-LF conversion, rejecting lone CR. It does not compare parsed JSON or
equate numerical types: changed digits, rational strings, integer/float/string
types, property order, whitespace and hashes all reject. Controlled smoke tests
in `test_portable_parent.py` exercise both LF and CRLF execution-copy cases and
source/manifest tampering without running the native scientific pipeline.
