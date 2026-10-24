# Second-order obstruction for the seven-call address-twist pattern

**Scoped written proof with exact finite corroboration. No new kappa.**

[PR4953](https://github.com/CrocSwap/integer-mult-bounds/pull/4953) left a
concrete task: test its seven-call `J/P_s/D_s` pattern modulo the cube of
the augmentation ideal, allowing all `S3 x S3` address twists. This package
rules out that entire pattern, in every order, without a global twist search.
It does not prove that arbitrary words with two-sided twists need nine calls.

## Result and added coverage

[PROOF.md](PROOF.md) proves the following necessary condition. Give the
three-role pattern one all-role call `J`, three private-column calls `P_s`,
and three diagonal calls `D_s`. Conjugate each call by arbitrary independent
per-register maps `B -> L B R`, with `L,R` invertible over the odd-denominator
rationals; allow arbitrary odd-denominator rank-one paid frames and every
call order. If it agrees with a diagonal target through degree two, each
target frame has rank at most one modulo two. The three `I_3` targets violate
this condition.

The first-order off-diagonal condition equates the shared and private frame
vectors. The next layer, tested on arbitrary dirty degree-one inputs, forces
their relative transports to agree. Their diagonal first-order contributions
therefore cancel, leaving only `D_s`. This proves a structural obstruction
for the fixed pattern; the predecessor checked exact orders of one twist
assignment and showed why the first-order screen alone cannot exclude it.

For the predecessor's exact assignment, put `[E00]+[0]` in role zero and
zero in the other roles. Role one has residual

`t00^2 + t00*t11 != 0 (mod I^3)`

in every order; its target output is zero. The quotient retains polynomial
squares. It is formed over `M_3(Z_(2))`, not the divisible ambient rational
address group. We compare actual actions on filtered register contents and
do not assume a faithful crossed-product representation.

This closes the bounded second-order step of PR4953 Open next question 1,
including all per-call, per-register `S3 x S3` conjugations. The full question
whether two-sided twists can beat nine remains open.

## Exact corroboration

`verify.py` is a new implementation and imports no predecessor code. It checks:

* the degree-two quotient on all 55 basis monomials, with squares retained;
* 128 odd-denominator group-homomorphism fixtures and injectivity of
  multiplication by each of the 511 nonzero linear forms in nine variables;
* all 36 `S3 x S3` twists and two non-permutation, odd-denominator `PBQ`
  fixtures, including their nonlinear degree-two substitutions;
* all 11,664 reduced off-diagonal cancellation cases: 11,340 fail at degree
  two; the 324 passing cases have equal relative transports and equal source
  frames. All 10,368 cases with distinct source frames fail;
* the exact dirty residual and the filtration conditions that make it
  independent of order; three representative orders are evaluated, rather
  than repeating the predecessor's 5,040-order census;
* 110 comparisons against a separate sparse finite-group implementation
  over `F_2[(Z/4)^9]`, which applies the actual calls before projection;
* the direct nine-call positive control on all 165 register basis vectors;
* rejected call deletion, twist deletion and frame substitution, plus controls
  exposing the false pass from discarding degree two or polynomial squares.

These finite checks corroborate the quantified proof. They do not prove
the theorem by exhaustive sampling of general `PBQ` maps. The result is
author-checked with substantial AI assistance, not independent human or
proof-assistant verification. See [VALIDATION.md](VALIDATION.md) for the
executed commands, publication checks and limits.

## Reproduce

Python 3.12, standard library only; direct replay takes about one second:

```sh
python3.12 -I -W error -B research/bit-address-twist-second-order/verify.py
python3.12 -I -W error -O -B research/bit-address-twist-second-order/verify.py
python3.12 -B scripts/research_package.py --package research/bit-address-twist-second-order --check-only
python3.12 -B scripts/research_package.py --package research/bit-address-twist-second-order
```

Success is `PASS_BIT_ADDRESS_TWIST_SECOND_ORDER`. The verifier has no runtime
inputs outside its own source and also runs in a Git-free export. The selected
record, catalogue and predecessor files in [SOURCES.json](SOURCES.json) are
historical provenance only; their exact base blobs and hashes remain pinned.
The generic metadata/source-history commands require a Git checkout.

## Scope limits

Only the stated seven-call projector pattern and three arbitrary dirty roles
are covered. No additional interleaved scalar mixing, extra calls, clean or
dirty helpers, even-denominator frames, physical layout, or native price for
twists is supplied. There is no supplier admission, selected-frontier change,
or complete integer-multiplication theorem.

## Open next questions

1. **Can a different projector pattern escape the obstruction?** This matters
   to the still-open full two-sided model. A useful first step is to exhibit
   a first-order-feasible seven/eight-call pattern where an off-diagonal block
   has at least three nonzero contributions, then test its action on dirty
   degree-one inputs before a full word search. This proof excludes only the
   two-contribution cancellation pattern. No such candidate is supplied here.
2. **Can a native layout implement the proposed twists cheaply?** Even a
   formal saving would need a complete physical cost. Start from the selected
   bit layout and one explicit per-register twist; its producer, consumer and
   restoration bill are missing. This package does not treat those costs as zero
   outside its deliberately favorable formal model.

No further enumeration of this fixed pattern is justified by this result.

## Credit

JoyboyBrian's PR4953 (head `aa468fa11ed5ca04b389021d35d39f70bc211dfe`)
introduced the twist model, its one-sided theorem and the seven-call
first-order witness. Cinna Davis / 1337isnot1337's PR2110 supplies the
odd-denominator square-zero method. The register-model lineage includes
Ali Romman / PR468, eumemic / PR288 section 1.2, and huxint / PR203.
Their models and results retain their attribution.

The second-order obstruction, proof and new verifier were prepared by
Krzysztof Wójt / krzysztofwojt with substantial OpenAI Codex assistance;
a Luna supporting agent helped with overlap/packaging inventory and a
separate finite dirty-input calculation. The primary author checked and
corrected that calculation before using it as corroboration. No independent
human review is claimed. New work is Apache-2.0.

Coordination: [Discussion #4999](https://github.com/CrocSwap/integer-mult-bounds/discussions/4999),
continuing [the #1166 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19137725).
