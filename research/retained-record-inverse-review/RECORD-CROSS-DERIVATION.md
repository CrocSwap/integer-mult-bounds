# Post-seal source binding of the retained-record derivation

**Verdict: qualified PASS for the actual fixed-source producer/ledger/caller path and valid Python-integer field representation. No material record-inverse gap was found.** The source's record convention is not literally the unshifted residue notation in my abstract draft; that distinction is resolved explicitly below rather than changing the sealed draft.

My target-known first draft remains SHA256 `0897e63208288b5b0303a92d638467fd4fce23f5ebe60ec49323223e333a3407`. After both seals I read actual `INPUTS/{sampler.py.txt,PROOF.md,produce.py.txt,verify.py.txt,ledger.py.txt}` and peer `RECORD-CODE-DRAFT.md`, provided SHA256 `be6e2c8c9c6c272da7a6718699705c11ba80a34c00c6fcb549a0f40a99fd2b6b`. No first note/seal, source or package was edited. No source/new scientific program, source-word scan, NumPy import/install, constructor, all-column test, numerical experiment, mutation, census or kernel was executed.

Source: Ali Romman's PR6546 at `ff038070b8d122a43993f2b2524154323cc6b4d7`, `research/selected-absolute-stochastic-caller/`. Source pins identified by the peer are sampler `2f7ba4b7d01213beb2a3b070658617ff992e715e`, PROOF `178000008b30144cf607dabd0d1759056fd4a644`, producer `5ed6163e903da47268a3ca44786126e6e978dff6`, ledger `728b2901176f11de2958c0e296061755b7305727`, verifier `aea6fd3df8b1d666cf963ce1e338a0a4074035aa`. This note statically binds the coordinator-authenticated copies; it does not newly validate their source/receipt outcomes.

## 1. Actual producer and ledger define the relevant domain

`verify.run` authenticates its pinned source inputs, loads the selected word, invokes the recipe producer, and calls `ledger.analyze` before `execute`. The source's successful selected-word scan is inherited evidence, not reproduced here. Reading those guards establishes the implication they would enforce on the actual successful path; it is not a new verification of all22803 events or an arbitrary-program admission theorem.

The ledger checks nonzero scalar coefficients, dyadic positive denominators, target frame, numerator+/-1 for noninteger SCALE, distinct same-frame ADD/COPY operands, selected unit COPY, MOVE frame/ownership, INIT/CLEAR ownership lifetimes and final frame/ideal endpoints. The MOVE Boolean is ownership information, not an inverse flag. Integer SCALE's local inverse needs a nonzero signed integer and exact divisibility; the source's selected powers-of-two restriction is a narrower word fact, not needed to justify signed exact division itself.

The scalar helpers alone do not establish all these constraints. In particular `pack_remainders` uses `D.bit_length()-1`; this equals log2(D) only under the preceding dyadic denominator premise. The source checks abs(p)=1 locally for division records, but does not turn the helper into a general arbitrary-denominator API. The guard path supplies the needed conjunction.

Initial values in the actual caller fixture are a mapping of the intended public labels to lists of Gaussian integer tuples, with common N=512^f and positive integer f. Shape preservation is an invariant: INIT creates N entries, COPY preserves N, scalar operations preserve N when lengths agree, and native validates N. ADD's `zip` is not an independent malformed-shape validator. The general inverse conclusion is conditional on the common-shape contract and no interfering mutation, not on accepting arbitrary arrays/programs.

## 2. Actual fractional residue is seed-shifted

For one component the code uses

    y = (p*x+u)//D,
    r = (p*x+u)%D,

with D>0 and0<=u<D. Python exact integer floor and nonnegative remainder give

    p*x+u = D*y+r,    0<=r<D.

For the source fractional SCALE p=+/-1, multiplication by p is its own inverse, so

    x = p*(D*y+r-u).

This is exactly `restore_division`, including negative x and negative p. It is not an unshifted residue of p*x, nor a truncation-toward-zero quotient convention.

To reconcile my first draft's generic notation, let r0=(p*x)%D, q0=floor(p*x/D), and b=floor((r0+u)/D). Then y=q0+b and the actual packed residue is r=r0+u-D*b. Substitution gives

    D*y+r-u = D*(y-b)+r0 = p*x.

Thus both mathematical reconstructions describe the same reached value, but **the actual record is r, not r0**. One must not substitute the actual r into the abstract unshifted formula while also subtracting b. No source change or first-draft relabelling is needed; publication should use the source's simple seed-shifted identity.

The bit packer and restorer walk real then imaginary residues in the same coordinate order and low-to-high bit order. Under dyadic D their fixed bit fields hold every residue; the reader checks byte length and unused high padding. This is an exact record identity, not an execution of the original division fixtures or a universal forged-packet validator.

For integer SCALE, quantization with D=1,u=0 is exact multiplication. The inverse checks divisibility before using integer `//`. Negative divisors pose no problem on an exactly divisible reached value.

## 3. Native pair: conserved sum gives the same correction center

For x=(a,b),y=(c,d), `pair` computes sum s=x+y and difference d=x-y. Its seed-dependent correction vector c_seed is a deterministic function of that sum, its parity/sign and the retained sign seed. If the two sum components have the same parity no correction is needed; otherwise the selected odd component is nonzero, so its sign branch is unambiguous. Subtracting the correction, rotating and restoring it preserves the parity needed by the exact halves.

The difference map is

    d' = J*(d-c_seed)+c_seed,

where J is multiplication by i. The two outputs sum to the same s. Hence inverse `pair` recomputes the SAME c_seed and applies J^-1, giving

    J^-1*(d'-c_seed)+c_seed=d.

The even-numerator check makes division by2 exact. This proves the local inverse for arbitrary Gaussian integer magnitudes and either valid retained sign; it does not rely on a fresh sign for decoding or re-prove the pair's mean/variance/error theorem. A changed sign is not generally the same center.

`route` verifies its destination permutation for the recipe domain. The source compiler supplies the nine-axis recipe shape. `monomial` applies the destination/phase on each nine-bit tensor digit; its inverse reads from those destinations and negates the same summed phase. This is exact Gaussian-integer permutation/sign arithmetic, not a new validation that every recipe equals its intended native frame operator.

Forward `native` applies right monomial, pair layers in original index order, then left monomial. Inverse applies left inverse, iterates indices in reverse, uses the original `seeds[j]` for each original layer j, and ends with right inverse. Reversing the loop while retaining each original seed index is the needed association. It is not equivalent to arbitrarily renumbering retained signs. Within each layer the coordinate pairs are disjoint, so the local pair identity yields the complete layer inverse.

## 4. Whole-field records and reused ownership lifetimes

ADD is the exact translation in my abstract note: its increment depends on the distinct preserved source, q and retained scalar seed. After later instructions have been undone, that source equals its forward-time value; recomputation and subtraction restore the arbitrary dirty destination.

COPY retains the actual old destination before installing a new list of source values. The inverse checks equality with the restored source before reinstating the old list. CLEAR retains the actual removed field and its label, then inverse CLEAR checks absence and reinstates it. INIT requires an absent label, inserts zeros, and inverse INIT removes only a field checked exactly zero. The order of dictionary keys is not a field-layout obligation here; this actual representation uses labeled fields, unlike an ordered-stack implementation. The same descending event induction applies to restored label/lifetime state.

The source records are indexed by event j, not overwritten per reused field label. Undoing later lifetimes therefore precedes restoring an earlier popped field. `tape[j]=None` happens after binding that record to a local variable, so it does not destroy the value required by the current inverse step.

The retained list references remain valid snapshots in this specific path. Initial and output field lists are copied at the outer level; tuple components are immutable Python integers. COPY makes a new outer list; ADD and SCALE assign new lists; native begins with a new monomial list before replacing its pair entries. Neither saved old lists nor shared zero tuples are later mutated in place. The abstract value/snapshot premise is therefore supplied without requiring a deep-copy claim for arbitrary mutable payload representations.

Descending through the word restores every earlier source, record and structural label boundary before it is used. The final `fields==initial` gate is a complete field-value equality for the declared list/tuple input representation. This proves the intended reached-state decoding implication; it is not a complete source-claim replay performed by this review.

## 5. Representation and scope qualifications

The numerical sampler itself is pure Python integer/list/tuple arithmetic. It does not use fixed-width NumPy payload arrays. Thus my first draft's general warning about dtype overflow remains a valid boundary, but is not an unresolved int64-overflow gap in this sampler's declared arbitrary-integer representation. Resource feasibility of materializing huge N remains separate from algebraic invertibility.

NumPy int64 is confined to the separate fixed512-coordinate producer matrix comparison. The producer contains range gates and source assertions; its prior all-column outcomes are inherited evidence, not revalidated or extended to arbitrary tensor widths here. The larger tensor fixture in the verifier is not a complete all-width caller run. All-width algebra follows from valid-shape composition, not from claiming every f was executed.

The peer accurately restricts its PASS to generated source/data/recipe shapes and the actual producer/ledger path. The permissive sampler is not an arbitrary-program, arbitrary-NumPy, invalid-seed-side-effect or forged-record admission API. Fixed callbacks and immutable word/recipes must not mutate the fields/records between matching forward and inverse operations.

Same-seed inversion is deterministic and needs no forward freshness assumption. The source's conditional-error theorem does need fresh forward randomness and is not accepted merely because inversion works. Retaining/popping Python records does not prove their physical reversible erasure, restoration of fresh random tape, or a full finite-register permutation. The saved records contain the information discarded by rounded SCALE, COPY and CLEAR.

## Cross-review conclusion and credit

The peer's actual seed-shifted residue, conserved-pair center, original-index reversed layers, field-record snapshot and successful-ledger-path qualifications correctly bind the source to my abstract inverse proof. Its eight controls and my nine are written, overlapping **UNEXECUTED** deductions, not17 new experiments. No code correction is requested.

Ali Romman6546/6532 and the retained6509/6526 native/rounding/compiler lineage keep their original caller, pair, inverse/error/bill/count credit. The selected6030 word, existing6096 applicability and6547/6594 recovery work remain distinct and are not rederived or described as missing. No new numerical constants, source-word scan, all-column certificate, entropy floor, error/concentration proof, physical inverse/native/owned-erasure admission, human/kernel acceptance, kappa or frontier change follows from this written review.
