# General completion annex

This annex gives the accepted stronger form of the selected-query
completion. A unit selected minor is sufficient. The selected part of K
need not equal that inverse minor. If the query map is onto, the unit
minor is also necessary for a unit completion that retains all other
rows and reads the full query from the selected outputs.

When `RK=gI` and a unit d-field minor is available, the minimum number of
changed complete output fields in any linear unit repair of `I-KR` is
zero if `1-g` is a unit, and d otherwise. For the actual Gaussian-dyadic
matrix, reduction modulo 13 makes this minimum eight. This counts output
fields. It gives no lower bound on native children and no kappa improvement.

Read the [proof map](PROOF.md), the unchanged
[general proof](frozen/work/centre-encoding-campaign-20261014/lanes/schur-selection/unit-query-review-20261015/GENERAL-COMPLETION.md),
and its unchanged
[independent review](frozen/work/centre-encoding-campaign-20261014/lanes/paired-package-review/upstream-followthrough-20261015/general-completion-review/REVIEW.md).
The [source pins](SOURCE-PINS.json) bind all six copied source files.
The review corrects one notation point: the complement of c changed
fields is U_c and has n-c fields. The older symbol U has n-d fields.

## Replay

Use Python 3.10 or later and the standard library. Keep at least 3 GiB
free. From this annex directory, use a new output directory outside the
package:

```sh
python3 -I -O -B replay.py --out /tmp/borrowed-centre-general-completion
```

The final line must be:

```text
PASS_BORROWED_CENTRE_GENERAL_COMPLETION_ANNEX
```

The replay checks every annex file hash. It runs the unchanged independent
checker with the copied source layout and compares the complete new
CHECK.json byte for byte with the frozen receipt. The checker imports no
producer code. It checks both inverse orders in an ordered polynomial
ring, all 500 scalar cases over F5, including 400 incompatible selected-K
cases, two converse controls, the actual Gram identities, and both
Gaussian residue maps. These checks support the general proof.

The six copied files form the complete runtime input closure. The annex
can run from a copy outside the workspace without Git or network access.
It does not run a native kernel, physical word, controller, precision
check, or supplier invoice. Native access and admission remain separate
obligations. The original 104-file package and its accepted
PACKAGE-HASHES.json remain unchanged; GENERAL-COMPLETION-DELTA.json at the
package root binds this addition separately.

Some frozen text says that publication is on hold. That statement is
historical. The retained acceptance has a notation qualification and no
unresolved material finding. The [notice](NOTICE.md) identifies the
source lanes and AI assistance.
