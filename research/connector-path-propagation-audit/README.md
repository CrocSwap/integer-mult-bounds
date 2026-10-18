# Audit the singleton connector's path-domain propagation

The pinned `connector-covering-code` propagation rules preserve every feasible
simple universal path tuple under the contract below. This package gives a
written preservation proof and independently checks the actual native methods
against literal path and point oracles. No defect was found in this scope.

This completes the propagation follow-up requested by
[PR3224](https://github.com/CrocSwap/integer-mult-bounds/pull/3224), not the full
`f(7)=24` proof. No supplier, tariff, selected frontier or kappa changes.

## Sources and scope

Base main is `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
The audited source was introduced by conorholds at
`e67ca5f26351e09c5bb314821633e511212f88ec`:

```text
research/connector-covering-code/cycle_search.cpp
SHA256 597844fc32cde19c1d4104633fa6d3eb0d28c1ca140f8f3d2ba2cb632ecd30d1
```

[SOURCES.json](SOURCES.json) pins the source, its README, the original card and
selected-record context. [TASK.json](TASK.json) records the refined
`census-pruning-audit` scope. The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19002964)
takes PR3224's released handoff. Its exact predecessor head is
`69567e40e8d92542248eda0d6a400d83adc1d3a3`.

The old parity issue is already covered by Nicholas Stone's PR2973, Nick
Petalas's PR3005 and James Reed's PR3096. PR3215 separately audits the old
set/word boundary. This package does not repeat their exclusion searches or
PR3224's capacity-predicate proof.

## Preservation contract and proof

There are `b` low blocks, `1 <= b <= 10`. Their low states `l_i` form the
restored universal projection supplied to `Engine`. A domain `D_i` contains
valid translated simple paths in the three-dimensional high cube. A path has
start `s_i`, end `e_i`, high vertex set `H_i` and coordinate-count vector `c_i`.
A feasible tuple chooses one path from each domain such that:

1. `e_i = s_(i+1)` cyclically.
2. `H_i` and `H_j` are disjoint whenever `i != j` and `l_i = l_j`.
3. `sum c_i` equals the target coordinate counts.
4. If coverage is required, the prefix set
   `P = union_i ({l_i} x H_i)` satisfies `P+P = F2^7`.

The propagation theorem is conditional on this simple-word contract. It does
not make simplicity valid for arbitrary restored words. Initial start-zero,
gap-length and parity restrictions are supplied by the caller, not imposed
by `propagate` itself.

**Claim.** If a feasible tuple belongs to the input domains, `propagate`
returns true and retains every path of that tuple. With coverage disabled,
the same claim holds using only conditions 1 through 3.

Fix one feasible tuple and maintain its membership through every deletion.

- **Binary support.** Tags 1 and 2 enforce the two directed endpoint joins.
  Tag 8 enforces disjointness at equal low states. If a nonzero low difference
  has just one unordered block pair, all eight high differences must come
  from that pair. This is tag 4. Combined tags are conjunctions. The fixed
  tuple supplies a supporting candidate in the other domain for every tag,
  so an arc deletion cannot remove its candidate.
- **Coordinate totals.** Each chosen count lies between the domain minimum
  and maximum for that coordinate. The sum of minima cannot exceed the
  target, and the sum of maxima cannot fall below it. After fixing one
  candidate, replacing that block's extremum by its actual count gives the
  same necessary inequalities. A violated inequality therefore cannot occur
  for the fixed tuple. Extrema computed before other deletions are still
  conservative bounds, since those older domains contain the tuple.
- **Unconditional coverage.** For two different blocks, the sumset of their
  domain-union masks contains the sumset of their chosen paths. For a
  self-pair, the source unions each individual candidate's self-sumset.
  This too contains the chosen path's self-sumset. Unioning these sets over
  every unordered block pair at a low difference must contain all eight high
  differences whenever a feasible tuple exists. Missing a bit proves that
  no such tuple remains.
- **Conditional coverage.** Fix the candidate in block `i`. Pairs not incident
  to `i` retain the preceding optimistic contributions in `excluding`.
  Its self-pair contributes `H_i+H_i` at low difference zero. Every other
  incident pair contributes `H_i + union(D_j)` through `neighbors`. These
  include every contribution of the fixed tuple. Missing a bit cannot
  remove a candidate belonging to it. This argument includes different
  blocks with the same low state and every self-pair exactly where needed.

Immediate empty-domain returns contradict tuple membership. Other false
returns are the violated necessary conditions just proved. Repeating the
rules preserves the invariant. Each changed pass deletes at least one
candidate and no pass adds one, so there are at most `848*b` changed passes.
A fixed point therefore returns true with the tuple intact. This proves the
claim without assuming independence between domain choices.

The source's `pairs`, `neighbors` and tags implement the incidence used above.
The finite check compares their literal definitions on all 82 emitted low
templates. This does not prove that the template generator is complete.

## Separately implemented finite checks

`audit.cpp` includes the unchanged source and renames only its command-line
entry point. It invokes the actual `Tables`, `Engine` constructor and
`Engine::propagate`. Its independent oracles do not call native sumset tables
or propagation to decide feasibility.

- Enumerate all 3,280 high-coordinate strings of lengths zero through seven.
  Direct replay finds 112 simple paths and 106 distinct vertex-set,
  endpoint, count triples. These equal the native normalized table, and all
  848 translated candidates reconstruct correctly.
- Compare all six supported binary-relation tables against explicit vertex
  pairs and endpoint predicates. There are **4,314,624 comparisons**.
- Check every block-pair tag and low-difference incidence list for the five A
  and 77 B templates emitted by the source. There are 8,020 ordered block
  pairs. The source supplies the templates; their completeness is not assumed
  established by this check.
- Use conorholds' universal simple 24-step fixture. There are nine unordered
  high-coordinate choices leaving at most ten low blocks. Include all six
  high-label orders, both directions and every low-boundary rotation, giving
  **1,056 fixture occurrences**. Rotation replays from zero, so its high
  states are translated consistently.
- For each fixture, choose one deterministic alternative per block in each
  of three modes, respecting length, start parity and the first block's
  start-zero restriction. Exhaust the Cartesian domain with and without
  coverage. Each case has at most `2^10` tuples. Literal endpoints, distinct
  seven-bit points, coordinate counts and pairwise XORs decide feasibility.
  Every feasible tuple must survive native propagation, including each of
  its individual choices. This tests soundness, not propagation completeness.

The fresh [RESULT.json](RESULT.json) records:

| Quantity | Result |
|---|---:|
| Domain cases | 6,336 |
| Cartesian tuples | 5,114,880 |
| Feasible tuple occurrences with full coverage | 3,343 |
| Feasible tuple occurrences with coverage disabled | 3,375 |
| Feasible candidate occurrences retained | 65,934 |
| Native candidate deletions | 59,912 |
| Conditional-coverage deletions | 34 |
| Lost feasible choices | **0** |

Occurrences include repeated fixtures and choices across cases. These are not
counts of distinct seven-label words. Infeasible tuples may survive a sound
propagator, so the checker does not demand their complete rejection.

Fixed positive, wrong-total and wrong-cyclic-join controls run for every
fixture. Four further controls distinguish a simple noncovering 22-step word
from the universal repeated-prefix 24-step word. The former passes when
coverage is disabled and fails when enabled; the latter must fail simplicity
in either mode. There are 3,172 fixed controls in total.

Four compiled source mutations make endpoint, disjointness, total-count or
conditional-coverage pruning unsound; each is rejected. Separate exported-copy
controls reject a changed source hash and a corrupted expected receipt.
No frozen predecessor file is edited.

## Reproduce

Python 3.12 or later and GCC with C++17 support are sufficient. No solver,
network access, Lean or Docker is used. From the repository root:

```sh
python3.12 -I -B scripts/research_package.py \
  --package research/connector-path-propagation-audit --check-only
python3.12 -I -B scripts/research_package.py \
  --package research/connector-path-propagation-audit
```

The registered replay runs the audit and six failure controls, then repeats the
audit with Python assertions disabled. `RESULT.json` authenticates the exact
native source and driver; only mathematical counters are compared across
hosts, not environment strings. Builds and small source exports are disposable.
Set `TMPDIR` or use `verify.py --work EXISTING_DIRECTORY` to choose their parent.
A separate local diagnostic run is available:

```sh
python3.12 -I -B research/connector-path-propagation-audit/verify.py --sanitize
ruff check research/connector-path-propagation-audit/verify.py
```

The recorded environment is Linux x86-64 under WSL2, CPython 3.12.15 and
GCC 14.2.0. Compilation uses `-std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror`.
The exact environment and UTC time are in the receipt. A replay refreshes the
counters rather than trusting the stored PASS text. Locally, the registered
ordinary/optimized replay and all six failure controls pass. AddressSanitizer
and UndefinedBehaviorSanitizer report no diagnostics, and Clang 19.1.7 produces
identical counters under the same warning flags. These are local checks, not
hosted CI or independent human review.

## Engineering limits

Build the Lever led to a rerunnable native checker rather than a prose-only
audit. Test Behavior, Not Implementation led to checking feasible-choice
preservation, not requiring the propagator to solve every infeasible domain.
Prove It Works led to compiling and invoking the pinned source itself.

The new native traversal is nonrecursive. Its path domain, fixture count and
Cartesian products have the explicit bounds above. The pinned source still
uses bounded recursion in table and template initialization, with at most
eight and eleven simultaneous generator frames. It is intentionally not
rewritten during an independent audit. A future source rewrite must retain
these exact comparison checks.

Power-of-Ten rule 3 has a bounded test-program deviation: C++ containers and
Python's runtime allocate while the audit runs. Native domains have at most ten
blocks and 848 candidates; tuple enumeration retains one tuple at a time.
Python limits each input to 256,000 bytes, the pin inventory to sixteen rows,
and native subprocesses to ninety seconds each. Scoped temporary directories
own and remove builds and exports on every exit. A fixed-allocation embedded
implementation would need a separate rewrite; none is claimed here. Rule 8's
entry-point rename is the only preprocessor adapter and does not alter the
source's statements. The driver uses explicit checked failures rather than
assertions that optimization could remove.

## Open next questions

A separate implementation could audit search completeness and exhaust all 77 B
orbits. First bind the literal low representatives, gap enumeration, start
restrictions, branching and path-to-word reconstruction. Budget that complete
replay separately; this audit is not an authorization to launch it by default.
The published covering-code bound, classification/transcription, non-simple
branch, template completeness and full census remain separate obligations.
No physical consumer, supplier admission, full multiplication theorem, hosted
CI or independent human review is claimed. Structured next work is in TASK.json.

## Credit

Nick Petalas, with substantial automated assistance. Apache-2.0.
conorholds supplied the audited source, its finite exclusion, path contract
and the simple 24-step fixture. PR3224 supplied the capacity audit and explicit
propagation handoff. Nicholas Stone supplied the corrected parity census;
Aaron Wang and James Reed supplied credited predecessor investigations;
Ross Richardson supplied the PR943 singleton interface; Douglas Colkitt
supplied PR1185 and the Gray upper construction. All predecessor bytes and
attribution remain unchanged.
