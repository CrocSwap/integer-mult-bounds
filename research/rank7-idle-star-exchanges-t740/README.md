# Idle rank-48 star exchanges on PR3148's T740 fill: conditional κ = 0.001730189061233850760095 − 10⁻⁴⁶ − 10⁻⁷⁰

**Author-checked conditional candidate; not maintainer-reviewed.** The selected record
on `main` remains #1094 (κ = 0.001672660197076918). This package stacks on the open,
unreviewed PR3148 (Jeremy Diviney: PR3133's words at their T740 packing cap) and does not
change its words, helpers, fill rows, order or dispatch.

```text
                       complex root bracket (1e-25)                         κ headline
PR3148 (baseline)      [0.0017297774946785970118869, ...8870]               0.001729777494678597011886 − 1e-46 − 1e-70
this package           [0.0017301890612338507600957, ...0958]               0.001730189061233850760095 − 1e-46 − 1e-70
gain                                                                         +4.11566555253748209e-7  (+0.0238%)
```

## Changed hypothesis

PR3133's fixed-capacity relaxation cap (RELAX-CAP) and PR3148's cap-attaining fill both
charge **one idle child per bin, of rank `capacity − used`**. They never move idle
capacity *between* bins. In PR3148's fill, **282,569** capacity-48 bins are completely
idle: no helper row touches them. They lie in 82,880 (replica, port) groups of sizes
`{1: 414, 2: 19103, 3: 9503, 4: 53860}`.

Gonzalo-Mier's PR1252 showed on #1094 that two such children can exchange three axes,
`48 + 48 → 45 + 51`. The move is legal when every moved axis commutes with all of the
receiver's axes, every stage entry/exit X and Y translation, the terminal Y translation
and both children's terminal translations. The group's total axis set, and hence its Z4
phase polynomial, is unchanged. `research/frontier1094-idle-star-ceiling` (Guéorgui
Maissouradze) extended this to **stars**: one centre sends three axes to each of several
leaves.

**The data needed for this rule is on main.** The rank-seven T74/T740 lineage uses the
same exact data-phase recipe as #1094 (`DATA-PHASES.json`, SHA-256
`c5916ff3…e8251fa`; GLOBAL-TEMPLATE `exact_data_phase_recipe_sha256`). Its per-port idle
children carry the orthogonal axis sets. For all 4,866 #1094 idle rank-48 children, these
axes equal the hosted `IDLE-REMAINDER-FRAMES` that PR1252 used, so legality is a
port-local property. It does not depend on the replica or on the local word.

## Result

The exhaustive per-group star optimum covers every role assignment of the idle children
(untouched, centre, or leaf of one centre). Each candidate is checked by an exact
disjoint 3-axis matching:

| Group shape after exchange | Groups |
|---|---:|
| `[51,51,48,42]` | 37,080 |
| `[48,48]` (no movable axes) | 19,083 |
| `[51,51,45,45]` | 16,780 |
| `[51,51,42]` | 8,463 |
| `[51,48,45]` | 1,040 |
| `[48]` (singleton) | 414 |
| `[51,45]` | 20 |

The search makes 125,706 three-axis moves and changes 205,869 children. The idle bill
`{48: 282569}` becomes `{42: 45543, 45: 34620, 48: 76700, 51: 125706}`. The rank mass
`65088·740` is unchanged. The maximum child rank is 51, and the finite halving guard still
holds: `73² = 5329 > 2·51² = 5202`.

The complete paid profile is
`{1:16376940, 2:4821840, 3:1567431, 4:679320, 5:147075, 8:53280, 42:45543, 45:34620, 48:76700, 51:125706}`.

The complex side still binds: the bit supplier is #589 at 0.001733427… > 0.00173019. The
within-group ceiling (any repartition of each group, `51^(k−1), 51−3k`) has root
0.00173069001404…. The star class captures 45% of that headroom.

## Reproduce

```sh
# baseline input: PR3148's own deterministic materializer (head f2927a4b)
python3 -B research/coupled-carrier-cap740/materialize.py --output /tmp/t740   # on PR3148's branch
python3 -B research/rank7-idle-star-exchanges-t740/build.py --fill /tmp/t740/COMPOSED-FILL.json.gz
python3 -B research/rank7-idle-star-exchanges-t740/verify.py --fill /tmp/t740/COMPOSED-FILL.json.gz
```

`build.py` authenticates DATA-PHASES and the decoded PR3148 fill payload
(`8f4d6965…`). It then derives `IDLE-48-BINS.json.gz` and `STAR-MOVES.json.gz`, and
writes `RESULT.json` with an exact rational root bracket. That bracket reproduces
PR3148's published one exactly for the baseline profile. Building takes about 15 s.

`verify.py` does not import `build.py`. It works from the committed files and does not
need the fill; the optional `--fill` flag rebinds the idle bins. It re-derives:

- every moved axis's commuting rule;
- disjoint stars, single-use axes and single-centre leaves;
- orthonormal, independent final axis sets;
- unchanged per-group axis multisets;
- the rank cap and halving guard;
- the complete profile and rank mass;
- the root bracket, using its own directed-rounding interval arithmetic (10⁻⁷²);
- the headline κ, gated above PR3148 and PR3143.

All nine mutation controls are rejected: non-commuting axis, axis moved twice, reused
leaf, foreign axis, centre that is also a leaf, hosted child, two-axis move, wrong profile
and the next root grid point. The receipt is `AUDIT.json`; the run takes about 3.5 min.

## Scope and remaining obligations

What is established: a literal, port-local axis overlay on PR3148's untouched idle
children. Every move satisfies PR1252's commuting rule, and the exact complete-profile
root with the lineage's headline convention is computed.

What is **not** run here:

- PR3148/PR3133's complete native admission, controller/owner audit and modern outer
  release with this overlay. That audit, `audit_mixed.py` in the T74 release chain, must
  be generalized to read idle axis overlays, as PR1252 did for the #1094 async auditor.
- Re-pinning the outer finite check `halving_integer_inequality = [5329, 4608]` to
  `[5329, 5202]`.

Soundness of the star class is inherited from PR1252's pair argument (unchanged group
axis set and phase polynomial, commuting moved axes), as in the star-ceiling package. All
inherited all-size compiler, realization, hosting, precision/tape, recovery and
analytic-transfer obligations of the lineage remain. PR3148 itself is an unreviewed
author claim; if it is not admitted, the same overlay applies to PR3133's T74 fill.

## Credit

- Gonzalo-Mier (PR1252): the idle exchange move, its commuting rule and its pricing
  recipe.
- Guéorgui Maissouradze (PatatePatatePatate): the star class and the per-group optimum
  (`frontier1094-idle-star-ceiling`).
- Jeremy Diviney (PR3148): the T740 cap-attaining fill.
- dcharb78 (PR3133, PR3042): the words.
- Marius-Paul Dumitrean (PR2979).
- Jeremy Kothe (PR3015).
- Nick Petalas (PR3024 lift).
- The credited rank-seven, T37-envelope and data-phase lineage.

Prepared by Rohan Arun. This was done with help from **OpenCode (Space bunny free)**,
which identified the idle-exchange lever and proposed porting it to the rank-seven line,
and with substantial Anthropic Claude assistance. Apache-2.0.
