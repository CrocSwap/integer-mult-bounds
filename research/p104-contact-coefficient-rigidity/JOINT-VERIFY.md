# Joint-compensator verification

`verify_joint.py` checks the fixed deletion of original event 10947 with
zero, one or two other existing scalar coefficients changed. It is a
registered extension of the contact-rigidity package. No new kappa is claimed.
`JOINT-PROOF.md` supplies the domain-completeness argument, determinant
identity, and the distinction between endpoint wrappers and replacement
of the actual zero/full hubs.

## Invocation

The checker requires the primary package directory explicitly. It has no
workspace path embedded in its code. After integration, run from the
repository root:

```sh
python3 -I -B research/p104-contact-coefficient-rigidity/verify_joint.py --package research/p104-contact-coefficient-rigidity
python3 -I -O -B research/p104-contact-coefficient-rigidity/verify_joint.py --package research/p104-contact-coefficient-rigidity
```

`--output PATH` writes a JSON certificate; no output file is required.
The registered replay runs both normal and optimized modes with a
120-second timeout per command.

## Authenticated inputs

Before executing the primary module, the checker hashes its `verify.py`
source bytes and requires SHA-256
`b1561af0138ebae887728eb561005a2336f00887b5948a3b03f5b44b379b39c5`.
It compiles those bytes directly, bypassing source-module bytecode caches.
A reviewed change to the primary verifier requires an explicit pin update.

The primary loader authenticates the retained word's length, SHA-256 and
Git blob hash. The extension additionally requires canonical native
payload digest
`d3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821`,
from #6824 at `2a7ca44fbda3abaa4df355b183ed7d7478eef7c1`.
No network, third-party package, prior exploration report, or other checkout
is needed beyond the supplied primary package.

## Checks performed afresh

1. Validate the original native source and explicitly replay its full
   public endpoint as A. Check the prescribed deletion and MOVE pair,
   the unique intervening helper touch, and the two rank-1 MOVEs.
2. Replay the deleted word, check its full rank-one endpoint update,
   require its determinant to equal one, and verify both products with
   the constructed inverse. This precedes every determinant calculation.
3. Recompute every prefix row and suffix response in the deleted word.
   Reconstruct both direction classes, including their zero directions,
   and the complete unordered pair domain. Require 46,381 pairs and the
   independently rebuilt canonical domain digest
   `b43d8f9399c442c9e67753741c4c4c1e407143bf2d0cd5f44b5d73f2df43d4c1`.
4. Recompute the four possible one-compensator cases at events
   12280, 12282, 12287 and 12288 and verify their singular determinants.
   This closes the x=0 or y=0 cases without importing a frozen result.
   With both changes zero, the checked nonzero C1 defect already rejects
   the deleted word.
5. Obtain each pair's exact transfer by forward or reverse propagation.
   Express C1 in a basis consisting of the target direction and its
   quotient direction. Perform rational row reduction in x,y,Z and
   compute the rank-two determinant polynomial.
6. Prove each pair inconsistent or singular. The 2,948 cases remaining
   after the linear-in-monomials check must each have exactly one RREF
   equation, with no Z coefficient and exactly one nonzero x/y
   coefficient. Substitute that fixed value and require both coefficients
   of the remaining determinant polynomial to vanish. An unexpected
   residual shape fails verification; there is no general polynomial
   solver or numerical root search.
7. Replay all 14 declared native controls literally. Compare the complete
   public matrix with the two-update formula, compare expanded C1
   equations with the compressed equations, check C1 directly, and use
   separate sparse row elimination to produce a nonzero null vector.
8. In the genuine joint control at events 12280 and 12282, deliberately
   omit the mixed term and require disagreement with the literal endpoint.
   This rejects a semantically incorrect two-update formula.
9. Verify a small positive joint-repair example. Its changed coefficients
   are 0, 2, 3/2; its endpoint is diag(2,1/2), repaired by supported dyadic
   hubs. The singularity classifier must not reject that positive example.

The expected joint classification, recomputed rather than read, is:

| Exact disposition | Pairs |
|---|---:|
| Inconsistent linear monomial system | 99 |
| Determinant in the C1 linear span | 43,334 |
| Determinant identically zero after fixing x | 2,012 |
| Determinant identically zero after fixing y | 936 |
| Total | 46,381 |

The last two categories contain direct singularity identities, not an
unreported mixture of irrational roots and inconsistent nonlinear cases.
All arithmetic is exact rational arithmetic. Zero and nondyadic scalar
values, including zero SCALE values, are admitted in the obstruction;
changed-word scalar legality is not used to prune the equations.

## Certificate and interpretation

`JOINT-CERTIFICATE.json` records the source pins, direction and domain
counts, fresh one-compensator checks, exact dispositions, 14 literal null
vectors, mixed-term rejection and positive control. Normal and `-O` runs
must agree in every field except diagnostic elapsed time. All checks use
explicit exceptions, not Python assertions.

A separately implemented `independent_joint_audit.py` uses its own native
replay and full 772-row Gaussian inverse to rebuild all 46,381 expanded
boundary systems and determinant closures. Its registered optimized replay
includes literal determinant/null-vector and transfer-corruption controls.
`JOINT-INDEPENDENT-AUDIT.json` retains the compact receipt; `--details PATH`
can regenerate all residual equation records. See `REVIEW.md` for independence
and exact review boundaries.

The source-bound count and identities depend on the complete rank-screen
proof in `JOINT-PROOF.md`. The checker is not a proof-kernel formalization.
It establishes a necessary public-map obstruction for this one deletion
and coefficient-edit domain. It constructs no improved native word,
invoice, supplier, compiler replay or outer multiplication theorem. The
selected frontier and its five framework assumptions are unchanged.

Jerry Chen / @CubeJerry, with substantial OpenAI ChatGPT assistance.
Predecessor source, event semantics and native-word credits remain those
in the primary package NOTICE and SOURCES.json.
