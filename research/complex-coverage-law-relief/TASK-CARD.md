# Local task card (autoresearch.md section 3)

Task ID / proposed scope key: `complex-new-helper-inventory` / `5868e5281a1e63d41a22`
(chosen by `scripts/choose_research_task.py`, track `complex-mechanisms`, OS-random
nonce `6ddf1b6647d8c5131033b16d30f0045b`).

Base commit: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.

Exact predecessors / dependency heads (read-only, not vendored):
- https://github.com/CrocSwap/integer-mult-bounds/pull/1240 head
  `1e136b8c4a552050820334ad113628775182f08c` — coverage-law moment model and the
  incumbent-word packing ceiling `a < 0.001690054109089` (semantics reference only;
  this package's arithmetic is written independently).
- CrocSwap/integer-mult-bounds#1012 coverage identity (via
  https://github.com/CrocSwap/integer-mult-bounds/pull/1240 and
  `research/community-batch1099-audit`): paid rank mass = `(m - unpaid) * W +
  centre * N` per template.
- `research/heterogeneous-owner-assembly/` (Ali Romman) — frozen provider-catalogue
  mixture bound; its controls already reject the U10 delta (CrocSwap/integer-mult-bounds#987)
  and the R489/R480 helper-inventory changes (CrocSwap/integer-mult-bounds#1004 and
  CrocSwap/integer-mult-bounds#1005), so new cost interfaces are outside it.

Concrete object and question:
The hosted nine-stage coverage law of the selected line: width `m = 73`,
`w = families/stages = 896/9` live families per call, centre charge `64` per call,
`unpaid = 1` coordinate per family, halving-guard idle rank cap `R = 51`, with the
selected CrocSwap/integer-mult-bounds#1094 local word
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` (paid mass 5586 per call). Question:
which changes of the local cost interface (unpaid coordinates per family `u`,
centre charge `c`, families per call `w`, and paid-word excess spend `E`) are
*necessary and which are sufficient* for the optimistic whole-construction moment
to admit saving `a >= 1/99`, and what are the exact thresholds and trade-offs
between them?

Scope status: **refined**. The card asks for a new physically realizable helper
inventory; this session runs the card's stated first experiment (the complete
optimistic child histogram, rejecting routes without headroom) on *changed
coverage-law interfaces* instead of proposing a full new contract. Reason: the
optimistic screen is what decides whether any contract with given interface
parameters can have headroom at all, and
https://github.com/CrocSwap/integer-mult-bounds/pull/1240's open question asks
for exactly this quantification on the coverage-law side.

Existing restriction being changed (or exact claim audited):
The coverage-law parameters `(unpaid=1, centre=64, families=896, stages=9)` and
the paid-word excess spend of the incumbent word; audited claim is the optimism
of the relaxation itself (fractional idle counts, all repackings allowed).

Method; explicit parameter ranges / candidate alphabet:
Independent stdlib exact-rational interval moment (atanh-chain logarithm, Taylor
exponential with Lagrange remainder, outward rounding), bisection ceiling in `a`.
Domain: `u` in {1,...,12} integer and the exact continuous threshold in `(1, 12]`;
`c` in [0, 64] rational; `w` in [50, 2000] families per call at `stages = 9`
(families integer 450..18000); paid-word excess spend scaled continuously down
from the incumbent's. Positive control: reproduce
https://github.com/CrocSwap/integer-mult-bounds/pull/1240's incumbent ceiling.
Failure controls: mutated profile, halving-guard violation, over-paid word.

Nearest overlapping PRs and why this adds something:
- https://github.com/CrocSwap/integer-mult-bounds/pull/1240 screens one fixed
  word's repacking ceiling and states the coverage-law change as an open
  direction; this package quantifies that direction exactly.
- https://github.com/CrocSwap/integer-mult-bounds/pull/1264 screens 14 open
  claims' words at the *unchanged* coverage law; it does not vary interface
  parameters.
- https://github.com/CrocSwap/integer-mult-bounds/pull/1272 (director, pending)
  narrows this card with a ceiling screen; this package is the screen applied to
  changed interfaces, consistent with that narrowing.
- https://github.com/CrocSwap/integer-mult-bounds/discussions/1265 covers
  within-group idle repartitions at fixed coverage law.

Optimistic full cost budget; required observable improvement:
The relaxation already grants fractional idle, all idle at the cheapest admissible
rank and no extra charges; thresholds computed here are necessary conditions for
any realized construction (a failing relaxation falsifies the route) and optimistic
sufficiency only (a passing relaxation is not a contract). Observable improvement:
certified brackets showing `relax(1/99) < 1` or `> 1` at each named threshold.

Success evidence; falsification test; time/compute cap:
Success = exact interval reproduction of the incumbent ceiling plus a threshold
table with certified brackets. Falsification = any control mutation accepted.
Compute cap: minutes of stdlib runtime; no network beyond the board/PR checks.

Predecessor authors; intended artifact and reproduction command:
Douglas Colkitt (https://github.com/CrocSwap/integer-mult-bounds/pull/1240,
https://github.com/CrocSwap/integer-mult-bounds/pull/1264 and the coverage-law
model; CrocSwap/integer-mult-bounds#1012 identity), Ali Romman
(heterogeneous-owner-assembly), the selected-line authors (see
`certificates/selected-result.json`). Artifact:
`research/complex-coverage-law-relief/` with `verify.py`; reproduction
`python3 -I -B research/complex-coverage-law-relief/verify.py`.
Contributor: Navinor, with help from opencode.
