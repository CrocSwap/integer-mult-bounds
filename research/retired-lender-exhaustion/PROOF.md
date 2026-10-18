# A source-bound upper bound for every sequence in one alias class

This proves the *exhaustion implication* behind PR2559's existing maximum-two
claim, not a new alias construction. The initial objects are the exact two
PR2526 words at `113c427bf6abe2572184621ebfa00ce7cdf06c46`. The final objects
are PR2559's words at `383ce6c84d92b7b3f00fe267cb23bf3233eecc77`. The newer
PR2526 head has identical word bytes; its other changes are not inputs here.

## Precisely delimited class

Each step removes a still-present ordinary helper h by substituting one
still-present retired lender L throughout h's B/restore uses. It may insert
one invertible K_G warp at h's first B use, mapping L's current frame U to
an equal-dimensional E contained in that use's required frame F. Cleanup is
rederived as the same inverse-reverse word; original A/prelude, source order,
scalar coefficients, event frame requirements and terminal labels are fixed.
Between such warps all frame transitions are the original monotone climbs.

The helper is noncold, has no restored-input private buffer, is not a centre,
has no use in precondition/compensation/A/cut, first occurs in B, and is not an
existing warp carrier. A lender is neither a target nor a centre and has no
original A/B/restore use or scheduled warp at or after the new first-use cut.
Removed labels cannot be borrowed again. All occurrences of a helper are
replaced together. Arbitrary choices of invertible G and E are allowed within
these rules; the bound is not limited to the builder's chosen basis completion.

This is the ordinary one-warp retired-lender class used by the two new
PR2559 aliases. It excludes lifted-target compensation, new preludes,
source-partner recovery, splitting a helper lifetime, altered frame paths,
changed terminal obligations and simultaneous algebraic substitutions that
cannot be ordered as such steps. It is not an unrestricted helper minimum.

## Necessary candidates, derived independently

For each remaining role, read its exact initial frame and ordered uses.
Represent a frame by its complete subset of the 512 vectors of GF(2)^9.
At scalar events the current subset must be contained in the event frame;
at a warp its from-frame must agree and its dimension is preserved. Signed
prelude warps already contain their chronological from/to frames: their
negative operator sign does not reverse those two recorded fields again.
Record every role's first/last use, and the frame after its last use, before
the final climb. Private cleanup is not a retirement event: it is separately
regenerated and does not license lending a private restored-input buffer.

An admissible h->L must pass these necessary tests:

1. L is strictly retired before h's first use.
2. dim(U_L) <= dim(F_h), since an invertible warp preserves dimension and its
   image E must fit inside F_h.
3. The dimension of h's last required frame is no larger than L's fixed
   terminal dimension, since there is no further return warp in this class.

The last test intentionally uses **dimension only**, a relaxation of exact
subspace containment. The resulting nine pairs are a necessary superset;
the certificate does not assert every pair is a separately admitted native
alias. Both initial orientations give exactly:

```
606 -> 68      635 -> 68      638 -> 68      639 -> 68
653 -> 49, 68, 83, 98, 101
```

The complete census considers 64 eligible helpers and 532 eligible lenders,
including helper lenders. All surviving lenders happen to be sources. The
complete per-role chronology and independent binary-elimination census agree.
The end-frame lower test is necessary because no terminal label is changed;
its dimension-only relaxation makes the exclusion stronger evidence, not an
extra restriction chosen to obtain the count.

## Why later steps cannot create a missing candidate

Induct on a sequence of admissible substitutions. Initially every step must
be one of the nine pairs above. Assume previous choices have been among them.
Their lenders are source roles, and their helpers are removed. No other
helper's event slots, required frames, eligibility or terminal label changes.
Unselected lenders are unchanged. A selected source lender acquires the
removed helper's later uses. Its retirement can only move later. Its original
retirement frame has dimension four; the newly inserted warp preserves this
dimension, and subsequent climbs cannot decrease it. Its new retirement
dimension is therefore at least the original one. Its terminal frame stays
full. Thus none of tests 1--3 can change from failure to success for an
unselected helper and a selected lender. A removed role is unavailable.

Consequently every later candidate is also in the initial nine-edge graph.
This argument is the missing transition from a rescan of one shipped endpoint
to an upper bound on *every sequence* in the stated class. An arbitrary local
search need not have this property; the source-only lenders and unchanged
remaining helper intervals are checked premises specific to these words.

## Overlap gives a two-alias upper bound

The five possible helper lifetimes, in B event indices, are:

| Helper | First use | Last use |
|---|---:|---:|
|606|963|1497|
|635|1037|1632|
|638|1043|1625|
|639|1046|1621|
|653|1084|1693|

All contain the interval [1084,1497]. A lender that is carrying one cannot be
strictly retired before another starts. Hence a source lender may participate
in at most one selected edge, even if repeated lending is allowed in principle.
Each helper can be removed only once. Any legal sequence is therefore a
matching in the displayed graph. Four helpers have only neighbour 68; the
fifth is 653. A matching has size at most two. The sixteen size-two matchings
are four choices of the first helper times four choices of a lender for653
other than 68. They are sixteen combinatorial possibilities, not sixteen newly
admitted or repriced native words.

The existing shipped selection 606->68,653->49 has two edges. The checker binds
its complete changed word to those substitutions, authenticates both new
invertible 9-by-9 binary maps and their frame images, regenerates every inverse
cleanup instruction, and independently checks the full frame/profile ledger.
The endpoint/dirty-borrow realization is inherited from PR2559's source-native
audit and conditional supplier admission; this package does not rerun that
full native/global/outer pipeline. Thus the upper bound is attained by the
already supplied word under its retained admission assumptions. Both shipped
words also have zero remaining necessary candidates.

## What is and is not established

The original nine-candidate/two-alias assertion is credited to Philippe Van
Velzen/PR2559. The added result is an independent finite necessary census,
the all-sequence noncreation and interval proof, and an exact binding of its
attainer to the declared edit and ledger. The paid delta is +H1-2H5 and the
width inventory removes one width4 and one width5 helper, as already claimed.
No owner fill, real runtime, improved moment, new kappa or unrestricted
exhaustion theorem follows. Further savings must change this precisely stated
class or its fixed source words; the certificate says nothing about their
availability or cost.
