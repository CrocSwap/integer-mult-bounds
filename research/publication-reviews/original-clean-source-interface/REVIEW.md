# Independent publication review: original clean-source interface

Status: **PASS_LOCAL_PUBLICATION_REVIEW**. There are no open local publication
blockers. This is a separate agent review. It is not human review or full
supplier admission.

The reviewed package manifest SHA-256 is
`54b73508241ee124872dbbeb01305c7b70bf3d7c214fc153233725220196e07b`.
It covers 65 files; the manifest is the 66th file. The package has
6,915,673 bytes. All 52 pinned inputs match their original sources.
The five archive members match the original archive. The full archive hash
also matches its pin. No frozen source file changed during this review.

The decision applies to the exact local construction, its physical helper
interface, and its binding to the original owner schedule. It does not prove
the changed global data word, a complete supplier cost, or a kappa improvement.
The package makes these limits explicit.

## Cold replay and source checks

I copied the package to `cold/package` in this review directory. I ran the
documented runner there with a new `cold/replay` output directory, isolated
Python, disabled bytecode writes, and one thread for numerical libraries.
The runner runs one checker process at a time. The executed command is in
[COMMANDS.sh](COMMANDS.sh).

All three checks passed normally and with `python -O`. All six output receipts
equal the frozen receipts byte for byte. The normal and optimized receipts
also match. The sum of checker times was 12.625 seconds on Python 3.14.7.
The final status was `PASS_ORIGINAL_CLEAN_SOURCE_INTERFACE`.

The runner and all input files in the cold copy stayed unchanged. The final
package differs from the cold snapshot only by the later `RESULT.json`,
`validation/REPLAY.json`, and package manifest. All 63 files present at cold
copy time still match the final package.

[PACKAGE-CHECKS.json](PACKAGE-CHECKS.json) records a second source and package
check. It verifies the complete file inventory, hashes, exact original source
bytes, archive bytes, payload hashes, and local links in the three wrapper
Markdown files. It also checks the actual R matrix and the cost arithmetic.
Disk space stayed above the required 3 GiB; this check ended with
8,937,009,152 bytes free.

The two portable scripts change source roots and archive-member reads only.
They retain the individual member hash checks and the mathematical checks.
The original scripts and exact diffs remain in the package. The whole archive
check occurs at extraction and was repeated independently here.

I inspected the runner and all three executed checkers. They import only
standard-library modules. They do not import a producer. Their file paths
resolve to the private copied package or the stated output. The runner copies
the input trees for each check before a checker writes its receipt. I found
no hidden source import. This review did not add a runtime file-access audit.

All four scripts have zero Python `assert` nodes. I called each script's
explicit failure guard with false input in normal and optimized Python.
All eight controls failed with the expected `ValueError`. The content checker
also executed its four forward and five backward mutation controls in both
modes. Receipt equality alone is therefore not the only check against an
optimized false pass.

## Ordered local proof

I read the wrapper [proof](../../original-clean-source-interface/PROOF.md),
the original clean-source proof, the free-group content review, the physical
review, and the original-owner review. I also read the raw-mode and original
phase premises needed by those proofs. The package's direct-source manifest
identifies those files.

The actual R matrix is 8 by 112, has 448 nonzero entries, and satisfies
`RR^T=56I`. For `K=R^T/4`, all 112 diagonal entries of `KR` equal one.
These facts were checked directly from the frozen matrix with exact fractions.

The accepted raw forward map has helper output `-u-2Rx` and data update
`(I-KR)x-Ku`. The three input operations restore the helper input `u=z`
and add `Kz+KRQx` to Y. The raw core then cancels `Kz`. Its final helper
read and sign restore z. This gives the exact kernel
`D_plus=I-KR+KRQ` in the displayed order.

For the backward map, the input helper read gives `u=z-Ry/4`. Substitution
in the accepted raw map gives `x-y+KRy-8Kz` and helper content `-z`.
The output Y frame is `F9 Q^-1`. Thus the output read and scatter add
`8Kz-KRQ^-1y`. The read cleanup and final sign restore z. This gives
`D_minus=I-KR+KRQ^-1`. Using Q in that output read would give the wrong
data endpoint even if the helpers still restored.

Neither calculation moves Q through R, K, or KR. Neither uses even width,
a characteristic phase, or `Q^4=I`. The checker works over free signed
port words and cancels adjacent inverse letters only. It covers all 704
formal input columns, including arbitrary helper input. Both data outputs
have zero helper-input coefficients, and all 480 helper content rows restore.

The claim that the two kernels differ at every positive tensor width is
supported. Actual port zero has label 11. Character 1 gives Q multiplier i
and inverse multiplier -i. Since `(KR)_(0,0)=1`, the same-port difference
is 2i. At greater width, character zero in the other layers preserves that
witness. The missing-final-sign witness also holds at every width: on the
all-zero character the required helper multiplier is +1 and the omitted-sign
multiplier is -1.

The displayed identities
`D_plus Q^-1 + D_minus = I+Q^-1` and
`D_minus Q + D_plus = I+Q`
follow by expansion with the same factor order. They do not provide a kernel
inverse. Each individual shear is invertible by reversing its update sign.
The two stated shears on the same banks are not mutual inverses.

## Physical helper and owner scope

The helper argument uses a complete physical job. At stage s, the exterior
operator acts on coordinates 9 through `8s+8`; F9 acts on coordinates 0
through 8. Their disjoint supports give exact commutation. For arbitrary
physical input h, the proof can write `h=E_s z`. This is a coordinate change,
not an input preparation or promise. Restored content in output frame
`E_s F9` gives `E_s F9 E_s^-1 h=F9 h`.

Thus the eight selected helpers still perform their complete F9 jobs.
Their physical endpoint is not the identity. The other 472 helper jobs stay
unchanged. This holds for correlated input arrays because the full content
map has no cross-helper or helper/data endpoint terms. With old whole-job
views A and B, the endpoint stays `B F9 A`. The proof does not require an
owner's prior completed prefix to equal the invocation's exterior frame.

The original-owner check binds all 144 invocations: 80 forward and 64
backward. It checks all 69,120 helper jobs, including the 1,152 selected
width-nine occurrences. The retained schedule has 482 positions, 14,336
live families, and 14,826 physical families. The source body's 704 families
are distinct, and each fixed-role cover route is a bijection. The replacement
must keep its prefix, core, suffix, and signs inside the body and finish the
cover before the next old schedule event.

The selected jobs retain nine actual pending phase vectors and their native
views. The full chart gives native covariance with phase. The old complete
axis-history proof is an inherited premise. The new check binds to that
history; it does not replay the entire old history. The package states this
limit. The even-width source reviews supply only unchanged raw-core and old
owner facts. Their characteristic maps and changed boundaries are not used.

## Terminal condition and cost

I checked the ordered terminal equation. The old preterminal frames are
`(F,FQ^-1)`; the old Y translation Q squared gives `(F,FQ)`. This step uses
the exact native translation commutation, not a commutation with KR.
The physical output is

```text
F W diag(I,Q) E diag(Q^-1,I).
```

The same paired-port Q and the signed exchange W give
`W diag(I,Q) W^-1=diag(Q,I)`. Substitution and multiplication by the
displayed inverses show that the required output F is equivalent to
`E=W^-1`. The package does not prove this condition for the routed new
kernels. Owner counts and helper restoration do not settle it.

The literal prefix and suffix counts agree with the cost claims. Each
orientation adds 1,792 complex ADDs and eight complex negations. Under the
stated primitive-cost convention, the added costs are 17,040 forward and
22,416 backward. With the raw bound 204,418, the totals are 221,458 and
226,834. The 80/64 invocation subtotal is 32,234,016.

The 5,056 retained native events include adapters. The paid profile
`{1:2412,2:418,3:432,4:142,5:82}` has mass 5,522. With retained idle
suffixes, the full listed component profile has mass 1,032,192. I checked
the arithmetic. These are component counts before data-controller closure.
No extra productive credit follows from the retained helper stock.

## Provenance and remaining publication gates

The retained notices give the historical supplier and construction credit,
including icekylinx, Hao Yan, Jeremy Kothe, Chafik Boukhalfa, and Rohan Arun
in their stated roles. The package preserves the source notices and license.
It separates the later campaign work and AI assistance from predecessor
credit. I found no attribution change needed for this wrapper.

The historical source commit is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
The packaging base is `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`.
The new selected PR #4470 is context only. Neither a new source pin nor
applicability to that selected construction is inferred from it.

I did not rerun the raw native kernel proof, the dense native phase compiler,
or the complete old axis-history suite. I did not establish parser lowering,
full routing and control costs, prefix growth, finite precision, recursive
costs, integer recovery, or complete kappa. These remain explicit limits.

No package fix is required. The publishing agent must still check the final
PR description against the workspace standard, verify its live and
commit-pinned links, inspect rendered Markdown, and read the published body
back. This review made no commit, push, merge, or PR write.
