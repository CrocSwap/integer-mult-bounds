# Global ceiling for the two-chain invoice

**No new κ.** For the frozen 104-port native profile and complete two-chain
invoice defined in `PROOF.md`, the unique best positive-integer length pair is
`(9,9)`. Its raw crossing lies strictly between `0.0033718004754` and
`0.0033718004755`. Concavity and a monotonic normalization prove the result over
all lengths; a finite search is not the impossibility argument.

The pending construction in CrocSwap/integer-mult-bounds#6833 expressly leaves
global optimality open. This package independently recounts its literal caller
and proves that changing the two lengths, ordered child partitions or full binary child trees cannot improve the declared bill.
This identifies which restriction a further complex-supplier improvement must
change. It does not establish compiler admission, replace the selected result,
or rule out different roots, native circuits or idle lifetimes.

## Exact sources and scope

- Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
- Construction: DreamingOfClouds, CrocSwap/integer-mult-bounds#6833,
  `ad24ad966b857dbfed50d9121624db84b2eccc92`,
  `research/p104-chain-nested-root/`.
- Seven required source files are retained byte for byte with their notice;
  `ORIGINS.json` records paths, Git blob IDs and SHA256 digests. No network,
  unmerged Git object or predecessor Python module is required to run the
  standalone verifier.
- `SOURCES.json` binds the original task card and selected record as provenance.
  The native helper/paid profile is an authenticated inherited input, not a new
  operator replay. The `(9,9)` complete bill is recounted from `CALLER.json`.

The all-positive-length invoice family is deliberately broader than the
source-proved odd/odd construction. Its all-parity extension only strengthens
the upper bound; realizability of every even or mixed-parity bill is not claimed.
Applicability requires exactly the declared native, productive-target and paid
profiles. The five inherited framework assumptions remain outside this result:
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`,
`analytic_recovery`.

## Result and proof mechanism

For a fixed total length, strict concavity balances the two sides. The balanced
margin then has strictly decreasing increments in total length. Independent
directed intervals certify a positive increment from 17 to 18 and a negative
increment from 18 to 19 throughout the raw-root bracket. A rational derivative
bound after normalization by `9^(1-C)` rules out a later favorable interval.
A concave envelope additionally bounds arbitrary ordered partitions and full
binary child trees, including all their internal thin-query costs. The unique
optimum has nine individual native calls on each side.

The source recount returns 12,232 target fields, 64,184 paid jobs, paid rank mass
166,812 and surplus 760. The interval implementation is new and uses integer
arithmetic, explicit logarithm/exponential tails and outward rounding. It does
not import the construction, pricing engine or predecessor arithmetic.
`PROOF.md` contains the complete argument; `RESULT.json` contains deterministic
certificate endpoints and check coverage.

## Reproduction and executed checks

```sh
python3 -B research/chain-root-global-ceiling/verify.py
```

Expected first line: `PASS_CHAIN_ROOT_GLOBAL_CEILING`. The second line reports
the rational root bracket, `(9,9)`, 20 rejected negative controls and 961 finite
corroboration pairs. The same command with `-O` checks that optimized Python
does not disable rejection. Standard-library Python 3.12 is sufficient.

The grid is exactly `1<=left,right<=31`, with no random seed; its stopping rule
is exhaustion of those 961 pairs. It corroborates the formula and is not used
to infer the infinite-domain theorem. Exact integer-power and square-root
controls independently check power enclosures. Semantic controls reject omitted
thin queries and idle jobs, an undercharged merged rank, a missing target axis,
an incorrect target exponent, an undercharged native job, false maximizing
lengths, and the favorable lower endpoint as a ceiling. Every retained source
file is separately altered and rejected. The grouped-tree extension additionally checks every ordered forest pair with
total native leaves 2 through 7, the predecessor gate crossing, and a control
that omits an internal thin-query charge. Full native operator replay and full
supplier admission were not performed.

The registered package runner can additionally validate provenance and run both
normal and optimized commands:

```sh
python3 -B scripts/research_package.py --package research/chain-root-global-ceiling
```

## Open next questions

1. Can a changed root or multiple coupling fields improve the complete bill?
   Derive the full productive and paid profile first. A concrete alternative
   caller with an exact operator and physical-interface proof is still needed.
2. How does a verified new native profile move the best length? Substitute its
   authenticated coefficients, then recheck the derivative and adjacent signs;
   the present ceiling does not transfer automatically.

These questions and blockers are also recorded in `TASK.json`.

## Credit and license

Prepared for @CubeJerry with substantial OpenAI assistance in the proof,
implementation and review. The two-chain construction, native payload and
retained source evidence are due to DreamingOfClouds in
CrocSwap/integer-mult-bounds#6833, extending the native profile of
CrocSwap/integer-mult-bounds#6824 and its credited predecessors. This package's
new contribution is the global fixed-family proof and independently implemented
source-bound certificate. Retained files are unchanged, with their original
notice. Apache-2.0.
