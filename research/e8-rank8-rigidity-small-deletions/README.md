# Rank-8 rigidity of the E8 pattern after deleting at most 8 lines (closes hypothesis (1) of Lemma RIGD for |D| <= 8; no kappa claim)

> **Scope.** Pure matrix classification on the E8 unit (120 lines). **No kappa claim**, no window, no supplier, no decoder cost. R1 for an **arbitrary** number of extra zeros is **not** claimed and stays open (see "Not claimed").
> Labels: **PROVEN** (written argument), **CHECKED** (recomputed by `verify.sh`; SAT steps are kissat UNSAT with a DRAT proof accepted by the standard `drat-trim`; the exhaustive searches are plain C/C++ DFS, no proof object, but two independent implementations), **CONDITIONAL** (inherited, cited).
> **Credit.** The problem (R1/R2/R3, universal rigidity R2 for the complement of a small set, normal forms) is philippeVV's (Discussion #1587). Rank-8 rigidity with the full iff pattern is #1212. The zero-pattern SAT model and the frame calculus are those of the merged package `research/e8-rank9-extra-zeros/` (#2864, Theorem RK) and `research/e8-rank9-realisations/` (#2819).

## Result
Setting (as #2864 Theorem RK): `D` a set of at most 8 lines of E8, `L' = E8 \ D`; `N` a matrix over a field of characteristic 0 indexed by `L'`, rank <= 8, `N_tt != 0`, `N_ts = 0` for `t` orthogonal to `s`, all other entries free (extra zeros allowed). **Then `N` has no extra zero and `N = D1 G D2` with `D1, D2` invertible** (a root realisation). #2864 proves this for `D` a clique; here `D` is **arbitrary** with `|D| <= 8`. This is hypothesis (1) of Lemma RIGD (the rank-8 rigidity hypothesis) for all `|D| <= 8`.

## Proof structure (details and the claim-to-check map: `PROOF_MAP.md`)
* **Step 1 (no extra zero).** Rank is monotone under restriction. If a local core `U` (a set of lines containing the pair `(u0, s0)` and some E8 frames inside `U`) has an UNSAT zero-pattern model with goal `N_{u0 s0} = 0`, then no `N` on any `L' containing U` has that zero. `W(E8)` is transitive on ordered non-orthogonal pairs (orbit 6720), so `(u0, s0) = (0, 2)`; the stabiliser `W(E6)` (order 51840) maps cores to cores. Ten cores (27 to 38 lines) have UNSAT models (DRAT checked). Step 1 holds for `D` iff `D` (not containing 0, 2) misses at least one `W(E6)`-image of some core; exhaustive search: **no `D` with `|D| <= 8` meets all images** (two implementations).
* **Step 2 (iff pattern implies Gram).** With no extra zero `N` has the iff pattern; the frame calculus of #2819 (Theorem P, #1212's argument) needs one frame `F` inside `L'` in which each of the 14 tetrads holds at most one line of `D`. Exhaustive search: **no `D` with `|D| <= 8` meets two lines of a tetrad in every one of the 2025 frames** (two implementations; the search is run for the two `W(E8)` orbits of line pairs as roots).

## Not claimed
* R1 for an arbitrary number of extra zeros (the P/A/Sigma/S steps without the per-line budget): **open**. This package only supplies the rigidity input for `|D| <= 8`; it does not remove the per-row / per-column budget of #2864 Theorem Z3'.
* Larger `D` (`|D| = 9`: the same searches were run as a probe only: HIT with 9 found none in the sampled orbits (logs `evidence/R1-RIG3/h9_*.out`), not part of `verify.sh` and not claimed).
* Inherited: the zero-pattern model's equivalence to Theorem RK is **assumed from #2864** (see `PROOF_MAP.md`, A1): #2864 ships the model generator and one-line rule proofs (`evidence/ZPIN*_THEORY_snapshot.md`) but its README does not state this exact core-restriction use; the CNF generator here (`checks/core.py`) is the same rule set specialised to a core, and its soundness is not re-proved here.

## Verification
`bash verify.sh` (about 15 CPU-minutes by default; needs numpy, `cc`, `c++`, `xz`; drat-trim is built from the shipped `checks/drat-trim.c`, MIT, copyright in the file and `checks/DRAT-TRIM-LICENSE`). `FULL=1` adds the complete independent HIT and FRAMES searches (about 1.3 CPU-hours each, chunked, every chunk under 20 minutes).
