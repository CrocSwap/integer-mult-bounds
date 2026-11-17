# Exact independent-radical dirty fanout on a directed cycle

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. For the
three independent demands `(e,h,e+h+z)` over
`R16=F2[e,h,z]/(e,h,z)^2`, the exact complete abstract tariff is

    OPT = 2 min_i(mu_i) + 6c,
    min_i(mu_i) >= 6c,   reverse-edge prices >= 6c.

Here the cycle ADDs `0 -> 1 -> 2 -> 0` cost c>0, and insertion into row i
costs mu_i. All coefficients are available at stationary coefficient-independent
prices. Three arbitrary dirty rows and one preserved disjoint source are
required; every dirt column returns. There are no other rows, observations,
free basis changes or clearing operations. The theorem holds at every
positive data width under this algebraic contract.

At insertion and reverse prices 100 and cycle price 1, the optimum is
**206**. The destination-row relaxation from lee-phys's
[#6210](https://github.com/CrocSwap/integer-mult-bounds/pull/6210) gives 204
when every incoming ADD is priced one. This new directed-edge obligation
costs two additional ADDs. Three direct insertions cost 300.

The new eight-gate word, in chronological order, is

    P_0(1+e), E_10(1+h), E_21(e+h+z), E_10(1),
    P_0(1),   E_10(1+h), E_21(e+h+z), E_10(1).

Cyclic relabeling gives an attaining word at any minimum-price insertion
root. [PROOF.md](PROOF.md) proves that every two-insertion cycle word needs
at least six ADDs, with arbitrary interleaving and coefficients, and proves
the complete price-cone result. The proof does not infer an all-word optimum
from a bounded search alone. The first improvement was retained without
expanding to a broader price classification.

## Reproduce

From the repository root, CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/r16-independent-cycle-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/r16-independent-cycle-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/r16-independent-cycle-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/r16-independent-cycle-tariff --check-source-history
```

Other machines may substitute their CPython 3.12 path. No predecessor
executable is imported or replayed. Each invocation writes no files and
prints a generated JSON receipt bound to all six package-file hashes.
The expected marker is `PASS_R16_INDEPENDENT_CYCLE_TARIFF`.

The checker tests 504 words, one for every independent radical demand triple
and root, forward and inverse on their entire dirt/source matrices. It also
checks 393,216 literal forward/inverse scalar evaluations for the stated
demand, ten price fixtures and sixteen rejection controls. Its separate
exact first-order enumeration excludes every two-unit-insertion cycle word
with at most five ADDs. Layer sizes are
`[1,9,57,283,1186,4201,11842,18061]`, with 95,562 transitions and 2,481
closing transitions. These are enumeration counts, not distinct literal
word counts. The written proof supplies the all-word argument.

## Credit, scope and overlap

Credit lee-phys / #6210 for this demand, the arbitrary-dirty contract,
incoming-row return lemma, two-unit insertion argument and directed-price
open question. Retain lee-phys's #5259/#5163, Ali Romman's #5310/#5266,
Krzysztof Wojt's #5045, Ross Richardson's #3063/#3121, Nick Petalas's
#4916/#5208 and the retained fanout lineage. The first-order subspace
method is adapted from Nick Petalas's older #6693; its receiving-row
frontier is cited, not rechecked. The new bit packing and bounded cycle
search are standalone. The older #5933 and #6663 solve other directed
cycle demands, not this independent radical triple. No general priority
is claimed for square-zero expansion, elementary matrices or dirty echoes.

This takes Open next question 2 of #6210. The historical `bit-helper-contract`
card is marked changed to this algebraic interface side result in
[TASK.json](TASK.json). It supplies a sharp local directed-price obstruction,
not an emitted BIT word or a selected assumption discharge. The selected
binding baseline passed at main `e54523517d0f03e58352e647c403a5af3e525a57`,
κ `0.00363005817`, with priority revision 8 predating that selection.

Entry overlap covered 477 open PRs and 7,122 Discussion records with complete
reported remote pagination. Its sparse local note scan omitted 9,973 HEAD
note paths. Targeted all-main README searches and all-state/merged searches
for R16, radical fanout, independent demands and directed cycle supplemented
that scan. No equivalent result was found in that coverage. Historical
diffs, unpublished work and later changes remain coverage limits.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19538457).

No arbitrary-price classification, larger ring theorem, extra-workspace
optimum, physical coefficient preparation, routing, precision/tape, stock,
supplier admission, new kappa or complete multiplication theorem is claimed.
Independent human and formal proof-kernel review are unclaimed. No selected
cold replay, native suite, Lean or Docker run was required for this local
result. Exact source provenance is in [SOURCES.json](SOURCES.json).

## Open next questions

- Determine the exact tariff outside this price cone. Start with the same
  independent radical demand and one cheap reverse edge; count every directed
  edge separately. The six-ADD lower bound alone does not price unequal edges.
- Find a physical caller with these independent radical demands and complete
  source/ADD prices. First identify the actual coefficient algebra and its
  routing, precision and restoration charges. None is supplied here.

Structured first steps and blockers are in [TASK.json](TASK.json).

## Verifier constraints

There is no recursion, subprocess, network, dynamic code execution or external
scientific input in the verifier. Seven transition rounds and a 200,000-state
per-layer cap bound the search; exhaustion raises an error. Each search basis has
at most seven 12-bit vectors. Finite word fixtures have eight gates; the
literal domain is exactly three roots and 16^4 scalar inputs. Functions are
below 60 lines. Explicit exceptions preserve all checks under optimization;
both registered commands make warnings errors. SHA256 receipts are generated
only after the actual checks pass.

Power of Ten rule 3 deviation: CPython allocates integers, tuples and sets
while checking. The fixed finite domains, per-layer capacity check and
serial execution bound live collections; there is no growing service or
unbounded input. Package-file reads are at most one MiB each. A fixed-allocation
embedded implementation would need a separate runtime. Normal and optimized
replay exercise these controls; no external static analyzer is claimed.
