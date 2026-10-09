# Terminal-elided shrunk frames with saturated deferred readouts

Conditional **κ = 110875518403/10¹⁵ = 1.10875518403×10⁻⁴**, about
**0.257% above the pinned PR #125 parent**
(110591581647/10¹⁵ = 1.10591581647×10⁻⁴). The complex side still binds.

This package keeps PR114's complete construction: PR117's immutable
91,770-addition complex DAG (eumemic), the same carrier matching and 28,705
dirty roles, PR110's lifted binary frames and deferred readouts, and PR114's
saturated placement with priority 2^dim / reached_targets². The frame shrink
is PR #125 by Joel Pulikkan. The terminal-role deletion and source-time
redirect idea follows PR #122 by SovereignSteak. This candidate composes them
on the fixed PR #125 word; it does not claim either predecessor's mechanism as
new.

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

| Complex network (PR117 DAG) | PR #125 parent | This composition |
|---|---:|---:|
| physical roles / carrier links | 28,705 / 71,185 | 28,324 / 71,185* |
| shrunk frames | 16,031 | 16,031 |
| deferred readouts | 4,706 | 4,325 |
| terminal roles removed / direct updates | — | 381 / 1,167 |
| strict complex saving | 110616162/10¹² | **13862528107/125000000000000** |
| κ | 1.10591581647e-4 | **1.10875518403e-4** |

*The matched DAG's 71,185 links are retained; its `additions + roots - links`
role count is the pre-elimination count. The final physical word removes 381
terminal roles. Each is an ordinary deferred output role with no later
consumer. For a removed role with old scratch value z and incoming updates
uᵢ, the old pair of readouts contributes `-αz + α(z + Σuᵢ)`. The replacement
adds each `αuᵢ` to its target at the original update time. The independent
audit checks all 1,167 source-time updates, their frames and signs, and two
modular dirty-scratch replays.

W = 122,848,704, recursive rank mass 70,758,991,424 and maximum child 574 of
576. The deficit remains 1,862,080. The full paid child histogram is
reconstructed from both the forward and reflected frame traces. Every
surviving copied centre, exterior, source/target front, data projector and
endpoint correction remains paid. The bit supplier is unchanged:
Swapnil Jain's round-seven word, stopped saving 1240189553/10¹³.

## Checks

```sh
python3 research/shrunk-frames/verify.py
```

The verifier regenerates the PR #125 parent in memory, checks its frozen
profile and reflection receipt, writes a transient parent word, and builds the
combined output in a temporary tree. Section D of `complex_deferred.py`
rechecks each parent role chain against the actual shrunk frames: start, every
gate, linked continuations, root frame and F. It checks each chain is nested
and every frame is nondegenerate.

`terminal_elision_audit.py` independently rediscovers the eligible terminal
roles and rebuilds the simultaneous target schedule. It checks every event in
chronological order, source-time snapshots, the exact local dirty-scratch
identity, modular replay, forward and reflected frame transitions, and the
complete child histogram. Four event mutations are rejected. `certificate.py`
recomputes both moments exactly and rejects the next complex grid point. Its
scalar-group bound explicitly includes all 1,167 direct updates; it checks all
47 strict constraints, seven margins and the next κ grid point.

Frozen comparison profiles are `controls/pr114-complex-profile.json` and
`controls/pr125-complex-profile.json`. The PR #125 parent profile contracts at
its own saving and fails at the composed candidate's larger saving.

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
and scalar charge); Joel Pulikkan (PR #125 shrunk-frame step, Anthropic Claude
assistance); SovereignSteak (PR #122 terminal-role elimination); this fixed-
parent composition, independent audit and certificate integration were
prepared with OpenAI Codex assistance. Avi
Eisenberg / ikeboy (PR110 deferred complex compiler, PR62); Rohan Arun
(PR111/113/116/118); icekylinx (PR104/115); Swapnil Jain (round-seven words,
lifted frames, deferred readouts); Zhihao Chen / jacklightChen; Aurel Prosz /
Paureel; RaD / hipotures; Douglas Colkitt; OpenAI and all inherited
contributors. Original notices and AI disclosures remain. The shrunk-frame
step was prepared by Joel Pulikkan with Anthropic Claude assistance.
