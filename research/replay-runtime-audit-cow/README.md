# Copy-on-write controls for the selected T16 audit

This package measures one bounded stage from the selected PR1094 reproduction:
the T16 asynchronous controller audit in the exact PR1087 source archive. It
does not run the full selected reproduction or change any frozen source.

The pinned audit makes 15 negative-control variants of one large owner map. It
deep-copies the complete map for each variant even though each control changes
one small path. The opt-in candidate shallow-copies just the containers along
the path being changed. The original source template is serialized before and
after the controls, so an incorrect copy path fails instead of leaking a
mutation into later checks.

The reproduction extracts the exact selected replay archive, checks the
upstream package inventory, and runs the original and generated candidate on
the same base and hosted artifacts. It compares all four generated files by
SHA-256 and retains the original 15 rejection controls. Source changes fail
the pinned digest and exact-text patch checks. The code adds no persistent
cache; every run rebuilds the candidate from the pinned source bytes.

## Measured result

On Linux with Python 3.12.3, three alternating unprofiled process pairs gave a
26.5959 s median for the original audit and 9.3909 s for the candidate: 2.832x
faster, saving 17.2049 s (64.7%) in this stage. Each run rejected the same 15
mutations and emitted identical digests for the audit report, owner/profile
receipt, frame receipt and compressed frame artifact. The full measurements
are in [MEASUREMENTS.json](MEASUREMENTS.json).

A separate cProfile diagnostic counted 288,684,580 calls in 87.191 profiler
seconds. The 15 control calls spent 75.993 s cumulatively in deep-copy code;
the audit function itself accounted for 9.636 s under profiling. That
instrumented time is diagnostic and is not used in the before/after timings.
The selected archive's historical stage receipt recorded 32.603 s for this
audit on its original host; this session's unprofiled comparison uses the same
extracted fixture on one Linux host for both variants.

## Result boundary

Only the selected T16 audit stage is in scope. The improvement does not cover
the other stages in the PR1094 reproduction, multi-provider audits, or a cold
rebuild of the predecessor chain. It establishes no supplier improvement,
mathematical result, new kappa, or selected-frontier change.

The upstream audit source is retained from PR1087, head
589d1cedf5ef5f231182f4ec86408616311a8af0. The selected fixture belongs to the
PR1094 result at base 20ecf2891d80b5acf18d980b2164fb44ea7faa90. Credit the
original PR1087 audit and its retained PR858/PR870 T16 controller lineage, as
well as Rohan Arun's selected PR1094 package and the contributors listed in its
source notices. This package is a runtime-only successor experiment; it edits
none of those inputs.

## Reproduction

Use Python 3.12 or later and a single CPU slot. From the repository root:

    flock /home/cinna/int-bounds-pass/20261018-luna-xhigh/compute.lock \
      python3.12 scripts/research_package.py \
        --package research/replay-runtime-audit-cow

The registered verifier runs three alternating original/candidate pairs,
verifies their exact output digests and all negative controls, tests that a
changed audit source is rejected by the source pin, and prints the paired
wall times.

## Open next questions

- Does the same small-path cloning opportunity occur in another independently
  pinned replay stage with a different control object?
- Should a source-pinned successor of the upstream audit adopt this
  optimization, after a maintainer checks provenance and runs its registered
  environment?
- What are the end-to-end savings when the same control-heavy audit is called
  from a cold replay on another supported host?

Prepared by Codex with substantial AI assistance. Apache-2.0.
