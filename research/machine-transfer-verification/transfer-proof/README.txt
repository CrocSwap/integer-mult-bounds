Physical transfer and newest finite-certificate checkpoint
=========================================================

This local checkpoint extends the research published in draft PR64:
https://github.com/CrocSwap/integer-mult-bounds/pull/64
The published head remains 790a14e28e935398072b9a9a68694ce7fba8940f.
Neither this package nor the preceding next-proof package has been pushed.

Established results
-------------------
recurrence/: 35 audited Lean declarations prove the literal floor recurrence,
executable logarithmic recursion depth, exact integer row-stock closure, and
a uniform state-indexed cost bound. Physical child and cost contracts are
explicit assumptions; monotonicity of the cost function is not assumed.

tapes/: 36 audited declarations prove literal finite-control tape push and
pop, with four tape symbols and at most three tapes. Their bounds are 2n+2
and 3n+5 transitions. The original source is reused as the restored output.
Constant-cost marker installation/removal and empty-stream cases are covered.

framed/: 19 new audited address-gauge declarations prove nested/complementary
partial-swap identities and an endpoint theorem under explicit typed-trace
and scalar-permutation hypotheses. A separate concrete Python check of both
PR64 local forward schedules includes all literal clearing gates, fresh
center copies and explicit side flags. It exactly reproduces the charged
CRT profiler inputs. Seven malformed schedules are rejected. This finite
check is not a generated Lean trace of the complete ambient construction.

latest-analytic/: 14 audited PR68 declarations, including one repeated generic
identity, prove the actual real characteristic inequality at the exact public
bit saving 51037731934993/10^18 and instantiate the uniform state-cost bound.
The literal 27-row profile is bound to PR68 commit
85781f662b57521743cce07cdd5ea194e6f3879d. The exact rational upper-bound gap is
9542461156808503791/34287951500000000000000000000000000000 > 0.
No analytic-enclosure premise remains in the finite real inequality.

Together these packages audit 104 declarations in new namespaces/modules;
one is a repeated generic power identity. Rebuilt dependency declarations
are excluded from that count. All successful audits contain only standard
Lean foundational axioms. See each package's scope map and build receipt.

Finite frontier and research outcome
-----------------------------------
The 19:01 UTC repository snapshot contains 68 PRs. The strongest independently
reproduced finite candidate is the updated PR68 at the pin above, with
conditional kappa = 51035127217697/10^18 = 5.1035127217697e-5.
This public composition is credited to Dominik Scholz, with Rohan Arun's
cost-aware retired-slot work and all inherited upstream credits preserved.
audit/ records fresh focused validation, independent complete word/basis
checks, CRT profiles and independent exact assembly arithmetic.

Three bounded axis experiments and six exact pair screens found no improved
construction; experiments/ records the negative result. The new progress in
this checkpoint concerns verification and physical transfer lemmas, not a
new numerical exponent beyond public PR68.

Remaining proof boundary
------------------------
The complete multiplication theorem remains conditional. Concrete ambient
two-direction frame traces, all-size residual compilation, recursive tape
scheduling with child cleanup, uniform movement and descriptor costs,
eligible-prime reduction/setup, Gaussian resampling, precision and exact
recovery still need integration into one fixed machine.

The formal finite real inequality is unconditional. The state-cost theorem
is conditional on its named physical contracts. The local finite phase
check and external CRT/profile checks must not be confused with either a
Lean proof of the whole trace or a full machine-time theorem.

Reproduction and archive layout
------------------------------
Individual package READMEs give commands. Lean checks use an existing cached
Lean 4.21.0 / Mathlib 308445d7985027f538e281e18df29ca16ede2ba3 project;
the scripts install nothing. Python finite checkers use the standard library.
The archive preserves paths relative to outputs/, including analytic
dependencies and the selected compressed words needed for phase replay.
Reproducing all upstream CRT/repository tests additionally requires the
specified pinned upstream checkout. Saved receipts state the checks run.

checkpoint.json summarizes the checkpoint. file-manifest.json binds all
archived files except itself. transfer-proof-bundle.json beside the archive
records its SHA-256 and successful archive-integrity check. The earlier
research-bundle.zip and next-proof-bundle.zip remain historical snapshots.
