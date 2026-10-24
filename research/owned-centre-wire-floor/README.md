# Owned-centre wire floor on #4470 (no new κ)

This package gives a negative answer to the open question of #4534 (`research/frame-aware-native`) for #4470's selected native word. Retiming the owned C wire, which #4534's theorem allows when every C transition is paid, cannot make the eight rank-8 centre transports cheaper. It also cannot fund #4534's rejected rank-5 merge candidate.

**Claim type:** a written floor with an exact finite check, plus search evidence. **No new κ.**

## Results

- **Floor.** Every scalar contact may be retimed: L roles climb along nested frames, and C moves along nested frames in either direction. Under these rules the C wire of each of the 8 centre blocks pays rank mass at least 8, in both orientations. That equals the current single rank-8 job, so the centre charge of #4470 is already optimal in this model. The proof (`PROOF.md`) combines interval propagation of the lowest and highest legal chart of every contact with the path bound "cost ≥ dim g_0 − dim(g_0 ∩ … ∩ g_n)" for nested moves. In every block, the source contact is forced into a frame of dimension 8, and the 22 targets' upper frames meet that frame only in 0. A single target alone would give only 7, and at most 8 of the 22 targets share any nonzero line.
- **Rejected candidate.** #4534's candidate replaces 56 rank-1 + 56 rank-4 jobs by 56 rank-5 jobs per full call. On #4470's complete invoice it nominally raises the raw root from 0.0030201659 to 0.0030511780 (+1.03%). A net extra C charge between 0.42 and 0.43 rank-1 jobs per full call cancels that gain (certified roots). By the floor, the C wire has nothing to give back.
- **Search.** A joint retiming search with the C wire as a variable (`search/`) covers all units, adjacent pairs and connected triples in two unit models, plus about 3.5 M annealing steps. It finds no improving move.

## Verification

```sh
python3.12 -B scripts/research_package.py --package research/owned-centre-wire-floor --check-only
python3.12 -B scripts/research_package.py --package research/owned-centre-wire-floor
```

`verify.py` uses only the standard library and takes about 10 s. It rebuilds #4470's word with `research/joint-helper-lattice/native_joint.py` and recovers the local paid profile `{1:2237,2:388,3:494,4:147,5:36,8:8}` from contact charts in both orientations. It then checks the centre structure (8 blocks, 22 targets, one rank-8 transport each), the propagation and the floor in all 16 block-orientations, and certified roots of the candidate variants with `mixed_target_probe`'s interval series. The controls are the weaker single-target bound (7), the 8-of-22 line count, a corrupted frame that propagation must reject, and one extra rank-8 transport per call lowering the root. It also checks that `RESULT.json` is reproduced exactly.

## Scope

The floor is for nested transports, the fixed chronological scalar word, fixed warps and fixed helper boundaries. A non-nested C transition priced by its actual Clifford rank, a changed scalar order or warp word, and joint changes of helper entrances and exits are not covered and stay open. The search is evidence only. The floor does not depend on it.

## Open next questions

1. Can a non-nested owned-C transition, priced by its exact Clifford rank, beat the nested floor of 8 per block? Start by enumerating C charts outside the nested lattice between Low(source) and the targets' Up frames, then lower those transports exactly.
2. Can helper entrances and exits move jointly with the C-contact charts? #4470's own gain came from moving helper boundaries jointly. Add them as variables to `search/cwire_joint.py`, with whole-job productive credit.

## Credit

Dugongue's #4534 owned-C retiming theorem and its rejected candidate. Cinna Davis's #4470 / #4440 / #4441 / #4447 native word and invoice, with zxv's native supplier and the scalar, Clifford, geometry and outer-ledger lineage retained there. The interval engine comes from `research/kappa-rebuild/architecture/mixed_target_probe.py`. Prepared by Matarener with substantial Claude Code assistance. Apache-2.0.
