# Independent fixed-inventory optimum audit

Status: **PASS within the stated finite packing model; no exponent improvement found.**
Audited PR2863 head `34328b1d5e5bebac62d5cabec993dfbfd7b2123f`, package
`research/shared-kernel-packing/`. This is an intentionally independent audit
of the primal/dual implication, not another packing search or a full native release.
Prepared with OpenAI Codex assistance; all construction credit remains with
Dugongue and the contributors credited by PR2863, including PR2857, PR2856,
PR2848/2855 and the retained lineage. Apache-2.0.

## Reproduce

Python standard library only; no imports from the audited package:

```sh
python3 -B check_optimum.py \
  /workspace/scratch/bc9e58970b2a/continuation-20261016/pr2863/research/shared-kernel-packing \
  evidence
```

The final invocation exited 0 in approximately 0.37 seconds. `RUN.json` records
the interpreter, command, hashes and exit code. `evidence/RESULT.json` binds all
read scientific inputs by SHA256. `evidence/PATTERNS.json` contains every checked
constraint and its exact rational interval. The only displayed floating decimals
below are explanatory; acceptance uses exact `Fraction` arithmetic.

## Independent method and result

The checker reconstructs the nine symbolic dual prices by rational Gaussian
elimination of the nine tight support equations. It does not import or copy
the predecessor's explicit dual formulas. A recursive bounded-composition
enumeration independently produces all **1,163** feasible patterns, with
**11** symbolically exact equalities. Every other slack is strictly positive
uniformly on the root interval. The smallest positive slack exceeds
`0.00403024772582256767`; it occurs for capacity48 and widths `(4,8,9,9,9,9)`.

Transcendental bounds use a rational log series with a geometric tail, followed
by alternating Taylor polynomials for `exp(-t)` of degrees40 and41. Every
polynomial operation is rounded outward to decimal rational denominator
`10^80`. This avoids the predecessor's dyadic positive-exp/reciprocal path.
The log tail is independently bounded by replacing every omitted denominator
by the first omitted denominator. Alternating-series remainders bound the
negative exponential because `0 <= t < 1` throughout.

The exact primal reproduces every capacity count and inventory count. Its
objective equals the reconstructed dual symbolically. The literal candidate
profile is exactly185 times the complete per-replica optimum, including native
paid costs. The actual claim's `live=165760`, `calls=1665`, `roles=679320`,
`replicas=185` are checked against normalization896 and nine calls per replica.
The independently certified moment root lies strictly inside

`[0.00172010080541688592794400, 0.00172010080541688592794401]`.

The unnormalized moment signs at these endpoints are approximately
`-1.310784674194671e-21` and `+5.417557471291652e-22`. The check binds the
released outer rational to the conservative lower endpoint minus`10^-46`
minus`10^-70`, and checks the exact claimed difference from PR2857. This
arithmetic binding does not itself reprove the outer transfer theorem.

Four actual negative controls reject:

- removing one supported bin (capacity conservation),
- replacing one width9 by width8 without changing the inventory invoice,
- increasing the width9 dual price by`10^-6` (violates the tight `(7,9)` bin),
- charging one additional rank-one child (destroys the tiny endpoint slack).

## What is closed, and what is still open

The optimum closes **all whole-role packing changes** that retain capacities
`{8:672,16:448,32:448,48:448}`, nine copies of inventory
`{4:26,5:2,7:62,8:84,9:234}`, native paid costs, and normalization`896*73^p`
per replica. The relaxation has already discarded chronology constraints.
Consequently better retiming, neutral exchanges, relay paths, source windows,
or arbitrary replica counts cannot improve the optimum while these quantities
stay fixed. Every actual packing maps to a feasible fractional point; actual
T185 attains the lower bound. This argument does not require integral
attainment for every other replica count.

This does **not** bound changed native words, changed helper inventories,
new widths, splitting/reusing roles, changed capacities, different source
geometry or normalization, or changed outer transfer contracts. Such changes
must carry their own dirty-state, frame, restoration, transport and precision
costs. Retained all-size/compiler, source-access, mutable-source, hosting,
precision/tape, recovery, ordinary-recursion, BIT and analytic assumptions
remain outside this finite LP check.

The main complete-cost diagnostic is fixed rank mass65088 against budget65408,
a deficit320 per replica. At the root, rank-one children contribute about33.55%
of paid moment, rank-two17.78%, and idle rank48 children26.56%. This indicates
where genuine circuit or inventory changes would matter; it is not evidence
that any improvement is feasible.

## A reusable rejection rule for changed words

For changes retaining the existing width alphabet and capacities, the old
dual remains feasible. If a new local word changes the native paid moment by
`Delta L` and helper counts by`Delta I_w`, then the complete per-call change
is bounded **below** by

`Delta L + sum_w mu_w Delta I_w`.

If that lower bound is nonnegative at the target exponent, even an ideal
new packing cannot improve the target. A negative bound only clears this
necessary screen; it does not construct or certify a better packing.
The exact marginal intervals are retained in `evidence/RESULT.json`.

Examples at the current root:

- width9→8 costs at least`0.9878107358275071` in idle moment per changed role;
  a native saving must exceed that amount.
- width8→9 buys at most the same amount. Paying one whole rank-one child to
  obtain it fails even the optimistic test by about`0.0121892641724929`.
- a hypothetical additional quartet with native change`3H1-2H2` and one
  width9→8 change has optimistic complete change about`-0.007422974026313926`.
  It survives screening, but requires a genuinely new exact word and a valid
  packing; the known four quartets are already included.
- splitting one width9 role into width4+width5 has a dual idle lower-bound
  change about`-0.0349342218075312` before any extra native/caller costs.
  This is a changed contract, not a legal move in the frozen LP.

## Reproduction defect and boundary

The parent run found the published portable manifest expects164files while
the Git tree contains162: package-root`.gitattributes` and
`vendor/pr2857/.gitattributes` are absent. Both expected hashes equal
`705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da`, the hash
of bytes`* -text\n`. The parent is retaining the immutable original and making
an explicitly labelled repaired copy using the exact recovered bytes, without
changing the manifest. This standalone mathematical audit neither needs nor
silently repairs those files. Full native/outer replay is owned by the parent;
no pass of that larger release is asserted here.

## Open next question and stopping rule

The useful next experiment changes a native operation/frame contract or
helper inventory and first applies the complete-cost dual screen above.
The structural-search agent owns that work. Stop further fixed-inventory
packing work unless an explicit hypothesis above changes or a concrete flaw
is found in the map from actual assignments to the LP. No such flaw was found.
An independent all-size interface lemma could also be useful but would not,
by itself, raise the exponent saving.
