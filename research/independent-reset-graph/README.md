# Independent chronological verification of the complete reset graph

**Independent finite verification; no new kappa.** A separately written sparse
interpreter corroborates every one of PR1552's **1,431 reset intervals in four
dirty-state contexts**, including **1,325 intervals absent from every supplied
complete schedule**. It reconstructs incoming states by executing eager words,
then recomputes all 1,017 width thresholds, the 31-point optimal frontier and
2,052 published distance entries. No discrepancy was found in those graph,
invoice and witness fields of the pinned certificate.

The mathematical frontier belongs to
[PR1552](https://github.com/CrocSwap/integer-mult-bounds/pull/1552), exact head
`4db7213c90288b1eb83983e08c5ef401d19b7844`. That package already supplies
Fraction-column checks of its 31 frontier words and exhaustive smaller cases.
This contribution adds a separate **complete interval-graph check**, with its
own fixture generator, instruction emitter, sparse arithmetic, chronological
entry states and suffix optimizer. It imports no executable from PR1552,
PR1537, or the abandoned local construction package. The original scoped
frontier was discovered concurrently; no priority for it is claimed here.

## Reproduce and result

Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/independent-reset-graph
```

Expected:

```
PASS_INDEPENDENT_RESET_GRAPH edges=1431 contexts=5724 off_path_edges=1325 frontier=31 schedules=40 small_partitions=255 controls=10 no_new_kappa
PASS_RESET_AUDIT_PACKAGE ...
PASS_REGISTERED_RESEARCH_PACKAGE research/independent-reset-graph outcome=completed
```

Standalone: `python3 -I -O -B verify.py` in this directory.
`verify.py --emit` prints the canonical [RESULT.json](RESULT.json) without
changing files. The original certificate is retained byte-for-byte in
[sources/pr1552-CERTIFICATE.json](sources/pr1552-CERTIFICATE.json), with SHA256
`9125320a3785904a89ad38b5d7b8f6ee4e8d90e3f5776aa9b30a732ad6e3b211`.
All source bytes and Git blobs are bound in [SOURCES.json](SOURCES.json).

The audited conclusions are:

| Pinned conclusion | Corroborated complete invoice / width |
|---|---|
| Eager restoration | 2,494 ADDs, peak 87 |
| No saving at feasible caps below 788 | Minimum complete unit-price cost 2,494 |
| Cap 1,023 | 2,188 ADDs + 260 SCALEs = 2,448 operations |
| Cap 2,047 | 2,138 ADDs + 192 SCALEs = 2,330 operations |
| Reset after 52, then 53 | 2,114 ADDs + 120 SCALEs = 2,234, peak 3,932 |
| Original unsplit PR1537 word | Same 2,234 operations, peak 4,195 |

These are fixed scalar-word counts and exact prefix row-L1 norms. They are not
physical runtime or selected-supplier precision claims. The full saving needs
cap at least 3,932 within this partition class. The normalized complete edge
table hashes to `3ffd73bfcb732b7f1851a32f8d6da0734a0376afac418409a619e6c3059aaf02`.

## Object, dependency and complete recurrence

The inherited PR1537 fixture has 53 fixed children, five two-coordinate
workspace pairs and reader seed 53. Assignment seed 59 chooses the follow-up;
it does not alter the source fixture. Over exact rationals or complex components,

```
Q = [[1,1],[0,1]], P = diag(Q,Q,Q,Q,Q),
C_i(D,U) = (D + R_i U, P U), R_i P = Q R_i.
```

All 22 input coordinates are arbitrary: two output, ten source and ten dirty
workspace coordinates. Children retain their trailing P and restore any
private scratch. A group of l consecutive children aligns D by Q between
children, then uses the fixed binary `P^(-l)` and `Q^(1-l)` returns. It gives
`D += (sum R_i) U` and restores U. The full echo is
`U+=X; G; U-=X; G^(-1)`, with literal inversion. The inherited intertwining
identity proves composition; this check separately replays its finite words.

For `a(l)=popcount(l)` and `s(l)=2 floor(log2(l))`, both zero at zero,
the inherited boundary is

```
b_A(l,m) = l-1 + m*a(l) + a(l-1)
b_S(l,m) =       m*s(l) + s(l-1).
A_root = 2 sum_i A_i + 4m + 2 sum_groups b_A
S_root = 2 sum_i S_i      + 2 sum_groups b_S.
```

For a nonroot child add m ADDs for its required final P. At the fixed root,
the complete unit-price bill is `1964 + 2*boundary_cost`. Every child, inverse,
source load/unload, alignment, binary doubling/halving and restoration is paid.
Sums of compatible readers remain compatible, so this is a finite-depth typed
recurrence. It is not a contracting input-size recurrence for multiplication.

Every ADD reads two data coordinates; every SCALE reads one; each writes one
and consumes one instruction record. Both directions' access counts and the
source-then-destination coordinate travel score are rechecked. Actual physical
cost still needs admission and coefficient preparation, instruction storage and
control, width-dependent arithmetic, routing, adapters and any required head
returns. Complete fixed instruction tariffs may absorb those only if a backend
establishes them. The code does not make those costs free or certify a backend.

## Independent method and why all edges matter

PR1552 constructs interval entrances from closed-form prefix sums. This checker
instead executes the complete **eager echo and its literal inverse** on a
sparse identity operator, saving each restored boundary state. Earlier reset
choices cannot affect those boundaries: each completed group adds its reader
sum and returns U and the output frame. Consequently the saved eager states
are valid for every contiguous partition.

For interval `[i,j)`, the checker independently emits its canonical group and
replays it from four saved entrances: the two passes of the forward echo and
the two passes of its inverse. It checks each exit against the corresponding
chronological snapshot and computes the largest prefix row norm. Integer
halvings must divide every coefficient exactly. It compares all four context
values, their maximum and both instruction charges with the original record.
This covers 5,724 contextual interval executions, not a sample of winning edges.

There are 106 edges among the two baselines, 31 frontier schedules and seven
bit-cap schedules; 1,325 others are absent from those paths. The separate
verification of all those edges matters because an underestimated losing edge
could create a false optimum even when every published winning word is right.
One control corrupts edge `[0,2)`, absent from every supplied path. Another
changes a nonmaximal context while leaving the recorded maximum unchanged.
Both reject after hash authentication has been bypassed for the in-memory
test, so rejection is mathematical, not merely an immutable-file mismatch.

The checker solves the graph in the opposite direction using suffix costs.
All 1,017 distinct thresholds are checked; the graph is constant between them.
For each of the 38 published optimum records, it separately solves every
prefix target and checks all 54 distance entries, the chosen path and the
attained bill. This accounts for all `2^52` contiguous partitions by the
finite DAG reduction; it does not execute `2^52` complete programs.

Every one of the 40 supplied schedule records (33 distinct complete words) is
independently re-emitted and checked in both directions against the desired
linear map, the instruction hash, every invoice field, and the prefix witness.
Rational scalar execution checks the maximizing sign inputs and fractional
dirty states. A contextual warning is reproduced: group `[7,21)` has standalone
peak 294, but peak 788 when accumulated output and both echo directions count.

As a separate control, all 255 partitions for k=1 through 8 at m=2 and reader
seed 59 are fully replayed. All 86 cap decisions agree with literal enumeration.
This extends the check to a different small fixture; it is not another theorem.

Ten mathematical controls reject: an unused edge bound, a hidden context bound,
a duplicate edge with unchanged inventory size, unpaid interval scaling, an
invented frontier saving, a wrong nonterminal distance, a false growth
attainer, undercharged inverse access, omitted source load and omitted
restoring halving. [test_package.py](test_package.py) adds actual source/receipt
corruption checks, deterministic regeneration and read-only source relocation.

## Scope, overlap and credit

Base: `64039f1bd3b6a523b96083fd858ad040a75e3030`. The selected certificate at
that base is PR1094, `kappa=836330098538459/500000000000000000`, whose complex
side binds. Its source manifest, actual assembly and maintainer review are
recorded as historical provenance. No selected/frozen source, supplier, ledger
or upstream file changes.

The direct audited source is Hanson Sun's concurrent, separately authored
PR1552 at the head above. Its predecessor is **Sagar Thakrar's PR1537**, head
`407f00df6ca0bf86b455b5640f18ec2f62ee77b9`. Credit PR1537 for the fixed fixture,
paid binary return and echo recurrence; Ross Richardson's PR1287 for the
output-frame framework; Sagar Thakrar's PR1227 and the PR889/1203 reader lineage
for earlier mechanisms. Original notes/model bytes are retained unchanged;
none of their executable code is imported.

[CLAIM.txt](CLAIM.txt) records the initial recursive-interface assignment and
three candidates. No pinned issue existed, so the claim remained local. The
final overlap refresh found PR1552 and active Discussion1542; this prompted one
pivot to independent verification. [OVERLAP.json](OVERLAP.json) preserves the
coverage and the already-written sparse verifier's hash at discovery. The
discussion investigates construction/cap optimization; this package supplies
complete-graph corroboration with another method. No novelty is inferred from
search absence, and the duplicate construction is not submitted.

That discussion subsequently produced concurrent
[PR1563](https://github.com/CrocSwap/integer-mult-bounds/pull/1563), observed at
`e7d1ebfc3093a704b55c14ea4d10d0d0bdfdd0db`. It corroborates the same canonical
31-point control and changes the root word by cancelling a terminal output
return pair, proposing a 35-point extended frontier. This audit is pinned to
PR1552's fully materialized canonical words; PR1563's changed words and graph
have not been independently checked here. No global optimality is inferred
from the canonical-class certificate.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex
assistance** in derivation, implementation, checks and prose. One agent in this
session; source and audit authors share the same account and AI assistance.
The implementation independence is as described above, not independent human
review. New work is Apache-2.0; retained sources preserve attribution.

This finite certificate concerns the unchanged ordered children, contiguous
fully restored groups, fixed binary-return alphabet and equal instruction
prices. No discrepancy is claimed in PR1552. Alternative return synthesis,
child fusion, nonzero cut phases, nested precision bounds, physical hosting,
rounded arithmetic, a real indivisible selected-supplier child, full selected
cold replay and the multiplication theorem remain outside the audit.

## Open next questions

The inherited application question remains: find an actual supplier child
whose exit drift cannot be removed internally. Inspecting one real caller is
the feasible first step; neither source nor audit provides that caller.

An all-edge chronological audit of PR1563's extended graph remains separate.
The first step is to account for its cancelled return pair at the echo midpoint
and rederive the actual incoming states. The changed literal-word contract is
the blocker to reusing this certificate unchanged. Structured questions and
limits are in [TASK.json](TASK.json).
