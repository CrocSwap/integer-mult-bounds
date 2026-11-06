# Abstract derivation of the retained-record inverse

## Verdict, role and exposure

**Verdict: the supplied whole-record inverse implication holds under the exact value, operation, rounding and record hypotheses below.** It is a reached-state injection/inverse statement, not an unrecorded rounded-map inverse, clean erasure or a hardware permutation theorem. The actual PR6546 implementation still has to be bound to these hypotheses after sealing.

The coordinator supplied the target behavior for this external review of PR6546: integer-grid field arrays, fixed retained seeds, additive translations, restricted SCALE cases, native-layer compositions and chronological structural records. No current6546 PROOF/sampler file or current peer draft was opened for this assignment before sealing. Historical source familiarity is not excluded, and the statement was known: no blind-discovery or never-exposed claim is made. The source's existing caller/error/inverse/bill/count results retain their credit.

No source/new scientific program, import, compilation, constructor, NumPy operation, numerical experiment, census, kernel or native operation was executed. This note establishes no new numerical constants, field/event counts, all-width machine representability bound or source replay outcome. Only a written derivation and metadata seal were authored.

## 1. State, records and exact arithmetic domain

Fix a positive integer width N. A live field is a value in Z^N; the state is a finite ordered collection of live fields with exact slot identities. Arbitrary signed values and arbitrary dirty destination values are permitted. Fields have value semantics: changing one field cannot silently change another or a saved record through array aliasing. All arithmetic in this abstract argument is exact integer arithmetic. A common grid unit can be suppressed by storing integer cell counts.

The word is fixed and finite. Instructions, indices, coefficients, structural ownership restrictions and per-instruction seed identities are known and valid at their respective live-field layouts. In particular a read source and write destination in ADD are distinct; operations do not use a field that is not live. Structural operations insert/remove only slots authorized by the grammar, without overwriting an unrelated protected owner. If the source grammar requires stack-last helpers, fresh names or further unit restrictions, those are additional conditions, not consequences of this abstract identity.

Each seed sigma specifies a deterministic rounding function for the fixed width/coordinate convention. Regeneration means the same function, shape, ordering and algorithm, not merely the same integer seed passed to a different RNG or a different draw schedule. Seeds and other record data are retained unmodified. No randomness or fairness is required for the algebra once these values are fixed.

Each forward instruction may append a record carrying its tag, slot/coefficient/seed identity as needed, and the stated saved values. The instruction word may supply some of this metadata, but an inverse must bind each consumed record to the corresponding instruction. A saved array means its exact prior value, not an alias subsequently mutated by the forward computation.

## 2. Additive rounded translations

Let s and d be distinct live slots and define a deterministic integer increment

    f_(I,sigma)(X_s) in Z^N,

which can include exact multiplication by an instruction rational followed by seeded rounding. It may depend on the source, fixed instruction parameters, coordinate convention and sigma, but not on the dirty destination or unretained mutable state. Forward ADD is

    X'_d = X_d + f_(I,sigma)(X_s),
    X'_s = X_s,

with every other live field unchanged. Its inverse, when that same source value and function are available, is

    X_d = X'_d - f_(I,sigma)(X'_s).

No old destination snapshot is required because this is a translation of the full integer lattice, valid for arbitrary signed dirty X_d. ADD inversion does not require the rounding function itself to be injective or unbiased. It does require exact regeneration of the same increment; “round the negative source” is not generally equivalent to subtracting the original rounded increment.

The source/destination distinction is important. If they are the same slot, the increment can depend on the value being replaced; the operation is no longer the displayed translation and may be many-to-one. Nor may a target-dependent or stateful rounding function be silently substituted into this proof.

## 3. Fractional SCALE with numerator plus or minus one

Let the SCALE coefficient be epsilon/D, with epsilon in{+1,-1} and D a positive integer. Work coordinatewise and write z=epsilon*x. A forward operation chooses an exact signed-division decomposition

    z = D*q + r,    q,r integers.                           (1)

It retains the actual r and the seed needed for its rounded output. A conventional Euclidean choice is0<=r<D with q=floor(z/D). A truncation-toward-zero quotient and signed remainder is also an admissible representation if (1) is exact, the actual r is retained, and the rounding correction below follows the same convention. The proof does not confuse a negative signed remainder with an unsigned Euclidean one.

Let rho_sigma be the deterministic rational-to-integer rounding function used by this SCALE, with the necessary integer-translation property

    rho_sigma(q+t) = q + rho_sigma(t)

for integer q at the relevant fixed coordinate. Ordinary seeded floor/ceiling rounding with the same coordinate draw has this property in exact arithmetic. It is an explicit hypothesis; deterministic behavior alone would not imply it.

Define b=rho_sigma(r/D). The rounded forward result is

    y = rho_sigma(z/D) = q+b.                              (2)

The retained r and sigma regenerate b, so the inverse is

    x = epsilon * [D*(y-b)+r].                             (3)

Indeed (2) recovers q=y-b, and (1) then recovers z. Since epsilon^2=1, (3) recovers x exactly. This also covers negative x or negative z. With Euclidean residues b is usually a0/1 correction; with a signed remainder b may be negative. The algebra requires the correct integer b, not an assumed Boolean for every convention.

For an array, apply this identity to every coordinate with its retained residue and exactly regenerated per-coordinate draw. The retained seed may compactly specify all draws, provided the source implementation's indexing/replay contract really does so. Alternatively retaining the actual correction array b would also suffice mathematically, but that is a different record and must not be attributed to a seed-only implementation without inspection.

The residue alone is not enough: the same y,r can correspond to different q depending on the rounding correction. The seed alone is also not enough to recover discarded residues. Both retained components, or an explicitly sufficient alternative record, participate in the inverse. No assertion is made that a generic fractional numerator other than+/-1 is supported by this instruction grammar.

## 4. Nonzero integer SCALE

For an integer coefficient a!=0, forward SCALE is y=a*x. On its reached image, every y coordinate is divisible by a and exact division gives x=y/a, including negative a. This is an exact-division identity; applying a rounded or floating reciprocal is not the same inverse.

An actual implementation may rely on reached-image divisibility rather than check it at a public interface. That can be sufficient for this inverse theorem but does not validate arbitrary forged arrays or corrupted records. Coefficient zero would require retaining more information and is excluded here. The overlap D=1, epsilon=+/-1 is consistent with both SCALE cases.

## 5. Structural operations preserve lost information in the record

### COPY

Let a permitted COPY replace destination field d by source field s. Retain the exact old destination value A=X_d before replacement. The lifted result includes that record. Its inverse restores A to d; it does not need to infer A from the copied source or from the new destination. The source and other slots are not modified by the replacement under the value/aliasing premise. If the source grammar requires distinct slots, that restriction remains; no broader input API is inferred.

### CLEAR

Let a permitted CLEAR remove a live field at a known slot. Retain its full popped value and insertion position, unless the fixed word uniquely determines that position. Inverse CLEAR reinserts that exact field in that exact position, restoring slot order and live-field count. The value may be dirty or a rounding residual: recording it supplies information that plain deletion would lose.

If the source grammar defines CLEAR only for a field proved zero, that adds a domain restriction. Conversely, an inverse that saves a nonzero popped field has not physically erased that information; it moved it into the record. Neither interpretation is a free owned-scratch cleanup theorem.

### INIT

A permitted INIT inserts a new zero field in a fresh/authorized position. It must not silently overwrite a prior owner or existing dirty slot. Its inverse removes that same slot only when its current value is **exactly zero**. On the reached chronological inverse path that zero follows from undoing every later instruction that touched it, not from an approximate norm bound or a rounding tolerance. The shape and structural layout must be restored before any earlier instruction uses its indices.

These operations are inverses on their specified lifted state/record image. They are not bijections of an unrecorded fixed-size array state space.

## 6. Native compositions and the chronological word inverse

A native layer can inherit this algebra if its actual algorithm is an explicitly ordered composition of these deterministic recorded primitives, or if its backend has a separately established same-seed exact inverse on the reached integer-grid state. It is not enough that its ideal real matrix has a formal inverse. Rounding a general matrix product and then applying a rounded real inverse need not undo it.

For a native composition B_l ... B_1 with its actual retained records/seeds, invert in order B_l^-1,...,B_1^-1. Each primitive must receive the same restored source value and exact record it had at its forward boundary. Reusing a seed under a changed shape, primitive order or draw schedule is not this contract. If the source offers a single native inverse function, post-seal code review must bind it to that ordered/same-seed property rather than infer it from the function name.

For the full instruction word I_1,...,I_M, let X_j be the field state immediately after instruction j and let R_j be its accumulated record prefix. Each local lifted map satisfies

    Inv_j(X_j,R_j) = (X_(j-1),R_(j-1))                     (4)

on actual forward outputs, using the correct instruction/tag/layout. Begin with the complete reached final pair (X_M,R_M). Applying (4) at j=M yields exactly the preceding pair. Induction down j then restores every intermediate boundary and finally X_0,R_0.

This reverse-order induction is what justifies the ADD source premise: by the time an earlier ADD is undone, every later change to its source has already been undone. Likewise COPY/CLEAR/INIT layouts and saved values are restored before earlier records need them. No commutativity of rounded updates is assumed.

Consequently the complete lifted forward map is injective on its legal input domain: equal complete final state+records would have equal decoded initial states. The inverse is exact on the reached image. It need not define a valid inverse on arbitrary modified arrays/record streams, and it does not imply that the projected final fields alone are injective. Records can retain seeds, residues and complete old fields; they are part of the information budget.

## 7. Representation, randomness and physical boundaries

The proof is parametric in positive N as an integer-array identity. It is not an automatic theorem for arbitrary-width fixed-word NumPy arrays. Actual dtype ranges, intermediate products/shifts, floor/division semantics, seed expansion, array copying, shapes and index bounds must implement these exact operations without overflow, floating approximation or aliasing. An explicit source precondition or independent representation proof is needed; a few finite examples would not establish every-width safety.

Freshness/unbiasedness assumptions belong to a forward stochastic error or sampling analysis. They are unnecessary for the deterministic inverse once the actual seeds/draws are fixed. Conversely, exact same-seed inversion does not establish independent fresh randomness for a repeated forward call, a distribution conditional on retained records, or an error bound. The record may reveal the lost residue and the output history. It is not automatically a clean or reusable entropy resource.

The claim is not a full hardware permutation, an owned-erasure proof, native admission or a physical inverse-price theorem. It leaves actual array representation and the forward caller/error/bill/count claims to their source scopes. No numerical charge constants or path counts are recomputed here.

## 8. Discriminating written controls — all UNEXECUTED

1. **A different seed on inverse ADD.** A half-grid increment may round to0 under one seed and1 under another. Adding the first and subtracting the second changes a dirty target instead of restoring it. The seed identity is not optional.
2. **Round the negative instead of subtracting the same draw.** Ties or asymmetric deterministic seed rules can give rho(-t)!=-rho(t). The inverse must subtract the retained forward increment, not request an unrelated rounding of the negated rational.
3. **Undo in forward order.** Start with fields x=1,y=0,z=0; add x into y, then y into z. If y is undone first, the later inverse reads y=0 and leaves z=1. Reverse chronological order restores z before changing y.
4. **Drop a fractional residue or its correction.** For D=3, x=2 has q=0,r=2; a seed rounding upward gives y=1. Formula D*y+r without subtracting the actual correction returns5, not2. The correct record formula gives3*(1-1)+2=2. This is hand arithmetic, not a source case run.
5. **Mix signed division conventions.** For a negative numerator, substituting a positive Euclidean remainder while keeping a truncation quotient can violate z=Dq+r. The record must retain the actual consistent decomposition; sign flags alone do not repair an inconsistent pair.
6. **Allow nontranslation-equivariant rounding without another record.** A rounding choice depending on the unretained integer quotient can make the same y,r,seed arise from different q. Determinism alone then fails to justify(3). The implementation must establish the stated covariance or retain the missing correction information.
7. **Use an overlapping ADD source/target or erase with SCALE0.** Both can be many-to-one without the missing prior value in a record. The distinct-slot/nonzero-unit grammar is a genuine hypothesis, not a cosmetic index convention.
8. **Save a view or discard structural records.** A saved COPY destination aliased to a later-mutated array is not its old value. CLEAR without the popped field loses dirty data. INIT inverse accepting a nonzero slot silently deletes information. Exact snapshots and reached zero are different obligations.
9. **Infer hardware cleanliness from reached-state decoding.** An inverse can restore visible fields while its retained log still contains residues, seeds and old arrays. That is not record erasure, fresh randomness, a bounded physical workspace or a total inverse on corrupt packets. Dtype overflow can also break the abstract integer identities even when the operation names match.

These are deductions about weakened hypotheses, not executed mutations, source defects or newly observed numerical failures.

## Credit and post-seal binding

PR6546 retains its existing complete stochastic numerical caller, retained-state inverse, error analysis and bill. Prior inverse/rounding/native/compiler work and actual6096 applicability remain credited in their respective scopes; no global missing-caller claim is made. Ordinary translation inverses, exact quotient/remainder reconstruction and reverse-order composition are classical algebraic principles, not new methods.

Post-seal review must bind the actual instruction grammar, distinct ADD operands, SCALE domain and residue convention, seeded integer-translation property, native same-seed implementation, snapshot semantics, structural ownership/zero checks and finite-array representation limits. Until then this is an abstract target-known derivation only, with no current source proof/code acceptance. Human/formal-kernel acceptance, all selected assumptions, physical costs and the selected frontier remain unchanged.
