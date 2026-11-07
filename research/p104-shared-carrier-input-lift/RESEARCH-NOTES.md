# Scope and boundaries of the input-lift step

The object is one exact edit of the pending #6805 native word under the same
#6726 caller. The frozen heads and scope are in `TASK.json`; the previous step's
notes are retained unchanged as `RESEARCH-NOTES-6805.md` (with `discover.py`,
which belongs to that step and is not used by the lift).

## The move class

A helper that is born at frame 3 and first moves at a later time may instead
be born inside that move's first destination, if every frame-3 row that read it
receives its response there. This is the native input lifting of
[#6349](https://github.com/CrocSwap/integer-mult-bounds/pull/6349) by Ali Romman
(see also #6353, #6372) and the shared-carrier form of #6375. Here two helpers
(556, 664; the second with the partner 665 in the same preparation rows) share
the carrier 120 and the receiver 179, and one repair event restores the
partner. Everything is dyadic and uses frames already in the word (frame 105).

## What is checked

* `lift.py` asserts each bound source event of the edit list and the
  preconditions (helpers born at frame 3, independent, exits full frames,
  birth frame inside each exit frame).
* Arbitrary-input identity: the new word's complete endpoint (all 801 x 801
  coefficients) equals the identity, by the primary replay and an independent
  adjoint; the defect vector `D120, D179, D665` before delivery and its
  cancellation, and unchanged erased values at all 47 `CLEAR` events, are
  recomputed independently (`independent/check_native.py`, `PROOF.md`).
* Chart legality: every used native pair (2,940 maps) by signed Pauli action
  and phase, plus all 512 columns of each of the ten pairs named by the
  split, the inserted moves and the lifted helper endpoints.
* Invoice: both caller retirements, all contacts, allocation, ordinary
  budget recomputed from the literal word (535,415,008, unchanged), both
  interval engines at the new endpoints, strictification, compiler and
  54+4 outer inequalities at κ = 330823/100000000.
* Negative controls reject a wrong coefficient at each inserted `ADD`, a
  missing final repair, aliased lifted helpers, a stale bound source event
  and a missing carrier delivery.

## Changed numeric literals (old to new)

KAPPA .00330814 to .00330823; TESTED .003308145 to .003308234; PREVIOUS
.00330720 to .00330814; raw crossing interval to
(.00330823456614, .00330823456615); compiler gap 1/1,400,000,000 to
1/1,750,000,000; helper profile 9:360 to 359 and 7:9 to 10; paid profile 1:+2,
3:-1, 4:+1, 5:-1 per call; paid requests 66,870 to 66,888; paid rank mass
178,080 to 178,044; native scalar allowance 138,374 to 138,352. The ordinary
bound 535,415,008 and the 10^9 budget are unchanged after recomputation.

## Limits

The gain is a local identity on one word and helper pair. No claim is made that
other pairs, frames or carriers behave the same. The five framework
assumptions remain, the selected κ is unchanged and external review is open.
