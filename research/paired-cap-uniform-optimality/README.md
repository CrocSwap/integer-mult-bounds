# Uniform optimality of PR2930's fixed-inventory packing

The complete paid profile in [Marius-Paul Dumitrean's PR2930](https://github.com/CrocSwap/integer-mult-bounds/pull/2930),
at `81f3b5d12977eba09e06fbff729167d59faabe90`, attains the **exact complex-moment
root optimum of its stated fixed-inventory packing relaxation**. This independent
certificate proves dual feasibility throughout the source's existing root interval:

```text
0.001722499906443274564357 <= b <= 0.0017224999064432745643571.
```

Of all 1,163 feasible bin patterns, eleven have identically zero reduced cost.
Every other pattern has reduced cost **greater than 1/250 throughout this interval**.
Both strict endpoint signs and the source basis' primal feasibility also pass.
There is no new kappa, physical allocation or selected-frontier change.

## What this adds

PR2930 already supplies the allocation, integral basis, exact cap bracket and
author-checked complete supplier replay. Its retained
[relax_exact.py](inputs/relax_exact.py) certifies dual signs at the **upper endpoint**.
That establishes the reported bracket. Equality of two printed brackets alone
does not establish equality of their unknown exact roots. The uniform inequalities
below justify the stronger exact-attainment conclusion at the root itself.
The existing numerical bound is corroborated, not corrected.

Arham Tahir's [PR2893](https://github.com/CrocSwap/integer-mult-bounds/pull/2893)
already establishes a uniform dual and integer optimal-face theorem for
PR2863's different inventory and earlier, disjoint root interval. This is a
source-specific independent application to PR2930, not a new general method.
The previous [PR2932](https://github.com/CrocSwap/integer-mult-bounds/pull/2932)
checks PR2917's local frame ledger; it does not establish this packing implication.

## Model and exact proof

Each replica has nine local calls, 896 live families and base width 73. The
fixed helper widths per call are `{4:26,5:2,7:62,8:96,9:222}`; the paid local
profile is `{1:2416,2:640,3:280,4:110,5:26,8:8}`. Bin capacities 8, 16, 32 and
48 have respective per-replica quotas 672, 448, 448 and 448. A pattern is an
unordered multiset of these helper widths with total at most its capacity.
Each bin pays one child of its residual rank, with no child for residual zero.
These are the source model's hypotheses, not a universal hosting contract.

Put `H_r(b)=r*(73/r)^b` for `1<=r<=48`, and `H_0(b)=0`. For `T` replicas and
complete profile `n_r`, the moment is

```text
M(b) = sum_r n_r H_r(b) / (73*896*T).
```

The nine stored basis patterns have these integral multiplicities per replica:

| Capacity | Helper multiset | Count | Residual |
|---|---|---:|---:|
| 8 | [8] | 672 | 0 |
| 16 | [7,9] | 352 | 0 |
| 16 | [8,8] | 96 | 0 |
| 32 | [7,7,9,9] | 103 | 0 |
| 32 | [5,9,9,9] | 18 | 0 |
| 32 | [9,9,9] | 93 | 5 |
| 32 | [4,9,9,9] | 234 | 1 |
| 48 | [9,9,9,9,9] | 81 | 3 |
| 48 | [] | 367 | 48 |

Their columns satisfy all four capacity and five width-inventory equations.
Thus the idle profile per replica is `{1:234,3:81,5:93,48:367}` and the
complete profile is `{1:21978,2:5760,3:2601,4:990,5:327,8:72,48:367}`.
Multiplication by 74 gives the exact frozen PR2930 `PROFILE.json`.
Capacity mass 48,384 minus helper mass 29,826 leaves idle mass 18,558;
adding local mass 46,530 gives complete rank mass 65,088 per replica.

Here is an explicit dual. Write
`A=(-3H_3+5H_5+3H_48)/20`. The four capacity prices are
`(A,2A,4A,H_48)`. The five width prices, in order `(4,5,7,8,9)`, are

```text
(H_1-H_5, -H_5, (H_3-5H_5-H_48)/10, -A, (H_3-H_48)/5).
```

For pattern `p`, let `a_p` be its capacity-indicator and width-count column,
and `r_p` its residual. Its reduced cost is
`delta_p(b)=H_(r_p)(b)-a_p dot y(b)`. The checker derives `y` by exact rational
elimination from the nine basis columns; it does not trust this displayed formula.
Recursive enumeration produces every count vector once: 6, 27, 215 and 915
patterns for the four capacities. Besides the nine basis types, precisely
`(32,[7,8,8,9])` and `(32,[8,8,8,8])` have identically zero reduced cost.
For every other pattern, directed rational bounds prove `delta_p(b)>1/250`
simultaneously on the closed interval. The weakest certified pattern is
`(48,[4,8,9,9,9,9])`, with

```text
delta = (25H_5 - 19H_3 - H_48 - 20H_1)/20,
uniform lower bound =
8131515346620953906790491034765372390079774482261 /
2000000000000000000000000000000000000000000000000000 > 1/250.
```

**Exact attainment.** Let `b*` be the unique root of the basis profile's
moment. Every positive-rank term is continuous and strictly increasing;
the certified endpoint signs place `b*` strictly inside the interval.
Every feasible profile has `M(0)=65088/65408<1`, while its fixed local
contribution gives `M(1)>=31320/896>1`. Thus every competing profile also
has a unique root in `(0,1)`.
For any nonnegative feasible pattern multiplicities `x`, the inventory
equalities give

```text
sum_p x_p H_(r_p)(b) - rhs dot y(b) = sum_p x_p delta_p(b) >= 0.
```

The source basis uses only zero-cost patterns, so it attains this bound.
Adding the common paid local profile preserves the comparison. At `b*`,
every feasible packing therefore has moment at least one and has root no
larger than `b*`. A packing using any positive amount of a non-tight pattern
has strictly larger moment there. This proves exact root optimality, not
just agreement to the displayed decimal precision. Scaling the integral basis
preserves abstract feasibility for positive integer `T`; it supplies no physical
schedule for a new replica count.

The source's delivered conditional headline is the lower endpoint minus
`10^-46+10^-70`. It is **not** the exact root `b*`, and this audit does not
change that headline or claim another outer transfer.

## Independently certified arithmetic

`uniform.py` imports no predecessor implementation. For `1<=x<=2`, it sets
`z=1-1/x` and uses

```text
x^b = sum_(n>=0) (b)_n z^n / n!,       0<=b<=1, 0<=z<=1/2.
```

All terms are nonnegative. The next-term ratio is at most `z`, so the first
omitted term divided by `1-z` bounds the tail. Each recurrence step rounds
outward on the integer scale `10^50`; 192 nonconstant terms are retained. Powers of two
reduce larger bases, with outward-rounded interval multiplication. Since
`73/r>1`, lower-endpoint lower bounds and upper-endpoint upper bounds enclose
each `H_r` throughout the interval. Signed linear combinations use the
appropriate end of each enclosure. This differs from PR2930's log/exp engine.

The full deterministic receipt in [RESULT.json](RESULT.json) records the dual,
tight types, minimum margin, endpoint intervals, conservation equations and
a digest of all reduced-cost records. The optional Python API
`verify_certificate(cert, profile, details=True)` exposes every record.

## Reproduce and evidence

Python 3.12, standard library only. The portable direct commands also work
without Git or the rest of the repository:

```sh
python3.12 -I -B research/paired-cap-uniform-optimality/verify.py
python3.12 -I -O -B research/paired-cap-uniform-optimality/verify.py
python3.12 -I -B research/paired-cap-uniform-optimality/test_verify.py
python3.12 -B scripts/research_package.py --package research/paired-cap-uniform-optimality
```

Verification is read-only. `--emit` prints the complete recomputed receipt;
`--write-result` explicitly regenerates it. [INPUTS.json](INPUTS.json) binds
eight frozen source files by SHA256, Git blob ID and length. Documentary Python
files under `inputs/` are never executed. Generic provenance is in
[SOURCES.json](SOURCES.json). `PROFILE.json` is an authenticated source claim;
this package does not reconstruct it from the literal owner placements.

Seventeen test groups include an independent Cartesian pattern census, exact
rational square-root calibrations, basis singularity/capacity/count failures,
a same-rank-mass profile corruption, false brackets, warm-cache type rejection,
source/manifest/inventory corruption, typed receipt comparison and a machine-readable
single-document `--emit` response. A broad
containing interval deliberately fails the conservative uniform-bound check;
that control is not a proof that the true dual fails on the wider interval.
See [VALIDATION.md](VALIDATION.md) for the recorded execution and limitations.

## Scope

This establishes a finite, source-bound packing theorem with a written proof
and exact executable certificate. It does not verify the literal source windows,
physical owner families, native operators, buffers, precision, full supplier or
outer release. The words' inventory/local-profile derivation is inherited.
All-size/compiler, realization, hosting, precision/tape and analytic conditions
remain separate. No formal-kernel proof or independent human review is claimed.

## Open next questions

The joint-extraction work in [Discussion2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612)
was published during this session as [PR2942](https://github.com/CrocSwap/integer-mult-bounds/pull/2942),
head `a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf`. It changes the words and
inventory and reports a fractional basis at T74. Its claim is not replayed here.
This theorem cannot be transferred merely by changing a headline or seed.
The next useful independent test is to pin that changed complete profile,
solve its primal inventory equations and certify its own dual throughout
its own root interval, separating fractional optimality from integer and
physical attainment. [TASK.json](TASK.json) records this bounded question;
no further fixed-PR2917 allocation search is proposed.

## Credit

Marius-Paul Dumitrean/PR2930 supplies the fixed-inventory model, basis, cap and
allocation; Mason Hale/PR2917 the changed paired-helper words; Jeremy Diviney/PR2908
the paired extraction; Jeremy Kothe/PR2894/2833 the source construction;
Yiyang Lu/PR2857/2848 the flow/realization lineage; Dugongue/PR2863/2839 and
Tekalign the retained packing and owner checks. Arham Tahir/PR2893 supplies the
closest prior uniform optimal-face method; earlier R480 work by Ali Romman
retains its separate precedent. Original [credits](inputs/CREDITS.md) and
[NOTICE](inputs/NOTICE) are preserved byte for byte.

New audit by ToikY, with substantial OpenAI Codex assistance in derivation,
implementation, testing, separate AI checks and writing. Apache-2.0 under the
repository license.
