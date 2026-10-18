# B260 VERDICT: NO-GO at the design gate. The savings bound is 0 helpers, i.e. ≈ 0% (< +0.5%), at the fixed multiset and also under port-aligned rebuild. No word was built, so there is no κ and no SHIP CANDIDATE. Nothing was pushed, no heavy job was run, and SPEC/HEADROOM were not touched.
Why: today's shared registers are ALREADY port-aligned at the minimum span. Every copy's content is already inside its union group's common perp. What forces the copy is the ORIGINAL register's other uses (drag + versions), and regrouping by target port leaves those uses unchanged.
## (1) Geometry (exact; geo.py, groups.py; ports = w1018 'ports'; u·u = 1 for 112/112; cap verified)
- Dim-2 groups are exactly the PAIRS (cap ⇒ a dim-2 subspace holds ≤ 2 ports): 6216. Common perp dim 7, holding 20-26 ports. 3 ports always span dim 3, so the card's "3 ports in 2 dims" never happens.
- Dim-3 groups: all 227,920 triples (common perp dim 6) plus the ZERO-SUM QUADS, the maximum group size in dim 3 (arc of PG(2,2)): 24,276.
  - By block pattern: 196 in one block (14 per block = the affine planes of the block's AG(3,2)), 4,368 split 2+2 over two blocks, 19,712 over 4 different blocks. Patterns 3+1 and 2+1+1: 0.
- Each source block is an affine 3-flat: 8 ports, span dim 4, the maximum cap in a dim-4 space. In-block orthogonality is bipartite (two halves of 4; dot 1 within a half, 0 across).
- Delivery: M = I − G/2 is nonzero off the diagonal exactly where u_s·u_t = 0 (5824/5824, 52 per target). So a group T can share content only from S_T = {s : u_s ⊥ all of T}.
  - Pairs: |S_T| 20-26. Max rank-1 (shareable) sub-sum: 24 or 25 for orthogonal pairs, 10-12 for non-orthogonal pairs.
  - In-block quads: 168 have one 8-source rank-1 class spanning dim 5; 28 have none.
  - Cross-block quads: ≤ 10 sources.
## (2) Today's sharing is already minimum-span (rd.py; direct target reads in A/B)
Every register read by ≥ 2 targets has reader-port span = the minimum possible for its size:
- 54 h + 25 x + 24 y read by pairs (dim 2);
- 16 h + 16 x read by triples across 3 blocks (dim 3);
- 56 h read by in-block zero-sum quads (dim 3, 4 per block).
No "spread-out" group exists to tighten.
Copies (merge.py, pure.py): 248 helper-from-register events (a helper initialised as q·s, then both h and s are read by targets). Union reader group T: 200 pairs, 33 triples, 15 quads (dim 4, never zero-sum).
- At the copy instant, s's ancestor-port span AND its value x-support lie inside ∩_T u^⊥ in 248/248 cases. The copy IS already the port-aligned shared intermediate.
- After the copy, s fails the ancestor floor for T in 213/248, through VERSIONS (s written before h's last read, 218) and DRAG (s read by non-targets, 229). 35/248 pass the ancestor floor, a necessary test only, and they are covered by B172 (268/268 necessary in any order).
## Savings bound and regrouping cost
- Deleting a copy needs s's out-of-cap uses served by another register (a version) or moved after the capped reads (B256/B257, killed or open there). Port regrouping does neither, so it removes 0 copies.
- Rebuilding a port-aligned factory register from S_T sources costs 1 helper + |supp| ADDs. It replaces a copy that costs 1 helper + 1 ADD: net helpers 0, ops +(|supp|−1), so the saving is ≤ 0 × B248 rate (0.0725-0.15%/w9 helper).
- Sharing NEW sub-sums across groups is capped by reader order. In a group, every non-last reader must read while its frame is ⊆ ∩ perp of the later readers. After a non-last read of an in-block-quad 8-sum (span dim 5), a target's later co-readers must lie in a dim-4 space (≤ 8 ports). This is the B248 one-pair-per-target matching, generalised, and the word already uses it (56 quad helpers).
- Bound ≤ 0 helpers, far below the +0.5% gate. Ceiling context: all copies gone = bit cap +3.52% (B248), not reachable this way.
## Kill protocol (provisional)
Assumptions: fixed target ports (D8 roots, skeleton); direct-read frames per caps.py; the copy census is the ancestor/value necessary test (frames ⊇ ancestor span).
Escapes:
- (E1) change the packet's out-of-cap consumers so s itself is read only in-cap (internal factory redesign = multiset change);
- (E2) joint delete+reorder (B257);
- (E3) a decoder/skeleton that changes the u_t (Lemma R scope).
Rescue check: rd.py on any new skeleton word. If any multi-reader register has span > minimum, or any copy's content at the copy instant lies outside ∩_T u^⊥, re-open.
Files (cards/B260): geo.py, groups.py, rd.py, val.py, cp.py, anc.py, merge.py (merge.pkl), pure.py. All are single-process, run in seconds.
