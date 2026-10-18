# Complex supplier claim — seed 22

- Start: 2026-10-13 08:05 PDT. Planned finish: 09:05 PDT. Stop experiments by 08:50 and reserve the final 15 minutes for verification and handoff; finish sooner if verification is complete.
- Fresh OS assignment: `secrets.randbelow(100)` returned **22**, complex supplier.
- Exact fetched base: `007664306fff84fbb1c9a1b4053b69f439764034`.
- Current selected result: PR890 U8/T21, conditional kappa `0.001661957774647029`; unchanged by this work. Its construction, selected source pointers and maintainer review were read.
- Three narrow candidates: (0) another factory diagonal gauge (already bounded by PR949); (1) joint Horner windows of up to four distinct sources in historical X4 nonzero-frame backward runs; (2) two-scratch single-coefficient synthesis after PR882 (higher search cost and an extra scratch clearing bill). Seed `22 % 3 = 1` chooses candidate 1; `3 + 22 % 3 = 4` sets the maximum fan-in.
- Object: the byte-pinned PR799 backward scalar program retained under `research/complex-x4-compensation-pairs/inputs/`. Candidate windows are consecutive ADDs with one common target, one identical nonzero frame and 2–4 distinct immutable sources. No aliases or crossing non-scalar events.
- Method: shared binary Horner preparation at a common denominator in the existing coefficient stream; charge every copy, source addition, shift, accumulation and clear. Exact interval scheduling maximizes savings among disjoint windows that beat redundant-clear removal alone.
- New class: PR945 handles pairs. This permits simultaneous three/four-source work, whose shared shifts and accumulation can beat every partition into pairs. Not merely a longer search of the pair class. Credit PR945's mechanism and 13,072 saving separately; no assumption of additive savings.
- Optimistic complete arithmetic pricing before implementation: backward pair-only saving 13,072; maximum-four saving 22,048 real-component primitives over PR696. Forward is retained, so it will bind the orientation maximum. This is not a kappa gain.
- Deliverable: exact emitted words, complete scalar endpoint/prefix accounting, an independently implemented census/selection/replay, source pins, adverse controls, and a focused finite-construction PR if verified. One completed 2–4 window census is the stopping rule.
- Coordination: no pinned sprint issue found (open issues 650 and 913 are unrelated). Local claim used. Refreshed open PRs through #966 and all-state Horner search. PR945 at `a3245bf22fa2a2eb778b11128cbc605b130d737f` is the direct comparator. PR751/830 cover historical JP8 fan-in; PR769 CK ladders; PR932/961 zero-frame target forests; PR949 factory scales. These are distinct and not composed.
- Scope: only this new research package. No changes to upstream, selected certificates, production emitters or predecessor packages. Inherited uniform, physical/frame/phase, hosting, precision/tape and analytic obligations remain. Subagents stay within this claim.
- Attribution: prepared for ToikY with substantial OpenAI Codex assistance; Apache-2.0. Full predecessor credits and exact verification limits will accompany the result.

## Result update

The complete 16,431-window census finished. The chosen 1,174 disjoint windows
reduce backward scalar primitives from 143,674 to 121,626: 22,048 saved,
including 8,976 beyond PR945. The unchanged forward count 143,658 still binds;
there is no further orientation-maximum gain over PR945 and no new kappa.
Two exact engines, all 737 input columns, nine independent controls and seven
package test groups pass. Typed physical/hosted integration remains open.

Final overlap refresh through #971 found no duplicate of this extension;
PR945's head is unchanged. Main advanced to
`bbc600db2fc15007b7c914f4f2b2ed55fa909c87` (PR942 U8/T37). All nine historical
input pins are unchanged. [Validation](VALIDATION.md) records the checks.
The completed contribution is on
[codex/complex-supplier-seed22](https://github.com/ToikY/integer-mult-bounds/tree/codex/complex-supplier-seed22/research/x4-four-source-horner).
