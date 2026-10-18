# V45 keeps its subspace in the shipped words and adds no buffer

**Partial. No new exponent.**

Both shipped words end helpers 249, 251, 265 and 267 on the rank-7 subspace
from the V45 check. Those four helpers are already in the parent, so the joint
drop adds no private buffer. The buffer count goes from 86 to 91 because five
later extractions appear. The recorded fixed-capacity brackets rise from the
parent through stage 1 and on to the final bracket. The cap basis is not
re-solved here.

## What was executed

The parent end frame of each V45 helper is `[256, 128, 64, 33, 16, 9, 5, 2]`,
rank 8. The shipped end frame is `[256, 128, 64, 35, 16, 11, 5]`, rank 7, and
it lies inside the parent frame. Both providers agree.

The parent has 86 `helper_final` entries and each shipped word has 91. The five
new keys are 226, 228, 230, 363 and 395. None of the V45 helpers is new.

The stage-1 local profile is the joint stage's recorded profile, not the
shipped profile. The shipped profile is the later one, after the extractions
and the rewrites. The four recorded brackets are nonempty, and each stage's
upper bound is below the next stage's lower bound.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this
reading of the shipped words. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the two shipped words, the two parents, the
stage certificates, the final cap certificate and the task catalogue. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/rank7-v45-shipped-invoice/verify.py
python3.12 -B research/rank7-v45-shipped-invoice/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank7-v45-shipped-invoice
```

Both commands finish in under a second.

## Open next questions

The recorded brackets rise, and this check does not show that the rise is
forced by V45's margin of 22,972. Re-solving one stage basis would be the next
certificate check. It is separate from reading these words.

## Credit

Dugongue supplied the shipped words and the relaxation certificates. The V45
frame and margin check is the predecessor of the helpers read here.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
