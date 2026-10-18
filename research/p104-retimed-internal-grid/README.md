# Exact internal precision for the ADD-retimed P104 dual

The sharp uniform guard `ceil(9*lambda/2)+2` also applies to Vasek / flyingviper's
[PR2725](https://github.com/CrocSwap/integer-mult-bounds/pull/2725), exact head
`71d24b655c2fdddc063b9aaf285e8425ce197499`. Seven extra fractional bits suffice
and are necessary at one 512-coordinate layer. This includes native internal
butterflies, scalar multiplication temporaries and all eight private erasures.
Initial public physical real and imaginary components may be arbitrary multiples
of `2^-f`.

This is a **changed-source applicability result**. Ross Richardson's
[sharp Clifford-grid finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18959185)
already supplies the denominator argument for the unchanged PR2586 word.
PR2772's sufficient-grid package also binds that earlier word. Neither binding
alone certifies PR2725, whose README explicitly leaves precision transfer open.
Here the literal retimed word, its new recipes, every scalar product and the
sharp witness are rebound. No new Clifford denominator lemma is claimed.

Native operator correctness and the tensor-lift convention remain inherited.
This is not a paid recursive implementation, physical hosting result, complete
supplier or new kappa. The selected frontier is unchanged.

## Exact source boundary

| Input | Exact source | Use |
|---|---|---|
| Retimed word and two new recipes | PR2725 `71d24b655c2fdddc063b9aaf285e8425ce197499` | Actual chronological object |
| 128 fused recipes | commdata2338 / PR2662 `b67542b2896c21106f3945673bbf5b6e131408cc` | Surviving endpoint fusions |
| Original 1,245 recipes | PR2772 `69ba5a423246a1c9281bdd5c1f51240b454f2aa6`, retaining ywz65 / PR2586 | Unchanged native ancestry |
| Sharp-grid argument | Ross Richardson's linked finding | Credited proof method, not predecessor execution |

[SOURCES.json](SOURCES.json) binds exact copied bytes, Git blobs, paths and
heads. Original notices and source READMEs are retained in `inputs/`.
`kernel.py` adapts PR2772's Gaussian kernels and canonical-chart formulas;
that source is retained byte-for-byte as `inputs/PR2772-arithmetic.py` for
attribution, not execution. Only the dense scalar oracle is a separately
implemented checker. No predecessor executable is imported. The direct replay
needs no Git or network.

The recipe pool has 1,337 distinct frame-pair keys. The checker binds all
1,940 occurrences, including both new rank-seven/eight edges, and validates
all 1,917 distinct wrapper permutations and quadratic phase descriptions.
The complete paid profile and rank mass 3,542 are unchanged from PR2725.
This is structural and occurrence coverage, not a new cold proof that every
retained native operator equals its stated chart transport.

## Proof and applicability checks

### Clifford denominator bound, retained method

Let a dyadic Gaussian Clifford act on `n` binary coordinates. A computational
basis column is a stabilizer state. Project its stabilizer's Pauli labels onto
the X translations, obtaining a binary subgroup of dimension `h`. The diagonal
Pauli constraints restrict support to one affine coset of that subgroup.
Translation constraints make its `2^h` nonzero amplitudes have equal magnitude.
Unitarity makes that magnitude `2^(-h/2)`.

Write a nonzero amplitude in reduced dyadic form `(a+ib)/2^d`, with at least
one of `a,b` odd. Its norm gives `a^2+b^2 = 2^(2d-h)`. If exactly one is odd,
the exponent is zero. If both are odd, their squares sum to two modulo four,
so the exponent is one. Thus `d=ceil(h/2)<=ceil(n/2)`.

Every retained chart, chart inverse, native C gate and Gaussian-unit affine
quadratic monomial is a dyadic Gaussian Clifford. Products and tensor lifts
remain in that class. The validated wrapper schema admits no higher-degree
phase term. Correct association of a recipe with its chart transport remains
an inherited native-correctness premise.

### The actual retimed chronology

For register `r`, let `a[r,s]` be its logical scalar coefficient on public input
`s`, `Delta_W` its current chart and `Delta_Vs` input `s`'s initial chart. Its
physical value is

```
sum_s a[r,s] * Delta_W * Delta_Vs^-1 * x[s].
```

The independent sparse rational replay checks every common ADD frame and
nested transport. Every stored coefficient is in `(1/4)Z`. Crucially, every
pre-add coefficient product `c*a[source,s]` is also in `(1/4)Z`, before any
cancellation with the target. There are 30,007 such nonzero products and
101,334 stored-row term visits. The largest logical row or product L1 norm
is `127/2`. A separate dense integer interpreter reproduces all products,
eight zero erasures and the complete credited endpoint hash without importing
the rational interpreter or physical kernel.

During a native prefix, replace `Delta_W` by that prefix composed with the
entrance chart. Relative to each public input's initial inverse chart, the
result is still a dyadic Gaussian Clifford on `n=9*lambda` coordinates.
The denominator bound and the quarter-grid scalar coefficients therefore
put every component on the grid

```
2^(-f-ceil(9*lambda/2)-2) Z.
```

A partially written C stage stores rows from either the preceding or completed
stage, with the same bound. Four-term integer numerators need no division
until the pair is complete. Every halving and scalar division is exact on
this grid. Scalar products use the separately checked pre-add coefficients.
Induction then preserves all logical rows and exact private zeros. The
all-depth statement is this written argument, not extrapolation from fixtures.

### Sharpness at the changed source cut

Set `Y2=2^-f delta_0` and every other public input to zero. In the retimed
word, zero-based event **2040** transports D18 to the full frame. Its Y2
coefficient is `-1/4`, and Y2's initial chart is empty. The first physical
component at tensor depth `lambda` is

```
-2^-f * (1/4) * ((1-i)/32)^lambda.
```

It needs exactly `ceil(9*lambda/2)+2` extra fractional bits. At one layer it
is `2^-f*(-1+i)/128`. The actual seven-bit execution reaches integer pair
`(-1,1)` in units of `2^(-f-7)`; six-bit execution rejects an inexact halving.
This is an atomic-boundary witness, independent of the order of commuting
internal tensor factors. It does not exclude per-field grids, rescaling,
changed words or approximate endpoint contracts.

### Magnitude and scratch

If each initial real/imaginary component has absolute value less than `H`,
unitarity bounds each relative Clifford row's L1 norm by `2^(9*lambda/2)`.
The checked scalar norm gives component magnitude less than

```
H * 2^(ceil((9*lambda+1)/2)+6).
```

This covers stored fields, native prefixes and scalar products. Four-term
butterfly scratch needs at most two further magnitude bits. These are finite
format bounds, not physical bit-operation or storage-cost admission.

## Reproduce

Standard-library Python 3.12 or later, from the repository root:

```sh
python3.12 -I -O -B research/p104-retimed-internal-grid/verify.py
python3.12 -I -O -B research/p104-retimed-internal-grid/independent.py
python3.12 -B -m unittest discover -s research/p104-retimed-internal-grid -p 'test_*.py'
python3.12 scripts/research_package.py --package research/p104-retimed-internal-grid
```

Expected main marker is `PASS_P104_RETIMED_INTERNAL_GRID`. The main replay
executes the complete 5,268-event word twice, with exact divisions inside every
C butterfly. Y2-delta and all-public dense complex fixtures each match all
183,296 endpoint complex coordinates against a separate canonical-chart
calculation and erase all eight private fields. It also checks the phase
column of both new edges. This is not all-column native recertification.

Seven semantic faults reject: stale retimed ADD chart, an eighth-grid scalar
product hidden by a coarser final sum, nonbijective wrapper, wrong native rank,
wrong global phase, missing private update and six-bit execution. Tests exercise
literal C/inverse values, the independent integer oracle, Git-free read-only
optimized replay, source corruption, typed receipt corruption and overwrite
refusal. `--out NEW.json` writes exclusively; normal verification writes nothing.

## Limits and expansion decision

This closes one precision-transfer implication for the exact PR2725 word.
It does not compose PR2712 with PR2725 or extend a certificate merely because
profiles match. Native/chart correctness and tensor lifting are inherited;
physical fixtures cover one layer. No native compiler regeneration, selected
cold replay, hosted CI or formal-kernel/human review is claimed.

The conditional consumer-budget objections in
[PR2744](https://github.com/CrocSwap/integer-mult-bounds/pull/2744) and
[PR2741](https://github.com/CrocSwap/integer-mult-bounds/pull/2741) are not removed
by this exact-format result. No owner search or further construction expansion
is proposed. Recursive representation, scalar/address and movement costs,
actual owner windows, idle/residual children, other correction rows and supplier
admission remain unresolved.

The replay has no recursion or subprocess trees. Managed-runtime allocation is
a deliberate deviation from fixed post-initialization storage. Hash-bound
inputs limit the work to 358 public rows, 5,268 events, 1,375 recipe records,
9-coordinate frames, 512-entry vectors and 64 witness depths. At most two
compiled recipe pools coexist during controls, each with at most 1,917
512-entry wrapper plans. Python object overhead is not a physical-memory
certificate. The test runner caps child commands at 120 seconds; registered
commands have explicit limits. Runtime guards remain enabled with `-O`.

## Open next questions

Can a complete consumer outside the credited conditional budget obstructions
use an admitted recursive representation at these exact entrances and exits?
The first useful step is one actual child invocation with an explicit grid,
scratch, restoration and bit-operation/access/movement bill. Generic residue
cardinalities cannot be added across correlated child inputs. The missing
consumer and recursive implementation contract block supplier admission;
smaller fixed-grid guards alone do not justify another construction round.

## Credit

Vasek / flyingviper supplies PR2725 and its explicit precision-transfer caveat.
commdata2338 supplies PR2662's endpoint fusion. ywz65 supplies PR2586 and PR2497;
PR2551 distinguishes the physical boundary. Ross Richardson supplies the sharp
Clifford-grid method and public finding. Nick Petalas supplies PR2772/2754 and
complementary-frame work; Arham Tahir supplies PR2674/2665. The retained lineage
also credits Alejandro Zarzuelo Urdiales, Hiroki Kumazaki, Philippe Van Velzen,
Chafik Boukhalfa, Rohan Arun, Adam Gall, Josie Elliston, Ali Romman, icekylinx and
the upstream geometry/compiler/interpreter contributors. Original notices and
detailed source credit remain unchanged. New material is Apache-2.0.
