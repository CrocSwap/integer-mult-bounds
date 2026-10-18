# Four mixed affine targets in a four-register bit model

This is a seed-pinned construction search in the noncommutative group algebra
of AGL2(F2). It restricts the paid alphabet to four affine labels and tests
whether a mixed four-target tuple can beat its direct ten calls. The closed
PR #1333 theorem gives cost six when all rank-one affine labels are available;
this experiment asks how much this fixed four-label subset costs.

The paid labels are:

* a(x0,x1)=(x0+x1,x1)
* b(x0,x1)=(x0,x0+x1)
* tx(x0,x1)=(x0+1,x1)
* ty(x0,x1)=(x0,x1+1)

The target is diag(h,h^-1,tx,ty), with h(x0,x1)=(x1,x0+1) and
h^-1(x0,x1)=(x1+1,x0). A paid call is D_N(g)=I+([g]+[1])N for any rank-one
idempotent N in M4(F2). Arbitrary dirty registers are allowed. Free GL4(F2)
mixing is represented by conjugating the idempotents while moving scalar maps
through the paid gates; augmentation forces the net scalar map to identity.

## Cost screen

The homogeneous 3-by-3 affine representation maps the four target blocks to
displacement ranks 2, 2, 1, and 1, hence rank six total. Each paid generator
has rank-one displacement and each register coefficient has rank one, so one
call can alter the displacement rank by at most one. The direct construction
uses ten calls, leaving at most four calls above this optimistic floor before
any physical, recursive, helper, frame, copying, hosting, or restoration cost.
This local finite model cannot itself change the selected kappa. The full
rank-one affine alphabet in [PR #1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333)
has exact minimum six for this target; the current four-label subset is
strictly smaller and is the changed hypothesis tested here. The finished
claim for that theorem is [Discussion #1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317).

## Exact q=6 result

verify.py enumerates all 120 rank-one idempotents in M4(F2) and all four
labels (480 factors). Any six-call identity from this target must lower the
displacement rank at every step. The exhaustive lowering frontiers are
recorded in CERTIFICATE.json; the search reaches no rank-one state after five
drops, so no six-call word exists in this declared model.

The certificate includes hashes of the complete unique-state frontiers. The
verifier also checks the direct ten-call positive control, a deleted-call
negative control, and a wrong-label negative control. All arithmetic is exact
over F2.

## Exact q=7 result

A seven-call word must have exactly six rank drops and one neutral step:
the target starts at displacement rank six, each factor changes rank by at
most one, and seven steps must end at zero. q7_trajectory_search.py covers
all such trajectories, allowing the neutral step at any position. The complete
frontiers are in Q7-OUTPUT.txt:

| Depth | Incoming states | Next states | Neutral unused | Neutral used |
|---:|---:|---:|---:|---:|
| 1 | 1 | 352 | 112 | 240 |
| 2 | 352 | 15,368 | 960 | 14,408 |
| 3 | 15,368 | 58,352 | 656 | 57,696 |
| 4 | 58,352 | 16,772 | 32 | 16,740 |
| 5 | 16,772 | 164 | 0 | 164 |
| 6 | 164 | 0 | 0 | 0 |

There are no length-six prefixes in the complete rank-compatible search,
so no seven-call endpoint is possible. This is a necessary-condition
obstruction in the homogeneous affine representation and therefore excludes
an exact group-algebra word in the declared model. Combined with the rank-six
floor and the direct ten-call word, the minimum with this four-label subset is
between eight and ten calls. The exact minimum is unresolved. PR #1333 allows
every rank-one affine displacement as a paid label and proves minimum six;
therefore any six-call attaining word from that theorem must use a label
outside this restricted set. No result here applies to the larger alphabet.

Run the finite trajectory search with:

    python3 -I -B research/affine-mixed-four-targets-seed5638/q7_trajectory_search.py

The recorded run took about ten minutes. The q=6 verifier checks the pinned
q=7 script/output hashes and frontier summary; rerunning this command checks
the full q=7 enumeration from scratch.

## Reproduction

    python3 -I -B research/affine-mixed-four-targets-seed5638/verify.py

Expected marker: PASS_AFFINE_MIXED_Q6_OBSTRUCTION. The output includes the
certificate SHA-256.

## Pins and overlap

* Accepted selector seed: 5638c49abc39ff4644ef875d73a20996
* Track/task: bit-mechanisms / bit-new-register-model, catalogue revision 3
* Base commit: 0b1cccf86e2f5132ed286a26ef0a681a495740ea
* Selected-result SHA-256: 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32
* Source hashes: SOURCES.json
* Active claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/1727
* Review PR: https://github.com/CrocSwap/integer-mult-bounds/pull/1745 (open)

The final pre-submission overlap scan completed at 2026-10-14 08:28:13 UTC: it
covered 419 open PRs and 375 Discussions with complete pagination and no warnings. Direct predecessor [PR #1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333)
(closed; head 7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2) proves the exact
six-call optimum for the full rank-one affine alphabet and names restricted
coordinate CNOT/translation alphabets as a next question. This package fixes
the four labels {a,b,tx,ty} and one four-register target tuple. Open PR #1711
is a two-target affine minimum; open PR #1716 is a restricted three-register
AGL2 triple. Discussion #1738 is a concurrent three-register UT3 central-pair
claim with labels {x,y} and a full group-algebra radius search. Those have
different target tuples, register counts, groups, and methods. Cycle 1's open
[PR #1733](https://github.com/CrocSwap/integer-mult-bounds/pull/1733) concerns
rational address relations rather than this binary-affine label restriction.
Active Discussion #1727 is this task's separate four-register tuple with
standalone translations; it was the original coordination claim for this run.

The direct ten-call word and the interval 8..10 provide no kappa improvement.
No physical supplier or recursive charge was established. No independent
human review is claimed. Prepared with substantial OpenAI Codex assistance in
framing, finite enumeration, verifier implementation, and writing.

## Open next questions

1. Can an exact eight- or nine-call word realize the same tuple? Any positive
   candidate needs full formal group-algebra replay and full interface pricing.
2. Can another four-register mixed affine tuple yield a real paid-call saving?
   A distinct target would need its own optimistic rank screen and complete
   helper, copying, hosting, recursive, frame, precision, and restoration bill.

The q=6/q=7 obstruction above is the complete stopping point for this seed;
no q=8..10 search was performed.
