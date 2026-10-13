# Power-of-two weights cannot improve CK target forests

**Scoped negative result; no new kappa.** On the historical PR626 CK
compensation matrix, the PR816 signed-unit forest remains optimal when every
parent weight may be **any signed power of two**, including different
exponents on overlapping branches. The exact floor stays **16,364 primitives
per real component**, or 32,728 counting both coordinates.

Every nonunit edge costs at least **10 primitives per component** more than
making its child a root. Removing such an edge leaves all other child-row
costs unchanged. Consequently a forest with `m` nonunit edges costs at least
`16,364 + 10 m` per component. This is a bound for the explicitly defined
one-parent forest class, not all target bases or complex circuits.

This closes a restriction left open by **@dd-hemant's PR816**, which proves
the unit-weight forest optimum. **ToikY's PR909** supplies the credited
power-of-two tail method for disjoint pairs on a different X4 matrix. This
package adds the CK census and the edge-deletion argument for overlapping
forests. The retained 66,520-real-primitive saving per complete orientation
belongs to PR816; no additional construction or saving is claimed here.

The final queue refresh found concurrent **woklerx PR961**, head
`4257ddf4b755cd0ac3bd3b0f6281cc5b2b1f72ad`, which closes the broader class of
all nonzero dyadic parent coefficients on the **X4** matrix. Its exchange
argument is related; its matrix and coefficient domain differ. This package
adds independently checked CK evidence and the uniform penalty for nonunit
powers, and leaves CK weights with other dyadic numerators open. No PR961
implementation or numerical result is imported, and no priority is claimed
for a general forest-exchange argument.

## Reproduce

Python 3.12+ and its standard library, from the repository root:

```sh
python3 -I -B research/ck-power-forest-bound/verify.py
```

This command checks source bindings, regenerates the complete finite core,
checks the retained tree against every signed edge, replays its arbitrary-input
panel, runs controls, compares the entire committed receipt and invokes the
separate dense integer/literal-Horner/Prim checker.

Expected final line:

```text
PASS_CK_POWER_FOREST_BOUND: 174048 finite cases; all integer exponents; forest floor 16364; original witness retained; no new kappa
```

The all-integer statement combines the finite core with the written proof in
[PROOF.md](PROOF.md); it is not a claim to execute infinitely many cases.
The independent checker can also run by itself:

```sh
python3 -I -O -B research/ck-power-forest-bound/independent.py
python3 -I -O -B research/ck-power-forest-bound/test_package.py
```

Both verifier entrypoints accept `--source-root` for an offline minimal source
tree. Development-only `--write NEW_PATH` generates a fresh receipt rather
than comparing the existing one, and refuses an existing destination. The
primary `--write` does not run the independent checker; default verification
does. Compressed source artifacts are admitted by their decompressed payloads.
Historical Git blob IDs are retained as provenance, not a regenerated gzip
equality test.

## Exact evidence

The complete finite core covers all 112 × 111 ordered target pairs, both
signs and exponents -3 through 3: **174,048 cases**. All nonunit cases strictly
lose to a root; unit cases are retained as positive controls.

| Exponent | Minimum extra primitives per component | Profitable cases |
|---|---:|---:|
| -3 | 467 | 0 |
| -2 | 275 | 0 |
| -1 | 71 | 0 |
| 0 | -565 | 3,175 |
| 1 | 10 | 0 |
| 2 | 145 | 0 |
| 3 | 278 | 0 |

For every exponent outside this core, the quarter-grid alphabet gives an
affine coefficient cost with nonnegative slope; the two basis operations add
a strictly positive slope. The anchors at ±3 close both infinite tails.
The verifier checks the finite arithmetic premises in 162 coefficient/direction
families, including exponents 36, 64 and 127. These finite tests corroborate
the elementary tail proof.

The unchanged PR816 witness has six roots, maximum depth nine and 106
preparation + 3,130 residual + 106 restoration macros. All **12,544** unit
multigraph cycle inequalities hold. A separately coded dense Prim algorithm
finds the same 16,364 floor. Two implementations replay the original and
retained panels on **all 716 arbitrary input columns in each orientation**.

The independent checker prices the core by literal coefficient programs,
not the primary cost formula. It executes **1,058 coefficient cases / 72,632
primitive instructions** on independent target/source/private-work symbols,
and compares every price with the exact pinned native emitter function.
Complete census digests agree. Nine primary controls, two coefficient controls
and seven package tests cover pricing, arbitrary dirt, malformed trees,
source corruption, equivalent recompression, receipt types and output
preservation. The tests also check all **169 weighted forests on three
targets**, with weights ±2 and ±1/2 in both orientations, and reject all
11 cyclic parent topologies. [VALIDATION.md](VALIDATION.md) records execution.

## Scope and source pins

Base: `007664306fff84fbb1c9a1b4053b69f439764034`. OS seed **36** selected the
complex track and, modulo three, CK from the CK/JP8/X4 candidate objects.
Coverage is exhaustive within the stated finite core and independent of a
seeded search outcome. The initial bounded price screen found no construction;
this pass then completed the all-exponent class closure. No restart or timeout
cutoff is hidden.

The object is **historical PR626 CK**, head
`660de893d27bb7abd1d5b01b1640207528a5c851`, with 112 targets, 492 public helpers,
254 helpers active in this panel, and 8,704 original compensation additions.
Exact source, SPEC, program, recipe and proof pins are in [SOURCES.json](SOURCES.json).
The current accepted PR890 conditional κ remains **0.001661957774647029**;
this package changes no selected source or record and claims no transport to
the U8/T21 supplier.

The class fixes the frame-zero panel, its original row matrix, acyclic
one-parent structure and separately cleared binary-Horner lowering. General
non-power-of-two dyadic weights, multiple-parent transformations, helper-basis
changes, coefficient sharing, cheaper primitive lowering, and folding the
basis operations into surrounding code are outside this bound. A future
improvement must change at least one such restriction, rather than extend
the exponent search.

No changed whole supplier, native frame/wrapper replay, global hosting invoice,
outer assembly, all-length compiler or physical precision/tape proof is
provided. Those are not consequences of a scalar cost lower bound. The
inherited multiplication assumptions remain. [NOTICE.md](NOTICE.md) credits
the construction and proof lineage and discloses AI assistance.
