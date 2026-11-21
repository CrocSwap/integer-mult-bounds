# YFIRST (Nov 20, Opus): gather-then-jump helper class. Code (own, stdlib, 1 proc): size.py, ffree.py, home.py, trivial.py,
meetdims.py, stayclass.py, single.py, rebirth.py, swapsize.py (all read ../fewstops/load.py; exact PRICEKIT).
Differs from FEWSTOPS: FS searched reorder/re-chart with t7669's ops fixed. This lane asks whether the gather-then-jump (GDJ)
class can exist at all, and sizes every relaxation of it.

## Result: no κ gain, no build. The literal class is either trivial or is a carrier with the same stops.
1. [C] t7669 is already y-first at bulk. Helper–Y meetings: 26,615 at dim 0 and ~700 at dims 1–8. Helper–X meetings: 28,151 at
   dim 9 and ~1.8k at dims 1–4 (meetdims.py). The split lives only in a thin middle band: X leaf reads and the gather tree at
   dims 1–4, Y deliveries at the Ys' own charts 2/5/7/8, owned-decoder meetings at dims 1–8 (~700). That band is the decoder
   interface.
2. [P] Content order. Public charts ascend, and every chart of X_t contains span(q_t). So any register holding content that
   came from X_t over an all-public chain has q_t in every later chart. A carrier must pick up before it delivers, and cleanup
   of x content needs that content. "Cleanup before any x port" is therefore impossible for a register that carries x content.
3. [P] Split lemma (subadditivity of r^(1-κ)). Suppose a helper's life has a token-home point: row = e_h and no other register
   holds e_h. Splitting it there into two helpers weakly raises κ (strictly if both parts climb), and the second part can be born
   at its first chart. So GDJ in the literal sense (y-phase finished clean, then x-phase in one jump) = an independent y-helper +
   a single-chart scratch register (zero cost, no transport). It adds no transport capacity. [C] t7669 has 0 token-home points
   among its 3346 mid-life helper moves. At those moves the median row has 184 terms and 24 other registers hold residues. The
   14 helpers with an empty first/last stay are idle single jumps, so there is no gain there.
4. [C] Order-free ceiling. Reorder each register's own ops arbitrarily (any y-first sort) with FS's partner L/U held fixed:
   helper stays 5384 vs 5520, κ ≤ .0040077 (ffree.py). That equals FS's DAG-reorder bound .004008, so the per-register op order
   is not binding. Partner bounds are. The +7.7% is the most any self-reordering can give, and FS realised 0 of it.
5. [P] The obstruction at an XY-forced boundary. Stay k meets p, whose future is ⊆ q_s^⊥. Stay k+1 meets z, whose past ∋ q_t,
   with q_t ∉ q_s^⊥. Merging the two needs p at a chart containing q_t, or z at a chart without it. Both are impossible. A
   commutator-compensated reorder needs a p–z co-location, which is the same forbidden meeting. Removing the stop means changing
   WHO meets p and z (the partner/decoder charts), which is a joint decoder+helper redesign (BIGBUILD2 scope), not a helper class.
6. Sanity [C] (trivial.py): a helper-free word replays with rows equal to t7669 (owned rank-1 transfers at the main endpoints),
   but S = −208 (owned mass 226). Owned mass is first order (D = R = 56 at the floor), which is why public helpers carry content.
   Splits are second order.

## Sizing (optimistic histogram edits, mains untouched, κ):
| single jump (helpers floor) .0065264 | keep first + last stop .0043854 | drop stops at dims 2,3 (tree flatten) .0041634 |
| drop dims 1–3 .0044450 | drop dims 6–8 .0044526 | order-free reorder .0040077 | swap-courier endings (below) .0039049 |

## INTERLEAVE's swap-courier (INT.md C4) as the helper class
[P] It is compatible with item 2: the courier picks up after taking the target's token, and the target's own register absorbs the
content. So it is the right minimal carrier. Its stops = the number of distinct source charts on the target's chain. On t7669:
- [C] Optimistic: 369 helpers have a stay at a Y/Y2 FINAL chart as their last stop before the jump to 9. Ending them there
  (no jump, no cleanup) gives κ .0039049 (+4.9%) (swapsize.py).
- [C] Not realisable as is: 359/369 make ≥10 gates at their dim-9 stay (213 make ≥50). They carry content that is not the Y
  increment, so they are not couriers. Relabelling stops from a Y main onto a courier changes nothing. The bill is identical
  (main climb credited by the caller, courier climb by T). Gain needs fewer distinct source charts per target, and those
  charts are set by the decoder's pinned charts (D/R chains).
Next (word design, not routing): give each Y target its decoder deliveries on ONE chart of its chain (decoder rows grouped by
target final chart), then serve them with swap-couriers 0→c→q_s^⊥. Size it first by counting the distinct delivery charts per Y.
