# Closed-form κ ceiling for the exponent assembly

> **Arithmetic note; no new κ claim.** Both in-tree assembly checks already compute
> this ceiling (`minimum_margin`, in
> [`structured_bulk_assembly.py`](../../scripts/structured_bulk_assembly.py) and
> [`balanced_assembly.py`](../../research/copied-fixed/balanced_assembly.py)).
> [`scripts/assembly_ceiling.py`](../../scripts/assembly_ceiling.py) adds the ceiling
> as a closed form, a table of which of the 47 constraints can fail, and tests at
> finitely many exact points. The reduction follows from the short argument below;
> it is not machine-checked or formally verified, and no human has reviewed it.
> Whether the balanced layout is valid for any particular network is a separate
> hypothesis not examined here. Numbers refer to commit `d1d6c07`.

With bit saving `a`, complex saving `b` and backoff η (`h` for the balanced prefix)
put q = a(1−2η), ε = (1−η)/D and G = εq:

| prefix | D | ceiling G |
|---|---|---|
| original (`structured_bulk_assembly.py`) | 1+q(2+η) | a(1−η)(1−2η) / (1+a(1−2η)(2+η)) |
| balanced (`balanced_assembly.py`) | 1+q | a(1−h)(1−2h) / (1+a(1−2h)) |

## The claim

For exact rational inputs the reference accepts (a, b, κ, β, η) exactly when the
conditions below have positive slack. So the accepted κ form (−∞, G) for the original
prefix and (0, G) for the balanced one (its reference also requires κ>0). G is not
attained and equals `minimum_margin`. Letting η→0⁺ gives a/(1+2a) and a/(1+a),
which [the RaD report](../../references/semantic-bulk/rad20/reports/downstream-semantic-bulk-assembly.md)
(lines 56–59) states informally; since a<(1−β)b<1/32, κ<1/34 and κ<1/33.

At the six original certificates `minimum_margin` equals `ceiling()` exactly, with κ
below it by 9.4×10⁻¹³ to 9.9×10⁻¹¹ (paired-cube: κ = 4.609169×10⁻⁴, G = 4.609169995×10⁻⁴).
The same holds at 24 balanced files (22 under `research/`, plus
`certificates/joint-dual-kappa.json` and `certificates/skip-frame-kappa.json`).

## Reduced conditions

Each needs strictly positive slack. Domain conditions are evaluated first; if one
fails the later slacks are not evaluated, so nothing divides by zero.

| condition | slack | kind |
|---|---|---|
| `bit_positive` | a | domain |
| `beta_positive`, `beta_below_one` | β, 1−β | domain |
| `backoff_positive` | η | domain |
| `q_positive` | q (η<1/2 once a>0) | domain |
| `complex_below_one_over32` | 1/32−b | bound |
| `leaf_saving_above_bit` | (1−β)b−a | bound |
| `kappa_below_ceiling` | G−κ | kappa |
| `literal_scalar_guard`, `row_product_gap` | network constants `strict_literal_gap`, `degree_gap` | bridge |
| `kappa_positive` | κ (balanced only) | kappa |

Three carry the content: `complex_below_one_over32`, `leaf_saving_above_bit` and
`kappa_below_ceiling`. `leaf_saving_above_bit` forces 0<a<(1−β)b<b<1/32, so the
reference's `max(σ−τ,0)` branch is dead: `internal` always equals τ.

`COVERAGE` in the module has one row per reference constraint: a status (`reduced`,
`duplicate`, `identity` or `implied`), the conditions it depends on and the
expression that makes it positive. Original prefix: 9 reduced, 17 identity, 12
duplicate, 9 implied; balanced: 9, 14, 14, 10. 22 constraints per prefix depend only
on the three domain conditions `bit_positive`, `backoff_positive` and `q_positive`.

## Why the reduction is exact

Write s = (1−β)b−a and take the conditions as hypotheses. They give
0<a<(1−β)b<b<1/32, hence 0<q<a (since 0<η<1/2), D>1, 0<ε<1 and 0<G<q<1/32.

**A failed condition makes the reference reject.** Eight conditions are constraints
of the reference word for word. The other three equal one up to a positive factor:
`backoff_positive` is `delta_positive` (δ = η/8), `kappa_below_ceiling` is the margin
`compact_phase_layer` minus κ (that margin is G), and the balanced `kappa_positive`
is that reference's own κ>0 check.

**All conditions holding makes the reference accept.** Each of the other 36
constraints is positive for one of three elementary reasons:

1. *A positive multiple of a slack known to be positive*, e.g. `lambda_above_tau` =
   aη, and `q_below_internal` = 2aη (internal = τ because b>a).
2. *A sum of positive terms*, e.g. b−a = s+βb; 1−ε = G+η+εc (G+h for balanced);
   `q_below_leaf` = s+2aη. Every margin other than G is G plus a positive term (the
   original prefix margin is G+η), so each `*_above_kappa` row is (G−κ) plus a
   positive term.
3. *A simple bound from a<1/32 and η<1/2*, e.g. `cell_above_band` ∝ 2−3η−q(1+2η) >
   7/16, `alpha_below_one_fourth` ∝ 1−a(4−η) > 7/8, `short_record_fallback` ∝
   1−η−a−aq(2+η) > 0.46, `artificial_boundary` > 8−1−1/16−1/32 > 6.

The references' post-checks then hold automatically: `min(margins) = G`, and the
prefix identities (e.g. 1−ε(1+c+q) = η) are algebraic. Since κ appears only in the
seven `*_above_kappa` constraints, the accepted κ are exactly those below G.

## What the tests check

`tests/test_assembly_ceiling.py` checks the argument at finitely many exact points:
agreement with both references at the 6 original and 24 balanced certified points
and on a grid of 2400 points per prefix (κ at G−10⁻¹⁵, G, G+10⁻¹⁵, G/2, 0 and below
0); each condition violated once, with exact boundary points; that every `by` list
is sufficient; and the identities and proportionalities at every certified point.
These are evidence, not proof. Independent AI-assisted re-derivations and adversarial
searches were also run outside this repository; they are not committed and nothing
here relies on them.

## Where the two references differ

* **κ>0.** The original accepts κ≤0; the balanced rejects it. The module mirrors each.
* **Defaults.** η=10⁻⁸, β=1/4 (original) against h=10⁻¹², β=1/20 (balanced), so
  `backoff` and `beta` are required arguments.
* **Errors.** At 1+q(2+η)=0 the original raises `ZeroDivisionError` and the balanced
  `InvalidAssembly`; `check()` never raises on exact values.
* **Switches.** The balanced reference's `original_prefix`, `old_guard` and
  `old_exposures` keep the balanced c and ε, so `original_prefix` is not the original
  family; they are not modelled here.

## Scope and use

Arithmetic only: not a formal verification (see [CONTRIBUTING.md](../../CONTRIBUTING.md)),
and silent on the producers, the finite networks and the analytic hypotheses. The six
selected certificates use the **original** prefix; open pull requests that add
certificates change the numbers above. The bridge gaps can have thousands of digits,
so the module never converts a numerator to `str` or `float`.

```sh
python3 -m unittest discover -s tests -p test_assembly_ceiling.py -v   # Python 3.11+, no -O
```

```python
from fractions import Fraction as Q
import assembly_ceiling as ac   # scripts/ on sys.path

ac.ceiling(Q(1, 100), prefix='original', backoff=Q(1, 10))    # 9/1271
v = ac.check(a, b, kappa, beta, prefix='original', backoff=eta,
             literal_scalar_guard=gap, row_product_gap=degree_gap)
v.ok, v.complete, v.headroom, v.failing, v.reference_names
ac.feasible(a, b, kappa, beta, prefix='balanced', backoff=h,
            literal_scalar_guard=gap, row_product_gap=degree_gap)
```

`Verdict.ok` means no checked condition failed, and is also true when a bridge
constant was left out; use `complete` or `feasible()` for a full verdict.
