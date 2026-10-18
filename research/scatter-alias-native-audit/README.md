# Retained aliases at the native scatter boundary

PR3128's balanced retained-helper alias passes the actual native legality and
883-column five-stage checks **when compiled for ten COPY/ERASE pairs**.
The unchanged selected nine-copy builds reject it at their count checks.
The opt-in simple-support guard rejects it before checking or exporting,
even though this particular ten-copy word has the correct F2 endpoint.

This closes PR3128's unrun finite native step: four predecessor fixtures,
one unused-slot control and two copied-centre contracts. It does not admit a ten-total supplier. No saving or
new kappa is claimed; selected and frozen sources remain unchanged.

## Precise additional check

[Sricharan Vagvala's PR3128](../retained-alias-parity-audit/README.md) supplied
the alias-grouped scalar criterion and fixtures. The selected word has nine
distinct retained helpers. Slot 8 names helper 480; row 64 is `[2,4,6]`.
The balanced fixture appends helper 480 as slot 9 and appends `[8,8,9,9]` to
that row. Symbolic occurrence parity cancels each pair. Export instead emits
two separate ADDs of the same helper value, which also cancel over F2.

That scalar argument belongs to PR3128. This audit checks the next boundary
using the unchanged exporter, staging program, C++ legality checker and C++
formal-column checker. The selected build is
`HDIM=8, VPORTS=111, RHELP=439, NCOPY=9`. The same bytes are separately compiled
with `NCOPY=10`, explicitly changing the finite copied-centre contract.

| Fixture | Full symbolic | NCOPY=9 legality / columns | NCOPY=10 legality / columns | Guard |
|---|---|---|---|---|
| Selected baseline | pass | pass / pass | count reject / count reject | pass |
| Balanced alias | pass | count reject / count reject | pass / pass | reject |
| Unpaired even slot | pass | count reject / count reject | pass / endpoint reject | reject |
| Distinct helpers | pass | count reject / count reject | pass / endpoint reject | reject |
| Unused alias slot | pass | count reject / count reject | pass / pass | pass |

The unpaired control appends only `[8,8]`, keeping the tenth retained slot.
The distinct-helper control appends `[8,8,9,9]` but makes slot 9 name helper
479. Both preserve the symbolic endpoint. Their exports differ only at output
175; dirty input 480 is a witness. An independent interpreter checks all 661
input columns, reproducing PR3128's full difference supports and stream hashes.

Count rejection is `unclosed COPY` in legality and `center boundaries` in
columns. At the correct count, bad endpoints reject at
`local defining-decoder full formal column`. Rejections create no success receipt.

The unused-slot control only appends helper 480 to `ret`; all scatter rows
remain unchanged and simple. It passes both actual guard entry points and the
ten-copy native checks, while the nine-copy native builds reject it. Thus the
guard enforces row support, not retained-list injectivity or the selected copy
count. It pays one extra COPY/ERASE pair and rank 7, without an extra ADD.

## Complete literal local invoice

| Quantity | Selected | Balanced alias | Delta |
|---|---:|---:|---:|
| Records | 27,234 | 27,238 | +4 |
| MOVEs | 2,911 | 2,911 | 0 |
| ADDs | 24,305 | 24,307 | +2 |
| Scatter ADDs | 527 | 529 | +2 |
| COPY/ERASE pairs | 9 | 10 | +1 |
| COPY rank sum | 63 | 70 | +7 |
| Local paid rank mass | 5,129 | 5,136 | +7 |

Only the rank-seven histogram entry changes, from 19 to 20. The frame
dictionary is byte-identical. The baseline native receipts also match the
pinned PR2977 receipts after normalizing only the validated temporary stream
path and elapsed-time fields.

The five-stage receipt charges 121,535 ADDs instead of 121,525, 50 fresh copies
instead of 45, and 20 reverse-stage copies instead of 18. The six bridges still
cost 666 ADDs. These are complete event counts at this boundary, not an
integrated nine-stage or supplier bill.

A separate unbounded-integer implementation agrees with the native
cancellation-free prefix recurrence for every fixture: forward maximum 49,347,
reverse maximum 1,113,070, and payload bound
`64 * 49347^3 * 1113070^2 = 9528119495320518471870892800`.
Its bit length remains 93, strictly below `2^104`. The unchanged maximum does
not remove any added COPY or ADD charge.

## Guard and controls

The actual [PR2992 entry points](../simple-scatter-boundary/boundary.py) accept
the selected word and preserve all three exporter artifacts byte for byte.
They reject all duplicate-row fixtures before delegation or output creation.
Rejected export leaves all three preexisting artifacts unchanged. Receipt
fields use `null` for checks not applicable to a fixture.

Three additional mutations separate the native obligations:

| Mutation of balanced export | Legality | Columns |
|---|---|---|
| Underprice last COPY, rank 7 to 6 | rejects COPY rank | passes |
| Bind its ERASE to helper 479 instead of 480 | rejects lifecycle | rejects source binding |
| Omit its final scatter ADD | passes | rejects endpoint |

Scalar checking therefore cannot replace pricing/lifecycle checking, and
legality cannot replace endpoint checking. Simple support is a sufficient,
intentionally conservative guard even at this finite native boundary; its
rejection does not imply every repeated-row operator is incorrect.

## Reproduce

From the repository root, with Python 3.12 and a C++17 compiler:

```sh
python3 -I -O -Werror -B research/scatter-alias-native-audit/verify.py --native
```

Expected final line:

```text
PASS_SCATTER_ALIAS_NATIVE_AUDIT fixtures=5 contracts=2 native_columns=883 controls=3 no_new_kappa
```

This authenticates inputs, executes the full symbolic/export/guard audit,
compiles four binaries sequentially and checks [NATIVE.json](NATIVE.json).
It uses the credited [checked 128-bit cpp_int stand-in](../bit589-checked-cpp-int-seed92/README.md),
which refuses overflow, rather than system Boost. Python's independent prefix
cross-check uses unbounded integers. Exact backend, headers, subjects and
staging bytes are pinned.

The standard-library registered replay does **not** compile native code:

```sh
python3 -B scripts/research_package.py --package research/scatter-alias-native-audit
python3 -I -O -Werror -B research/scatter-alias-native-audit/verify.py
python3 -I -O -Werror -B research/scatter-alias-native-audit/test_verify.py
```

It checks [RESULT.json](RESULT.json) and six behavioral groups: alias
cancellation and charges, unpaired/changed-helper columns, source corruption,
lifetimes/alignment, prefix growth despite cancellation, and tampered saved
native invoices. Checking a saved receipt does not replace the explicit native
command. `--emit`, with or without `--native`, reconstructs a receipt on stdout;
normal replay leaves evidence unchanged.

All audit subjects execute from authenticated private snapshots. Original
scripts retain assertions even when this audit uses `-O`. Native compilations
are sequential, with 120-second deadlines; delegates have 60-second deadlines.
The legacy legality program aborts on some rejected inputs. Core files are
suppressed; exact diagnostics and absence of success receipts are required.
Platform-specific abort wrappers are excluded from deterministic evidence.

Local validation used CPython 3.12.3 and GCC 13.3.0 on Linux x86_64. Native
replay, registered replay, six groups and package metadata/source-pin checks
pass. Hosted CI, system-Boost replay and independent human review are not claimed.

## Scope and sources

Base main: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
The claim is in [Discussion #2976](https://github.com/CrocSwap/integer-mult-bounds/discussions/2976#discussioncomment-19001909).
[TASK.json](TASK.json) records the refined card, domain and remaining obligations;
[SOURCES.json](SOURCES.json) pins inputs by Git blob and SHA-256.

Exact predecessors: PR3128 `2bf13e5b55f8318ae74a8f17db36a19447ba8c7f`;
PR2977 `cd23d242dfe0e7a71cafba0ad5590dc4f2fbf4f2`;
PR2992 `b31bf0360ad702b1be71dea7a33edc11711084af`;
PR3004 `ce08d19f6e43bbc6f552858d93154efe3aa98916`;
selected PR589 `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
The original #2977 paired-mismatch replay and selected-source binding
orientation also passed during preparation.

Native staging uses an empty kernel selection and no source owners/donors.
The receipt's reference to a separate bank audit is inherited text, not a
newly executed proof. Physical projectors, bank completion, hosting, full
nine-stage allocation, supplier moments, all-size compilation, precision/tape
and analytic transfer remain open here. Formal columns are over F2; the prefix
bound is not a new general-ring endpoint theorem. No complete cold replay or
selected-frontier change follows.

## Open next questions

Should a separately versioned supplier adopt `simple-scatter-v1` with an
explicit retained-slot/count contract? Review these fixtures and both native
contracts, then bind successor entry points and run the complete
symbolic/export/native and bank/hosting replay. Source binding and full
supplier admission remain blockers. Changing `NCOPY` alone is not adoption.
No new construction search is justified by this audit.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Sricharan Vagvala (@theon199), PR3128, retains credit for the alias criterion
and full-size fixtures. Nick Petalas, PR2977, discovered the scatter/export
mismatch and supplied native controls and the checked-backend replay pattern.
Arham Tahir, PR2992, supplied the operational simple-support boundary. Hiroki
Kumazaki, PR3004, supplied the independent-slot parity characterization; James
Reed, PR3099, supplied a separate scalar corroboration. The concurrent odd-multiplicity
native audit in Discussion #2976 keeps nine distinct retained helpers fixed
and is complementary.

Credit eumemic and DreamingOfClouds for the word/checker lineage, Dylan Crow
for the exporter/native/staging programs, Douglas Colkitt for selected bindings
and review, and Sagar Thakrar for the checked cpp_int stand-in. Original notices and
source bytes remain unchanged. New work is Apache-2.0. No independent human or
proof-assistant review is claimed.
