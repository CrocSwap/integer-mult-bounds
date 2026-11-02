# Optimal multilinear queries through dirty input rows

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped algebraic proof with exact finite corroboration.**
A generic d-linear Boolean operation can be delivered through d arbitrary
dirty borrowed input rows using exactly 2^d evaluations and 2^d source
toggles, with all borrowed rows restored. At d=2 the literal word uses
**eight complete calls instead of ten** for the matched nested commutator.
No native supplier or new kappa is claimed.

For the complete calls

```text
S_j: z_j ^= x_j                         price c_j > 0
E:   y   ^= B(z_1,...,z_d)              price b > 0,
```

where B is separately F2-linear, the exact generic optimum, for
c_1 >= ... >= c_d, is

```text
2^d b + 2 c_1 + sum_(j=2)^d 2^(j-1) c_j.
```

The sources x_j are preserved; every z_j and y can have arbitrary independent
initial dirt. There is no clean row or extra public workspace. The query word
can depend on prices, but not on data. Direct B(x_1,...,x_d), source mixing,
simultaneous toggles, observations and free basis maps are outside the
alphabet. The bound allows arbitrarily long words and repeated states.
It applies to a word correct for every B, and already follows from the fixed
scalar product B(z)=product_j z_j. Special maps such as zero can be cheaper.

[PROOF.md](PROOF.md) gives the exact contract and all-d proof. Boolean
polynomial coefficients force an odd number of evaluations at every cube
vertex. Projected closed-walk bounds then give the weighted lower bound.
A reflected Gray walk attains every bound and cancels all initial dirt by
separate linearity. B need not be symmetric; ordered matrix multiplication
is one verified noncommuting example.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/multilinear-dirty-cube/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/multilinear-dirty-cube/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/multilinear-dirty-cube
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/multilinear-dirty-cube --check-source-history
```

Another CPython 3.12 path can replace the absolute interpreter. The publication
preflight requires a committed package and its pinned history. The direct
verifier writes nothing and prints `PASS_MULTILINEAR_DIRTY_CUBE` in a generated
JSON receipt with the interpreter, all counts and SHA256 hashes of all six
package files. The registered runner executes both normal and optimized modes.
All checks use explicit exceptions, so optimization preserves them.

The verifier establishes the following finite evidence:

- Exact formal endpoints and inverse words in dimensions 1 through 8, with
  rational prices. In dimensions 1 through 3 it enumerates all 276 possible
  read-parity vectors and finds exactly the all-ones solution in each domain.
- All 2,728 scalar source/dirt/target states in dimensions 1 through 5,
  checking the Gray word, matched nested word and literal inverse.
- All 65,536 ordered source/dirt tuples of two 2-by-2 binary matrix sources
  and two borrowed matrices. Forward and inverse words use literal ordered
  matrix multiplication, with the target initialized to the identity. Target
  updates are XORs independent of its old value; the written identity covers
  every target baseline.
- An independent Dijkstra search over position/visited-set states for all
  84 price tuples from {1,2,3,4}^d, d=1,2,3. It settles 25,948 states and
  matches the formula, permitting detours and repeated vertices.
- Eight individual event deletions, eight invalid price inputs, a legal
  expensive ordering costing 44 instead of 32, a charged restoring detour,
  and the strict 10-to-8 nested-word comparison.

These checks corroborate the written universal proof. They are not a finite
enumeration of all d-linear maps, all dimensions or all query words.

## Scope, sources and credit

The `connector-alphabet-change` card is refined to the new multilinear
evaluation operation. Its first working linear-connector example passed:
945 pairings, maximum coverage 31, 74 queries and 182 leaf calls. That is
orientation only and is not this contribution's result. The selected metadata
orientation also passed and identifies conditional kappa 781451/250000000.
No selected scientific replay is run or claimed.

The new result is a complete abstract call invoice and matching lower bound
for this interface. No actual native E, coefficient producer, physical routing,
instruction construction, stock schedule, all-size compiler, favorable complete
recursive moment or multiplication theorem is supplied. The fixed complete
prices must pay those parts of a call where applicable; source admission and
program generation also need payment in an application. A nonlinear operation
cannot be used in a linear compensation proof without a new interface argument.

Credit Ross Richardson's PR934/943 complete-call dirty-connector lineage,
retained in [universal-connector-boundary](../universal-connector-boundary/README.md).
Reflected Gray codes, finite differences, Boolean-lattice inversion and
summation by parts are classical. The new repository contribution is the
multilinear dirty-input word, its exact weighted all-word optimum and its
deterministic verifier. Global literature priority is unclaimed. No predecessor
code is imported and no predecessor result is audited. Independent human and
formal proof-kernel review are unclaimed.

The base is canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority
revision 8. [SOURCES.json](SOURCES.json) binds the catalogue, selected record
and linear-connector README as historical provenance, not live inputs. The
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19358983)
records the new question. Live open PRs, recent handoffs, local reservations,
main README searches and merged searches were checked. The overlap cache had
complete pagination of 331 open PRs and 6,214 Discussion records at entry;
sparse local notes omitted 8,810 tracked paths. Direct main-tree searches
supplemented that cache. Unpublished work and arbitrary historical diffs remain
coverage limits; the searches do not prove novelty.

## Implementation bounds

Build the Lever led to a literal word constructor and separate shortest-walk
oracle. Prove It Works led to complete dirty-state endpoints and inverse replay.
The code has no recursion, subprocess, network call or write path. The
constructor is bounded to dimensions 1 through 8 and positive exact prices
at most 4,096 with denominators at most 4,096. Words have at most 1,024 calls.
The Dijkstra oracle is restricted to dimension at most three, at most 2,048
states and at most 6,145 heap pops per context. All functions are below 60
physical lines. Internal input bounds and explicit checks remain active.

Power of Ten rule 3 has a managed-runtime deviation. CPython allocates
integers, tuples, lists and dictionaries during these bounded checks. The
fixed fixture domains, word and oracle capacities bound live collections.
A fixed-memory implementation would be needed for a steady service. Rule 9
uses bounded standard-library iterator and heap operations; no dynamic user
callback is introduced. Warning-strict normal/optimized replay and in-memory
syntax compilation are the available diagnostics. No separate static analyzer
or proof-kernel check is run. Shared tooling is unchanged.

## Open next questions

1. Can a selected BIT caller expose a concrete bilinear response through two
   borrowed input rows with a favorable complete invoice? First identify B,
   input versions and borrowed-row lifetimes, then price every S and E call
   and compare the paid and productive profiles. No such native query or
   selected producer/consumer is supplied here.
2. Can a named non-generic multilinear map avoid a cube evaluation through
   a proved relation among its dirty-input response functions? First give
   that exact relation while retaining independent dirt. A concrete native
   relation and its complete physical price remain missing.

Structured first steps and blockers are in [TASK.json](TASK.json). Lean,
Docker and a full selected supplier replay are unrun.
