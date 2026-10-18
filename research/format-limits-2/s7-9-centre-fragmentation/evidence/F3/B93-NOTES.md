# B93 (LIT): group-frame theory for S1's 24-form frame. VERDICT: KILL at gate (~15 min incl. 87 s run). ship=false
Scope: block (0,1,2,3) of B90 snaps.pkl (exact Fractions); other blocks conjugate (B90 h-c). Script: scratchpad g.py/g2.py (single process, no heavy job).
Literature (from memory, not re-fetched): Vale-Waldron 2005 (symmetry group of a frame = unitaries permuting it up to unimodular scalars; group frame = one orbit) and Waldron 2018 ch.6 (harmonic/group frames). Lemma used: a group frame's symmetry group acts transitively on one orbit; the number of generators = orbit count.
## Computation
- 24 forms (8 lines + 16 scratch over the 8 lines) = 22 DISTINCT up to scale (2 exact duplicates; B92's territory). Support sizes: 1x2, 2x8, 4x8, 8x4.
- Symmetry group restricted to signed permutations of the 8 lines (monomial; the only kind that are free relabel/sign gauge): order 8 (16 with global sign). Elements are involution-like perms of the line indices (id, 3 disjoint-transposition types...), acts on the 22 forms with 7 ORBITS of sizes 2,2,2,4,4,4,4. Not transitive: NOT a group frame; not even a few-orbit frame (max orbit 4).
## Kill gate
1. Group order 8 -> at best 22/8 -> 7 orbits; replacing 16 scratch by generators saves at most 9 registers/block, only if every orbit member were free.
2. Fatal: B69/B38 make relabel/sign free only as ONE per-word gauge (whole word, all blocks/times, fixed labelling). A symmetry g maps form f to g(f) as a different REGISTER's content; to "read g(f) from f" one would need g applied at the read site = a data-side basis change on the reader, outside the swap contract (B69: non-uniform T breaks common-frame ADD). The registers are not reusable across the 8 symmetries within a single word; reads in B span all orbit members simultaneously (B90: scratch read across whole of B).
3. The group is not a gauge of the word anyway: it permutes the 8 lines inside a block, while the lines are partitioned among frames (B90: 112 = 14x8).
Verdict: no price run, no legality check (B11) needed.
## Knowledge gained
S1 per-block form set has monomial symmetry of order 8 and 7 orbits; it is not a harmonic/group frame (consistent with B90: only 4 Walsh characters). Haar lifting pairs are the structure, not a group orbit.
## TRANSFER
Orbit structure (7 orbits, 22 distinct forms) gives B92 an independent dedup count: 2 exact duplicates per block = 28 total, matching "equals another register up to scale". Any future S1 recompute (time-multiplexing, B90 lead) could use the 7 generators + the 152-op program as the compressed spec, but symmetry itself earns no free registers.
