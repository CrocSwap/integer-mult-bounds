Pinned PR68 actual real characteristic and state-cost transfer
=============================================================

This separate package binds the public PR68 candidate at commit
85781f662b57521743cce07cdd5ea194e6f3879d to a Lean theorem about its actual real
characteristic. Earlier selected-profile proofs are unchanged.

Source:
https://github.com/DominikScholz/integer-mult-bounds/blob/85781f662b57521743cce07cdd5ea194e6f3879d/research/cost-live-both/candidate.json

The copied pr68-candidate.json was checked byte-for-byte against that Git blob.
SOURCE.json records its SHA256, source pin, path, and exact public parameters.
The public finite composition is Dominik Scholz's PR68, built on Rohan Arun's
PR67 cost-aware selection, Chafik Boukhalfa's PR60 ranked reclamation, eumemic's
PR57 joint compiler, and Avi Eisenberg/ikeboy's PR62 graph. This proof package
adds Lean certificates with OpenAI Codex assistance; it does not claim the
underlying finite optimization as new. Predecessor and repository attribution
and license terms remain applicable.

Proved result
-------------

Pr68ProfileReal.actual_power_characteristic_lt_one proves, with no hypotheses,

  sum over all 27 literal rows of (n_t/W)*(t/m)^(1-a) < 1,

where m=575, W=137151806, rank mass=78860441550, and

  a = 51037731934993 / 1000000000000000000.

This is a theorem about Lean's real power, logarithm and exponential functions,
not a rational approximation reinterpreted as a real enclosure assumption.
The rational upper bound is below 1 by exactly

  9542461156808503791 / 34287951500000000000000000000000000000,

approximately 2.783036238490e-19. This is the certified rational upper-bound gap;
it is not an assertion that the actual characteristic gap equals that fraction.

Pr68ProfileCertificate.lean independently checks every row's rational witness
by ordinary kernel computation. Pr68ProfileReal.lean applies the generic
AnalyticEnclosures theorems: nonnegative 24-term lower exponential polynomials
certify logarithm upper bounds after exact power-of-two range reduction; the
8-term exponential polynomial plus its proved remainder gives each upper
witness. The generator only discovers witnesses. Its analytic reasoning is
not in the trusted proof chain.

Pr68PhysicalCost.state_cost_bound instantiates the generic state-indexed floor
transfer at these actual public parameters. For arbitrary invocation states,
it proves cost(s) <= A*volume(s)*width(s)^(1-a), uniformly in all volumes and
spectators. Its explicit physical contracts require nonnegative volumes,
actual child widths t*(e/m), actual child volumes V/W, a uniform base cost B*V,
and the unnormalized recurrence C*V plus the sum of every indexed child's cost.
The constant is A=max(0,B)+|C|/(1-characteristic). There is no normalized
worst-case function or supremum over states. Multiplicities remain symbolic
Fin(n_t) sums, not lists with billions of entries.

The candidate's public global kappa=51035127217697/10^18 is provenance metadata.
This package proves its finite real characteristic and conditional state-cost
transfer, not the complete multiplication theorem at that kappa. Concrete
compiler-to-tape semantics, uniform physical cost contracts, analytic reduction,
precision and exact recovery remain external. The independent finite replay/
CRT receipts reside in the adjacent audit package; no expensive finite replay
or compiler run was repeated here.

Reproduce
---------

Use the preserved Lean4.21.0 toolchain and a built Mathlib project pinned to
308445d7985027f538e281e18df29ca16ede2ba3. Put the matching Lean/Lake on PATH.
From the mission directory:

  python3 outputs/transfer-proof/latest-analytic/check.py \
    --lake-project work/agents/lean-foundations/formal/lean \
    --repository work/agents/repository-audit/pr68-cost

The optional --repository flag repeats the pinned Git-blob equality check.
Without it, the included candidate is still checked against the pinned SHA256.
--candidate, --analytic-dir, --recurrence-dir and --output can override paths.
No installation or repository mutation is performed. --check-sources-only
checks all pins, source hashes and literal bindings without compiling.

The checker compiles the 52 already-audited dependency theorems and 14 PR68
namespace declarations into one isolated olean directory, then audits all 66
declarations. Of the 14, power_term_identity repeats the previously proved
generic identity; the other 13 are specific certificate/transfer declarations
for the new pinned profile. No generic dependency is counted as new progress.
Only propext, Classical.choice and Quot.sound are allowed. The verification
directory contains the fresh build logs, source-binding.json and axiom audit.
The manifest pins every proof source and both dependency manifests.

Regenerate the finite witness module independently:

  python3 outputs/transfer-proof/latest-analytic/generate_pr68.py \
    outputs/transfer-proof/latest-analytic/pr68-candidate.json \
    --output-dir /tmp/pr68-witnesses \
    --lean-output /tmp/pr68-witnesses/Pr68ProfileCertificate.lean

The regenerated Lean source and pr68-witnesses.json match the shipped copies
byte-for-byte. A source-data binding check independently compares every literal
width/multiplicity, m, W, saving and mass against the public candidate.
