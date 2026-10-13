# Local sprint claim

- Track: complex supplier; OS assignment seed **20**, drawn once with
  `secrets.randbelow(100)` at 2026-10-13 07:29:52 UTC.
- Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
- Current accepted conditional saving at that base:
  `1661634653669567/1000000000000000000`, from #799/#741 with #589/#555.
- Chosen object: the historical #626 **CK** scalar program, same-source,
  same-frame consecutive nonunit additions. Seed parity selects CK over JP8.
- Hypothesis: carrying coefficient work through a signed source read,
  `b = 2^v (2^u a + epsilon)`, epsilon in {-1,+1}, can save primitives
  beyond reset, power-only reuse, and positive-only source reads.
- Bounded domain: all eligible consecutive coefficient pairs in both CK
  orientations; u,v in [-16,16]. Preserve target order, frames and logical
  macros; clear work at every run boundary. Charge every primitive.
- Expected deliverable: executable finite circuit, exact source/cost receipt,
  complete scalar endpoint and prefix replay, negative controls, and a scoped
  proof/accounting note. No new kappa is expected or claimed.
- Planned finish: 2026-10-13 08:20 UTC. Selection is limited to the first ten
  minutes of this 50-minute budget; final 12.5 minutes reserved for verification
  and handoff. Stop after this finite domain; one evidence-driven pivot at most.

Three candidates considered: (1) the chosen signed continuation mechanism,
(2) shortest single-macro coefficient circuits beyond bidirectional Horner,
(3) restored CK target-basis changes. Candidate 2 overlaps #837 and candidate 3
overlaps #807/#816. #769 covers CK power-only reuse; #811 covers positive
one-read transitions for JP8 and explicitly excludes signed transitions;
#830 transposes #811. Those contributions will be credited, not rediscovered
or silently combined. Fixed-order frame exclusions (#776/#815), read-exchange
searches (#775), and retired decoder searches are not reopened.

Coordination check: the open issue search found only #650 (a request to enable
Discussions), with no comments and no pinned sprint coordination issue. No
separate reservation issue was opened. Recent open PRs through #847 and targeted
signed/coefficient searches were inspected before this local claim.

Prepared for Joseph / AmazedBot (@amazedbot), with substantial OpenAI Codex
assistance. New files are Apache-2.0. No independent human review is claimed.

## Result and final local claim update

Completed the signed-read CK construction and exact bounded-domain verification.
Using accepted PR696 copy-initialized resets, subtraction saves **926 forward
real-component primitives across 202 transitions**, and **zero backward**
primitives beyond the same-domain positive-read comparator. The preliminary
clear-plus-add reset comparator was retired after it overstated novelty.
All 725 input columns in both orientations, 1,080,288 independent integer
one-read cases, 15 mathematical controls and six portable-package tests pass.
Prefix bounds rise to 43/63 bits, still within 192; no new kappa is claimed.

See [README.md](README.md), [EXPECTED.json](EXPECTED.json),
[ROUTES.json](ROUTES.json), and [VALIDATION.md](VALIDATION.md). The final
metadata check reached #856, with PR769/811 comparison heads unchanged.
No coordination thread exists to update. A clean patch and offline replay
bundle are the handoff because target push access and a writable fork are
unavailable. No PR was opened and no remote source or frontier was changed.

## Submission continuation

The user created `https://github.com/amazedbot/integer-mult-bounds` after the
initial patch handoff. Write access was verified on 2026-10-13. The contribution
is now being submitted as one focused PR from that fork. No circuit, receipt,
source pin or mathematical claim changed during this continuation. The final
metadata refresh through #858 found no duplicate; no coordination issue exists.
