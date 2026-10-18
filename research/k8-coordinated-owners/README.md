# Coordinated k8 owners: conditional κ = 0.001672196274581061

Coordinated reassignment of complete calls improves the conditional κ from
PR1018's **0.001671665283218770** to **0.001672196274581061**, a **0.0317642%**
gain. The circuit is PR1018's R480 k8 leaver word with seven additional
triangle slots. This contribution improves its whole-helper ownership map.
Larger κ is better in the bound `n (log n)^(1−κ)`.

The fresh k8 and slot rebuild reproduced PR1018 before the changed ownership
map was admitted. This is a conditional finite construction; the inherited
all-size/compiler, mutable-source realization, hosting, precision/tape,
analytic-transfer and bit H1–H5 assumptions remain. See [NOTICE.md](NOTICE.md)
for attribution and precise reuse scope.

| Quantity | Verified result |
|---|---:|
| κ | 0.001672196274581061 |
| Complex saving lower endpoint | 0.001674997198656588841754 |
| Bit saving lower endpoint, unchanged | 0.001733427039589844234749 |
| Replicas / complete calls / helpers per call | 8 / 72 / 480 |
| Serialized helper roles | 34,560 |
| Live / physical families | 7,168 / 7,658 |
| Rank mass / deficit | 520,704 / 2,560 |
| Global coefficient prefix / charged bits | 253 / 512 |
| Physical row coefficient / retained limit | 16,467 / 20,161 |

The per-call profile is `{1:2412,2:418,3:432,4:142,5:82,8:8}`. The helper-width
inventory is `{4:56,5:32,7:30,8:122,9:240}`. The idle remainder profile changes
from `{1:1099,2:9,3:179,7:54,16:23,48:2419}` to
`{1:1110,3:247,23:2,32:4,39:1,48:2426}`. The actual controller, spectator
permutations and complete invoice are rebuilt from the serialized roles.

## Search and verification

A single-call min-cost reassignment found no improvement. The new search
removes two, three or four complete calls, groups available bins by their
remaining capacity and allowed calls, and solves an integer pattern assignment.
Each pattern uses a bin at most once per call. Six-call searches specifically
target occupied capacity-48 bins; these moves hold widths 5 and 7 fixed and
jointly place widths 4, 8 and 9. A final four-call pass cleans up residuals.
Stable prefix compaction emits the literal owner map.

The objective uses floating arithmetic for discovery. Integer assignments are
checked before use, and timed-out solves may contribute feasible incumbents.
There is no claim that a neighborhood or the final map is globally optimal.
The independent physical audit and two rational moment engines determine the
claim, rather than the optimizer objective.

The admission runtime copies PR1018's verifier files **byte for byte**. Only
the owner file, derived PLAN fields and frozen expected-value SPEC change.
There are no relaxed guards or special-case acceptance paths.

The completed run includes the 21-stage k8 chain, five sets of 95 cold-end
controls, 34 slot-control outcomes, fresh native forward/backward programs,
exact local phases, independent local audit, and the strict global replay.
The latter checks 15 controller mutants, 69 admission mutants, 12 bit-supplier
mutants, both rational moment engines, 47 strict outer inequalities, and the
next-grid and recurrence-model controls. The bit circuit is cited unchanged
and repriced; it is not rebuilt by this run.

## Reproduce

Use Python 3.11+ and the repository's native verifier prerequisites, including
Boost where required. The verifier itself does not need SciPy. From the
repository root, choose fresh output directories:

```sh
python -B research/gauge44-slots/construction/reproduce.py \
  --main . --pr635 research/complex-sw4-frame8/vendor/pr635 \
  --out /tmp/k8-initial --until word

python -B research/k8-coordinated-owners/verify.py \
  --word-dir /tmp/k8-initial --work /tmp/k8-coordinated
```

The first command builds the historical shadow/hamming inputs; the verifier
then constructs the k8 word and slot layer. A completed native rebuild may be
explicitly reused with `--native-from /path/to/native` instead of `--word-dir`.
That directory must contain completed `word/`, `chain/`, and `slots/` runs.
The verifier rechecks their step coverage, pinned programs, canonical words,
Clifford recipes, control counts and baseline result, then rebuilds the entire
changed global controller and admission. The recorded run freshly built this
native chain and subsequently used that explicit reuse path for final admission.

The optional search requires NumPy and SciPy/HiGHS. It is not part of admission.
Run `discovery/search_calls.py --help` from the repository root. The recorded
sequence is `(block, passes, seed, seconds per solve)`:

```text
(1, 12, 13, 3)       negative single-call screen (stopped after 3 unchanged passes)
(2, 240, 13, 2)      starting from the upstream owner map
(3, 360, 27, 2)      starting from the preceding output
(4, 240, 41, 3)
(6, 24, 53, 5)      --target48
(6, 48, 67, 3)      --target48
(4, 160, 79, 2)
```

Use `--input previous-output --out fresh-output` to chain searches.
Solver timing/version can change the nominated map. The frozen `OWNERS.json.gz`
and `SPEC.json`, rather than a rerun optimizer, reproduce the certified result.
`discovery/SEARCH-LOG.json` records accepted changes and solver statuses.

## Exact limit of this packing family

An independent extension of PR942's signed-dual argument proves that **every
replica count** for this fixed local circuit, helper inventory and bin stock
has κ-grid upper bound **0.001674097969905390**. This is an upper relaxation,
not an attained construction. It leaves about **0.114%** improvement above the
present result; a major increase must change assumptions of this packing family.

With PR795/890 width prices `(-1,-20,-8,-2,4)` and capacity bonuses
`(2,4,8,-13)`, two independently structured enumerations agree on all 1,163
bin patterns. The remainder mass per replica is 14,814, the signed price is
−1,084, and the required dual credit is 140,550. Thus the supporting rank-one
solution has normalized remainders `{1:5622/37,48:11302/37}`. Both exact
rational engines certify the supporting inequalities and the next-endpoint
rejection. Every feasible physical owner map is subject to these necessary
inequalities. Since the retained outer transfer has `κ < b/(1+b)`, the certified
upper endpoint for `b` gives the stated grid ceiling.

```sh
python -B research/k8-coordinated-owners/independent/all_t_bound.py \
  --out /tmp/k8-all-t-bound.json
```

The separate floating stage-count screen considers bank-free paired-chain
relaxations with 5, 7, 9, 11 and 13 stages. It finds no improvement over nine
stages in that search. It is not a proof against other circuits, banked
constructions, helper splitting, or different recursion geometries.

`CLAIM.json` contains the frozen numerical claim. `evidence/RESULT.json` and
`evidence/ASSEMBLY.json` contain the completed strict admission;
`evidence/ALL-T-BOUND.json` contains the separate exact upper-bound certificate.
