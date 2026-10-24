# Independent postrun review: completed reduced packed caller

**PASS for the recorded finite staged endpoint and declared lifecycle controls. The observed integer is 0; the true product is 43113955509404415; observed minus true is −43113955509404415.** The 64 returned zero bits match the reduced staged reference. They do not recover the true product, establish production accuracy or support an integer-multiplication claim.

The constructor's single authorized replacement completed in **781.405280 seconds** with two complete Tensor calls and three complete CRT calls. This review did not rerun that process, import the numerical cohort, construct an owner or execute an operator. `check_postrun.py` performs only JSON/hash checks and independent host-integer calculations over captured actual arrays; it completed in about 0.21 seconds. Its status is `PASS_INDEPENDENT_POSTRUN_STAGED_EVIDENCE_REVIEW` in `POSTRUN-CHECK-RESULT.json`.

## Exact evidence binding and preservation

| Evidence | SHA256 |
|---|---|
| FULL-PACKED-ATTEMPT2-RESULT.json | `01e85556753356dbcced9a43116b67cb6d9ea34126f5ef987821f23c06aab2b8` |
| FULL-PACKED-ATTEMPT2-CHILD-CHECKPOINT.json | `daa909a832d5b494716273cc2fefbdb525ddf3865d1c61a4877c8725f9dacfbf` |
| FULL-PACKED-ATTEMPT2.log | `0092b0e2fcd39723631273fe9b97bbeff11215ab12d21a5701f96bae708e8322` |
| FULL-ATTEMPT2-REPORT.md | `18af0487a87b1c21d18573c2a957a25d60dc7c4d52b0f5254f07171e06807728` |
| Executed run_full_packed_attempt2_DRAFT.py | `c7bb6a705f42469709995f7d8a4c29ab0c12764d744546508a443151ec0345dc` |
| Candidate packed_sandwich_DRAFT.py | `5dfcdfe63d9d03a89a00dd92e681ab0a0efc5bbc86aa7edae58f007baf752483` |

All entries in the author's FULL-ATTEMPT2-FREEZE.json match current bytes. The receipt's before/after maps are equal, and this review independently rehashed every listed current file: **83 staged source files plus the candidate**, 84 entries total. The executed harness also matches its reviewed hash. The cached packet remains the pinned p48 (5,7) source asset; no new coefficient preparation or source/operator modification appears in this evidence.

All eight first-attempt original artifacts and their frozen copies retain their recorded hashes. That attempt remains the **580.390962-second deadline-triggered FAIL**, including inherited scratch-lease and marker-erasure cleanup errors. This normal-return success neither repairs that interruption failure nor converts its missing observations into retained data. Prior static/optimistic-budget artifacts were left unchanged.

## Durable actual records and independent arithmetic

The completed-child checkpoint and final receipt have exactly equal Tensor/CRT observation lists and actual product bits. Each actual child return contains a valid bit array of the prescribed full length; its independently recomputed SHA256 matches the stored return hash. The five child returns have lengths **3500, 3500, 3500, 3500 and 3010 bits**: 35 complex records with two 50-bit components for both Tensors and both forward CRTs, then 35 signed 86-bit records for inverse CRT. Both captured forward-CRT inputs and the inverse-CRT input also have matching hashes and exact lengths. The two forward/opposite completion messages appear once each in the log, consistent with two completed durable Tensor returns rather than merely two dispatches.

The signed codec was checked from the authenticated nested source as data: `ring_check_words.word_bits` emits low bit first, and `ring_words.read_signed`/`write_signed` use width-bit two's complement. These were read through the frozen expansion→core→word→ring archive chain, not imported. The host checker independently decodes/encodes that format.

1. From the captured actual forward-CRT inputs, it reconstructs exact p48 ingress for the two independent b8/q4 streams `[255,0,3,17]` and `[1,254,0,9]`, padded to 35 records. It independently applies the source CRT map `k -> (k mod5,3k mod7)` and checks all actual returned records, including zero imaginary parts.
2. It packs the two **actual** CRT returns as u+i v, checks the actual forward Tensor input hash, and verifies its strict half-disk bound. The captured forward H contains 28 nonzero complex records and matches all 35 frozen staged-reference records.
3. It computes JH from that actual H by `(-i mod5,-j mod7)`. For each actual pair H=(a,b), JH=(c,d), it independently uses the four split operands `(a+c,b-d,b+d,c-a)`, verifies signed 51-bit headroom, forms the exact complex product, and truncates once toward zero by **50 bits**. This reproduces every actual product record and the product SHA256 `8697b1e5d265b236653847496b582ca5138709522dca434bf83b51a5c4b69382`. Its algebra is independently checked against the author's squared-difference formula. All 35 product records are nonzero.
4. It verifies that the actual opposite Tensor input hash equals this actual product, and checks its half-disk bound using exact integers. The maximum squared-norm numerator is `134891816039001096192` on denominator `2^96`, well below 1/4. The actual opposite return is **35 complex zeros**, matching all frozen staged-reference records.
5. From that captured actual opposite return, it independently applies S², shift 2b+4=20, nearest p48 rounding, inverse CRT and the 64-bit carry output. All 35 recovered/inverse-CRT coefficients and all 64 output bits are zero. Reconstructing the true radix operands separately gives 43113955509404415, preserving the exact mismatch above.

The actual J bank was compared record by record during the run by the reviewed observer. It is not separately retained as another raw physical bank in the receipt; the independently reconstructed J of captured H matches the recorded expected J, and the actual product is durably retained. This distinction does not create an additional captured-child claim.

**The zero opposite is a material discrimination limitation.** This run executes the original recovery and carry code, but a zero input to recovery cannot dynamically distinguish missing S, doubled gamma or many orientation/sign changes. The source normalization identity and exact code path retain their prior static/mathematical support; this fixture supplies no new nonzero recovery-normalization test. The four whole-stage mutation controls remain explicitly unrun. No new model/Tensor replay was performed by this reviewer to extend that scope.

## Lifecycle and finite bill

The exact executed harness reaches PASS only after its assertions for successful normal closure, idle child owners, empty parent live pool, pending return, restoration of both payloads/catalogue and b/q metadata values/heads, end-head pending rejection, paid consume, post-consume production-policy rejection and resident empty origins. The corresponding receipt flags are true. This review verifies their binding to the unchanged executed harness; it does not inspect terminated in-memory Tape objects or claim new exhaustive dynamic coverage.

The runtime preflight controls cover six metadata-to-payload aliases and five descendant-private aliases, plus the retained constructor rejection cases. Other port coincidences remain statically excluded by the preserved five-distinct-port predicate. The separate injected failure occurs **before the first original Converter numerical operation**, while the parent holds its first ingress bank. It adds one injected dispatch and zero numerical children, then verifies its declared parent/borrowed/metadata cleanup. It does not validate arbitrary exceptions inside an active numerical child or resolve the first attempt's deadline cleanup failure.

Recorded counters are consistent with the fixed path:

| Counter | Recorded value |
|---|---:|
| Complete Tensors / CRT conversions | 2 / 3 |
| Packed records / J axis passes | 35 / 2 |
| Product passes / split records | 1 / 35 |
| Split signed operations / parent-declared real products | 140 / 140 |
| Each Tensor: padding, gathers, halos | 4, 4, 4 |
| Each Tensor: expansion, compression, assembly axes, chirps | 2, 2, 2, 1 |
| Each CRT: global routes, triangular shifts, padding passes | 1, 2, 2 |
| Each CRT router: batches, edges, involutions, literal | 1, 3, 2, 1 |

Parent counters are not a new independent meter of every nested physical primitive. The declared 30,200 J-loop source moves and 7,000 writes, and 70 width-86 recovery products, remain source-derived finite bills. They do not include every metadata, setup, storage, reset/clear and Tape transition. Checkpoint/fsync/reference/capture work is experiment overhead. There is no matched three-Tensor baseline here and no complete priced total saving certificate. The earlier method-leaf measurements retain their narrower supplied-bank scope.

## Accepted scope

The evidence supports **one physically executed two-complete-Tensor finite wrapper chain conforming to the reduced staged reference**, with its tested normal lifecycle and precisely declared pre-dispatch failure control. It preserves `require_recovery=False` and default production rejection. It does not recover the true integer product; establish ideal Fourier/production accuracy, all-input correctness or arbitrary interrupted-child cleanup; price a total finite profit; create a recursive Gaussian reward; or improve a compiler reserve, selected bound or κ.

Root requested no additional heavy runs, and none were performed. Review command: `python3 -B outputs/packed-caller-independent-gate-20261023/check_postrun.py`. Original source/candidate/evidence and earlier review receipts were preserved. Credit remains with the source Tensor/CRT/native/word/recovery authors, the packed-caller constructor and prior mathematical/static reviewers. Review/checker prepared with substantial OpenAI Codex assistance; no independent human or formal-kernel acceptance claimed.
