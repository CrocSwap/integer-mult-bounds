# A G20 frame conversion and its inverse do not both emit

**Route obstruction. No new κ.** Selected κ stays `781451/250000000`
in [certificates/selected-result.json](../../certificates/selected-result.json).
The argument is in [PROOF.md](PROOF.md).

On Ali Romman's PR #5708 word, the published route table has 2369 edges.
Every edge drops frame dimension, and the rank equals that drop. Frame 1
is the only dimension-8 frame and has indegree 0, so no route returns to
it. A conversion and its inverse therefore do not both emit. There is no
route-legal two-query bill.

Helper 222 starts on frame 1. Its first scalar records are six `ADD`s,
events 5638 through 5643, all declared on frame 1. Those `ADD`s are
ill-typed after any published exit, because the helper cannot come back.

At the opening cut, each of the 413 public helpers is a one-field carrier
of boundary rank 1 and internal rank 1. Frame 1 has 189 empty
compatible exits, 9 of rank 1 and 180 of rank 2. `(1, 517, 1)` is one
rank-1 exit. That exit creates the singleton channel and then leaves the
six `ADD`s ill-typed. It is not a completed word.

No field outside a helper group has an odd singleton pairing at any cut.
Across the published exits into occupied compatible banks, 2650155
span-admitted pairings keep boundary rank 0. An off-route move of field
208 from frame 622 into frame 509 does raise boundary rank from 0 to 1,
and the route table does not contain that edge. The census is not blind.

## Task and overlap

Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
Card `bit-helper-contract`, scope **refined**.

Session r78, item 1 of the ordered eligible list rebuilt on this main.
The 19 October handoffs (discussion comments 19030045, 19030047,
19030049, and 19030053) are closed. Later handoffs whose artifact is an
open pull request, including the H25 requests and the PR #6353/#6361
audit chain, are excluded. The remaining list is the revision-8
first-mention open questions of #5679, #5708, #5718, #5615, and #5717,
after dropping delivered items:

1. **This package.** #5679's different physical role for the early
   output. The common-frame part is Nick Petalas's free-carrier
   certificate. The paid frame conversion and its inverse were still open.
2. #5679: another paid-query removal on the changed split word.
3. #5679: a stronger Gaussian caller for that BIT component.
4. #5708: a noncoordinate public input contract. The longer-identity
   question is delivered by #6290 and #6305.
5. #5718: other legal boundary pairs. The first boundary-functional
   check is delivered by #6341.
6. #5718: one retained framework assumption.
7. #5615: whether a current source cut gains a channel under the full
   dyadic criterion. #5611's physical-target question is delivered by #6297.
8. #5717: rebind the explicit-inventory audit to a changed caller or helper ABI.
9. #5717: the retained compiler, precision, storage and analytic premises.
10. #5713: whether the emitted artifact matches the credited edit under
    the native and caller contracts.

Dropped before this list: #5708's stronger-caller question, delivered by
`research/g20-component-stock-gate`, and the one-move correction-frame
census in `research/g20-moved-correction-frame`. That census moves an A2
correction. It does not decide a carrier-frame round trip.

## Reproduce

CPython 3.12, standard library only, from the repository root:

```sh
python3 -B research/g20-frame-round-trip-gap/verify.py
python3 -O -B research/g20-frame-round-trip-gap/verify.py
python3 -B scripts/research_package.py --package research/g20-frame-round-trip-gap --check-only
python3 -B scripts/research_package.py --package research/g20-frame-round-trip-gap
```

Both verifier modes print `PASS_G20_FRAME_ROUND_TRIP_GAP`. The package
check prints `PASS_REGISTERED_RESEARCH_PACKAGE`. One mode takes about 80
seconds. The 512 three-bit dependency controls, the unit channel, the
orthogonal images, and the off-route rank-1 bank are required failures
of a broken pairing routine.

`python3 -B scripts/research_selected_baseline.py` is binding orientation
only. No Lean, Docker, or selected-frontier replay was run.

## Limits

Member exits into an occupied bank are not in this census. The singleton
channel is not a rewritten schedule. Native admission, the caller, the
compiler, and the five framework assumptions remain. The route moment
`Σ_r n_r r^t` is the published edge weight, not a new κ calculation.

## Open next questions

- Can a published exit of a group member into an occupied compatible
  bank raise the boundary rank? The non-member census does not answer it.
- Can the six frame-1 `ADD`s of helper 222 be retargeted onto frame 517
  with a finite route and restoration bill? The pairing alone is not
  that word.

## Credit

The word, the routes, and the open role question are Ali Romman's
PR #5679 and PR #5708. The common-frame obstruction is Nick Petalas's.
Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.
