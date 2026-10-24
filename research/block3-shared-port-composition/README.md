# Chronological shared ports and exact rank-three fusion

Four actual three-call ports and one two-call closing port from #4743, placed on the five shared banks proposed in #4813, admit **four chronological rank-three fusions**. The emitted paid profile is **two rank-one plus four rank-three children**, with 24 monomial passes and ten scalar ADD passes. Both raw and fused words are retained in WORD.json. This is a construction of a coupled, all-input reversible interface, not five independent rank-three targets or a new κ.

The chronological endpoint is explicit. Set A=C0, D=J W C0, B=D(P+2Q)A, F=A(P+2Q)A, u0=x0 and u_j=D x_j+B u_(j-1) for j=1,...,4. The five outputs are

    (A² x0 + F u4, A u1, A u2, A u3, A u4).

Consequently the final output on bank0 has the rank-zero diagonal A², while its incoming term contains dependent information. None of the other four outputs is automatically an autonomous job on its original input. The first two ports alone output `(A x0, A D x1+A B x0, D x2+B D x1+B² x0, x3, x4)`. The shared bank entering port2 is its actual dirty current value.

## Complete optimistic screen and stopping rule

Grant, optimistically, that a free completion recovers all five independent K jobs. At C in [0,1), the best resulting recursive moment of the fused profile is

    M_opt(C) = 5*3^(1-C) - (4*3^(1-C)+2) = 3^(1-C)-2.

This only grants construction headroom: free completion remains unproved. Any additional rank-one child gives `M <= 3^(1-C)-3 <= 0`, strictly negative for C>0, even before finite work. Thus this exact profile cannot fund even one additional ordinary rank-one completion call while claiming all five jobs. A valid next improvement needs a zero-recursive-call completion, a reduction of the existing bill, or a different independent target inventory. This is a scoped moment ceiling, not a universal circuit lower bound.

A literal copy-and-reset alternative that forces each port to see its original input costs23 rank-one calls before cleanup:14 port calls plus four D^-1 resets at two calls each and one A^-1 reset before closing. It saves five output fields, whose final restoration is additional. The price23 describes this fixed policy; it is not a bound on all changed compositions or on a caller using differently sized recursive children. A single-bank monomial/Gaussian reset path needs at least2 and1 rank-one calls respectively, by column-support4 and2. Split-register decoders fall outside that lower-bound domain.

## Exact implementation and verification

The primitive word maps and restores source P/Q before each ADD, preserves both dirty banks, and carries every phase. A raw inverse transpose is emitted gatewise in the **same chronological order**: a unitary single-bank gate G becomes conjugate(G), while `dst += c*src` becomes `src -= c*dst`. A separate reverse traversal uses inverse primitives. No Hermitian transpose is substituted for the raw inverse transpose.

The four fusions each replace an actually adjacent pure-word segment `A D` by `N K`, where `N=A D K*` is verified to have one entry from {1,i,-1,-i} per row and column. This is a pure-word identity and therefore tensorizes before any addition. The emitted fused word has the same all-width block identity as the original word. In particular B_f is `M_f C2_f+2 K_f a_f`; the verifier never tensorizes the sum B_1.

Finite replay checks all40 input basis columns and one dirty vector at width1; fourteen basis columns and one dirty vector at width2. The independent endpoint recurrence, literal inverse and raw inverse transpose are checked, including all1,600 bilinear inverse-transpose entries at width1. Source Gaussian arithmetic/letters are reused with explicit attribution; the chronological emitter, fuser, interpreter and endpoint recurrence are new. This is a written block-algebra proof with finite corroboration, not a formal proof-kernel certificate or all-width inference from finite tests.

```sh
python3 -I -B research/block3-shared-port-composition/verify.py
python3 -I -O -B research/block3-shared-port-composition/verify.py
python3 -B scripts/research_package.py --package research/block3-shared-port-composition
```

Expected: `PASS_BLOCK3_SHARED_PORT_COMPOSITION`. The mutation checker rejects a changed retained-source byte, an actually corrupted serialized raw-dual ADD sign and a false κ receipt in separate optimized subprocesses. The copied source bytes are preserved with local `-text` attributes. Owned address/permutation workspace and all scalar/routing/precision costs stay separate. Source #4743 gives ordinary native realizations and bounded-word precision for each port; composing them requires the applicable full internal-cut error bill. This package gives exact array-pass counts and recursive costs, not a priced machine-level compiler or multiplication theorem.

## Provenance and overlap

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision7. #4813 head `f982ecc06826e7087e69b9468d3ff52589fd0822`; native #4743 head `158048812f4e0aeb132408f4d7cda57ba008b0d5`; bound context #4628 head `ee4fd87f064017c23e5a86fc1dcfe0a5237caed3`. Five exact source files, original blobs/hashes and immutable URLs are retained in ORIGINS.json. No cached unmerged commit is needed for scientific replay.

Live PR-body searches `4813 chronology`, `"shared" "port"`, and `"block3"` were checked at this round. Neighbours include #4828's two-bank norm result, #4835's address-algebra kernel, and #4703's different complementary supplier. This contribution emits the actual shared-bank chronology and a different-size-child fusion; it does not repeat their results or the earlier complete-cascade conditioning audit. Fresh #4841 (`6debdcdac8fe1c87958f8cd42ccb7db73c0a0eef`) was also read: its general changed-chart compiler and compensated retiming do not emit this particular five-bank word, fusion or completion screen. It independently notes that #4813/#4818 inversion checks do not yet establish a priced supplier. Full unpublished work and exhaustive Discussion novelty are unclaimed. Parent coordinates public handoffs and pre-submission refresh.

## Open next questions

- Can the explicit coupled endpoint be converted into five independent K outputs with zero additional recursive calls and all work fields restored? Start from WORD.json and the exact endpoint above. Any additional rank-one call fails the stated moment screen unless another cost or reward changes.
- Can an alternative ordering or interface remove one of the two remaining rank-one calls while retaining every independent input? Test an actual emitted word and its raw dual; a new ideal observation matrix is insufficient.
- If a profitable complete endpoint is found, bind native movement, storage, precision, complete caller, compiler reserve and outer transfer before claiming any κ gain.

Prepared for Chris R / Clear1nsight with substantial OpenAI Codex assistance, Apache-2.0. Credit Dugongue #4743 for actual all-input ports and native/precision theorem, Yiyang/Lyy-iiis #4710 and lee-phys #4688 for residual and phase lineage, hexapode #4813 for the proposed five-bank cascade, and Jacob Alan Sussman #4628 for the all-width small-unit model and scoped bounds. Existing notices are retained.

## Completion addendum: the fixed producer fails the free-decoder gate

The original construction, WORD.json, RESULT.json, proof, raw inverse transpose
and retained inputs above remain byte-for-byte unchanged at PR4856 head
`0970de4ec97fc942e6202403ffd7586d19559391`. The new `completion/` subtree
answers the previously open zero-recursive-call completion question for one
explicit decoder alphabet; it does not change the native word or claim a new κ.

For the fixed five-bank producer, allow arbitrary rectangular linear pre- and
postcontrollers over the full monomial Clifford algebra of a fixed finite
one-column gate group. This includes cross-output ADD, Gaussian-dyadic scalars,
owned clean buffers, linear copying, dropping/resetting work fields, and saved
original-input identity bypass. Free controls act before or after this one
producer. Prefix taps, new interleaved gates, changed producer words,
nonmonomial transformed helper resources and arbitrary non-columnwise address
operations remain outside the result.

The exact group-algebra expansion binds **all 25 blocks** of both actual raw and
fused WORD.json schedules, retaining absolute phases and keeping scalar2 outside
tensor powers. Its grade3 projection has zero first row and first column and a
lower4-by-4 triangular block with unit AD diagonal. Its image from the regular
monomial input module has dimension exactly `4*dim(B_f)`. Rectangular free
pre/postcontrollers and identity/clean bypass cannot increase this dimension;
five independent rank3 Gaussian targets require `5*dim(B_f)`. Hence this
completion is impossible even with clean copy/drop/reset buffers. A separate
rank0 witness also excludes invertible free controllers with restored dirty
identity scratch.

This closes more than the all-five-K target request. Among any five independent
pure Gaussian targets of ranks at most3, at most four can have rank3. With
`t=1-C`, the best optimistic reward and unchanged paid bill satisfy

    reward <= 4*3^t+2^t,
    paid = 4*3^t+2,
    moment <= 2^t-2 <= 0,  0<=t<=1.

Thus a lower-rank fifth output also fails the strict recursive moment gate.
Granting all five rank3 rewards and paying one extra H1 would likewise give
`3^t-3<=0`. These bounds precede every finite movement, precision, compiler and
outer reserve. No positive κ or new admitted supplier follows.

[completion/PROOF.md](completion/PROOF.md) gives the self-contained all-width
proof using the finite-phase central-character quotient and separating tensor
powers. It permits width-dependent scalar coefficients within the same fixed
columnwise alphabet and does not extrapolate one-column matrix sums. The proof
credits the projection/faithfulness lineage of PR4920 at
`7eb4ef5251f7ba96c7e5d78c42fc98e66b7be4ba` as a citation; no PR4920 file or Git
object is required for this replay. The source construction and its predecessor
credit above are retained.

```sh
python3 -I -W error -B research/block3-shared-port-composition/completion/check_grade.py
python3 -I -O -W error -B research/block3-shared-port-composition/completion/check_grade.py
```

Both default runs are read-only. They authenticate six exact PR4856 source files,
replay raw/fused schedules in the group algebra, verify the grade0 witness and
grade3 rank structure, and compare the frozen completion receipt. Actual wrong
ADD-sign and omitted closing-A mutations fail the endpoint binding. The original
native/inverse/raw-dual sciences remain separate and are still registered.
Independent agent review is disclosed in the completion audit records; there is
no independent human or formal-kernel acceptance claim.

The historical first open question above is now closed within this decoder
model. The next useful construction must change the paid native word, target
inventory or an actual available nonmonomial resource; alternatively it must
specify a different prefix/interleaved interface outside this pre/post model.
Name the real chronological operation and complete bill before extending the
search. Refining conditioning or repeating free completion of this unchanged
producer cannot remove the stated rank obstruction.

`completion/HANDOFF.md`, RUNS.json and the audit records preserve the producer's
original local checkpoint byte-for-byte, including its historical outputs-only
status and output-directory paths. Use the package-relative commands in this
README for published reproduction. Current publication and hosted-CI status are
tracked in the existing [PR4856](https://github.com/CrocSwap/integer-mult-bounds/pull/4856);
the archived local handoff does not report their current state. The parent owns
the public handoff and PR description update.
