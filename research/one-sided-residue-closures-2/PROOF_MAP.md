# Claim -> check (anything else is CONDITIONAL)
| # | Claim | Check |
|---|---|---|
| Q1 | non-root minimal leftover of two 7-flats is 14 (D7) | verify 1: implB, a2_g777 |
| Q2 | covered root: minimal leftovers <=11 are 315 Q (size 8, F2 rank 4, D4 minus a frame) | verify 1: lo2 (A), implB (B), a2_g777 (audit) |
| Q3 | 9450 Q, each leftover of 4 roots, none inside | verify 1: nq (A), a2b_m13 (audit) |
| Q4 | `E = M(+l)` serves <=4 roots; <=13+20 < 36 | verify 1: m13 (A), implB2 (B), a2b_m13 (audit) |
| Q5 | Lemma Q4 inequality kills rows 18, 582-595 | verify 4 `new_kills.py` (criterion recomputed from rows) |
| Q6 | Circuit Lemma / ClassI / g-table premises | inherited from #2985 (CONDITIONAL here) |
| B1 | rows 448, 449 by the count lemma | verify 4 `new_kills.py` via `asm.py` |
| B2 | (6,6,5,5,5,4) cannot cover the 84 lines outside E6 | verify 2: `tight.py`, `verify_e6.py` |
| B3 | rows 168, 324, 325, 328, 457 (all other scenarios by IMM/COUNT/RRC) | verify 4 via `asm.py` |
| B4 | rows 169, 332, 333, 464, 424, 426, 427 | NOT CLAIMED (CONDITIONAL, single implementation) |
| C1 | four span passes are complete and crack-free | verify 3 `sc_check.py` (shipped outputs) and on the reruns |
| C2 | passes reproduce from `s3z.c` | verify 3 `sc_rerun.sh` (FULL=1: all chunks) |
| C3 | pass at T, d >= T => span <= d-1; row/config mapping | `checks/sc/row_cert.py`: for every one of the 56 span-pass rows, an explicit Lemma-B certificate (e-subset B, sum g < 53, packing into the passed config) is found and printed; replaces the inherited dominance table |
| L | ledger: 480+78 KILLED, 7 prior-only, 38 OPEN | verify 4 recomputation compared with `data/ledger2_consolidated.csv` |
