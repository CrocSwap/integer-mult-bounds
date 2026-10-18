# Filtered elimination and state-version transport

These are sufficient compilation theorems. They do not assert that a desired low-cost factorization exists, that the searched family is complete, or that scalar rank alone determines the recurrence exponent. Every elementary operation and changed frame transition remains part of the actual invoice.

## Theorem 1: elimination with reusable donors and reversed execution

Let C be the observed target-response matrix on helper coordinates over a field. Suppose we have stages j=1,...,k. At stage j choose new pivots P_j, donor indices D_j disjoint from P_j, and relations between the current response columns

    C_j[:,p] = sum_{d in D_j} q[d,p] C_j[:,d].

No previously eliminated pivot may be used again as a new pivot or a donor. A donor may become a pivot at a later stage. Form U_j from the commuting shears d <- d-q[d,p]p. Then right multiplication by U_j changes only the pivot columns, setting them to zero, and leaves all other columns unchanged. Thus, by induction, C U_1 ... U_k has zero columns at every selected pivot, including pivots which previously served as donors. The products are invertible, with explicit inverse obtained by reversing the elementary operations and their signs.

The actual physical prefix must execute the stage blocks in order k,...,1, since column states are multiplied on the left while the response map is on the right. This reversal is essential: merely concatenating algebraic discovery order is generally wrong. The numerical relations at later stages can be evaluated on the original remaining columns because only already-eliminated columns changed.

For each helper, collect the frames of every stage touching it in physical execution order, followed by its original first-touch frame. Require this list to be nested. A pivot starts at its own elimination frame; other helpers start at their specified old entrance. Require all initial frames to be contained in their first physical touch. These are finite sufficient geometric tests. Regenerate the inverse background cleanup. If the background subsystem never reads output target registers, this cleanup restores every background coordinate for arbitrary initial dirt. Zero response of every warm pivot ensures its dirt never needs a forbidden zero-frame output compensation. Existing gauges may be retained only under explicitly checked separation or a proved read-before-injection order, not by ignoring overlap.

The exact local resource signature is obtained register by register from the successive dimension differences in this list. Repeated equal frames cost zero; every positive difference contributes one child of that rank. A pivot's residual width decreases by its entrance dimension. This chain invoice is valid even when supports overlap and the simple sum of disjoint component invoices is not. Full wrapper and physical owner costs remain separate.

Proof of the response assertion is the elementary column-update identity above and induction. Proof of geometric legality is exactly the nested-chain test at every instruction. Proof of restoration is inversion of the explicitly changed background product. There is no existential oracle in the construction.

## Concrete application: the PR535 static quotient presentation

The frozen PR535 construction has 40 static rank-one pivots, 112 post-center gauges and 56 rank-four post-center pivots. We leave its post-center construction unchanged and replace only the static response presentation. The new selection uses six line classes:

| Frame | Pivots | Active donor list size |
| --- | ---: | ---: |
| 96 | 8 | 8 |
| 102 | 8 | 8 |
| 120 | 8 | 8 |
| 126 | 8 | 8 |
| 480 | 10 | 14 |
| 486 | 2 | 6 |

This gives 44 static pivots. The actual scalar word loses exactly four rank-one children; all other local rank multiplicities remain identical. Residual inventory changes from 56 width-five, 152 width-eight, 296 width-nine to 56 width-five, 156 width-eight, 292 width-nine.

This witness is a depth-one special case of the staged theorem: its selected supports do not need donor-to-pivot reuse. The broader nested search generated it, but we do not attribute its numerical change to deeper nesting. The gain here comes from choosing a different joint response presentation across line classes, rather than maximizing each public component in isolation.

`build_static44_portable.py` recomputes every selected rational relation, retains the original downstream scalar operations and frame labels, regenerates cleanup, and checks source/result semantic hashes. It checks the actual nested frames, complete local histogram and dyadic scalar contract. `STATIC44-SCALAR-AUDIT.json` independently checks every one of the 728 formal columns in both orientations and rejects all 44 omitted-static-correction controls with the correct compensation held fixed. Arbitrary helper dirt is included among these columns. This is a checked local construction, not a claimed globally hosted bound. The final package may continue to use unchanged PR535 if the bit supplier still binds.

## Theorem 2: compensation transport along exact register versions

Split state into background X and outputs Y. Let an invertible background prefix act by X -> A X and leave Y unchanged. The old compensation is Y -> Y+D X. Then the exact identity

    [A on X] after [add D X to Y]
      = [add (D A^{-1}) X to Y] after [A on X]

holds on every input, including arbitrary helper dirt. Therefore compensation may be moved to another program cut by computing the inverse-version response D A^{-1}. One must factor the transported map into actual allowed scalar gates and check that every source and target frame can reach the chosen common frame and still reach their next uses. If those finite checks pass, the transformed program has precisely the same full scalar endpoint. It is not enough to compare clean-input columns or to reuse D without the inverse-version factor.

For a sequence of elementary background gates, D A^{-1} is computed by the opposite column update, in the original prefix order. Thus this theorem supplies a constructive compiler pass with an exact rejection test. The untouched-register case gives a useful safe normal form: each dirty compensation read can be delayed up to the first instruction that touches its helper, while the target remains at frame zero. This special case needs no extra storage and preserves the frame-chain invoice. It is not claimed as an exponent improvement. `transport_compensation.py` implements this normal form on R480: all 480 helper dirt reads move to their last untouched versions, all 720 scalar columns agree exactly, and every deduplicated register frame chain is unchanged. The exact receipt is `transport-bit510/TRANSPORT.json`. This appendix does not claim a new native phase or global-program replay.

## Bounded screens and scope

On the original filtered504 source, 100 native nested-elimination trials were preserved; they reached up to 92 pivots and rank188, but became secondary when PR535 moved the frontier. No whole-profile gain is inferred from those counts.

On the new binding R480 bit source, the exact post-center compensation screen rejected every individual helper under its specified first-B-frame schedule: 448 failed because a transported source frame was already above the target frame, and 23 failed the next-use containment test. The full transported compensator had 1273 incompatible support entries in that schedule. A separate exact screen of 120 additional non-root sum/difference lines, together with all 120 root lines, found no entry response circuit. These are bounded family failures, not a theorem excluding other cuts, joint cancellation, general frames, or other schedules.

On PR535, all 112 post-center gauges already attain rank one in the intersection of their actual first frames, target first-use caps and donor-kernel caps. The remaining static census examined 27195 first-frame subspaces and found 12 nonzero-nullity line classes and no higher-rank candidate in that restricted interface. A bounded 100-seed presentation search yielded the checked 44-pivot witness above. No optimality claim follows.

## Structural source references

Mathlib's matrix transvection file supplies explicit left/right elementary update identities and reverse-inverse product identities. OpenAI's congruence elementary-matrix development supplies `clear_step`: an elementary update clears another entry while preserving an already-cleared prefix. We inspected these actual statements as structural models for the inductive invariant and product order. The new geometric compilation theorem and its changed provider were proved and checked here; they are not asserted to be direct imports or newly Lean-certified theorems. Exact source hashes are in META-SOURCES.json.
