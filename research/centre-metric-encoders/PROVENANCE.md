# Source record

The source campaign is `centre-encoding-campaign-20261014`. Each file under
`frozen/` is an exact copy from that campaign. [SOURCE-MANIFEST.json](SOURCE-MANIFEST.json)
records its original campaign path, SHA256, size, and reason for inclusion.
Compressed inputs also have a decompressed SHA256. The package includes
the closure required by the seven selected exact checks. It does not
include every producer prototype or every predecessor replay.

The normal and optimized native reviews retain the exact source phases,
physical fields, endpoint adapters, and word bytes. The new replay uses
those bytes. It does not replace their pins with later upstream objects.
These local results are historical source-bound constructions, not the
current selected supplier.

The publication context was checked on 2026-10-22 against upstream main
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`. Its selected record names
[PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470), with
kappa 60403/20000000 = 0.00302015. The exact record is retained in
[SELECTED-CONTEXT.json](evidence/SELECTED-CONTEXT.json). That selection is
not an input to these checks. The package does not transplant its local
words into that construction or change its complete cost.

## Portable entry point

Six checks run their frozen source directly. The seventh uses
[portable/check_signed_clean.py](portable/check_signed_clean.py), a copy of
[the frozen signed-native checker](frozen/lanes/new-native-recipes-20261017/signed-clean-native-review-20261020/check.py).
Only its source-directory binding and absolute-source-path resolution
change. The resolver maps the single campaign path component to the local
frozen tree. It still checks every original payload digest. All arithmetic,
phase checks, endpoint checks, cost checks, and negative controls are
unchanged. The [exact diff](evidence/PORTABILITY.diff) records the change.

The new [replay receipt](evidence/REPLAY.json) records both current checker
hashes. The runner uses Python file-access audit events to reject a read
outside the package, output directory, or Python runtime. This check does
not change a matrix, instruction, import, or producer result. Each result
must match its frozen receipt byte for byte.

The root's earlier 32-coordinate proof and receipts remain as proof
ancestry for the finite-field theorem. The accepted actual construction
and native replay use C24. The rational C16 is the first actual packing,
not the later supported-packing extension. No source field is silently
substituted between these constructions.

## Attribution and scope

The root lane supplied the finite-field bound, array extension, general
signed-family word, and a separate exact engine. The new-core-transfer
lane supplied the actual C24 and signed-code constructions and native
words. The independent-review lane supplied the distinct C24 proof check
and the first rational packing. The bridge-access lane supplied the paid
rational word and grid analysis. The bridge-review lane supplied the
signed basis, matrix proof, and word/cost review. The native-review lane
supplied the independent native bindings, complete-block proof, rational
division-domain check, and all-power argument. The controller, oblique,
and earlier native packets supplied the actual readers and native inputs.
Substantial OpenAI Codex assistance was used throughout.

[NOTICE.md](NOTICE.md) records the license and retained external source.
Human contributor credit must be based on source notices, not inferred
from the account that submits the package. Publication, GitHub link
verification, and rendered PR checks are separate from this local replay.
