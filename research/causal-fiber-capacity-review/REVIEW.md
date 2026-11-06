# Causal certificate, simultaneous fiber and recovery capacity

## Result and source boundary

Qualified written PASS for the **conditional implication** from the actual source certificate predicates to the simultaneous all-width family and recovery-capacity argument. No material gap was found on the declared numerical caller/read-set domain. This review does not independently establish that the complete selected word satisfies those predicates: no word was fetched, decompressed or scanned here.

Target: Nick Petalas [PR6594](https://github.com/CrocSwap/integer-mult-bounds/pull/6594), head `2502a6defbe0e78d7f9285c5eb1ff88146a968ab`, `research/rounded-read-caller-fiber/`. Exact `PROOF.md` blob `672bc4e88cd7b7d27690d6ae248560d43619e173` and `verify.py` blob `d09d0950545fe1693dfa76156c157849bbc56e2d` are retained, with original README/SOURCES context and root license/NOTICE. The code is inert `verify.py.txt`. SOURCE-PINS.json binds their bytes and remote custody separately from canonical-main provenance.

The source owns its 60-field/39-read/17-read-bearing-field membership, cut10448, 120N floor, 129 literal replays, nine rejection controls, two boundary witnesses and matching family code. None is a new computed result of this review. Its successful fixed-word certificate and those counts remain source evidence, **unreplayed here**. The new deliverable is an inspectable proof-to-predicate/recovery-interface review, not a new family, floor, global maximum fiber, every-seed strengthening or physical memory minimum.

## Exact contract and quantified statement

Use the original same-grid numerical ABI: 770 unrestricted public fields, each N complex coordinates in h·Z[i], h>0, N=512^f, integer f≥1; owned fields initially zero and source allocation/liveness semantics respected. Work componentwise in integer units h. Scalar q=p/D is reduced with nonzero p and D>0. Its retained legal seed u∈{0,...,D−1} defines

    Q(q,x,u)=floor((p*x+u)/D).

ADD adds Q of its source to its destination; SCALE replaces its destination by Q. COPY uses its literal source/destination data. MOVE reads only its declared field and fixes the all-zero field for every fixed legal native seed. Native frame descriptors are not extra data operands under this stipulated caller contract. Retained records do not feed the forward data path. These read sets, native zero preservation, valid shapes and source ownership are inherited premises, not newly checked compiled/native semantics.

Fix **one** scalar schedule u=0 for p>0, u=D−1 for p<0, shared across every family member and coordinate; fix the native seeds too. This is a legal realization, independent of the input. No uniformity, probability, independence, typical-seed or every-seed lower bound is inferred. The source's cited Ali Romman6547 every-seed86N result is distinct and not reaudited.

Let C be K distinct valid public labels admitted by the actual normalized causal certificate. Independently choose one bit for each real and imaginary coordinate of every C-field; every other initial data coordinate is zero. The input map from these 2KN bits to initial public arrays is injective because the labels/coordinates are distinct. The claim audited below is: **if the full certificate succeeds on the fixed normalized word, all those inputs have the same zero data output for the fixed seeds**. K=60 and hence2KN=120N are the source's reported substitution, not a new event scan or recount.

## Predicate hierarchy in the actual source

`load_operations(raw)` first requires SHA256 `7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f`, then decompresses/parses. It checks public/owned counts770/29, event count22803, the six allowed opcodes, exact integer destination/source bounds0,...,798, bounded coefficient text and nonzero reduced Fraction numerator/denominator. It normalizes ADD/COPY source from event[2]; for all other kinds source is destination. ADD and SCALE take their literal coefficient, while other kinds use1. This authenticates/normalizes a fixed source; it is not a complete arbitrary-program parser, native read-set verifier or lifetime/type admission system.

`find_cohort` scans each candidate public label until its first SCALE or disqualifying access. A contracting first SCALE is a candidate. Earlier COPY/MOVE/INIT/CLEAR destinations disqualify it; COPY as source is also excluded by the coefficient-one source-read rule. Earlier ADD sources must be strictly fractional. ADD destinations are deliberately allowed. This per-field scan alone permits a generic contraction and therefore does **not** establish signed-half erasure.

`causal_certificate` is the stronger whole-word interface. It rejects duplicate/non-integer/out-of-range public labels, begins with every supplied label active (a certificate tag, independent of whether its current bits happen to be zero), and traverses all normalized events:

- active-source ADD requires |p|<D and records that read;
- SCALE on an active destination requires both contraction and exactly |p|=1,D=2, then removes that label and records its event;
- MOVE requires its destination inactive;
- COPY requires both source and destination inactive;
- INIT/CLEAR require their destination inactive;
- exit requires no active label remaining.

The helper trusts normalized operations. An unknown opcode, invalid coefficient or changed native read set supplied directly to it is not covered by this implication. `need` raises explicit ValueError rather than using removable Python asserts; no optimized execution was run here.

`main` joins the distinct checks: the per-field tuple must equal the fixed COHORT, sorted causal erasures must equal the per-field result, and original read counts, last-cut and native-count guards must pass. It separately checks silent endpoints, performs its original finite replays/controls and emits a source/verifier-bound receipt. This review reads the association but does not execute any of those operations. A successful actual run would establish the finite word membership; this written audit alone does not supply that run.

## Simultaneous induction, rather than extension from generators

For b∈{0,1}, every strict fractional coefficient satisfies Q(p/D,b,u)=0 under the fixed sign schedule. For p>0, the possible numerators0,p lie in[0,D−1]. For p<0, D−1 and D−1+p also lie there, since −D<p<0. For any legal seed, Q(q,0,u)=0. In particular a signed-half SCALE maps both bits to zero under the chosen schedule.

At each event cut maintain the invariant: every active C-field retains its **original whole binary vector**; every other live data field is zero. This is one statement about all mixed assignments at once, not a linearity assumption about rounded arithmetic.

An ADD reads either a zero field or an active binary field. In the latter case the actual certificate supplies strict fractionality, so the increment is zero in every coordinate. The destination stays unchanged, including if it is active. An active SCALE is its certified signed-half event; it changes the field to zero and removes its label. A nonactive SCALE preserves zero. COPY/INIT/CLEAR cannot touch active labels and therefore only act on zero data. A MOVE operand is inactive and thus the whole zero field; the inherited single-field zero contract applies. This preserves the invariant for every event and every mixed bit choice.

Exit has no active label. Hence all live data are zero. Any remaining normalized operations preserve zero. The argument is componentwise for arbitrary N; no enumerative extrapolation from N=1,4,512 is needed. Proper event bookkeeping distinguishes an erasure **event** index e from the cut immediately after it, e+1. Each label is removed exactly once, at its first active signed-half SCALE, so its original bits are still available immediately before that event.

The source's one-bit generators and nine simultaneous patterns are finite corroboration. Basis replays alone could never establish this nonlinear family statement; the causal invariant is the uniform proof. Native zero calls in the certificate count declared normalized MOVEs, not a newly verified compiled implementation or hidden operand trace.

## Exact recovery counts distinguishable states

There are 2^(2KN) distinct initial public inputs, the same fixed seed and one common zero data output. A deterministic exact recovery service for every displayed input must distinguish all of them through its additional retained state. If that total state has at most2^b possibilities, injectivity gives2^(2KN)≤2^b and b≥2KN.

“b bits” includes the complete distinguishable state: original-input copies, overwritten seed contents, side records, record length/headers, allocation/address information used by the decoder and any other data-dependent channel. A bounded-length payload with uncounted length or altered seed is not automatically a b-bit state space. This is a fixed-capacity/zero-error statement; it does not prove the same minimum for expected length, lossy recovery, a probability-of-failure service or an unchanged-seed promise that is silently abandoned.

For an extra dirty bank with a finite, positive integer Q possible initial states, require exact recovery of its old state on the unrestricted **product** of family inputs and old bank states, and require the same common forward data output. If its final bank has at mostQ states and the remaining record at most2^b, injectivity gives

    2^(2KN)·Q ≤ 2^b·Q,

so the same bound remains. The bank must not secretly expand or change the forward output/read-set contract. Correlations restricting the initial product, permission to discard the old bank state, or extra output capacity change this argument. This is information capacity, not a clean scratch/hardware minimum or a free physical erasure schedule.

## The matching code is restricted to this family

At the first signed-half erasure the field still contains its original bits. The literal retained residue is r=(p·b+u) mod2. For p=+1,u=0 it is b; for p=−1,u=1 it is1−b. Thus each erased coordinate supplies one bijective encoding of its original bit. Label/event/real-imag/coordinate ordering is fixed by the certificate, so packing these2KN bits is an exact mathematical code on the displayed family; one decodes the bits, places them in the original C-fields and restores the other initial data to zero.

The retained verifier's `run_data` simulates data and checks zero operands/endpoints; it does not implement that packed encoder/decoder or retain residue records. The code construction here is already in the source PROOF, not a new executable codec or executed inverse check. Silent pre-erasure ADDs can have data-dependent residues even when their rounded increments vanish. No claim that the full6546 record is minimal, that its other fields may be physically deleted for free, or that general inputs use only2KN bits follows. The sufficient whole-record inverse and the necessary family capacity are different results.

## Written weakening controls and evidence limits

The separately sealed roles give inspectable **UNEXECUTED** challenges: change the negative seed, allow bit2, permit an exact/noncontracting source read or a non-half first SCALE, pass an active label to MOVE/COPY/owned operations, silently add a native data operand, infer mixed-family success from basis tests alone, omit final active exhaustion/duplicate checks, or hide information in seed changes/record length/a correlated or disposable dirty bank. They are proof challenges to changed premises, not observed faults or new source experiments. The source's original nine rejected controls and two computed witnesses remain its own evidence.

Only six inert input files/59214bytes are retained. The source SOURCES record declares the canonical compressed WORD Git blob `22f9ab02d1b73ea0aa4b07ce445a14cc2602c760` and the SHA above. Its raw compressed bytes and declared digest were not independently authenticated in this written session; the fixed-word acceptance is conditional. This subset is not a runnable original package. No scientific VERIFY hook is registered. No original/new source import, word scan, producer, data replay, numerical experiment, native/NumPy operation, fault campaign or proof kernel ran.

The coordinator read the earlier scout/source body and had informal preclaim reasoning. The abstract role was target-known, with summary/context exposure, and sealed before current6594 proof/code/peer reading; historical familiarity is not excluded. The code role had actual source exposure from its earlier scout and sealed before peer reading. Source cross-binding and exact-version assessment follow those unchanged first drafts. Role separation supplies inspectable arguments, not blind discovery, independent human review or proof-kernel acceptance.

## Credit and remaining obligations

Nick Petalas6594 owns the family, conditional all-width proof, certificate and original numbers/finite evidence. Ali Romman6546 supplies the same-grid numerical ABI/retained inverse;6547 supplies the preceding every-seed family/method, with6532/6509 pair/native lineage. Credit zxv6066 signed-half residues, DreamingOfClouds6030 and all retained P104/native/compiler/source-NOTICE contributors, including Cinna Davis. Chronological induction, zero-fiber injectivity and pigeonhole/product counting are classical. ToikY produced this external review with substantial OpenAI Codex and separate abstract/code/metadata/byte roles. Exact root license/NOTICE and source attribution text are retained; no predecessor endorsement is implied.

The full original formal-interface task card is retained with explicit CHANGED written-review scope and partial outcome. Its formal/kernel acceptance gate remains unmet. Actual word/caller/entrance-encoding membership, compiled native/read-set/ownership contracts, record/sampling/randomness/placement/routing/restoration/cleanup and full physical tariff remain separate obligations. Arbitrary multiplication entrance images can exclude the displayed family; no such reachability is proved. All five selected assumptions remain. No κ/frontier/adoption change, merge, full supplier or new multiplication theorem follows; follow-ons are unreserved.
