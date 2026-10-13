# Claim and scope

- Track: complex supplier. Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
- Accepted conditional saving at that base:
  `1661634653669567/1000000000000000000` (#799/#741 with #589/#555). Unchanged.
- Object: the historical #626 **CK** scalar program; runs of consecutive
  nonunit additions with the same source and frame.
- Hypothesis: carrying coefficient work through a signed source read,
  `b = 2^v (2^u a + epsilon)`, epsilon in {-1,+1}, saves primitives beyond
  copy reset, power-only reuse and positive-only reads.
- Domain: all eligible consecutive coefficient pairs in both CK orientations;
  u,v in [-16,16]. Target order, frames and logical macros preserved; work
  cleared at every run boundary; every primitive charged.

## Overlap

#769 covers CK power-only reuse; #811 covers positive one-read transitions for
JP8 and excludes signed transitions; #830 transposes #811. Shortest single-macro
lowerings (#837) and CK basis changes (#807/#816) are distinct and not
combined. Fixed-order frame exclusions (#776/#815), read-exchange searches
(#775) and retired decoder searches are not reopened. Open PRs through #858 and
targeted signed/coefficient searches found no duplicate; this is not a claim
to have read every file of every open PR.

## Result

With accepted PR696 copy-initialized resets, subtraction saves **926 forward
real-component primitives across 202 transitions** and **zero backward**
beyond the same-domain positive-read comparator. An earlier clear-plus-add
comparator overstated the gain (1,308 / 456) and was retired.

Costs of the change: the literal positive prefix rises to 43/63 bits (within
192), forward precision rises from 3 to 4 fractional bits (provider maximum
unchanged at 8), and private work stays live across target updates inside a
run, in its dedicated registers. Admitted into a fresh PR626 replay with
kappa reproduced exactly; no new kappa is claimed.

Prepared for Joseph / AmazedBot (@amazedbot) with substantial OpenAI Codex
assistance; the precision check, control tightening and PR626 admission were
added with Anthropic Claude assistance. New files are Apache-2.0. No human
review is claimed.
