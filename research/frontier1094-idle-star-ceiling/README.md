# Idle rank-48 repartitions on #1094: exact ceiling, PR1252 recount and a star-move lead

**Scoped finding; no new selected κ and no admitted construction.** For one named
residual subproblem of the selected #1094 packing, the idle rank-48 remainder, this
package gives an exact price ceiling, an independent recount of PR1252's matching
maximum, and the exact optimum of a broader move class with an explicit overlay. The
overlay is structurally verified but has **not** been through the controller, invoice
or strict assembly admission that PR1252 ran. The selected record, `upstream/` and
every frozen input are unchanged.

## Object

The frozen #1094 replay (`research/community-frontier1094-audit/selected-replay.tar.gz`,
`candidate/strict/global/hosted/IDLE-REMAINDER-FRAMES.json.gz`) has **4,866 idle
rank-48 children** that are unhosted, have no pending offset and are absent from the
T16 owner map. They lie in **1,792 (replica, port) groups** of sizes
`{1: 45, 2: 703, 3: 761, 4: 283}`. The rest of the idle remainder (hosted rank-1/3/7
children) and all local-word children are held fixed.

PR1252 (Gonzalo-Mier, head `1b9db2fa`) moves 3 commuting axes inside 1,825 disjoint
pairs, `48 + 48 → 45 + 51`. Its open questions ask for an independent reproduction of
the matching maximum and for coordinated moves among more than two children.

## Result

Exact native prices from the pinned multicold `moment`/`base_two_moment`/`outer` engines
(the price and outer recipe are PR1252's `math_support.price`, restated):

| Profile | 48-children become | κ (native) | Gain over #1094 | Share of ceiling gain |
|---|---|---|---:|---:|
| #1094 selected | 4,866 × 48 | 0.001672660197076918 | — | 0% |
| PR1252 pair class (independent recount: **1,825**) | 1,825×45, 1,216×48, 1,825×51 | 0.001672846574134982 | 1.864e-7 | 37.9% |
| **Disjoint-star class optimum** | 796×42, 765×45, 948×48, 2,357×51 | **0.001672987659462603** | 3.275e-7 | 66.6% |
| **Ceiling: any within-group repartition** | 283×39, 761×42, 703×45, 45×48, 3,074×51 | **0.001673151843213755** | 4.916e-7 | 100% |

Conservative prices are 0.001672660194225008 (matches the selected record), 0.001672846571282754
(matches PR1252), 0.001672987656610135 and 0.001673151840361007.

1. **Ceiling.** In a group of `k` such children the mass is `48k`. No child can be
   deleted, because `48k > 51(k−1)` for `k ≤ 16`, and splitting a child only raises the
   subadditive moment. The halving guard caps ranks at 51 (`73² > 2·51²`). The main
   moment `Σ r^(1−a)` is Schur-concave at a fixed child count, so the
   majorization-maximal vector `(51^(k−1), 51−3k)` minimizes it. With the outer recipe
   unchanged, **no within-group repartition of these children, under any commuting rule,
   can exceed κ = 0.001673151843213755**. As a control, four deterministic random
   repartitions are priced and all stay below the ceiling. This bounds PR1252's
   "multi-child moves" route at about **+0.00000049** κ, which is 3.4% of PR1240's
   fixed-word packing headroom (κ < 0.0016872026). Larger gains need hosted or
   local-word mass, which PR1240 covers, or a different word.
2. **PR1252 recount.** Under PR1252's rule, an independent per-group exhaustive
   matching finds exactly **1,825** pairs. Under the same rule, this reproduces its κ
   at both native and conservative precision.
3. **Star class.** A centre child sends up to 3 axes to each of several leaves, and
   leaves reach 51. Every moved axis satisfies the per-axis PR1252 rule: it commutes
   with all original leaf axes, every stage entry/exit X and Y, the terminal Y
   translation and the terminal translations of both centre and leaf. The class
   contains the pair class. The exact per-group optimum comes from enumerating set
   partitions × centres with bipartite b-matching of axes, and the choice is invariant
   between `a = 0.0016756` and `a = 0.01`. It yields **2,357 moves from 1,561
   centres** and κ = 0.001672987659462603. This is +1.41e-7 over PR1252 and two
   thirds of the ceiling gain. The moves are in `STAR-MOVES.json.gz`.

## Verification

```sh
python3 -B research/frontier1094-idle-star-ceiling/analyze.py --check   # ~5 s
python3 -B research/frontier1094-idle-star-ceiling/verify.py            # ~2 s
python3.12 scripts/research_package.py --package research/frontier1094-idle-star-ceiling
```

`analyze.py --check` recomputes everything from the committed replay archive and
requires byte-identical `RESULT.json` and star payloads. Each price asserts acceptance
at its exact endpoint, rejection at endpoint+1e-24, all 47 strict outer constraints,
and rejection of the next 1e-18 κ grid point. `verify.py` does not import
`analyze.py`. It re-derives every move's commuting conditions and checks the orthonormal
resulting axis sets, unchanged per-group axis multisets (hence each group's Z4 phase
polynomial), disjoint stars, the rank cap, the absence of hosted and owner children, and
the profile. Seven mutation controls must be rejected: a non-commuting axis, an axis
moved twice, a reused leaf, a rank-52 leaf, a foreign axis, a hosted leaf and a centre
that is also a leaf. Its receipt is `STAR-AUDIT.json`.

**Not checked:** the serialized controller/owner audit, the mixed-provider invoice and
the strict global assembly with its negative controls, for the star overlay. The
soundness of composing PR1252 transfers into stars is inherited from PR1252's pair
argument and not proved here (see the open questions). The all-size compiler,
common-label/mutable-source realization, hosting, precision/tape and analytic-transfer
obligations of the selected record remain conditional.

## Open next questions

The structured list is in [TASK.json](TASK.json):

- **Admission of the star overlay.** Generalize PR1252's `audit_allcold_idle_overlay.py`
  from pairs to `(centre, leaf, moved_axes)` records, re-pin the SPEC and rerun its
  controller and assembly controls. This is blocked on PR1252 being unmerged.
- **Contract for multi-leaf moves.** Does a moved idle axis need to commute with
  anything beyond the donor and receiver? The first step is to state the controller
  contract.
- **Stacking on stronger words.** Apply the same analysis to the idle remainders of the
  open X54 / mixed-T37 candidates (PR1218/PR1261, κ ≈ 0.0016758), since the gain is
  additive in the moment.

## Credit

Gonzalo-Mier's PR1252 provides the move, the commuting rule and the pricing recipe, and
its open questions define this scope. The #1094 replay, T16 owner map and engines are
those of the selected review and its retained supplier ancestry. PR1240 (Douglas Colkitt)
provides the broader fixed-word packing ceiling. Coordination is in
[Discussion #1265](https://github.com/CrocSwap/integer-mult-bounds/discussions/1265).
This package was prepared by Guéorgui Maissouradze (GitHub: PatatePatatePatate) with
substantial Claude (Anthropic) assistance. Apache-2.0.
