# Review of the whole retained-record inverse

**Verdict: no material inverse gap found on the fixed source producer/ledger path, with its stated exact-integer field representation and recipe premises.** Ali Romman’s PR #6546 has a compositional reached-state inverse across every literal opcode. This review explains the implication from actual guards, record formats and reverse dispatch. It does not reconstruct the caller, rescan its word, rerun its numerical suite or newly establish its error, retention or work totals.

Source head: `ff038070b8d122a43993f2b2524154323cc6b4d7`. Core blobs: sampler `2f7ba4b7d01213beb2a3b070658617ff992e715e`, proof `178000008b30144cf607dabd0d1759056fd4a644`, producer `5ed6163e903da47268a3ca44786126e6e978dff6`, ledger `728b2901176f11de2958c0e296061755b7305727`, verifier `aea6fd3df8b1d666cf963ce1e338a0a4074035aa`. Exact inert copies, source NOTICE and source pin metadata are retained separately from canonical provenance. No source, NumPy, caller, ledger, recipe producer, finite fixture, mutation or kernel was executed.

## 1. The actual caller supplies premises the sampler alone does not check

`verify.run` authenticates its declared inputs, loads the selected word, runs its recipe producer, and calls `ledger.analyze(word,bound['ranks'])` **before** `execute`. This is a review of the literal guard implication on that successful path. The source author’s successful validation of all 22,803 events and all native columns remains inherited evidence, not a fresh scan here.

`ledger.analyze` checks MOVE frame/ownership, unused owned INIT labels, live CLEAR labels and final ownership/frame closure. For scalars it checks a nonzero coefficient, power-of-two denominator and target frame. Fractional SCALE must have numerator ±1; integer SCALE is allowed. ADD/COPY require a distinct source in the same frame; selected COPY requires coefficient one and the specified owned/ideal-row condition. These clauses supply the local inverse’s algebraic and lifetime hypotheses. An ideal-zero COPY destination can still hold numerical error; it does not make the actual old value disposable.

The input domain is a mapping of the intended public labels to lists of `N=512^f` Gaussian pairs of Python integers, with positive integer `f`, fixed word/recipes and a noninterfering callback returning valid seeds. INIT, COPY, scalar operations and native preserve common field shape; native additionally checks `N` and seed count. Scalar `zip` is not a malformed-length validator. The final equality compares the declared list/tuple value representation; it is not a promise about arbitrary containers, Python object identity or external mutation.

The source compiler supplies nine-bit monomial recipes and ranks within the producer’s checked range 1–8. `route` checks its destination permutation. This review uses those source/shape premises to prove invertibility, without accepting anew that every recipe equals its intended native operator. The original source pins for WORD and the two compiler/oracle bodies are retained. Their main Git paths/blobs/modes were checked as metadata; raw bodies and their declared SHA256 values were not newly checked or executed by this review.

## 2. The literal Gaussian pair has the same correction center on reversal

Write the two Gaussian integer inputs as `x,y`, their sum as `s=x+y`, and difference as `d=x-y`. In `pair`, the retained sign and conserved sum determine a correction `c`: zero when the sum components have matching parity, otherwise a signed unit on the odd component. That component cannot be zero, so its sign choice is defined.

The forward difference transformation is

```text
d' = i*(d-c) + c.
```

When correction is zero, matching parity makes the final halves integral. Otherwise subtracting the correction makes both components of `d-c` even; rotating and restoring `c` gives the same parity as `s`. The code’s even-numerator check is consistent with this all-integer argument. The outputs sum to exactly the same `s`, so inverse `pair` recomputes **the same** `c` from that sum and retained sign and applies

```text
-i*(d'-c) + c = d.
```

The exact halves then recover `x,y`. This works for either valid retained sign and arbitrary integer magnitudes. It does not need a fair sign or establish the pair’s mean/variance anew. A different inverse sign can change the center and is not generally an inverse.

`phase` implements exact multiplication by a power of `i`. A source monomial sends coordinate `src` to its checked destination with its source-indexed phase. The inverse reads that same destination and negates that same phase. `monomial` applies this on each nine-bit tensor digit and sums phases, giving the literal inverse for every positive tensor width under the recipe premise.

Forward `native` is right monomial, ordered pair layers, left monomial. Its inverse starts with the left inverse, traverses the original layer indices in reverse, uses the original `seeds[j]` at index `j`, and finishes with the right inverse. Each layer consists of disjoint coordinate pairs, so the pair identity inverts it. Reversing order does not mean renumbering seeds. This proves the actual composition’s inverse; an ideal matrix inverse alone would not have justified rounded native recovery.

## 3. ADD subtracts the same deterministic translation

`quantized` uses exact integer arithmetic for coefficient `p/D` and valid seed `u`:

```text
Q_u(x) = floor((p*x+u)/D),   D>0, 0<=u<D.
```

ADD changes only its destination by adding the quantized increment from its distinct preserved source. Once later events have been undone, that source has exactly its forward-time value. Recomputing `Q_u` with the same coefficient, seed and coordinate order and subtracting it restores any dirty signed destination. The increment itself need not be injective or unbiased. Rounding the negative anew is not the specified subtract-inverse.

The distinct-source premise matters for the displayed code. A self-ADD with coefficient one sends `x` to `2x`; recomputing the increment from that changed source and subtracting it gives zero, rather than general `x`. This hand example concerns an unsupported call and the literal inverse rule. It does not assert that every self-ADD is noninjective. The actual preceding ledger forbids it.

## 4. Fractional SCALE stores seed-shifted Euclidean residues

The literal record is

```text
y = (p*x+u)//D,
r = (p*x+u)%D.
```

Positive `D` and Python’s exact floor/remainder convention give `p*x+u=D*y+r`, with `0<=r<D`, even for negative inputs or negative `p`. Fractional SCALE’s `p=±1` therefore yields exactly

```text
x = p*(D*y+r-u).
```

This is the expression in `restore_division`. It uses the actual shifted residue, rather than a residue of `p*x` with an independently applied rounding correction. The sealed abstract draft used a more general unshifted-residue/correction representation. Its post-seal note explicitly relates the two without changing the first draft: if `r0=(p*x)%D` and `b=floor((r0+u)/D)`, then actual `r=r0+u-D*b`, so `D*y+r-u=D*(y-b)+r0=p*x`. One must not mix those two record conventions.

Packing walks real then imaginary components, in coordinate order and low-to-high bit order. Under `D=2^k`, `k=D.bit_length()-1` bits store each complete residue. The reader walks the same fields and checks byte length and unused high padding. The pack/restore helpers do not themselves enforce dyadic `D`; the source proof and preceding ledger do. For example denominator three can require a residue that does not fit their one-bit field. That is an off-domain written control, not a defect in the valid selected caller or a newly executed failure.

Integer SCALE uses `D=1,u=0`, so multiplication by nonzero integer `p` is exact. Its inverse checks divisibility and uses exact integer division. Negative divisors are safe on a divisible reached image. The actual selected word has the narrower signed-power-of-two facts stated by the source; the local inverse only needs a nonzero integer. Zero is excluded by the ledger.

## 5. Old values and event order restore structural lifetimes

Forward COPY stores the **actual** old destination and installs a new list of source values. Reverse COPY, after all later changes have been undone, checks equality with that restored source and reinstates the old destination. CLEAR stores the whole popped field; its inverse requires the label absent and restores that value. INIT requires an unused label, inserts exactly zero, and its inverse checks zero before removing it.

The records are indexed by event, not overwritten by field label. If a label is cleared, initialized again and later cleared, the later lifetime is undone before the earlier record is consumed. This is restoration of a labeled field map, not a requirement to preserve Python dictionary insertion order.

Saved list references remain stable snapshots on this exact representation. Initial and output field lists are copied at the outer level. COPY, ADD and quantized SCALE assign new lists. Native begins with a new monomial list before replacing pair entries. Payload components are immutable integer tuples; INIT’s shared zero tuple is immutable. No later operation mutates a saved old list through an alias on the declared path. This argument does not extend to arbitrary mutable array views or interfering callbacks.

Let `X_j` be the field map immediately after event `j` and `R_j` its record prefix. Each local inverse restores `(X_(j-1),R_(j-1))` from the reached `(X_j,R_j)`. Descending through the fixed word therefore restores every earlier source, field lifetime and seed/residue boundary before it is used, and ultimately the entire initial value mapping. `tape[j]=None` occurs after the current record is bound locally; it does not remove the value needed by that step. The final equality guard is consistent with this uniform argument; finite equality checks alone would not prove it for all inputs.

## 6. The inverse’s information and representation limits

The augmented reached endpoint plus valid retained records determines the original input. This is not a claim that output fields alone are injective, that arbitrary forged records are accepted, or that all randomness is recovered from unrecorded output. The source returns a separate output snapshot while its internal inverse reconstructs initial fields using seeds, old values and residues.

The sampler uses Python arbitrary-precision integers, lists and tuples. NumPy int64 belongs to the separate fixed-size producer comparison. Thus the abstract draft’s general representation/overflow warning is resolved for this declared payload domain; it is not an unresolved fixed-int64 overflow gap in the sampler. No NumPy producer comparison, all-width caller run or practical memory feasibility claim follows from that fact. Algebraic composition handles arbitrary positive width under valid shapes; it does not identify every recursive caller with this tensor lift.

Exact inversion needs the actual retained seeds and no fairness assumption. Fresh uniform randomness conditional on prior state is a separate premise of the source’s forward error theorem. The deterministic fixture callback is not a randomness proof, and reusing a retained forward seed is not a fresh independent call.

Clearing Python record slots or releasing objects does not implement reversible physical erasure. The augmented record contains the information rounded SCALE, COPY and CLEAR would discard. A total permutation on identical finite hardware registers, owned entropy cleanup, physical tape placement and a fast recursive inverse bill require additional implementations and premises. The source’s 54 fields, residue/seed totals, peak 824 and error constants remain its original unreplayed results, not new minima or prices.

## 7. Controls, exposure and credit

The abstract draft has nine and the source-aware draft eight overlapping written controls; they are **UNEXECUTED** and are not seventeen independent experiments. They challenge wrong seeds or order, signed-division convention mixing, lost residues, unsupported denominator/numerator/zero cases, self-ADD, discarded old values, label/shape/view aliasing and physical/freshness overclaims. Source control themes retain source credit; none is reported as a newly observed source failure.

The abstract role knew the target before deriving it but sealed before opening current source or peer. The code role separately sealed before peer reading and disclosed prior sampler/proof scouting. Root’s scout/body and later actual-source exposure are explicit. Cross-review and exact assembled checks follow the seals. These are substantial OpenAI Codex written roles, without blind, human or proof-kernel acceptance.

Ali Romman owns PR #6546 and retained #6532/#6526/#6509 work. Retain Nick Petalas #6418/#6438, distinct #6594 capacity and Ali’s #6547 zero-fiber results; zxv #6066, DreamingOfClouds #6030/P104, Cinna Davis #4088/#2226, every original NOTICE author and the native/compiler/rounding lineage. Translation inversion, quotient/remainder reconstruction and reverse-record composition are classical.

The original formal/kernel gate is unmet. Source successful word membership, all-column correspondence, numerical error/concentration/precision, count/bill/retention and fixture claims were not rerun or newly accepted. Physical sampling/gates/tape, retained cleanup, accelerated recursive tariffs, outer recovery, complete native/compiler/ownership/precision/analytic/full-supplier obligations and all five selected assumptions remain. No κ/frontier/adoption change or merge follows.
