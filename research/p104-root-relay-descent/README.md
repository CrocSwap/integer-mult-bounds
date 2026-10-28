# Conditional kappa 0.003127137: owned registers 770 and 771 descend through the frames of helpers 705 and 706, which no longer relay them

This package edits the word of [PR #6030](https://github.com/CrocSwap/integer-mult-bounds/pull/6030)
(DreamingOfClouds, merged on main, conditional kappa 0.003125804) and re-certifies it with the chain PR #6030 used:
PR #5827's own verifier (aliromman, head `05cd36e5af06d7a3790e30ce3f449fa89b853768`), loaded unmodified apart from the declared pricing literals.
The complete conditional kappa is **0.003127137**, tested at 0.0031271420; the exact raw crossing lies in
(0.00312714448252, 0.00312714448253) = (78178612063/25000000000000, 312714448253/100000000000000),
which is +1.333e-06 above PR #6030's raw crossing (0.00312581155791). The paid bill falls to
**66798 calls** (PR #6030: 66,834) at an unchanged 13444 productive targets and rank-mass surplus
760. Public inputs, owned fields, owned lifetimes and peak occupancy (770, 29, 31, 13) are unchanged;
the word has 22,828 events (PR #6030: 22,803; retained cap 26,000).

## The edit

The edit removes two relays. In PR #6030's word, owned register 771 is loaded at frame 541 (COPY from helper 151), moves
once to frame 594 and is cleared there; helper 706 reads it at frame 594 and climbs 594 -> 117 -> 534 -> 541, delivering the
content at each frame and exchanging with 151 at frame 541. Likewise owned register 770 is loaded at frame 549 (COPY from
791), moves to frame 593 and is cleared; helper 705 reads it there and climbs 593 -> 1047 -> 553 -> 549, exchanging with 791 at frame 549.

In the edited word the owned registers walk those frames themselves, downwards: 771 runs 541 -> 534 -> 117 -> 594 and 770 runs
549 -> 553 -> 1047 -> 593. Helpers 706 and 705 no longer carry the content; each keeps a single hop, 3 -> 541 and 3 -> 549, to
its unchanged final frame. The reads move onto the owned registers:
- 771 is read at frame 594 by helpers 139, 213, 490, 491 (formerly from 706) and 449, 568, 569, 575, 576 (formerly from 707 / 732),
  and at frames 117 and 534 by 629 and 231 (formerly from 706);
- 770 is read at frame 593 by 112, 182, 469, 471, 549, 561 (formerly from 703 / 704) and by 174 and 184, and at frames 553 and
  1047 by 169 and 206 (formerly from 705); at frame 549, helper 121 reads 791 (coefficient 1/2) instead of 705.
The relays' initial-frame (frame 3) pre-reads are re-solved: 10 frame-3 ADD events that paired readers against 705's and 706's
initial values are removed and 40 are added, against 703, 704, 707, 732, 568 and 623. To keep peak occupancy at 13, both owned
lifetimes are placed after the peak window: the INIT/COPY of 771 and 770 move from events 13463-13465 / 13452-13456 to
13620-13621 / 13640-13641, and their CLEARs from 13471 / 13462 to 15431 / 15425.

Only the itineraries of 705, 706, 770 and 771 change; every other MOVE is unchanged. The INIT, CLEAR, COPY and SCALE events are
identical as multisets; 35 ADD events are removed and 62 added, and the event list grows from 22,803 to 22,828 events.

Boundary charts changed by the edit: none. Paid-profile change vs PR #6030: rank 1: -2, rank 6: -2, rank 7: +2.
Credited helper-rank change: .
Every public input column, every signed native map and the physical caller are re-checked in full (see Verification).

`EDIT.json.gz` is the explicit edit list: boundary changes plus the new event list as copy segments of
PR #6030's program and literal events. `construct.py` (standard library only) applies it to PR #6030's word, taken from
`inputs/pr6030-WORD.json.gz` (authenticated against main's `research/p104-helper470-twin-rung-removal/WORD.json.gz`, Git blob and SHA256 in `SOURCES.json`), and regenerates
the complete decompressed `WORD.json.gz` payload byte for byte (gzip-container bytes may differ by platform; this comparison is
PR #6030's merged portability repair, kept with its `test_portability.py`):

```sh
python3.12 -I -B research/p104-root-relay-descent/construct.py
```

## Verification

```sh
python3.12 -I -O -B research/p104-root-relay-descent/test_portability.py
python3.12 -I -B research/p104-root-relay-descent/verify.py
```

`verify.py` authenticates PR #6030's word and the pinned PR #5827 package (`inputs/pr5827-source.tar`, per-file SHA256 and Git blob;
byte-identical to the archive in PR #6030's package) and its seven-deep source chain, asserts that the shipped `pricing.py` equals
PR #5827's `pricing.py` plus the literal edits in `PRICING-EDITS.json` (claim, previous claim = PR #6030's, the paid-call count and two labels),
regenerates the word, and runs PR #5827's chain unchanged: exact replay and storage inventory, all 799 input columns with a separate
transpose, every signed native map, 208 main adapters, 1,124 helper normalizers, the exact physical caller, the complete invoice, both
interval engines, compiler and 54 strict plus 4 functional outer checks, a check that PR #6030's full profile fails at the new claim,
rejection controls, and the committed `RESULT.json`. `--part build` runs the authentication, regeneration and replay only.

## Conditions inherited

The five framework assumptions retained by the P104 line (native all-column implementation, owned erasure, uniform compiler closure,
precision and fixed-tape costs, claim accounting) and PR #5827's own checker are inherited unchanged. Author checks are not
independent human acceptance. The finite local word is materialized; the large uniform word and rounded multiplier are not. No merge,
closure or selected-frontier change is requested.

## Credits

The base word is PR #6030's (DreamingOfClouds, helper 470's frame-593 rung removal), an edit of PR #5907's word (DreamingOfClouds,
helper 468's frame-593 rung removal), itself an edit of PR #5827's word. The payload comparison in `construct.py`/`verify.py` and
`test_portability.py` are the maintainer portability repair merged with PR #6030 (Douglas Colkitt, with OpenAI Codex assistance).
The verifier chain is Ali Romman's (aliromman, PR #5827, with substantial OpenAI Codex assistance), built on PR #5811
(Mason Hale), PR #5786 and the earlier lineage back to PR #5565 (Pierre-Loic Doulcet), with all retained source notices in the pinned
archive. This package contributes only the edit above and its packaging.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## Open next questions

- Does an independent reviewer confirm the edit list, the regenerated word and the full chain? First step: run `construct.py` and
  `verify.py` as above, then compare the changed itineraries with PR #6030's word.
