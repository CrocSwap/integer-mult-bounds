# Two-block local gauge edits cannot beat the P112 copy cost

**Scoped exact negative result; no new κ.** On one fixed P112 nine-normal decoder, allow arbitrary rational per-root coefficient gauges on any one or two blocks of a fixed 14-block orthogonal partition, while keeping all exterior rows at their canonical sparsest gauges. The exact optimistic cost floor is at least **64** for every one of the 14 singleton blocks and 91 block pairs. The existing P112 decoder already costs 64, so this local support-change mechanism has no copy-cost headroom before frame or realization expenses.

Cycle 16 seed: `8232e87e36b7bc2bd06a84ddf3384413`; track `complex-mechanisms`; refined task `complex-rank-shape-decoder`; priority revision 3. The exact base is `ecc75c79c22d909fd42aa68437eb77c4c1361835`, and the selected-record SHA256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Selected κ remains `836330098538459/500000000000000000`. Source and predecessor pins are in [SOURCES.json](SOURCES.json).

## Object and result

The frame consists of the eight coordinate-frame normals removed for P112 plus the first four-contact extra root (line index 1). Its dependency is `(-1,-1,-1,-1,0,0,0,0,2)`. Each live-root coefficient row is `c_i+t_i z`; this retains the exact identity for every rational `t_i`.

The 112 live lines are greedily partitioned by increasing canonical line index into 14 disjoint orthogonal eight-line blocks. For any chosen block or block pair, freeze every exterior row at `Frame.sparsest(i)`. The sum of the nine F2 ranks from those exterior rows is an exact lower bound on every local gauge completion, because adding pairing rows cannot reduce rank.

| Changed blocks | Cases | Exact exterior floors |
|---|---:|---|
| One | 14 | 67 twice; 68 twelve times |
| Two | 91 | 64 once; 67 twenty-four times; 68 sixty-six times |

The unique pair floor 64 is attained by retaining ranks `(8,8,8,8,8,8,8,8,0)` from the exterior rows. This does not show that the completed decoder reaches 64; it shows only that this favorable local-edit model cannot go below it.

## Relation to nearby work

Merged PR #1224 supplies the nine-normal frame and per-root dependency gauge. Cycle 15’s PR #1962 studies one shared ternary shift vector; this package instead permits independent rational shifts on any one or two tetrad blocks and proves a monotone exterior-rank floor. Open PR #1909 proves a different tetrad-local masked-decoder bound and lists two-tetrad support escape as a next question. Here the exact construction family is fixed to the coordinate-plus-root frame and fixed exterior sparse gauges. No arbitrary masked supports or general frame excess theorem is claimed.

## Reproduce

```sh
python3 -I -B research/coord-root-p112-local-tetrad-gauge-seed8232/verify.py
python3 scripts/research_package.py --package research/coord-root-p112-local-tetrad-gauge-seed8232 --check-only
```

The exact verifier writes `RESULT.json`, checks the baseline decoder on all `112^2` live pairs, tests three nontrivial rational gauge completions, and rejects a one-coefficient mutation. The registered replay targets Python 3.12; the local environment provides Python 3.14.7.

## Open next questions

- Can coordinated gauge changes on three or more of these 14 blocks produce a copy floor below 64? First compute the exterior-rank floor for every three-block union, then continue only if it leaves headroom.
- Can another nine-normal frame on this same puncture make a sparse local gauge edit favorable? This changes the frame hypothesis and needs a separate optimistic screen.

Prepared with substantial OpenAI Codex assistance in the exact census, proof checks and writing. No independent human review, full supplier realization or κ change is claimed.
