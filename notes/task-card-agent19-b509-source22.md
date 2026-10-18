# Local task card (autoresearch.md section 3)

Task ID / proposed scope key: `bit-helper-contract` (drawn track `bit-mechanisms`,
chooser nonce `739c0098274f69cfc25fd435de0a325c`), refined to
`R439-B509/source22/lower-frame/inverse-column-invariant`.
Base commit; exact predecessor and dependency heads: base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`; predecessor [PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368) head
`6ae784908c57f3aa5a2165d382b21a40accdf7a6` (r439-bblock-frame-barrier);
second predecessor [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) head `f247c4e17b19e55c0db0ec8a1b660fd118adf014`
(r439-source19-dual-frame-obstruction); frozen word
`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`, SHA-256
`e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`.
Concrete object and question: on the fixed eleven-wire F509 map of R439 phase-B
block 509 (registers [17,22,33,38,50,60,67,77,87,92,468]), can any reversible
XOR circuit with retained monotone common-frame operand promotion leave
exceptional source 22 in a proper rational subframe of F509 and lower the
complete paid-frame moment (0<a<1), including carriers, continuation and
literal inverse cleanup? Or does the inverse-column frame invariant force
every exit to F509?
Scope status: refined (the drawn card's semantic-D H2/K question is already
covered by [PR1194](https://github.com/CrocSwap/integer-mult-bounds/pull/1194)/PR1311 and adjacent work; this is the concrete open request
in the handoffs thread https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18911407
and the open next question of [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511)).
Existing restriction being changed / claim audited: [PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368) leaves blocks 508
and 509 open because of exceptional sources 19 and 22; [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) closes only
B508/source 19 and names B509/source 22 as the remaining question.
Method; explicit parameter ranges/candidate alphabet: exact rational span
geometry over Q^8 and exact binary inversion over F2 on the pinned block map;
all finite circuit lengths; no synthesis search. The all-length invariant of
[PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) audit.md Section 3 is applied to a separately pinned boundary.
Nearest overlapping PRs and why this adds something: [PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368) (forward bounds,
eight blocks; leaves 508/509 open), [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) (closes B508/source 19 only; open
next question is exactly this). [Discussion 1476](https://github.com/CrocSwap/integer-mult-bounds/discussions/1476), [discussion 1503](https://github.com/CrocSwap/integer-mult-bounds/discussions/1503) and [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511) claims concern
helper-SWAP/three-cycle/dual-frame questions on other objects.
Optimistic full cost budget; required observable improvement: no construction;
acceptance is the fully priced obstruction itself (all eleven exits forced to
F509, single-climb invoice minimal for 0<a<1, continuation and cleanup
accounted), or an exact recorded obstruction if the invariant does not close.
Success evidence; falsification test; time/compute cap: stdlib verifier with
positive fixtures and failure controls (corrupt inverse bit, wrong
orientation, singular map, frame descent, one-sided operand hosting);
falsify by exhibiting a legal circuit or endpoint frame violating the claimed
forced exits. One session; verification in the final quarter.
Predecessor authors; intended artifact and reproduction command: Arham Tahir
([PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368)), Andrey Mas ([PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511)); contributor Aaron Wang / navinor, with help
from opencode. Artifact: research/r439-source22-dual-frame-obstruction/;
reproduce `python3 -I -O -B research/r439-source22-dual-frame-obstruction/verify.py`.
