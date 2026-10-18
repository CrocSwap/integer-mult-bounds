# Independent source-to-ledger audit of the T74 four-role change

This package independently derives the **local paid-frame difference** between
the exact PR2312 words adopted by PR2322 and PR2322's changed words, for both
`base` and `extra` providers. It confirms
`Delta H = {1:-8, 2:+8, 3:+4, 4:-4, 5:-4}`, four width-4 helper retirements,
and a local rank-mass decrease of 16. It also constructs an actual-word control
whose total mass and helper widths are unchanged while its rank distribution
differs. The checker rejects that control's stale profile.

This is a finite, source-bound independent pricing witness. It does not certify
scalar correctness, native phases, global hosting, a moment root, or a new
multiplication exponent. The selected record is unchanged.

## Sources and added coverage

- [PR2312](https://github.com/CrocSwap/integer-mult-bounds/pull/2312),
  adopted head `fb76f799ccf078f51780076ebed3fd26b1db11c0`: Jeremy Kothe's
  T74 borrow43 width exchange. Its manifest SHA256 is
  `c545968fb8cf6e550b82ba631e92fd756484db75e621aee211347749cff55313`.
  The subsequently observed live PR2312 head differs; this audit intentionally
  checks the historical source actually adopted by PR2322.
- [PR2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322),
  head `002304ef01c4416a127916169ae6d94c1bee052b`: Vlado-V's coherent four-role
  change and owner hillclimb.
- [Canonical coordination thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/2325#discussioncomment-18942169):
  this audit complements the author's subsequent owner reassignment work.

The primary generator already computes paid profiles. PR2322 also supplies
substantial native checks: reported full public-column checks, physical map
checks and failure controls. This package does **not** claim those checks were
absent, nor that enumerating 512 map images is novel. Its added result is the
compact direct **source-to-candidate role/section delta**, reconstructed from
both raw operation streams with a different representation, plus the
equal-mass actual-word failure control.

Eight unchanged source files are copied here because standalone replay consumes
their bytes. `SOURCES.json` records exact Git blobs, commits, upstream paths
and SHA256s. Replay verifies every file and joins both words to the original
manifests before parsing the compressed payloads. The copied claim binds the
adopted source head and four source-compact indices. No producer, emitter,
native checker, primary rank routine or moment engine is imported or executed.

## Independent method and result

`ledger.py` represents each subspace as the explicit set of its at most 512
vectors in GF(2)^9. Dimension is the base-2 logarithm of the set cardinality.
It starts from actual port/helper entrance spaces, checks every paid
containment step in A, B and restoration, reconstructs each center's separate
nested private-reader bill, and climbs the live roles to their actual endpoints.
Each zero-rank handoff is checked by its entire ambient image table and by the
image of the current subspace. Removed-role references are rejected.

The geometry is fixed at 112 source roles, 112 target roles and 480 raw helpers.
The zero-frame precondition and compensation sections are schema-checked and
unchanged across the pair; their scalar algebra is not evaluated. Cleanup is
outside this interface.

Both provider comparisons give:

| Quantity | Adopted source | Candidate | Difference |
|---|---:|---:|---:|
| H1 | 2343 | 2335 | -8 |
| H2 | 504 | 512 | +8 |
| H3 | 422 | 426 | +4 |
| H4 | 124 | 120 | -4 |
| H5 | 42 | 38 | -4 |
| H8 | 8 | 8 | 0 |
| Paid rank mass | 5387 | 5371 | -16 |
| Live helpers | 438 | 434 | -4 |
| Width-4 helpers | 37 | 33 | -4 |

Here Hr counts paid children of rank r. All other helper widths stay unchanged:
5:9, 7:38, 8:114, 9:240. The raw retired roles are
`619,621,622,623`, source-compact helper indices `384,386,387,388`.

The twelve changed roles split into three classes:

| Roles | Contribution per role |
|---|---|
| LOW: 616,617,618,620 | -H1 + H2 + H3 - H4 |
| retired HIGH: 619,621,622,623 | -4 H1 |
| lenders: 1,4,6,12 | +3 H1 + H2 - H5 |

For each LOW role, the relevant ascent
`1 -> 5 -> 6 -> 7 -> 8 -> 9` becomes
`1 -> 4 -> 6 -> 7 -> 8 -> 9`. Each HIGH role loses four rank-1
visits. Each lender replaces a terminal `4 -> 9` climb with a zero-rank
handoff followed by `4 -> 6 -> 7 -> 8 -> 9`.
Adding the four copies of these three expressions proves the displayed delta.
The event reconstruction separately places
`{-8H1,+8H2,+4H3,-4H4}` in B and `-4H5` in terminal climbs.
A, the private cut and restoration have zero difference.
The rank-mass identity is
`-8 + 2*8 + 3*4 - 4*4 - 5*4 = -16`,
matching the four retired width-4 helpers. This does not itself prove any
global idle or owner bill.

`RESULT.json` contains all twelve per-role profiles and section differences,
source/candidate inventories, and hashes of the complete event ledgers.
The optional full-ledger export includes every charged event, not merely sums.

## Why mass-only checking is insufficient

Keep the candidate's four new rank-4 handoffs and replace **only** the twelve
preparation charts at B indices 1019 through 1030:

- C4 = span(260,132,75,51);
- C5 = span(260,132,75,42,25), with 51 = 42 xor 25.

C4 is strictly contained in C5. The independent walk still satisfies its
containment, mapping and width checks, but the profile changes by
`{1:+12,2:-8,3:-4,4:+4}`. Its mass change is zero and helper widths are
identical. The resulting profile is
`{1:2347,2:504,3:422,4:124,5:38,8:8}`, with mass 5371.
Leaving the original report in this mutated word is rejected specifically for
its wrong local profile; supplying the independently expected changed report
passes the frame ledger.

This is a **frame-ledger-admissible control**, not a certification that the
mutated scalar/native construction is correct. It demonstrates why retaining
only a total-rank invariant would miss a pricing error relevant to a moment.

## Reproduce and evidence

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/t74-four-role-ledger-audit/verify.py
python3.12 -O -B research/t74-four-role-ledger-audit/verify.py
python3.12 scripts/research_package.py --package research/t74-four-role-ledger-audit --check-only
python3.12 scripts/research_package.py --package research/t74-four-role-ledger-audit
```

Default replay compares reconstructed evidence to committed `RESULT.json`.
Use `--write-result` only for intentional regeneration, or
`--full-ledger-output /path/to/ledgers.json` to export both full comparisons.
Source snapshots are never rewritten.

The registered replay runs normal and optimized Python. Controls include all
eight source-byte corruptions, a false equal-mass report, wrong helper width,
removed-role references, duplicate inventories, singular and wrong-subspace
handoffs, incorrect chronology, invalid private-copy source, unpriced nonzero
frames, noninvertible scalar scale, noncontaining ascent, and the actual C5
mutation. Equivalent redundant generators remain accepted.

A separate Codex review agent independently reconstructed the four raw profiles
using Gaussian elimination without importing this checker or producer code.
It corroborated the delta and C5 control. This is additional AI-assisted local
review, not independent human or maintainer approval.

## Limits

No source regeneration, native stream/circuit replay, scalar/cleanup identity,
physical Clifford phase audit, global owner schedule, global idle invoice,
moment/root computation, precision or all-size/outer admission is performed.
All inherited obligations remain with the cited construction. No selected
frontier file is changed.

## Open next questions

**Next question:** does a later coherent producer change preserve the claimed
raw-word retirement and rank-distribution identities? This matters because
equal rank mass does not authenticate a moment's distribution. A feasible first
step is to pin one later adopted pair and write its changed-role identity before
running the explicit-set ledger and a targeted equal-mass control. A distinct
new source and fresh overlap check are prerequisites; this package is not a
universal native compiler verifier. See the structured question in `TASK.json`.

## Attribution

Prepared by AAAmirinu with substantial OpenAI Codex assistance, including
separate implementation and review agents. New code and text: Apache-2.0.
Construction credit remains with Jeremy Kothe (PR2312), Vlado Vojdanovski /
Vlado-V (PR2322), Douglas Colkitt and the predecessor contributors documented
in the unchanged [generator notice](sources/pr2322/GENERATOR-NOTICE.txt).
The supplied source files and their original notices retain their licenses.
