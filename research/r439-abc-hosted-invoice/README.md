# Complete nine-stage hosted invoice for the PR1122 helper-mixing word

**Finite hosted construction replay; no new circuit, supplier selection or κ.**
The fixed 10,652-ADD word of [PR1122](https://github.com/CrocSwap/integer-mult-bounds/pull/1122)
passes the unchanged nine-stage emitter and owner auditor with PR589's frozen
hosting assignment. All **126,432 helper occurrences** are hosted without banks;
the complete emitted program has **3,911,328 instructions**. Its invoice retains
the selected bit profile and bit saving. The unrounded prefix and two-level
bounds use 176 and 390 bits, still charged at 192 and 512 bits.

PR1122 supplied the circuit and native evidence. [PR1194](https://github.com/CrocSwap/integer-mult-bounds/pull/1194)
supplied the semantic-D substitution argument; [PR1311](https://github.com/CrocSwap/integer-mult-bounds/pull/1311)
applied it to this changed-A word. Both the composition and bridge packages
explicitly left the **changed-word hosted emission/audit and invoice** open.
This package completes that finite handoff, binding those stages to one word.
It does not supply a new proof of the inherited physical or all-size premises.

## Exact object and complete bill

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The candidate is the unmodified
`research/r439-abc-semantic-bridge/inputs/candidate.json.gz`, inherited from
PR1122 head `a2551e70fce0cc34348f50f1a94e7cc4c80bbcbf`:

- File SHA256: `2b09a7a3851cdf2a7f19350d1555cf75788d001c9507a37e459cd931881ee066`.
- Canonical decoded SHA256: `7bbaed96041297cd38e89ff48eb055750cfab36609b9fdbeafcec1b2758c1254`.
- Emitted instruction SHA256: `8f2239a09b87367ba754a6c0ebd8989e81b295df3628ebf4991d1cab15fabfcf`.

| Quantity | PR589 selected bit word | Fixed PR1122 word |
| --- | ---: | ---: |
| Local ADDs, including preparation/restoration | 24,305 | 10,652 |
| Local MOVE/ADD/COPY/ERASE records | 27,234 | 13,581 |
| Local COPY / ERASE | 9 / 9 | 9 / 9 |
| Local rank mass | 5,129 | 5,129 |
| Nine-stage local invocations | 288 | 288 |
| Hosted helper occurrences / banks | 126,432 / 0 | 126,432 / 0 |
| Paid recursive children | 904,896 | 904,896 |
| Live / physical families | 28,416 / 28,425 | 28,416 / 28,425 |
| Prefix bits / charge | 177 / 192 | 176 / 192 |
| Two-level coefficient bits / charge | 393 / 512 | 390 / 512 |
| Row coefficient | 18,355 | 18,355 |

The baseline column is pinned PR589 evidence, not a new baseline hosted replay.
All gate savings are PR1122's and its predecessors'. The freshly recounted
hosted profile is
`{1:381024, 2:400416, 3:22752, 4:26880, 5:29376, 6:17376, 7:26784, 42:288}`.
Rank mass is 1,808,352 and deficit is 10,272. The bit saving remains
`1733427039589844234749 / 10^24`; the next grid point is rejected by exact
moment enclosures. The selected complex supplier still binds.

[RESULT.json](RESULT.json) retains every integer term of the invoice:
3,131,712 scalar additions (288 complete local words plus 63,936 bridges),
2,592 copied-centre episodes, selector, address, compiler, store and precision
terms. Each episode contains both COPY and ERASE; the inherited `J` term
also charges their lifecycle work. No virtual replacement D is executed or
billed. The row, child-size and 192/512-bit guards pass at their full charges.

## Reproduce

Python 3.12, C++17, Boost headers and the exact NumPy/SymPy/SciPy versions in
[VERIFY.json](VERIFY.json) are required. Set `BOOST_INCLUDE` to the directory
containing `boost/` if headers are not in `/usr/include`; `CXX` defaults to `c++`.
From the repository root:

```sh
python3.12 scripts/research_package.py --package research/r439-abc-hosted-invoice
```

Expected final lines:

```text
PASS_R439_ABC_HOSTED_INVOICE ADDs=10652 helpers=126432 banks=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/r439-abc-hosted-invoice outcome=completed
```

The registered command has a 600-second limit. To retain all emitted files,
native binaries, commands and logs, use a fresh output directory outside the
checkout:

```sh
python3.12 -I -B research/r439-abc-hosted-invoice/verify.py --output /tmp/r439-abc-hosted-run
```

The default replay is read-only with respect to repository files. Existing
output directories are refused. `--write` explicitly regenerates RESULT.json.
All checks in the wrapper remain enabled under `-O`; inherited scripts run
in separate interpreters with assertions enabled.

## What is checked

1. The unchanged PR1311 verifier checks the full arbitrary-dirty D boundary,
   raw J/V/K blocks, original-D chronological splice, geometry, endpoints and
   its nine semantic controls. Literal H2 and K syntax still reject the actual
   helper-mixing word; their predicates are not weakened.
2. The unchanged exporter, native legality checker and native 5/9-stage
   programs replay the actual candidate, with 883 and 1,327 formal columns.
   Local positive bounds are F=15,223 and B=3,910,388, using 92 bits below the
   104-bit cap. Six and eighteen omitted-bridge controls reject.
3. The inherited geometry and exact string parameterizers run afresh.
   PR589's fixed selection is read directly; no optimizer is invoked.
   The parent checks 4,839 independent unbanked scalar columns and rejects
   seventeen template mutations. The hosted auditor independently reconstructs
   ownership, windows, full instruction digest and paid profile, rejecting
   sixteen ownership/template mutations.
4. `invoice.py` expands the inherited bit invoice into inspectable integer
   terms. It also executes every statement of the unchanged adapted PR510
   bit-invoice prelude, through its `res` assignment, and compares the exact
   coefficient, two-level bound, scalar/selector counts and moment brackets.
   The subsequent historical complex/outer assembly loop is outside this task.
   This is a port-consistency check, not an independent mathematical method.
5. Seven additional controls reject mixed word/record receipts, an understated
   profile, prefix or COPY charge, a missing bridge control, and a stale
   hosted-parent binding. These mutate the actual output files at the collector
   boundary and restore them after each check.

The inherited geometry receipt contains elapsed time. Only that nonmathematical
field is normalized to zero **before** downstream hashing, so the final
certificate is reproducible. Every downstream producer and auditor consumes
and binds those same bytes. No geometry assertion or mathematical field changes.

[SOURCES.json](SOURCES.json) pins the complete 53-file input/context closure
to the base, Git blobs and SHA256. Runtime Python read inventories and native
compiler dependency files reject undeclared repository dependencies. Compiler,
Boost and third-party Python libraries remain trusted environment dependencies;
they are not vendored or claimed as independently verified. Catalogue and
selected-record pins are historical provenance, so later selections do not
silently retarget this experiment.

## Scope and inherited obligations

This is a finite, source-bound emitted-template and invoice result. It is not
an enumeration of the astronomical cover, a proof-assistant theorem, a new
all-size compiler, or unconditional admission of the supplier. It retains the
common-frame/label interpretation, mutable-source realization, chronological
substitution, whole-call correlated-helper hosting, precision/tape, exact
recovery and analytic-transfer premises of the cited chain. Maintainer
acceptance of the replacement semantic interface remains separate. No current
outer assembly or eleven-stage hosting replay is claimed. The selected record,
upstream files and all predecessor packages are unchanged.

## Open next questions

Should this exact word be admitted as a maintained supplier under semantic D?
The next step is a review of PR1194/PR1311 together with this bound hosted
receipt, followed by the repository's supplier-admission process if accepted.
The blockers are acceptance of the replacement interface and inherited
physical/all-size premises, not a missing finite nine-stage invoice. The paid
profile is unchanged, so this package gives no exponent-based reason to change
the selected frontier. [TASK.json](TASK.json) records the same handoff.

## Coordination and credit

Assignment seed **1**, bit supplier; card `bit-helper-contract`, refined to the
existing word's complete hosted bill. [Discussion1796](https://github.com/CrocSwap/integer-mult-bounds/discussions/1796)
records the claim. Three candidate scopes and the overlap check are in TASK.json.
Source-supported batch deletion (active Discussion1785), the already covered
3x4/4x4 feedback censuses (PR1557/1706), and PR1782's different copy-sharing
word were not repeated.

Prepared for **Matthieu Pascal (@mtpsl)** with substantial **OpenAI Codex
assistance** in implementation, checking and writing. Apache-2.0; no independent
human review claimed. Credit Gareth Davidson/PR1122 for the composed word and
native work; Arham Tahir/PR1311 and woklerx/PR1194 for the semantic bridge;
Sagar Thakrar/PR1062, Sricharan Vagvala/PR967, Aaron Wang/PR1015 and Ross
Richardson/PR923 for its circuit lineage; DreamingOfClouds/PR589/510 and
eumemic/PR555/543 for the supplier and parameterization; DaysSky, chafreaky,
Zhihao Chen, Dylan Crow and the retained exporter/native/hosting/moment
contributors. Their OpenAI/Anthropic assistance disclosures and source notices
are retained in the unchanged dependencies.
