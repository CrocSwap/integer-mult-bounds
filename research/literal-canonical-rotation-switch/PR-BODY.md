## What changes and why it matters

Nick Petalas's #7504 proves how to query a bit of the precise canonical
padded-rotation Beneš network without constructing its ROM. Its first open
question asks for a literal fixed-tape implementation with encoded inputs,
an owned Boolean return, preservation and complete costs. This package
implements that interface.

## Exact result

On the explicit binary ABI, one input-independent program has2096 locations
and14 tapes. For every legal h,s,a,j,x it returns the original canonical
row-j bit at the **current wire address x**, with complete time at most
`1024(h+3)^2` and additional historical backing at most`16(h+4)` cells.
It preserves five borrowed descriptors, returns every head, clears eight
private bodies and retires their guards, leaving one owned output bit.
Domain and length validation precede identity shortcuts. The graph uses
only fixed-symbol reads/writes, unit moves, fixed jumps and halts.

The formulas and child closure belong to #7504. The new result is their
literal physical lowering and ownership/cost proof. The original #4100
canonical compiler supplies expected table bits independently of the new graph.

## Verification and reproduction

Base: `e54523517d0f03e58352e647c403a5af3e525a57`. Exact source commits,
Git blobs and SHA256 pins are in SOURCE-PINS.json. Originals/notices remain
unchanged. Normal and optimized warning-strict primary results agree.

```sh
python3 -B scripts/research_package.py --package research/literal-canonical-rotation-switch
```

Primary checks include1566 queries covering49 full networks through h3,
all544 h5,s17,j6 entries,13 malformed/domain rejections, three detected
child/parity graph mutants, an owner-alias rejection and full-depth cases
through h129. Every call checks borrowed bytes, heads, private capacity,
guards, exteriors and historical spans. Universal correctness rests on the
written induction and emitted-loop counts, not these finite fixtures.

## Limits and kappa status

**No new kappa. All five selected foundational assumptions remain.**
The supplied binary ABI and initialized disjoint working windows are explicit.
Current CRT offset production, serialization, source transport, current-wire
payload updates and the full exceptional-key caller are not installed.
Repeated queries retain their complete quadratic bill and require comparison
against amortized ROM reuse. The544 separately supplied fixtures are not an
uninterrupted caller or a global speedup claim.

## Credit and AI assistance

Prepared for @CubeJerry with substantial OpenAI assistance. Credit Nick
Petalas #7504 for the arithmetic construction, Cinna Davis / 1337isnot1337
#4100 for the canonical compiler, ToikY #4192 and JoyboyBrian's ROM/current-row
lineage. #7388 and #7390 remain distinct caller/sort work. Original notices
and Apache-2.0 license are retained. No independent human or formal-kernel
acceptance is claimed. Full proof, receipts and open interfaces are packaged.

## Independent review

A separate reviewer reproduced universal arithmetic, cleanup, source-loop time and history bounds, then checked the frozen graph through an independent sparse interpreter and parity-union-find canonical-network oracle. All1566 small and544 required row queries pass. A child-parity mutant returns a wrong bit while restoring every head and private cell. Normal/optimized receipts agree. REVIEW.md, INDEPENDENT-RESULT.json and SOURCE-CHECK.json contain the exact evidence. This is model-assisted review, not human or formal-kernel acceptance.

## Publication checks

All four canonical registered commands, exact six-file origin comparisons, committed bytes/modes, whitespace and official export/input integrity checks passed. The full-history check is unavailable in the shallow checkout; no pass is claimed. PUBLICATION-CHECKS.json records exact local evidence. No hosted CI or independent human/formal acceptance is claimed.
