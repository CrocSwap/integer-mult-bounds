# A source-bound physical Core / first-face halo bridge

**Conditional source-bound bridge; no new kappa.** Prepared for **@CubeJerry**
with substantial OpenAI assistance. New code and prose are Apache-2.0.

This package supplies a precise conditional interface between the actual
five-factor finite Core and the source-bound first-face halo consumer of
CrocSwap/integer-mult-bounds#6904. The complete Core is concurrent work, copied
read-only at observed local head `1cfeb78e779d82d80b42f850dcb2bf51dd54f3cf` plus
its then-current exact files. It has since been published at
[`6fb9ab776b7d0956b8bcc2d3cfde0f3034421630`](https://github.com/CubeJerry/integer-mult-bounds/commit/6fb9ab776b7d0956b8bcc2d3cfde0f3034421630).
All 77 retained Core blobs have been compared to that public commit; the one
changed proof paragraph adds an explicit address/width cost guard and no
executable or numerical source changed. [DEPENDENCIES.json](DEPENDENCIES.json)
and [PUBLIC-CORE-PIN.json](PUBLIC-CORE-PIN.json) bind the final bytes. Source
publication does not establish upstream review or the admitted hypotheses.
Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Exact result and why the interface matters

The real Core returns an unnormalized global tensor in little-endian
two's-complement words on a fine grid. The halo consumes the immutable original
input and returns a normalized inverse in big-endian sign-magnitude records.
The existing generic splice cannot be applied by assigning a different
numerical meaning to those returned bits.

For a full field of T=2^n records with component-l1 radius R, the bridge funds
the real Core input radius using `R sqrt(T)`, checks the same immutable original
References and all K complete original-coordinate windows, exactly lifts the
input grid, calls the native Core, and normalizes its entire output once by
`2^U`, where U is the sum of the axis normalization exponents. It then truncates
both components toward zero on the common external grid. The additional
component-l1 defect from Core numerical error and this final rounding is

`E_core = 2^(-t-U) + 2^(1-q)`.

The first term includes the conversion from the Core's global complex
Euclidean error contract. The proof then combines this endpoint with the
previously proved finite-section tail and halo error, without assuming that
the Core normalized every intermediate axis. Details, assumptions and complete
time/space accounting are in [PROOF.md](PROOF.md).

Ten fixed additional tape roles implement the format and ownership seam. If
`F=d+w+(P-q)+(P+U-q)+1`, the full new payload work is O(TF), including protected
return copying, input erasure, source head restoration and primitive movement.
All native Core, source validation/preparation, halo, archive and retained
backing costs remain separately charged. In the admitted conservative source
family F=O(p), so this adds O(V) per balanced group. This is source compatibility,
not a new full multiplication recurrence or a supplier admission.

## Evidence actually executed

| Check | Evidence | Limitation |
|---|---|---|
| Literal codec | 3,936 input/return cases and 160 native extremes against an independent integer oracle; 34 rejection/detection controls | Does not prove all-size source admissions |
| Ownership and cost | No online Tape allocation or diagnostic decoding; ten fixed roles; pending-child failure controls; complete primitive bill for 1 through 64 records; retained blank backing | Identity protocol fixture is explicitly a test double |
| Same-source coordinate binding | Two actual References, 16 admitted original partitions, real halo pages, all 512 original coordinates and 11 adverse controls; finite next-group radius funded | Does not establish production carving of every context |
| Actual native Core boundary | Three dense native calls, 189 events, both sparse native calls, all borrowed source ports restored, all bridge payload erased; independent exact rational inverse oracle | Packed K=1,g=1,L=2 witness, not full first-face geometry |

The real native witness took about 311 seconds and returned
`[(256,-128),(-62,32)]/4096` after normalization by 2 from the exact input
`[(513,-257),(-123,63)]/4096`. Its original rational 2-by-2 Q is coupled and
nonidentity. The source endpoint error is below the proved `65/2048` allowance.
Its scalar interior A is exactly 1; the dense calls execute their full native
words but this finite fixture does not exercise a nonidentity dense interior.
Exact receipts are retained in [evidence](evidence/).

Finite tests exercise the new physical boundary. The universal claim relies on
the written proof and the named predecessor contracts. The selected certificate
and its five foundational assumptions are unchanged.

## Reproduction

Use Python 3.12 and the standard library, from a checkout containing this
package and the exact canonical live inputs listed by the retained Core's
[SOURCES.json](retained/core/SOURCES.json). The existing source archives are
reused; they are not regenerated. The loader checks the frozen retained bytes
and the original source loaders check their canonical inputs. The initial
pre-publication receipts are retained unchanged; the later remote blob check
establishes exactly which public source supplied those numerical bodies.

```sh
python3 -B scripts/research_package.py --package research/core-halo-source-bridge --check-only
python3 -B scripts/research_package.py --package research/core-halo-source-bridge
python3 -B research/core-halo-source-bridge/replay.py
python3 -B research/core-halo-source-bridge/verify_codec.py
python3 -B research/core-halo-source-bridge/verify_binding.py
python3 -B research/core-halo-source-bridge/verify_actual_core.py --output /tmp/core-halo-actual.json
```

Expected final markers are `PASS_CORE_HALO_SOURCE_CODEC`,
`PASS_CORE_HALO_SOURCE_BINDING`, and `PASS_ACTUAL_CORE_SOURCE_BRIDGE`.
The bounded metadata/codec/binding runs take seconds. Bound the actual native replay at 600
seconds; the recorded run took approximately 311 seconds. Diagnostic decoding
belongs only to independent test observers. The actual native fixture retains
the predecessor's q2 root and certified finite metadata-floor specialization,
which is stated explicitly in its receipt.

`replay.py` checks the codec and source binding in normal and optimized Python,
with a fresh bytecode namespace for every child. Add `--physical` to include
the native witness and compare all scientific fields and machine-operation
counts with the retained receipt. Historical publication labels and wall time
are excluded from that equality; numerical, source, ownership and cost fields
are retained. The default replay does not claim a fresh native execution.

The retained snapshot supports replay without relying on a locally cached
unmerged Git object. Source availability, passing fixtures and independent
review have separate scopes; none is an unconditional multiplication theorem.

## Novelty and predecessor credit

CrocSwap/integer-mult-bounds#6880 already supplies the finite-section locality,
factor-two tail and normalized generic splice. The sparse transport, shrinking
numerical halo and their first-face composition are also predecessors, including
CrocSwap/integer-mult-bounds#6904. The ongoing complete-Core package owns its
five-factor caller, real native source delivery, global numerical theorem and
full original-layout wrapper. This package does not reclaim those results.

The new work binds the actual source formats, full-volume radius, original
coordinate families, total normalizer, protected-return lifecycle and complete
added scan invoice. [NOTICE.md](NOTICE.md) and all retained notices preserve
the original contributors. The initial Core audit found no counterexample to
its stated admitted numerical endpoint; it does not certify all Core source
and native assumptions or imply that those foundational obligations are solved.

## Open next questions

1. **Run the complete original-layout Core and real halo at one common
   geometry.** This would expose composition faults outside the packed witness.
   Begin with one dyadic active axis, at least two Core sections, actual kept
   and discarded rows, a period cut and an identity hole. The blocker is the
   larger native run's cost and the requirement to preserve exact source
   admissions; no semantic Core test double should be counted as that run.
2. **Discharge all production-context admissions.** A tiny admitted interior
   demonstrates a finite exact source boundary; it does not prove the carve
   density or the empty-interior cases. Start with a classified original-window
   family and the exact same Reference's source-address pattern. This remains
   within the broader compiler/analytic obligations.
3. **Fund outer-group and final recovery scales.** The next actual group needs
   the accumulated radius and grid; final recovery pays the inverse of every
   normalization. Start with the frozen outer Gaussian/tensor/FFT interface
   and substitute the complete error and setup bills here. This package does
   not yet supply that global recurrence or ideal-transform comparison.
