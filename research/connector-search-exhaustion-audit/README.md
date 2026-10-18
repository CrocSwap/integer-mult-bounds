# Search completeness and interruption in the seven-source engine

This audit closes PR3261's named branch/backtrack obligation for conorholds'
pinned `Engine::search`. The new result is a written finite-search implication,
checked against a separate ordinary-word Cartesian oracle on 914 bounded roots.
There are 634 satisfiable and 280 unsatisfiable roots. Fifty satisfiable roots
and 22 unsatisfiable roots require recursive branching. No source defect was
found in this scope.

The source's `search` returns false both for an exhausted root and for an
interrupted root. A caller must also inspect `timed_out`. The outer
`enumerate` returns true only when neither a witness nor an interruption was
encountered. Three deterministic checkpoint controls test this distinction.
No full A/B census, `f(7)=24` validation, supplier or new kappa is claimed.

## Exact object and implication

The subject is `research/connector-covering-code/cycle_search.cpp`, SHA256
`597844fc32cde19c1d4104633fa6d3eb0d28c1ca140f8f3d2ba2cb632ecd30d1`,
at canonical main `463113d675af7410ac91d53a4fed51ec6494eb9a`.
Its tables contain 106 normalized simple Q3 paths and 848 translated candidates.
Each of eight or ten low blocks has a finite candidate domain. A legal root
uses only those candidate IDs and starts block zero at high state zero.
The low projection is restored and universal, as required by the constructor.
The engine is fresh, with `found=false` and `timed_out=false`.

A feasible tuple joins consecutive high endpoints cyclically, has the three
specified high-coordinate totals, and has disjoint high vertex sets between
blocks at the same low vertex. With `require_cover=true`, its ordinary
seven-coordinate prefix set must cover all 128 XOR differences.

For a legal root, if search completes without interruption, its return value
is true exactly when a feasible tuple exists. A successful witness belongs to
the original root and reconstructs such a word. Search takes domains by value,
so its caller's domains are unchanged. These statements apply with the
conditional-coverage filter enabled or disabled. Turning off `require_cover`
changes the target to the endpoint/count/simplicity problem, not universality.

### Why propagation does not remove a feasible tuple

Binary support requires the actual endpoint joins, same-low disjointness and
any unique-pair coverage constraint. A feasible tuple supplies its own partner
in each other domain. Coordinate minima/maxima bound every possible sum;
a feasible tuple lies inside those bounds, including when one candidate is
fixed. For coverage, every selected mask pair lies inside the optimistic union
of the remaining choices. Self-pairs use each candidate's actual self-sumset.
After fixing one block, the conditional union still contains all contributions
of a feasible tuple. Thus a deletion cannot remove that tuple's choice.

Every successful deletion decreases the finite total domain size. A repeat
with no deletion exits. This is the scope independently probed by PR3244;
the present audit inspects the actual rules and uses a new word-level oracle,
not that predecessor's executable or verdicts.

### Why branching is complete

After successful propagation, every domain is nonempty. If all are singletons,
the tuple is fully determined; the source reconstructs and checks it before
accepting. Otherwise the minimum-size/degree heuristic chooses some domain
with more than one member. The heuristic changes order, not the partition.

`Bits::each` visits each set bit once. Each child gets a separate copy of the
propagated domains, with only the chosen block fixed to that candidate.
Every remaining feasible tuple belongs to exactly one child. No sibling
inherits another child's reductions. A chosen block remains singleton in all
its descendants, so recursive depth is at most the block count, at most ten.
Induction on the number of nonsingleton blocks proves completeness.

The loop stops considering children only after success or a sticky timeout.
Success is supported by the checked singleton witness. A timeout propagates
without being relabeled exhaustion. In `enumerate`, the gap recursion also
stops on these flags, and `return !timed_out && !found` separates completed
negative searches from both other outcomes. Completeness of the gap domain
and soundness of capacity remain separate premises, not inferred from this
return expression. Checkpoints occur every 1,024 search calls and 256 gap
compositions. They are not strict per-call wall-clock limits.

## Independent finite check

`audit.cpp` includes the authenticated source with only its original `main`
renamed. The baseline changes no search, propagation or table code. The new
oracle does not consult `tags`, binary support, pair tables, propagation,
`word_from` or the source's `independent_oracle`. It enumerates every tuple
in each supplied Cartesian root, reconstructs literal high-path/low-step
words, and checks restoration, target counts, prefix distinctness and all
ordinary XOR differences. Path representatives and fixture-to-ID conversion
are reused from the subject and are not claimed as a new independent table
construction; PR3261 addresses that separate representation obligation.

The fixtures come from the source's credited swapped-Gray simple24 word.
They cover both low patterns, all six high-coordinate permutations, unions
of valid paths, midpoint count targets, deterministic three-choice nearby
roots, and empty roots. Every root is tested with an applicable coverage
mode; the permutation cases also test both conditional-filter settings.
The oracle evaluates 3,785,826 tuples and finds 728 solutions across the roots.
The actual searches visit 1,048 nodes, with a maximum of seven per root, and
all 634 returned witnesses pass the literal oracle. Counts are fixed-domain
coverage receipts, not performance measurements or a full census.

For interruption, an already-expired real deadline is paired with starting
node counters 1,022 and 1,023, reaching the unchanged 1,024-call checkpoint
inside a child and at the root. Both return false with a sticky timeout and
no witness. A gap counter initialized to 255 tests the unchanged 256th-gap
checkpoint. These are synthetic counter offsets, not newly exhausted trees.
A zero-high-count root exhausts negatively; full gap enumeration of the
simple24 positive rediscoveres a valid witness and does not report exhaustion.

Four compiled source mutants are rejected: only visiting the first branch,
sharing child domains, ignoring a child's timeout, and treating an interrupted
enumeration as exhausted. The first two controls test false-negative search
failures, not just malformed inputs. Six Python controls additionally check
valid exported sources and changed, missing, linked, truncated or duplicated
source inventories. [RESULT.json](RESULT.json) is regenerated by `--emit`.

## Reproduce

Python 3.12 and a C++17 compiler are required. No Python packages or solvers are
needed. Keep build files in an external, session-owned `TMPDIR`:

```sh
python3.12 -I -W error -B scripts/research_package.py \
  --package research/connector-search-exhaustion-audit
python3.13 -I -O -W error -B research/connector-search-exhaustion-audit/verify.py \
  --compiler clang++-19 --no-mutants
python3.13 -I -O -W error -B research/connector-search-exhaustion-audit/verify.py \
  --compiler clang++-19 --sanitize --no-mutants
```

All live inputs are canonical-main files declared in `VERIFY.json` and bound
by SHA256 and Git blob IDs in `SOURCES.json`. Direct replay of a committed
package export needs no Git executable, pending PR object or network access.
`CHECKS.json` records the observed environments and verification, including
limits. A dedicated Linux workflow checks the compiler explicitly.

## Scope, credit and family decision

Task `census-pruning-audit`, priority revision 6, is refined to PR3261's named
remaining search implication. The original card's `01021323` parity error and
PR2973 correction were read as calibration, not reported as new findings.
The baseline source-binding control passed before selection. PR3224 checks
capacity, PR3244 checks propagation, and PR3261 checks candidate representation.
This audit checks branching, witness return, sibling isolation and interruption.
No predecessor file, selected source or frontier record changes.

The family decision is to stop at this audit. Complete B exhaustion, all
82-template receipts and their CLI flags, literature/classification premises,
non-simple words and the full `f(7)=24` theorem remain unverified here. No
selected cold replay, Lean, Docker, physical compiler or supplier replay is
run. Evidence is author-checked with separately implemented predicates, not
independent human or proof-kernel review.

Credit conorholds for the engine, path tables and fixtures; krzysztofwojt/PR3261
for the representation proof and explicit handoff; commdata2338/PR3224 for the
capacity audit; Nick Petalas/PR3244 for propagation; Nicholas Stone/PR2973,
Aaron Wang, James Reed, Ross Richardson/PR943 and Douglas Colkitt/PR1185 for
the retained model, correction and construction lineage. Predecessor source
notices and frozen evidence remain unchanged. Nick Petalas. Apache-2.0.
Substantial automated assistance was used in derivation, implementation,
checking and writing.

## Engineering constraints

Build the Lever produced the retained Cartesian/native replay. Prove It Works
requires actual search returns and checked witnesses, plus a Git-free committed
export. Test Behavior, Not Implementation led to existence, witness, caller
state and timeout controls; node counts are diagnostic source-bound receipts,
not a replacement for those comparisons.

Power of Ten bounds new loops by 914 roots, at most 59,049 tuples per root,
80 word positions, 128 differences, ten blocks and 848 candidates. Each source
is at most 128 KiB. Native build and execution have 60/90-second process bounds.
New Python functions are under 60 lines. The cohesive C++ fixture generator is
kept together below 60 physical lines rather than split across hidden state.
Rules 1/8/9 deviate only for the authenticated subject's bounded recursion,
its include-time main rename and standard callback iteration. Search depth is
at most ten; path depth is at most seven. Frozen loops are audit subjects,
not rewritten. Rule 3 requires a managed-allocation deviation for Python/C++
containers; the fixed source, root, tuple and word capacities bound live data.
Library allocation internals are not audited. All builds enable pedantic
warnings as errors; sanitizer and optimized second-compiler checks exercise
these bounds. Reassess the domains before enlarging this audit.

## Open next questions

Bind all 82 actual A/B template IDs, conditional-cover flags, exit statuses and
completed receipts to a full source-pinned exclusion. First audit the replay
caller's receipt acceptance and interruption handling, then budget an independent
complete B exhaustion. The blocker is coverage of the entire requested domain,
not another test of the known parity counterexample. This local search proof
does not discharge that caller obligation or the inherited classification.
