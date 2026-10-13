# Swapnil Jain's parallel research: retained reference and finite checks

Reviewed 2026-10-08. Author: **Swapnil Jain**. Repository:
[Swapnil-jain/integer-mult-kappa](https://github.com/Swapnil-jain/integer-mult-kappa/tree/f2176bc1124821bf17eb63725bd366d7bdc020a3),
pinned at `f2176bc1124821bf17eb63725bd366d7bdc020a3`.
All 87 tracked files are preserved unchanged in `upstream/`, with Apache-2.0
licensing, predecessor credits and Claude assistance disclosures intact.
[SOURCE.json](SOURCE.json) binds every imported file by SHA-256.

This incorporates a reproducible parallel research reference and additional
verification. It does **not** replace the selected construction or increase this
repository's current conditional witness, approximately **5.1016920170078e-5**.
Swapnil's round-six witness is **3666565558019/100000000000000000**, approximately
**3.666565558019e-5**. Both exceed 2^-15 and remain below 2^-14.

## Contribution and relationship to the existing result

Swapnil's influence on the released construction is already documented by its
authors. Zhihao Chen's [pinned PR29 note](../../references/copied-centers/pr29/two-stage-16-note.tex)
explicitly credits Swapnil's research as the route to the two-stage topology and
macro batching. Its [source receipt](../../references/copied-centers/pr29/SOURCE.json)
pins Swapnil's earlier commit `ae405eb474d1486b2d8aef90139869f927f4836a`.
The topology and paid correction themselves retain Aurel Prosz's credit; this
review does not reassign that priority.

The later parallel repository contributes its own retained-point-total bit
producer, two-stage complex implementation, common flag-basis construction,
segmented Gaussian inverse analysis, and exact arithmetic checks in Lean.
Those are substantive research artifacts even where another composition has a
larger final witness. Their dependency acknowledgements include work by Aurel,
eumemic, Zhihao, icekylinx, David Leen and Douglas Colkitt.

## What was checked

Run from the root of this repository:

```sh
python3 research/swapnil-parallel/verify.py --lean
```

The optional `--lean` uses `leanprover/lean4:v4.31.0`; without it the finite Python
checks need only the standard library. [verification.json](verification.json)
records the deterministic results. The wrapper runs colliding upstream module
names in separate processes and treats failed checks as errors.

* **Source identity:** all imported file hashes match the pinned commit.
* **Round-six bit network, h=23:** regenerate the retained-total producer;
  independently reconstruct every active support from its input leaves; check
  topological, disjoint additions, common-point support, all 5,313 exclusion
  outputs and all 23 retained point totals. Recompute the child histogram and
  match the embedded Lean input exactly. The side compiler uses 40,077 roles.
* **Round-six complex network, h=24:** rerun the author's producer and explicit
  label checker, require zero failures on its 140,064 checked edges, match
  explicit label dimensions to the histogram, and match that histogram to
  Lean's input exactly. The side producer has 49,208 roles. This replays the
  supplied geometric checker; it is not a second implementation of the complete
  dirty-workspace scalar circuit or every frame incidence.
* **Rounds five and six arithmetic:** independently enclose all four moments
  using this repository's rational logarithm/exponential checker. Recompute the
  ten stated assembly constraints, eight margins and crude guard bound using
  signed fractions. This also avoids relying on the Lean encoding's saturating
  natural subtraction or the Python generator's floating logarithm.
* **Lean:** regenerate both files from their pinned histogram JSON; require
  byte-for-byte equality, compile, and inspect all ten theorem dependencies.
  Each declaration reports no axioms. Round-five network counts are treated as
  supplied inputs here; only round six's counts are freshly rebuilt.

The author's `make verify` also passed, including 23 unit tests and its numerical
and identity checks. A separate run of `flag_existence.py 23 0` found no zero
diagonal/inner corners over all 1,771 triple labels, zero strictly-upper entries
for three sampled lines, and nonzero entrance determinants for three sampled
pairs. The latter is a finite-field polynomial screen, **not** an exhaustive
rational certificate of every pair or a formal proof of the generic-basis
argument. Numerical inverse experiments likewise do not prove uniform analytic
bounds.

## What remains conditional

The ten Lean declarations prove concrete arithmetic predicates: two rank sums,
two rational moment inequalities and an assembly predicate in each round.
They do not formalize logarithmic analytic bounds, construct a Turing machine,
or prove integer multiplication end to end. The author's generator states this
boundary explicitly. A certificate of the assembly arithmetic is different
from a proof of the algorithmic interfaces used to derive that arithmetic.

Swapnil's global assembly uses longer coefficient digits, a segmented/reused
Gaussian inverse, fine-bit exposure and a CRT layout argument. This is a
different stack from the semantic/bulk assembly of our selected witness. Its
fixed-tape realization, uniform error/precision bounds, restoration and
all-size costs have **not** received a complete independent audit in this pass.
The common flag-basis proof and complete complex scalar/frame realization also
remain written dependencies beyond the finite checks listed above.

## Useful next integration targets

The reproduced complex histogram supports the author's stated saving
`36926111/500000000000` (about 7.38522e-5), slightly larger than the selected
complex saving 7.17e-5. Our selected bit saving is only about 5.10195e-5, so this
would not improve today's headline by itself. Before using it in the selected
assembly, audit the complete scalar/frame realization and match the physical
basis, child-batching and guard contracts. The common flag-basis and segmented
inverse notes are separately retained candidates for a future structural audit.

The [sixth-update announcement](https://x.com/SJ_Swapnil_Jain/status/2108196538568851574)
is the strongest directly inspected announcement from this pinned research
sequence. It is appropriate to credit both the earlier influence on our
construction and the later parallel development.
