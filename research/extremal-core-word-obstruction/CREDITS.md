# Sources and credit

Ali Romman prepared this proof and verifier with substantial OpenAI
Codex assistance. New work is Apache-2.0. Independent human and
formal-kernel review are unclaimed.

- CubeJerry's [PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782),
  head `685457252b51b9c7932ece363365bdf0b12c9c31`, supplies the
  five-dimensional restricted bridge-cancellation theorem and its
  associated-graded, star-quotient and chronology arguments. Read the
  [exact word proof](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/FIVE-CORE-WORD.md).
  Its notice states that the work was prepared for @CubeJerry with
  substantial OpenAI assistance. It credits the retained relation and
  augmentation framework; that lineage is not relabelled as new here.
- The full Laurent recurrence is adapted from the same source's
  [independent_five_word.py](https://github.com/CubeJerry/integer-mult-bounds/blob/685457252b51b9c7932ece363365bdf0b12c9c31/research/bit-three-relation-core/independent_five_word.py).
  The present verifier generalizes its dimension, exponent tuples and
  ambient projector factors. This adapted code is not a separately
  authored review. The prior k=3 case and wrong-sign bridge control
  retain their original credit.
- Ali Romman's [PR #7693](https://github.com/CrocSwap/integer-mult-bounds/pull/7693),
  head `dab13e010216570a00e22490b379b31b610f2890`, supplies the all-width
  classification and unique ambient link. Read its
  [exact proof](https://github.com/aliromman/integer-mult-bounds/blob/dab13e010216570a00e22490b379b31b610f2890/research/edge-extremal-pool-classification/PROOF.md).
  That theorem uses the matching bound from
  [PR #7692](https://github.com/CrocSwap/integer-mult-bounds/pull/7692),
  head `c2870a38841f515db7203a0761cd77f014f7fb7a`,
  [exact proof](https://github.com/aliromman/integer-mult-bounds/blob/c2870a38841f515db7203a0761cd77f014f7fb7a/research/edge-matching-image-bound/PROOF.md).
  Both are explicit mathematical dependencies; their complete packages
  are not rerun here.

The new result is the all-k, all-length word obstruction and its
full-ambient bridge deletion for this exact extremal alphabet.
The common degree-one kernel, five-core argument and known positive
pool family remain prior work. The new one-extra-relation control
shows the limit of the chronology statement without asserting a saving.

No external file is read at runtime. SOURCES.json binds the selected
state and task catalogue on main for provenance. Those records are
not mathematical premises. All required proof dependencies are linked
at their exact public commits.
