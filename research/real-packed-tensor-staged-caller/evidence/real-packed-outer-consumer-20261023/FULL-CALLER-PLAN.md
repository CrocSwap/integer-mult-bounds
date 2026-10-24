# One actual two-Tensor staged caller: static execution plan

**Not executed.** The frozen candidate remains `packed_sandwich_DRAFT.py`, SHA256 `5dfcdfe63d9d03a89a00dd92e681ab0a0efc5bbc86aa7edae58f007baf752483`. The proposed harness is `run_full_packed_DRAFT.py`; only AST parsing/static review has occurred. It requires a separate root execution GO. No Hermitian orbit, gamma-parity optimization, precision change, child allocator update or producer retuning is included.

## Exact fixture and matching rule

Use the authenticated public100402-byte catalogue `staged-source/research/physical-tensor-crt-sandwich-recovery/inputs/p48-5x7.bin`, SHA256 `7dd7adbe9e8f6d5ffbecd425a72827b31d7222ee51bcd67a4148ebfd03420381`. Do not run `prepare_fixture.py`, regenerate coefficients, or rerun the passed source leaves.

The single candidate fixture is source box(5,7), target box(8,8), p48/P80, b8, q4, independent digit streams `(255,0,3,17)` and `(1,254,0,9)`, rows1, **require_recovery=False**. It uses all35 records, both complex components and source-coordinate CRT/dilation conventions. The two high, asymmetric digit streams avoid a zero-input-only test. The staged oracle preflight must produce a nonzero packed forward and a nonzero nonlinear product, and the product must be in the opposite half-disk. If any of these qualifications fails, the process stops **before numerical child execution**, records that fixture limitation, and does not choose another input automatically.

The comparator is the unchanged source's separate natural-coordinate staged oracle, `sandwich_reference.full`. It is evaluated on the **same packed input**, followed by the same independently computed squared-difference product, then `full(product,raw,True)`. It never replaces the actual packed call with a sum of separately rounded forwards. Host formulas independently check CRT, J, raw split scale, both S factors, nearest rounding, inverse CRT and the prescribed64 output bits. The numerical candidate and comparator therefore match inputs, geometry, coefficient bytes, rounding semantics and outputs. This is conformance to the staged source operation, not accuracy against the ideal Fourier transform.

No original unchanged full numerical caller is repeated. Its verified Linux452.68-second three-Tensor run is context for budgeting, not a matched wall-clock benchmark for this changed q4 input. The old source case used q3; a total performance comparison would need its own controlled matched experiment. The new process is intended to bind this candidate's complete endpoint/lifecycle, not to establish total finite speedup.

## Numerical call census

Only one actual call to `RealPackedSandwich.run` is allowed to enter numerical children. Its delegated observer guards require:

| Actual numerical child | Count | Input and full return comparison |
|---|---:|---|
| Forward Converter | 2 | independent digit ingress banks → the two exact real natural-coordinate banks |
| Forward Tensor | 1 | one actual packed bank → all35 expected staged complex records |
| Opposite Tensor | 1 | actual once-truncated product → all35 expected opposite complex records |
| Inverse Converter | 1 | unchanged widened recovered records → all35 natural ordinary coefficients |

Both complete Tensor calls execute the original source body with its original numerical children. Converter `run_plan` likewise delegates into the original method. The observers reject a third Tensor, a fourth Converter, wrong opposite/inverse flags, or any numerical dispatch in a control phase. They retain every returned record as raw bits and hashes, together with the complete child's own count dictionary. No mock Tensor/Converter or dense replacement backend is substituted.

The local product must yield140 exact signed split operations,140 actual real products at width51 and final shift50. Parent counters must equal3conversions,2transforms,1pointwise pass,35packed records,2Jaxis passes and35split records. The inherited complete child setup/catalogue/routing/word bill remains paid; source preparation is not repeated because the authenticated produced catalogue already exists.

## Ownership, rejection and cleanup checks

Before enabling numerical calls, run the inherited constructor/entry controls **against the changed candidate class**. These dynamically cover three constructor rejection cases, six b/q-to-payload aliases, five descendant-private aliases, occupied end-head output, consume and subsequent production-policy rejection. Other external tape coincidences remain statically rejected by the unchanged five-distinct-port predicate; do not call the dynamic cases exhaustive.

For the numerical run, snapshot the values and exact initial heads of both independent payloads, catalogue and b/q metadata. Require identical values/heads after the run. Check complete child returns are consumed, closed owners and empty live pools; retain the candidate's single pending output. Move its borrowed output cursor to the end, then verify another call rejects before a numerical dispatch. `consume()` must perform the real clear/marker retirement. A subsequent default-policy call must reject the reduced catalogue as non-production and clean its parent state without numerical work.

Finally inject **one specific failure cut**: the first Converter dispatch throws before calling its original numerical method. At that point the parent owns the first ingress bank and catalogue metadata. Verify parent finally cleanup, borrowed/metadata values and heads, no pending output, empty live pool and canonical empty resident origins. This adds zero numerical child calls. It is not a test of failure inside a numerical child or after a completed later Tensor return.

Observer ownership is explicit. After an original child returns, its observer owns the obligation to clear/retire that return if inspection/comparison raises before the parent `child()` receives it. Both child observers have `except BaseException` cleanup for that case, returning the unchanged bank only on success. The draft source is not edited for observer instrumentation.

## Diagnostic assertions and limits

The harness records staged_integer, true_integer, their signed difference and an explicit equality flag. Diagnostic disagreement is retained visibly and is not a production arithmetic failure. It asserts the exact source-staged output, not equality to the true product.

Earlier actual-method evidence discriminated J, conjugation, division-by-i sign and raw split-product shift on a supplied bounded bank. The whole-run harness checks correct flags and exact full returns but does **not** execute four additional mutated numerical callers for wrong opposite sign, inverse-R, missing S or doubled gamma. Those unrun full-stage mutation controls are explicitly listed in the receipt. No stronger discrimination coverage is inferred when a particular opposite result is zero.

The same-(G) production error lemma has independent conditional mathematical PASS, but this reduced catalogue does not meet its production premises. Raising p at this fixed geometry remains insufficient. The fixture supplies no recursive κ gain, native helper reward, production supplier admission or all-size multiplication theorem.

## Process, timing and integrity

Proposed command, **only after root GO**:

    timeout -k 10s 600s python3 -I -B -W error run_full_packed_DRAFT.py > FULL-PACKED.log 2>&1

Resolve the script path from this packet when launching. No Git, network, catalogue preparation or original full replay is permitted inside the process. The internal580-second alarm leaves cleanup/receipt time before the hard600-second process cap; heartbeat output reports phase/counts every30seconds. No automatic retry or budget increase follows a timeout or finding.

The current source Linux full success is452.68seconds for three Tensor calls. A naive2/3 estimate would be301.79seconds, but fixed setup/reference/CRT work, differing inputs and machine variability prevent treating that as a forecast. Use a provisional **300–500second** planning envelope and one600-second cap. The complete result may still time out; retain partial call counts, logs and arrays without a conformance claim. The historical600-second timeout remains evidence of variability, while SOURCE-STATUS-UPDATE.md records the later successful source run.

Before and after, authenticate every consumed public source and the unchanged candidate. Pin the harness's own SHA256 and require it unchanged. Any source, candidate or harness drift forces FAIL and nonzero exit, even if all endpoint assertions had passed. `FULL-PACKED-RESULT.json` retains expected arrays, actual child returns, stage hashes, exact call counts, all controls, diagnostic difference and scope. A timeout/failure is not permission to modify the frozen candidate or try another fixture within this process.

The static harness has not been imported or run; no complete numerical call has been scheduled. Independent static review owns the final gate. Credit and predecessor notices remain in CONTRACT.md and the pinned source package.
