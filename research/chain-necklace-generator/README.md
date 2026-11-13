# Generate valid cyclic chain schedules without literal-word enumeration

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped constructive proof with exact finite conformance and a local algorithm
comparison. This answers the representative-generation question in SHIN09-git's
[PR6080](https://github.com/CrocSwap/integer-mult-bounds/pull/6080).

At `(m,c)=(5,1)`, the new generator emits the 356 credited valid cyclic classes
by testing 520 complete prenecklaces, with no rotation canonicalization. Its
complete preprocessing takes 20,912 residue transitions and stores 9,438 states
in 216 cells. Traversal pops 3,888 prefixes, tries 9,266 symbols, performs
7,007 prefix updates and completion lookups, and rejects 3,120 prefixes.
The separate literal comparator examines all 756,756 balanced words and
canonicalizes 5,340 valid words using 80,100 rotations. The complete output
sets agree. These named work counters are not interchangeable machine costs.

The construction joins an exact suffix-residue completion test to the
classical fixed-content prenecklace extension rule. [PROOF.md](PROOF.md) proves
safe pruning and exactly-once output for all positive moduli as an abstract
algorithm. The bounded implementation supports only `1<=m<=5`; its full
finite conformance covers every target in that range. The modulus-one case
is a combinatorial convention, not a characteristic-one ring.

## Reproduce

From the repository root, standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/chain-necklace-generator/generate.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/chain-necklace-generator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/chain-necklace-generator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/chain-necklace-generator
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/chain-necklace-generator --check-source-history
```

Any CPython 3.12 executable can replace the local path. `generate.py` prints
all 356 words using the source's letters `1,2,3`, together with work counters.
Internally the code uses `0,1,2`. The direct verifier prints a generated JSON
receipt bound to all eight package files and `PASS_CHAIN_NECKLACE_GENERATOR`.
It writes no files. No receipt is handwritten or committed.

The verifier compares all 15 target cases through modulus five against a
separate positional enumerator, with 3,927,606 literal word evaluations and
2,510 emitted representatives in total across those cases. Every emitted
word receives a complete four-role integer-matrix endpoint check. Small
suffix tables receive 187 independently constructed matrix-signature checks
and 210 completion queries. Eleven controls cover invalid inputs, periodic
classes, canonical orientation and chronological direction. In particular,
the `(3,1)` fixture retains two period-three classes and two period-nine
classes; filtering out all repeated words would be wrong.

## Local comparison

To reproduce the complete fresh-process comparison:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/chain-necklace-generator/benchmark.py
```

The script runs five alternating pairs at `(5,1)`, checks every returned word,
counts errors, and emits raw samples, environment, work counts and code hashes.
Every timed region includes process startup, imports, the complete computation,
JSON output of all 356 words and process exit. Each generator run rebuilds its
table. Parent-side output comparison is outside timing. No lazy iterator or
persisted cache is used. Timing is an optional local observation, not a CI
acceptance threshold or a comparison with the fastest possible generator.

On macOS 27.0.1 arm64 with CPython 3.12.15, the five-pair median complete
process time was 0.034534 seconds for the generator and 0.651576 seconds
for the literal comparator. The respective ranges were
0.033659 to 0.035091 seconds and 0.646261 to 0.653718 seconds. All ten processes
succeeded, with zero errors and five complete output-set comparisons.
Raw generator samples in seconds were `0.034534042, 0.035090750, 0.033994666, 0.033658959, 0.034655708`;
corresponding literal samples were `0.653717667, 0.646840042, 0.651576250, 0.652623667, 0.646261417`.
The shared host had 18 logical cores and load averages 1.86/2.80/3.06 before
measurement. Other processes remained running; interleaving exposes both
methods to that environment. These observations are local, not a guarantee
on another machine or a supplier runtime claim.

The literal comparator uses compiled binary searches to count the preceding
and following letters, and only canonicalizes words already known valid.
A separate profiling run identifies its full-word scan and binary searches
as the main computational cost. The new computation spends its remaining
work in prenecklace traversal, suffix construction and completion lookups.
Both run serially with the same interpreter and flags. No native supplier,
network or disk workload occurs in either computation.

## Scope and credit

SHIN09-git supplies the question, rotation/period contract and credited count
in PR6080. Nick Petalas's #6037/#4257/#4281/#4748 are count, endpoint and
rotation background; none of their code or stored count tables is imported
or replayed. Ross Richardson's #943/#934 retain the complete-call dirty-chain
lineage. The prenecklace theorem and fixed-content generation are classical;
credit Fredricksen, Kessler, Maiorana, Ruskey and Joe Sawada's
[2003 paper](https://www.socs.uoguelph.ca/~sawada/papers/alph.pdf), Theorem 1 and
Figure 1. The new contribution is the suffix-completion application, generator
and its exact finite work comparison, not a new general necklace algorithm.

[SOURCES.json](SOURCES.json) pins source prose at canonical base
`e54523517d0f03e58352e647c403a5af3e525a57`. Those files are historical provenance,
not runtime inputs. The source PR's head is
`abdcee87d8eb0f46db522b16596406f43e890d7e`. [TASK.json](TASK.json) records the
explicit change from `formal-interface-lemma` to this combinatorial side
question. The selected-baseline orientation passed with #7000 selected;
it supplies source-binding orientation only. The selected frontier is unchanged.
[Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19592067).

There is no new class-count formula, constant-amortized-time result, native
implementation, paid-profile saving, selected-assumption discharge, new kappa
or complete multiplication theorem. Physical routing, ownership, restoration,
precision, tape movement, stock, compiler and complete consumer costs remain
unpriced. No predecessor scientific suite, selected cold replay, Lean or Docker
run is included. Independent human and formal proof-kernel review are unclaimed.

## Implementation bounds

All retained Python functions fit within 60 physical lines. There is no
recursion, dynamic evaluation or network access. The modulus cap is five,
each suffix cell has at most 125 residues, and there are at most 216 cells.
Traversal has an explicit ternary-tree node bound and depth at most 15.
Matrix checks use four rows; receipt hashing accepts eight files capped at
256 KiB each. Explicit exceptions remain active under optimized execution.

Power of Ten rule 3 has a managed-runtime deviation in all three scripts.
Python allocates tuples, sets, dictionaries and exact integers during these
bounded computations. The caps above, stack depth, bounded output domain and
fixed source inventory constrain live storage. Runtime allocation internals
are not measured. A native fixed-buffer implementation would be required
before claiming allocation-free execution or lifting these limits.

Rule 9 has a standard-library dispatch deviation for iterators, sorting,
JSON and argument parsing. Targets are the named standard-library functions
and the two fixed comparison methods. The optional benchmark launches exactly
ten sequential bounded children, each with a 30-second timeout and checked
exit status, stderr and complete output. The registered scientific verifier
launches no child process. Warning-strict normal/optimized execution and AST
inspection provide local diagnostics; Ruff is unavailable in the specified
environment. No shared diagnostic configuration is changed.

## Open next questions

1. Can the suffix-state representation support a specified larger modulus
   with a useful memory bound? First estimate or prove the reachable cell
   sizes before raising the implementation cap. No output-sensitive traversal
   bound is supplied here.
2. Can an actual chain consumer use these representatives at lower complete
   cost? First specify its physical routing, precision and restored-owner
   contract and price the emitted schedules. Rotation equivalence alone
   supplies no such saving.

The structured questions and blockers are in TASK.json. No extension is
reserved or implemented after this first verified generator.
