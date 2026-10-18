# Where characteristic 2 starts to pay: a T² threshold for root-unit decoders (E6 ties, E7 first gain found; no κ claim)

> **What is claimed, and what is not.** This package explains, with exact computations and recorded searches, *where* the F2 cost of an exact root-unit decoder first drops below the number of lines v: the dense F2 cost of the full orthogonal pattern is about T·(rank of a block), the block rank is about T, so a gain over v needs v to exceed roughly **T²** lines. The data: D4, D5, D6, F4 and E6 tie (cost = v; E6 exactly 36 = 6²), A4–A6 are above v, **E7 is the first gain found (cost 49 < 63 at T = 7)**, E8 (72 < 120) is known (#1590, ERR1).
> **Claimed.** (1) CHECKED, exact: the F2 costs of the table in §2 (each is the cost of a stored or fully specified admissible pairing B for an exact decoder M = Gram). (2) CHECKED, exact: a realisation over Q of a Fano Levi graph has exact minimum cost 9 (T = 4) and 13 (T = 5, rank(PQᵀ) = 5, all five blocks nonempty) against v = 7: no gain at that size. (3) RECORDED: realisability of finite-geometry incidence structures (numerical), the annealing / clique / lattice-pool searches.
> **Not claimed.** **No claim that T ≤ 6 can never beat v**: the searches are not exhaustive and the law is an explanation plus evidence, not a theorem. The table's costs are *upper bounds on the minimum F2 cost* (cost of a specific B); that no smaller B exists is RECORDED (annealing), not proved. No κ gain, no window closed, nothing about T = 3 (see #2111).

## 0. Reading this package

Statuses: **PROVEN** (proof in this README), **CHECKED** (recomputed by `verify.sh`, exact), **RECORDED** (a result of our own working card `KPR4-GAP`, searches or numerical runs, shipped as the verbatim notes `evidence/KPR4-GAP-NOTES.md` and as the scripts used, but **not** re-run by `verify.sh`), **ARGUED / OPEN**.

```sh
bash research/char2-threshold/verify.sh /fresh/output/dir        # from a checkout or `git archive`; Python >= 3.11 (standard library) and cc
```

Step 0 checks every file against `MANIFEST.sha256` and every pin of `SOURCES.json` and stops with exit 1 on any mismatch; then `c/kgap.c` is compiled and two groups run in one process (8 PASS lines after step 0, 10 with step 0; seconds). Model, Theorem C cost and lemmas are those of the merged #1590 (`research/root-unit-decoder-lemmas`: exact decoder, pairing B, Lemma A for T ≤ 2, Lemma B lift identity, ERR1) and of #2111 (three-total decoders: reductions, the tight configuration tied_min, the lift route); #446 (Theorem C; closed) and #595 (merged) carry the cost formula. This package does not re-prove them.

**Setting.** A root unit is a set of v root lines with Gram matrix G. An exact decoder with T totals is M = Σ_{j≤T} p_j q_jᵀ over Q with M_tt ≠ 0 and M_ts = 0 wherever B_ts = 1 (s ≠ t); here M = G is realised by taking the coordinates of the roots in a basis of T roots as p(t) and q(t) = p(t)·(Gram of the basis) (`lib/units.py`, exact Fractions; checked: M = Gram). R_j = supp p_j, A_j = supp q_j, r_j = rank_F2 B[R_j, A_j]; **cost = Σ_j r_j** (Theorem C without the per-total floor). B0 denotes the full orthogonal pattern (B_ts = 1 iff t = s or r_t ⊥ r_s); any admissible B lies inside it. By Lemma B (#1590) the cost over Q is always ≥ v, so a certified gap is exactly an admissible F2 matrix with Σ_j r_j < v.

## 1. The law (ARGUED; the numbers behind it are CHECKED in §2)

For these units the pairing is the orthogonality (or symplectic) incidence of a finite geometry, and an "odd-or-zero" labelling of the lines realises F2 incidence exactly: for B = J + abᵀ-type blocks the F2 rank is about k + 1 where k is the rank of the label system. Each total j sees a block whose F2 rank is *about T*, so **the dense cost is at most about T·(k + 1) ≈ T²** while v is the number of lines. A gain over v therefore needs **more than about T² lines**. For the root systems v = 12, 20, 30, 36, 63, 120 at T = 4, 5, 6, 6, 7, 8 against T² = 16, 25, 36, 36, 49, 64: D4–D6 (v = T(T−1)) are below T² (and tie, since each block has rank T − 1); E6 sits exactly at T² (tie, 36 = 6²); E7 is the first with v > T² (63 > 49); E8 has v = 120 > 64. The exact block ranks in §2 show the mechanism (T − 1 for D, T for E6 and E7, T + 1 for E8: cost = T × block rank). The law is an **explanation**: it predicts where gains are possible, it is not a proof that none occurs below, and the block-rank behaviour (k + 1) is observed, not derived for arbitrary pairings.

## 2. The table (CHECKED, exact: `checks/units.py`, verify groups G1.*)

Cost of an admissible B for the exact decoder of the unit (the basis is stated). "cost − v" is computed, not asserted.

| unit | T | v | T² | pairing B | block ranks | cost | cost − v | check |
|---|---|---|---|---|---|---|---|---|
| D4 | 4 | 12 | 16 | B0, standard coordinates | 3,3,3,3 | 12 | 0 (tie) | G1.D-ties |
| D5 | 5 | 20 | 25 | B0, standard coordinates | 4×5 | 20 | 0 (tie) | G1.D-ties |
| D6 | 6 | 30 | 36 | B0, standard coordinates | 5×6 | 30 | 0 (tie) | G1.D-ties |
| E6 | 6 | 36 | 36 | stored B in a stored basis (`data/e6_best.json`, found by local search from B0) | 6×6 | 36 | 0 (tie, exactly T²) | G1.E6-tie |
| E7 | 7 | 63 | 49 | B0, first independent lines as basis | 7×7 | **49** | **−14 (first gain found)**; also checked by #1590 (G3.E7-dyadic) | G1.E7-gain |
| E8 | 8 | 120 | 64 | B0, first independent lines as basis | 9×8 | 72 | −48 (known; #1590 ERR1) | G1.E8-gain |
| A4 / A5 / A6 | 4 / 5 / 6 | 10 / 15 / 21 | 16 / 25 / 36 | B0 (upper bounds) | | 16 / 25 / 36 | +6 / +10 / +15 | G1.A-above |

- **E6 depends on the basis**: B0 costs 37 in the first-independent basis (this value, and E7 = 49, are also checked in #1590: G4.E6, G3.E7-dyadic) and 36 in the stored basis (the card found 36 as best, other bases 40–42 after annealing). The tie at 36 is the cost of the stored B (an upper bound on the F2 minimum).
- **RECORDED** (annealing over all admissible B, `kgap.c sa`, card KPR4-GAP notes): the best costs found are D4/D5/D6 = 12/20/30 (ties), F4 (24 rays, T = 4) = 24 (tie, 150 bases tried), E6 = 36 (best basis), A4/A5/A6 = 16/21/34 (above v; the B0 upper bounds above are weaker for A5, A6), E7 = 49 in any basis (annealing from scratch also finds the gain 14; subsets of 57–60 roots also gain 14). Nothing below v was found at T ≤ 6.
- Lemma B (#1590) shows the cost over Q is ≥ v, so each "tie" means the F2 matrix reaches exactly the Q lower bound; the gains at E7 and E8 are genuine char-2 cancellation.

## 3. Realisability of finite geometries (RECORDED, numerical)

For a symplectic geometry Sp_{2m}(2) (points = nonzero vectors of F2^{2m}, orthogonality = vanishing symplectic form), a real exact decoder with the incidence pattern needs vectors p, q ∈ R^T with p_t·q_s = 0 on orthogonal pairs and p_t·q_t = 1. Levenberg–Marquardt on this system (`scripts/realize.py`, residual² ~ 1e-25 means yes), card KPR4-GAP:
- the **Sp4 doily (15 points)** realises at **T = 4** and **not at T = 3** (residual² ≈ 2.0); (re-run once while preparing this package: seeds 0, 1 at T = 4 give 8.6e-26 and 3.0e-28, T = 3 gives 2.0);
- the **63-point Sp6** realises at **T = 7** and Levenberg–Marquardt **found no realisation at T = 6 or T = 5** (residual not near zero; the card records "10–21");
- E6's 36 nonsingular points plus up to 5 singular points of Sp6 realise at T = 6 (41 points, F2 rank 7: 41 < 42, no gain); greedy extension beyond that fails.
These are numerical (floating point) results: no exact rational realisation is shipped, so none is CHECKED. Consistent with the law: 63 = v(E7) needs T = 7 and 7² = 49 < 63.

## 4. The Fano Levi graph (CHECKED, exact: `checks/fano.py`, groups G2.*)

Seven points P_i ∈ Z^T, seven lines Q_L ∈ Z^T (null vectors of the three points of each Fano line L = (i, i+1, i+3)), matched by a permutation so that every p_t·q_t ≠ 0: a configuration of v = 7 lines whose orthogonality pattern contains the Levi graph of the Fano plane. The realisation exists over Q already at **T = 4**. `data/fano_T4.json`, `fano_T5.json` store the best realisation among 100 random draws each (found by `scripts/make_fano.py`); `verify.sh` checks that the zero pattern contains a Fano plane, that the points are distinct and the diagonal products nonzero, and computes the **exact minimum** of the F2 cost over all 2^f admissible B (`kgap ex`): **9 at T = 4 (f = 14) and 13 at T = 5 (f = 17), against v = 7**; both realisations have exact rank(PQᵀ) = T with all T blocks nonempty (checked). So there is no gain at that size. (The card, over 30 random draws, recorded 11 at T = 4 and 8 at T = 5, but its T = 5 realisations used only four coordinates, i.e. were rank 4; those are not used.) `scripts/make_fano.py` keeps the least cost over 100 random draws. The pattern is richer than the Levi graph (accidental orthogonalities are included, which can only lower the minimum), so the statement is: *this realisation* has cost > v. It is consistent with the law: T² = 16 or 25 ≫ 7.

## 5. Scope and negative searches (RECORDED)

- The searches are not exhaustive. Card KPR4-GAP: `ksubset` simulated annealing over subsets of pools (T = 4, 5; H = I, A, D, E, random), lattice pools of E6/D5/A5/D6 with norm ≤ 4, `ksearch` outer annealing at T = 3, 4 (only ties), maximum odd-or-zero cliques in lattice pools (E6, D5, D6, A6, Z^T), which equal the root counts; random symmetric / nonsymmetric forms at T = 4 give cliques up to 16 but gain ≤ 0. In all, no gain at T ≤ 6.
- An attempted E7 → T = 6 projection (dropping the minuscule node) fails: the 27 weight lines would need W–W orthogonal pairs of E7 to vanish in M′.
- **There is no claim that T ≤ 6 can never beat v.** A decoder with fewer totals than the T of the rank, or a non-root unit, is not covered; a unit with more than about T² lines and a low-rank F2 pattern is the thing to look for.
- Not done on the card: an exact Gröbner Q side (not needed: Lemma B gives cost over Q ≥ v), real-unit pricing, a minimal characterisation of the T = 7 seed, growth of the Fano gadget beyond v = 7.

## 6. Open problems

1. Is the threshold sharp: does every exact decoder with T totals on v ≤ T² lines (or on root units with v ≤ T²) have F2 cost ≥ v? (T = 3: the question of #2111.) The tie at E6 (v = T² = 36) suggests the boundary case.
2. A derivation of the block rank k + 1 for general odd-or-zero systems (the law in §1 is stated from examples).
3. A unit or a sub-configuration of a unit with T ≤ 6 and more than T² lines where B0-type patterns have block rank ≈ T.

## 7. Files

`verify.sh`, `scripts/provenance.py`, `MANIFEST.sha256`, `SOURCES.json`, `requirements.txt`, `LICENSE`, `NOTICE.md`; `c/kgap.c` (exhaustive / annealing F2 cost for T blocks, from the card, unchanged); `lib/roots.py`, `lib/units.py` (pure Python: root lines, exact decoders, ranks); `checks/units.py`, `checks/fano.py`, `checks/expect.py`; `data/e6_best.json`, `data/fano_T4.json`, `data/fano_T5.json`; authors' scripts not run by verify.sh: `scripts/search_e6.py`, `scripts/make_fano.py`, `scripts/realize.py`; `evidence/KPR4-GAP-NOTES.md` (verbatim notes of the card, snapshot 2026-10-14).
