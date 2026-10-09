# Shrunk lifted frames with saturated deferred readouts

Conditional **κ = 110591581647/10¹⁵ = 1.10591581647×10⁻⁴**, about
**1.19920% above PR114** (1.09281094468×10⁻⁴), 1.35%
above PR120 and 1.89% above PR118. The complex side still binds.

This package keeps PR114's complete construction: PR117's immutable
91,770-addition complex DAG (eumemic), the same carrier matching and 28,705
dirty roles, PR110's lifted binary frames and deferred readouts, and PR114's
saturated placement with priority 2^dim / reached_targets². One step is new.

## Shrunk frames

PR110's frame contract asks for each addition x a nondegenerate frame U_x with

    label(x) + Σ_{p → x} U_p  ⊆  U_x  ⊆  lifted kernel K_x^⊥,
    U_x ⊆ U_t for every successor t.

The lifted kernel is the largest choice. The inherited label fallback is
another. Every role pays one child per strict increase of its frame chain, with
cost t·log(m/t) in the moment for an increase t. That function is subadditive, so two
small increases cost more than one merged increase of the same total.

One forward pass in chronological order considers the minimal span
Lb_x = label(x) + Σ U_p. Suppose Lb_x is nondegenerate, smaller than U_x and contained in every
successor frame. Then U_x is replaced by Lb_x if that lowers the local
one-child cost of the role chains holding x. In practice, an increase at x is
delayed and merged into the next increase. The pass shrinks **16,031**
frames. Shrinking stays monotone. Lb_x contains every predecessor frame, and
successors are processed later against the updated frames. Deferral
candidates use the shrunk start frames.

| Complex network (PR117 DAG) | PR114 | This |
|---|---:|---:|
| roles / carrier links | 28,705 / 71,185 | 28,705 / 71,185 |
| shrunk frames | — | 16,031 |
| deferred readouts | 4,706 | 4,706 |
| strict complex saving | 109305097/10¹² | **110616162/10¹²** |
| κ | 1.09281094468e-4 | **1.10591581647e-4** |

W = 124,390,992, recursive rank mass 71,647,349,312 and maximum child 574 of
576 are unchanged. Only the split of each role chain into children changes.
Every copied centre, exterior, source/target front, data projector and
endpoint correction remains paid. The bit supplier is unchanged:
Swapnil Jain's round-seven word, stopped saving 1240189553/10¹³.

## Checks

```sh
python3 research/shrunk-frames/verify.py
```

The verifier regenerates everything in a temporary tree. It pins the
shrunk-frame count and all inherited graph counts. Section D of
`complex_deferred.py` rechecks each role chain against the actual shrunk frames:
start, every gate, linked continuations, root frame and F. It checks that each
chain is nested and each frame nondegenerate. It also checks every deferral
frame and target chain. Arbitrary-scratch replays are run over Z/(2^61−1).

The independent reflection audit consumes the same frames. It covers the
literal inverse, sign-negate and bank-swap word and the complemented frame
incidences. It also checks the paid histogram in both directions, the
bounded readout chunks and three mutations. `certificate.py` recomputes both
moments exactly and rejects the next complex grid point. It also checks the
expanded scalar charge, all 47 strict constraints, seven margins and the next
κ grid point.

A new control loads PR114's frozen unshrunk profile, which is
`controls/pr114-complex-profile.json`. That profile contracts at PR114's saving
and fails at the new one.

All retained transfer hypotheses remain unchanged:
- simultaneous rational bases and opposite-bank factorization;
- stopped atom streaming and the ordinary wrapper;
- translated complex endpoint gauges and the exact odd-denominator grid;
- routing, recovery and prime selection;
- analytic estimates and the fixed-tape implementation.

The finite checks verify that the shrunk frames meet the stated contract. They
are not a new general theorem. This is a finite conditional witness, not an
unconditional theorem, a measured speedup or a global optimum.

Credits: eumemic (PR117 producer, PR114 saturated placement, reflection audit
and scalar charge, with Anthropic Claude and OpenAI Codex assistance); Avi
Eisenberg / ikeboy (PR110 deferred complex compiler, PR62); Rohan Arun
(PR111/113/116/118); icekylinx (PR104/115); Swapnil Jain (round-seven words,
lifted frames, deferred readouts); Zhihao Chen / jacklightChen; Aurel Prosz /
Paureel; RaD / hipotures; Douglas Colkitt; OpenAI and all inherited
contributors. Original notices and AI disclosures remain. The shrunk-frame
step was prepared by Joel Pulikkan with Anthropic Claude assistance.
