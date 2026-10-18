# Executed checks and scope

Completed on Linux x86_64 with CPython 3.14.4 and CPython 3.12.3. No solver,
third-party Python package, compiler, network or prebuilt cache is required by
the package. One preliminary nomination screen used installed NetworkX 3.6.1;
the published bound and both complete verifiers do not use or trust it.

The default `verify.py` passed on Python 3.14.4, including its independent
checker subprocess. The standalone independent checker and seven tests also
passed. A minimal input copy containing this package and exactly the twelve
manifest-listed source/provenance files was made read-only. From `/tmp`,
`python3.12 -I -O -B` passed the primary command, the independent checker and
all seven tests. Both full receipts were also regenerated outside the input
tree and matched the committed receipts byte for byte:

| Receipt | SHA-256 of committed pretty-printed JSON |
|---|---|
| EXPECTED.json | `b56ce9b45a20ca3e338778b7fd71cce0df0d22417174c885ca7c462064a61b51` |
| INDEPENDENT.json | `b80f155df589848b4b4e4b99c32a3b0d6881456efec601222465c365c1350195` |

Coverage includes:

- All 174,048 ordered coefficient/target-pair cases, with 784 per-child and
  exponent minima and full ordered-record digest
  `8380689aec4fac803894fc198f369d040e8face6f9e2531c668fb34e5e9c2d40`.
  The independent dense implementation reproduces every summary/minimum and
  the complete digest, using literal coefficient prices.
- The 162 finite alphabet/direction tail families at exponents
  3, 4, 5, 8, 36, 64 and 127. The independent checker derives slopes from
  literal costs and checks the remaining samples. The proof covers all
  integers beyond the finite anchors; finite samples are not represented as
  exhaustive coverage of an infinite domain.
- The exact retained PR816 unit tree, all 12,544 signed multigraph cycle
  inequalities, and the separately constructed Prim minimum, all at 16,364.
  The original 3,342-macro panel is reconstructed exactly from its tree.
- Sparse Fraction and dense quarter-grid integer replays each compare the
  original and retained panel on all 716 arbitrary input columns in both
  orientations. The native full supplier is not rerun by this package.
- Literal lowering and execution of 1,058 coefficient inputs, totaling 72,632
  primitive instructions, with arbitrary target/source/private-work symbols.
  Every count is compared with the exact pinned emitter's `primitive_bound`
  function, extracted without running the emitter's file-writing top level.
  That source function's assertions remain enabled under an optimized driver.
- Exact historical SPEC/program/panel binding and recomputation of the
  unchanged full source invoices, 224,938 / 224,986 real primitives. This is
  an invoice recomputation, not fresh native frame/wrapper or whole-word
  execution.
- Nine primary controls, including a different synthetic matrix where a
  nonunit edge is profitable, an out-of-alphabet premise, underbilled and
  nonminimal trees, a disconnected cycle, omitted preparation/restoration,
  typed receipts and a weighted overlapping-chain deletion identity.
- Two independent coefficient controls reject omitted initial and final work
  clearing. Seven package tests cover all 169 three-target weighted forests
  and 11 cyclic topologies, arbitrary target dirt, source mutation,
  semantically equivalent gzip recompression, duplicate keys, typed receipts
  and existing-output preservation.

All twelve source/provenance objects match their named base Git blobs.
Runtime compressed-file admission checks decompressed bytes. The final fetch
left main at `007664306fff84fbb1c9a1b4053b69f439764034` and
`make selected-record-check` passed for the unchanged PR890 record.

The opening queue held 707 PRs through PR954. The final refresh through PR961
found a concurrent X4 all-dyadic forest bound; its exact head and relationship
are disclosed in README.md and NOTICE.md. The present result retains the
CK power-of-two scope chosen before that arrival. It does not extend its
claim to non-power-of-two dyadics or import the concurrent implementation.
No pinned sprint coordination issue existed, so the local claim is retained.

No full repository suite, fresh native supplier/frame/wrapper replay,
whole-hosted invoice, cold assembly replay, hosted CI pass or formal proof of
the multiplication theorem is claimed. The source circuit and selected
frontier are unchanged. The output is an exact scalar cost exclusion for the
stated class and independent checks of its existing attaining witness.
