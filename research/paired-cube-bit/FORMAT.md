# File formats (paired-cube bit word, `P` in {11, 12, 13}, `h = 2P`)

All files are plain JSON with sorted keys, written by `paired_cube_bit_word.py --p P`.
`--check` regenerates them byte-identically. The exceptions are `word_pP.json.gz`, a compact internal copy
written with gzip `mtime = 0`, and `profile_pP.json`. Nodes, ports and roles are zero-based integers.

## Conventions

- **Ports.** `labels[i]` is the triple of coordinates of port `i` (for example coordinate `2k + b` is
  member `b` of pair `k`). Port `i` is also graph node `i`, a source leaf.
- **Label.** `chi_S` in `Q^h` is the 0/1 indicator of `labels[S]`.
- **Target covector.** The target covector of port `T` is `3*chi_T - 1`. The cap of `T` is
  `{u : (3 chi_T - 1).u = 0}`, the H0-orthogonal complement of `chi_T` for `H0 = (I - J/9)/2`.
- **Nondegeneracy.** Nondegeneracy is tested for `G = I - J/9` (equivalently `H0`).
  - A frame with integer basis `B` is nondegenerate iff the integer matrix `9 B B^T - (B1)(B1)^T` is
    nonsingular.
  - A frame given by integer annihilator rows `A` is nondegenerate iff the dual matrix
    `(9-h) A A^T + (A1)(A1)^T` is nonsingular.
- **Scalars.** The payload is F2: every coefficient is 1 (mod 2), and every op is an XOR.

## `graph_pP.json` — scalar circuit and decoder

- `p`, `h`, `v`, `labels`.
- `args[x]`: `null` for the source leaves (`x < v`); otherwise `[a, b]`, where node `x` is the sum of
  nodes `a` and `b`. Supports are disjoint, so node `x` equals the XOR of the sources in its support.
- `roots[j]`: an object with fields `node`, `targets` (a list of ports), `kind` and `coefficient`:
  - `kind` is `side` or `center`; `coefficient` is always 1.
  - Side roots carry `channel`, one of `face0`, `edge12`, `face1`, `edge01`, `face2`, `edge02` or
    `partner`. A `partner` root's node is a source leaf (single-source root). At p = 12 (variant u) the
    merged channels `u01` (face1 + edge01) and `w02` (face2 + edge02) replace the four single reads.
  - Centre roots carry `coordinate c`. Their node is `star(c)` (the sum of all ports containing `c`), and
    their targets are all ports containing `c`.
  - Root `j` adds its node's value into `Y_t` for every `t` in `targets`. Broadcast roots have several
    targets: `face0` reaches 4 targets and `edge12` reaches 2.
- `partner_mix[k]`: an object `{carrier, passive, receivers:[a, b]}`. It adds `x_carrier + x_passive` to
  `Y_a` and `Y_b` through source-register mixing (see `kchron`).
- `decoder`: the identity being implemented,

      Y_T += x_T = sum_{c in T} star(c) + sum_{|S cap T| = 1} x_S   (mod 2).

  Stars are read with coefficient 1 for each `c in T`. The side part is the XOR of all side roots
  (including the partner singles) received by `T`, plus the partner-pair sum, and it equals
  `sum_{|S cap T|=1} x_S`.

## `word_pP.json` — compiled physical word (shaped like #144's `selection.json`)

- `ops[i] = [dest, control, node]`. This means `z[dest] ^= z[control]`, at the frame of `node`.
  - For an addition node, `dest` holds one operand and becomes the sum, while `control` keeps the other
    operand.
  - For a copy (an extra use of a value), `dest` is the fresh role and `control` is the value's role.
  - ops are listed in execution order.
- `sources[str(leaf)] = role`: the auxiliary role receiving `z[role] ^= x_leaf` (the V injection at the
  rank-one frame `<chi_leaf>`).
- `rootroles[j]`: the role that is read into the targets of `roots[j]`.
- `phase1`: indices of the ops in the centre closure, recomputed by the checker.
- `gauges[k] = {role, first, targets, dim, frame}`. Each entry is a deferred old-value read of `role`'s
  dirty content, at frame `frame` (an exact annihilator id in `frames`, of dimension `dim`):
  - `first` is the node of the role's first op;
  - `targets` is the role's response support;
  - selection order is listed, and the time order per target is the reverse of it, which is ascending.
- `order`: compile order of the active nodes; `arcs`: the frozen carrier links `[donor, use]`, with `use`
  either `["op", node, operand_slot]` or `["root", j]`.
- `plain`: nodes whose frame is the plain span of their support.
- `node_frame[str(node)]`: frame id of every active node. The frame of op `[dest, control, node]` is
  `node_frame[node]`.
- `root_frame[j]`: frame id of root `j`. For side roots this is the common cap of the targets; for centre
  roots it is the star span, of dimension `h-2`.
- `source_frame[S]`: frame id of `<chi_S>`. `full_frame`: id of `Q^h` (id 0, no annihilator rows).
- `conventions` and `schedule`: text restating the above.

## `frames_pP.json` — exact frames

- `frames[str(id)]` is an object `{dim, a}` or `{dim, b}`. Its rows are primitive integer vectors of
  length `h`, the rows of the rational RREF scaled to integers:
  - `a`: annihilator rows; the frame is their common kernel, of dimension `dim = h - len(a)`.
  - `b`: basis rows; the frame is their span, of dimension `dim = len(b)`.
- The representation with fewer rows is stored. The checker computes the other one exactly by integer
  elimination and verifies `A.B^T = 0` and `rank A + rank B = h`.
- `P_used_for_ranks`: the generator computes ranks modulo the Mersenne prime `2^127 - 1`. Every minor of
  the integer generator matrices involved is below this prime by Hadamard's bound for `h <= 26`, so
  modular ranks are rational ranks. The exported integer rows are recovered by rational reconstruction and
  are re-verified exactly by the checker, which uses no modular arithmetic.

## `kchron_pP.json` — partial-K chronology

`entries[k]` lists, for each partner pair `{carrier c, passive d}` and its receivers `[a, b]`, the
following fields:

- `mix_frame`: id of `M = span{chi_c, chi_d}` (dimension 2, H0-Gram `I_2`).
- `deliver_frame`: id of the receivers' shared cap `C`, the frame of `roots[deliver_after_root]`, whose
  targets are exactly `[a, b]` (the `edge12` root).
- `deliver_after_root`: the delivery happens right after this root's read, while `Y_a` and `Y_b` are at `C`.
- `undo_frame`: the full frame.
- `carrier_chain`: `[<chi_c>, M, C, full]`, with ranks `[1, h-4, 2]`.
- `passive_chain`: `[<chi_d>, M, full]`, with ranks `[1, h-2]`.

Chronology:

1. Run all V injections at the rank-one frames.
2. Raise `X_c` and `X_d` to `M`, then set `X_c ^= X_d`.
3. Raise `X_c` to `C`. After root `deliver_after_root` is read, set `Y_a ^= X_c` and `Y_b ^= X_c`.
4. After all target reads, raise `X_c` and `X_d` to full and set `X_c ^= X_d`.
5. Run the inverse producer and the V removal.

## `profile_pP.json` — PR #144 bit ledger

- `h, v, R, c, q, matched, loss` (copied-centre loss `= h(h-2)`).
- `m = 3h`, `W_per_vertex = 2v + R`, `rank_per_vertex`, `deficit_per_vertex = 2v - 3*loss`.
- `selected_rank_histogram` (gauge dimensions); `remaining_internal_histogram` (local auxiliary children
  after gauging, centre copies included); `source_data_histogram`; `target_data_histogram`.
- `child_histogram`, which is assembled as:
  - 3 times the local, source and target histograms;
  - plus one child of width `3*dim` per gauge;
  - plus `2v` children of width 2.

## `certificate_pP.json` — exact moment

The method is PR #144's `bit_certificate`:

- an exact upper moment with `log_upper` and `exp_upper`, rounded to the grid `2^-120`;
- the full `32 m^2` local-ring fallback on a fraction `1e-16` of every edge.

`coarse_saving` is the largest point `k/10^10` that passes, and `next_grid_point` is rejected.
`effective_bit_saving = (1 - 1e-3) * coarse + 1e-3 * 384599/1e10`.

## `data/`

- `pair_module_p{11,12,13}.json`: pinned pair-disjoint modules with provenance, re-derivable by
  `derive_pair_modules.py`.
  - p=11 and p=12 are cut from an h=21 bit witness (sha256 in the file).
  - p=13 is PR117's `restricted_pairs(12)`.
- `arcs_p{11,12,13}.json`: frozen carrier matchings. `--solve-matching` recomputes them deterministically
  with Hopcroft-Karp.
