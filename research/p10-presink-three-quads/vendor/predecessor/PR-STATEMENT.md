κ = 7.69556690340075e-4

This conditional finite construction improves PR #320 at immutable commit
`1b37957d1520c80b6ea796bf418e52be5109c2d4` from 7.69553898621543e-4 to
**30782267613603/40000000000000000 = 7.69556690340075e-4**.

Four `kernel_setup` frames are retimed after early restoration and before the seven terminal sinks:
three rank-8 frames become rank 9 and one rank-13 frame becomes rank 14. The reorder selection retains the same 133 scalar incidences and histogram delta; 24 equal-cost placements
use rank-19 anchors instead of rank-18 anchors. The pre-sink stage preserves the scalar/COPY sequence exactly;
the completed pipeline preserves the scalar map, entrances, endpoints, completions, R = 8,223 and literal
stock 658,290. The exact one-stage histogram delta is `{1:+12,2:-8,8:-3,9:+3,13:-1,14:+1}`.

The self-contained verifier regenerates all mandatory stages from an immutable archived PR #320 dependency,
checks every frame/source-span/reflected-ledger obligation, replays all scalar and dirty columns, checks
prime/chart/bank/global/finite obligations, and certifies the claim with both rational moment engines,
adjacent-grid rejection and all 47 outer constraints. `README.md` provides the command and
`PRESINK-PROOF.md` details the new stage. The inherited conditional theorem interfaces remain assumptions.

Prepared with OpenAI Codex assistance, building on Chafik Boukhalfa's PR #320, DreamingOfClouds' PR #315,
Rohan Arun's descent and constructed-frame methods, and all authors credited in `NOTICE.md`. Apache-2.0.
