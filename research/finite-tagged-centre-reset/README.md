# Finite tagged centre reset and exact pure-reset cost

This package contains a local nonlinear backward reset on a declared
physical dyadic input grid, and an exact cost theorem for every policy
in a fixed family of pure resets. It gives no improvement to the complete
kappa calculation.

The local word returns `(X-Y,Y)`, restores all 480 arbitrary helper
contents in their inherited output frames, and clears one existing owned
private field `C0`. It adds 2,361 field passes and no native child. Its
sufficient fine-accuracy profile contains 132 retained children:
124 of rank one and eight of rank four, with rank mass 156. The eight
removed private centre jobs have rank mass 64. This local choice has an
adverse precision cost under the declared width rule.

The complete policy theorem covers all `2^36` effective reset policies
through 12,288 exact group cases. The minimum all-query profile is
121 rank-one and eight rank-four jobs, with mass 153. For each nonempty
query subset, its added rank moment exceeds the removed centre moment
by at least 17 for `0 <= sigma <= 1`. The constant 17 is sharp. This is
a conditional cost theorem for the stated independent relative-error
width model. It is not a universal precision lower bound.

Read [PROOF.md](PROOF.md) for the exact hypotheses and the proof map.
[SOURCES.json](SOURCES.json) gives the source hashes.
[NOTICE.md](NOTICE.md) gives the source credit and license.

## Reproduce

Use CPython 3.10 or later with its standard library. No network, Git
database, compiled package, or external campaign path is required.
Keep at least 3 GiB of disk space free. From this package directory, run:

```sh
python3 -I -O -B replay.py --out /tmp/finite-tagged-centre-reset-replay
```

The output directory must not exist. Choose a new path for a later run.
The replay runs the two unchanged independent checkers in sequence and
compares every field of each new receipt with the frozen review receipt.
It writes logs, two mathematical receipts, and `REPLAY.json` outside the
package. Expected final status:

```text
PASS_FINITE_TAGGED_CENTRE_RESET_PACKAGE
```

The first check covers all 704 input columns, all 480 helper contents,
132 direct native error impulses, the complete added pass count, 11,025
exact decoder cases, 96 margin cases, and 27 carrier cases. Its controls
reject a coarse-only decoder allowance and a relative-only parent return
allowance. The second check reconstructs all 860 eligible reset sites,
all 12,288 group policies, all 255 nonempty query subsets, and 528 direct
native error impulses. It checks the sharp surplus witnesses.

The original producer scripts are retained as source evidence. The
supported portable command is `replay.py`; it uses the independent
checkers and does not rerun the producer scripts.

## Review state and limits

Use the corrected [version 2 local proof](frozen/work/centre-encoding-campaign-20261014/lanes/schur-selection/finite-grid/GRID-RESET-PROOF-V2.md)
and its [independent review](frozen/work/centre-encoding-campaign-20261014/lanes/paired-package-review/tagged-grid-review/REVIEW.md).
Parent return-grid rounding has a separate absolute error budget. It
cannot be included in the relative child error at a fixed parent width.
The fine-centre margin is `G+6`. The older proof is retained as history.

The [complete family proof](frozen/work/centre-encoding-campaign-20261014/lanes/temporal-reuse/EXACT-TAGGED-RESETS.md)
was accepted by the later [full-family review](frozen/work/centre-encoding-campaign-20261014/lanes/paired-package-review/exact-reset-policy-review/REVIEW.md).
That review proves the sharp surplus 17. The proof's older sentence
that review was pending is historical. The frozen files are unchanged.
The reviews used separate AI agents; they are not human reviews.

Actual native frames, phase recipes, and their tensor extension remain
explicit inherited premises. The retained [physical phase correction](frozen/work/centre-encoding-campaign-20261014/lanes/paired-package-review/centre-reset-review/PHYSICAL-GRID-V2.md)
uses the actual quadratic conjugation. A listed frame basis is not a
plain product of transforms on its vectors. The portable replay checks
scalar accesses and frame identities; it does not repeat the complete
phase audit or the historical row and tape precision audit.

The local theorem starts after every role input is on its declared grid.
Conversion from finer caller records, the complete node endpoint, owner
admission, and all new finite bit and tape costs remain open. Exact local
helper restoration refers to those grid inputs. It does not prove exact
restoration of finer records before entry conversion.

The publication base is `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`.
Its [selected record](context/selected-result-20261022.json) uses the changed
conditional construction in [PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470).
The historical source checks here do not establish admission to that
construction. No frontier update or complete supplier is claimed.

## Open next questions

- Prove a complete node endpoint and its entry-conversion error before
  importing the local grid word into a caller. The first check must
  include every row used as borrowed space. That endpoint is not proved.
- Evaluate a different native error contract or an access change only
  with a new input and response proof. Such a change can leave the policy
  theorem's class; the current theorem gives no cost outside that class.
- Price all new scans, rounding, record conversion, and tape movement
  if a complete candidate first meets its precision moment. This package
  has no favourable candidate and no complete finite invoice.
