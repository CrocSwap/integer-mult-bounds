# PR589 fixed-option cross-section A/B transport-pair census

## Question and scope

PR #1345's [transport atlas](https://github.com/CrocSwap/integer-mult-bounds/pull/1345), at head `b54a856aa79857d91cd5d65f8f7144e26c8c084f`, fixes the PR589 word and checks single transports and every within-section shared-register pair. It explicitly leaves out a simultaneous A transport and B transport that share a register. This package checks the subset formed from PR #1345’s independently generated fixed-boundary option lists on the fixed PR589 word. It does not claim to close the entire cross-section class, because a pair could make additional frame choices feasible through the changed boundary.

The domain contains one movable A operation and one movable B operation per assignment, with at least one register shared by the two operations. The slot/frame option lists are generated against the predecessor atlas’s fixed counterpart-stage boundary; this census does not expand a move’s frame options when the paired move changes that boundary. It freezes the gate multiset and operands, scatter, start/final frames, D section, rebuilt literal-reverse C section, and retained-output COPY frames. Each move uses the exact commutation window and the legal catalogue/closure frame options from the predecessor transport atlas. The combined A→B register chains are then rechecked, including the boundary climb, before scoring.

The precomputed domain is 336 shared registers, 6,151 cross-section operation pairs, and 88,181 non-home frame/slot assignments. An assignment touches at most four register chains. This price makes a full exact census feasible. It does not cover three or more simultaneous transports, disjoint cross-section pairs, other gate orders, or structural rewrites.

## Exact objective

The score is the full per-register paid frame-chain moment at the exact PR589 bit saving

`c = 1733427039589844234749 / 10^24`.

The pinned engine returns outward rational intervals; no floating-point comparison decides a result. An assignment is labeled improving or worse only when the entire interval has the corresponding strict sign. Identical paid profiles are reported as ties; interval overlaps for different profiles are reported as unresolved. Illegal A→B nesting and retained COPY-frame changes are counted separately.

The selected assembly at this base is complex-limited (`a_c = 0.0016754627 < a_b = 0.0017334270`), so this bit-side audit cannot itself establish a larger selected κ. It closes only the first-order cross-section pair search within the predecessor’s fixed-boundary option sets. Whether a paired boundary change enables additional frame options remains open.

## Result

The exhaustive fixed-option census found 76,840 assignments with the baseline paid profile and 11,341 strictly worse assignments; it found zero improving, illegal, or unresolved assignments. The exact counts and representative cases are in [`result.json`](result.json). Two combined assignments were applied to the literal word, C was rebuilt, and the paid profiles matched the frame-chain predictions: one profile tie and one strict loss. The scope claim is not a claim about boundary-adaptive frame options, larger interaction sets, or a global minimum.

## Reproduce

From the repository root, run:

```sh
bash research/bit589-fixed-option-cross-pairs-seed16/verify.sh
```

Expected final line:

```text
PASS_BIT589_FIXED_OPTION_CROSS_PAIRS seed=16 pairs=6151 assignments=88181
```

The verifier uses the standard library and the exact source pins in [`SOURCES.json`](SOURCES.json). The interval engine must match its recorded SHA-256 before the program runs.

## Attribution

This extension adapts the exact move generation and outward-rational pricing method from PR #1345, prepared by Qwen3.8-Flash. It credits the selected bit supplier from PR #589 and its predecessors PR #555 and PR #589's cited construction ancestry. The cross-section combined-chain scorer, census, package, and verification were prepared with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

- Recompute the legal A and B frame options jointly when a paired move changes the last-A/first-B boundary on a shared register. This is the immediate unclosed case and could add assignments absent from the fixed option lists used here.
- Extend the joint option model to multiple simultaneous moves only after pricing the boundary-dependent state space.
- Independently review whether the full paid moment, including unchanged scatter tops, remains the right objective for any proposed extension; the current census binds the exact PR589 saving and fixed profile model.
