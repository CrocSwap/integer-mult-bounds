# B2 NOTES: climb-neutral skeleton atoms (K-triangle gross value)

VERDICT: LOCAL-PRICE (knowledge result). ship=false. Scope: the K-triangle atom (#622) on the cold14 skeleton, priced with the
package's own moment engine (pr575 engines/moment.py, certify(H,73,7168)), reproducing b617=1.637861934e-3 exactly.
Premise "climbs ate 99% of the gross" is FALSE. Ceiling of the whole atom family at this price is ~+0.6-1.0% b, reachable only if
every conflict is free; realistic recoverable ~+0.2-0.4%. Below the +1% / kappa 1.64040e-3 bar. No heavy job was run.

## 1. Ledger #617 -> #622 (price = b % when the local paid-profile delta is applied to all 72 calls; scripts price.py ladder*.py climb.py)
Per-call local data come from the #623 verify work dir (r40/base/work/k492b/*/FULL-WORD.json.gz reports; jp8 chain, 504 shadow vs 492).
jp8 local paid mass per call: 504 pre-ends 6000 -> K pre-ends 5904 (-96) -> final 5758 (617 final 5812; net -54).

| line | local mass/call | b effect |
|---|---|---|
| 12 helpers removed, NET of their own K-read climbs (pre-ends 6000->5904) | -96 | +0.321% (0.0267%/helper) |
| climb charge of 48 rewired reads (108 ideal mass -96) | +12 | -0.17..-0.21% (the "climb" line) |
| => ideal gross, climbs free | -108 | ~+0.52% = 0.043%/helper (NOT 0.1-0.2%) |
| frame_regroup (24 changes {1:-3,2:+3,3:-1}) | 0 | +0.095% (gain, climb mitigation already in #622) |
| removed helpers' own hyperplane ends lost (46->34) | +12 | ~-0.05% (0.0041%/end) |
| 6 second cold ends (S b.9) lost in blocks 0-2, 11-13 | +30 | -0.19% (0.0321%/cold end) |
| atm3->ck provider swap, idle-remainder packing, dispatch | | ~-0.08% (model +0.044% vs true +0.0146%) |
| TRUE net | -54 | +0.0146% |

Width check: jp8 widths 4:36->30, 7:48->36, 9:260->266. Sum psi -153.6/8729 = -1.76% (12 width-7 removed, 6 cold 4->9 back).
Removed packet copies were already width-7 (hyperplane-ended), so the gross is psi(7) not psi(9).
Price per unit: a cold end ~0.032% b (matches brief 0.03-0.04). A removed width-9-equivalent helper ~0.043% ideal, 0.027% net of its reads.

## 2. Climb anatomy / what ate the gain
Climbs ate ~38% of the mass gross (12 of 108 units), not 99%. The larger single eater is the lost S b.9 cold ends (0.19%).
Cause (checked in recipes): the forward absorption in cold_end needs the dead port q to be dead and frame-equal to g (PROOF-NOTE (a)-(c)).
In 617 the q's for blocks 0-2 and 11-13 are registers 61,29,21 and 93,85,53; these are exactly K-coordinate registers that the
triangle now reads leavers into (TRI-SCHEDULE reads list 20,21,28,29,60,61,84,85,92,93...). They stay live and rise in frame, so
absorption is illegal. Not a climb price but a liveness/frame conflict with the cold end.
Not done: classifying each of the 48 reads as forced vs avoidable (needs the per-read frames; CP-SAT model not built, since price caps below).
Scope check of #622's exhaustive claim: PROOF-NOTE only certifies exactness; the 6-block exclusion is stated as "do not admit", not proved forced.

## 3. Bounds on the climb-neutral design
- Free climbs on the 4 existing triangles: +0.17..0.21%. Restoring the 6 cold ends: +0.19%. Both: ~+0.4%, kappa ~1.642e-3 (needs no new loss).
- Extending to (p,+1) triangles (4 more, 12 helpers): ideal gross 0.52%, minus hyperplane ends 0.05%, minus S b.10 conflict
  (a lost S b.10 cold unit costs 0.032%; 4 triangles touching ~6 blocks = 0.19%) and climbs 0.2% => ~+0.1% net. All 8 triangles with
  every conflict free: 24 helpers x 0.043 = ~1.0% ideal; with climbs/cold conflicts as priced here ~0.2-0.5%.
- So reaching +1% b is not plausible from this atom family alone.

## Escapes (outside the scope of this negative)
1. A different q (or a different cold-end absorption) for blocks 0-2/11-13: a dead port that is not a K-register, or absorbing into a
   triangle-leaver register after its last read. Requires Port480's construct2b (not in repo; only recipes). Worth ~+0.19% b.
2. Re-select the partition so full pairs avoid the 6 cold-end blocks (full_pairs are (0,1),(2,3),(4,5),(6,7)); an alternative full-pair set
   might move the conflict onto blocks whose cold ends are lost anyway.
3. Reading leavers before the K-register's frame grows past the cold frame, or splitting each K-register into a read-then-dead copy
   (costs a helper ~0.043%, may still net positive vs 0.032%/cold end).
4. Centres carrying the leaver sum (B1) so the K-coordinate reads become zero-climb descents; cost R40-C unpriced.

## Rescue check
Does B1 centre promotion make leaver reads climb-free? Not tested. Upper bound of the prize is the climb line only (+0.17..0.21%),
and the lost cold ends (0.19%) are untouched by it. Rescue of the verdict: if escape 1 gives a legal absorbing q for the 6 blocks,
price = +0.19%, still < 0.3%; combined with free climbs ~+0.4% (marginal GO bar +0.3%). Re-open only on that joint tool.

## Incidental structural gain
None verified. The only candidate (restoring 6 cold ends, +0.19% b) is unbuilt. ship=false.
