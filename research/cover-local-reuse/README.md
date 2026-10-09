# Optimized physical local reuse under the three-stage cover

Conditional **κ = 84386598001/250000000000000 = 3.37546392004e-4** on the
unpaired three-stage cover (`complex_saving = 337774769/10¹² = 3.37774769e-4`).

| Construction | Physical roles R | Streams per vertex | Complex saving | Certified κ |
| --- | ---: | ---: | ---: | ---: |
| PR #130 (unpaired baseline) | 28,705 | 90,163 | 3.147997e-4 | 3.146011e-4 |
| PR #131 (unpaired + local reuse) | 26,597 | 83,839 | 3.32426609e-4 | 3.32205398986e-4 |
| **This package (unpaired + optimized local reuse)** | **26,549** | **83,695** | **3.37774769e-4** (`337774769/10¹²`) | **3.37546392004e-4** |

> **Note on PR #132 / PR #134 first-stage lockstep pairing**: The paired Stage-1
> lockstep accounting (`3.68552409947e-4`) is marked retracted in
> `certificate.json` (`retracted_paired_lockstep_cover`) following the
> counterexample in [#132#issuecomment-6073516734](https://github.com/CrocSwap/integer-mult-bounds/pull/132#issuecomment-6073516734)
> (confirmed by `@ikeboy`, `@Swapnil-jain`, and #134). Only the **unpaired**
> three-stage cover bound **`κ = 3.37546392004e-4`** (`w = 2v + 3R = 83,695`
> streams per vertex) is claimed as the active certificate here; for cross-stage
> completed-core sharing on paired cubes, see [#146](https://github.com/CrocSwap/integer-mult-bounds/pull/146)
> (`κ = 4.61028508707e-4`).

The inherited weighted bit supplier (`a_bit,eff = 3.731650e-4`) remains unchanged.

## Local word and compensated birth-cut reuse

The construction places the independently replayed physical complex word on
PR #117's immutable scalar DAG (`91,770` additions, `8,120` roots, `71,185`
matched links, `28,705` virtual roles) inside PR #130's three-stage Cayley
cover (`m = 3h - 2 = 70`).

1. **Radical-complement frame lifting and phase-aware role compilation (PR #133)**:
   Whenever `ker(K[x])` is degenerate over `F_2^24`, `U[x]` is lifted to the
   maximal nondegenerate subspace `L + nonsingular_part(W ∩ L^⊥)` containing
   the node envelope (`69,450` lifted nodes). At fan-out nodes (`len(free) > 1`),
   phase-1 uses in `Anc` are assigned to copy roles while keeping a phase-2 use
   on the pivot role, preserving all `2,351` phase-1 donor roles while shrinking
   phase-2 target reach.
2. **Cover-weighted local search, donor-chain shrinking and recipient snapping**:
   Deferred birth gauges (`3,558` roles) and physical mixer gate frames are
   optimized under the exact `m = 70` cover moment weights. Targeted hull
   shrinking along the ancestor chains of unmatched phase-1 donors increases
   compensated birth-cut reuses from `2,108` to **`2,156`**, reducing physical
   scratch roles from `28,705` to **`26,549`**. Split recipient birth frames
   (`e < f < d_1`) are snapped toward their matched donor frame `A` when this
   improves the combined auxiliary and target moment objective, eliminating
   redundant intermediate transition steps `f - e`.
3. **Per-bank literal reflection audit**:
   The full source/workspace chronology and inverse retain every compensation.
   The literal frame scan in `reflection_audit.py` independently audits
   `source_data_histogram`, `target_data_histogram` and `internal_role_histogram`
   across the source (`0 <= s < v`), target (`v <= s < 2v`) and physical
   auxiliary (`s >= 2v`) port banks in both the forward and reflected words.
   The local source inventory has `744` distinct frames, including `1,402`
   physical roles with nonzero source gauges.

## Unpaired and paired three-stage cover profiles

In the **unpaired** three-stage cover (`m = 70`), each vertex has
`w = 2v + 3R = 83,695` persistent streams, recursive rank `5,856,258` and
deficit `2v - 3ℓ = 2,392`. Each physical role with source gauge dimension `s`
contributes three exterior children of rank `46 + s`, and every local child of
rank `r` contributes three children of rank `r`.

In the **paired first-stage lockstep** cover (Avi Eisenberg, PR #132), let
`κ_inv` be the coordinate involution of `E = A ⊥ B ⊥ C` (`dim A = 24`,
`dim B = dim C = 23`, `m = 70`) that exchanges `e_i` and `e_{24+i}` for
`i < 24`. It is orthogonal, `κ_inv^2 = 1`, and `κ_inv(A) ⊂ B + C` is orthogonal
to `A`. For every `k ∈ G = O(E)`, `kA` and `(k κ_inv)A` are orthogonal, and
`k ↦ k κ_inv` is a fixed-point-free involution pairing the first-stage
invocations. Because stage one has offset `0`, paired cores `k` and `k κ_inv`
touch only their orthogonal active spaces `kA` and `(k κ_inv)A`, share a single
auxiliary bank of `R = 26,549` streams per pair, and execute their identical
first-stage word in lockstep:
- Each internal auxiliary step of rank `r` in stage one merges across the two
  orthogonal subspaces `U_1 ⊕ U_2 ⊂ U_1' ⊕ U_2'` into a single child of width
  `2r` by PR #130's general Clifford transition lemma, and at the end of the
  joint word its shared dirty tail has rank `m - 2h + 2s = 22 + 2s`.
- Stages two and three (offsets `kB` and `k(B + C)`) and all six data banks per
  pair remain unshared (`4` auxiliary copies of `46 + s` and `r`, plus `6`
  copies of `source_data_histogram + target_data_histogram`).
- Per pair of vertices, the paired cover uses `w_2 = 4v + 5R = 140,841`
  persistent streams, recursive rank `9,854,086` and deficit
  `2(2v - 3ℓ) = 4,784`. The largest child is `68 < 70`.

## Verification

Run from the repository root:

```sh
python3 research/cover-local-reuse/verify.py
```

The verifier checks a closed frozen source inventory, copies it into a
temporary repository-shaped tree, rebuilds the complete local compiler and
reuse pairs, independently replays literal reflection, per-bank histograms and
dirty cleanup, recounts bounded scalar work, regenerates finite geometry checks
(including the Stage-1 pairing involution `K_pair` across all `2,024` triple
ports) and checks both the unpaired and paired exact cover certificates. The
generated local profile and reflection receipt must reproduce byte for byte.
Verification leaves its source tree unchanged and has no options to omit these
stages.

The 18 outer controls in `test_controls.py` reject missing dependencies,
altered and repinned DAG inputs, omitted reuse roles or paid children,
corrupted internal-role or target-data histograms, missing compensation or
reflection flags, changed source bindings, insufficient scalar guards,
formatting drift and optimized Python. All 47 strict assembly constraints and
seven margins are positive for both the unpaired and paired certificates.

This remains a conditional finite witness. PR #130's finite group geometry,
PR #132's first-stage lockstep pairing schedule, weighted local-ring
compilation, uniform batching and restored internal row borrowing are written
proof dependencies, together with inherited common bases, address adapters,
exact grids, prime selection, analytic estimates, streaming, recovery and
fixed-tape interfaces. [NOTICE](../../NOTICE) preserves attribution; the adopted
proof sources and original notices are pinned in `SOURCE.json`.

## Credits

- **icekylinx**: three-stage Cayley cover, general Clifford frames and weighted bit interface (PR #130), and the stopped product-ring framework (PR #104).
- **eumemic**: PR #117 local complex DAG, PR #129 physical gate-frame descent, and PR #131 cover-local-reuse verifier and reflection audit architecture.
- **jamesyc (James Chang)**: compensated birth-cut scratch reuse (PR #124).
- **Avi Eisenberg (ikeboy)**: paired lockstep first-stage cover (PR #132), saturated nondegenerate intersection placement (PR #110), and PR #120.
- **an664**: completed-core sharing on orthogonal subspaces (PR #128).
- **Rohan Arun**: PR #113, PR #118, PR #123; **Joel Pulikkan (GamingPuzzled)**: PR #125, PR #127, PR #134; **Daniele Corso (danicorso)**: PR #126.
- **Zhihao Chen (jacklightChen)** and **Swapnil Jain**: PR #97 physical deferred bit word and underlying witness.
- **Thomas Marchand**: radical-complement frame lifting, phase-aware role compilation, cover-weighted local search, donor-chain shrinking, recipient frame snapping, per-bank literal reflection audit, and paired/unpaired composition (PR #133 and this package, prepared with Google Antigravity assistance).
