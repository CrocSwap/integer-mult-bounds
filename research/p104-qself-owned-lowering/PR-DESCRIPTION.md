## Why this matters

DreamingOfClouds' E-free caller in CrocSwap/integer-mult-bounds#6937 removes
two empty-mask roles but introduces two QSELF instructions. Its shipped
checker does not replay the caller, and the owned/physical/cost connection
for that new instruction needs an explicit argument.

This package supplies a reproducible formal operator certificate, a
source-bound relative typed owned-bank lowering, and the complete cost comparison with
CrocSwap/integer-mult-bounds#6936. **No new κ; no selected certificate change.**

## Exact result

- The actual 2,991-event, 76-input caller has the declared diagonal endpoint
  over `Q(i)[q,D_1,...,D_18]/(q^4-1)`, with formal D variables and independent
  input coefficients. A separate backward-covector engine uses integer
  dyadics and faithful four-character evaluation with D still formal.
- All 192 instances of the two QSELF sites lower to INIT/COPY/query-in/
  PAID(1)/query-out/SWAP/CLEAR in the unchanged lifecycle IR. One reused
  owned query bank suffices, with no productive credit. The canonical
  owned-storage contract permits its contents and completed-child history.
  This package does not install a SERVICE registry for its new `qself6937`
  tokens or claim the frozen source-specific binders accept them.
- The query adapters implement inverse Q with exact absolute phase for every
  positive column count. Shape, grid, signed-range and actual provider-cost
  predicates remain explicit.
- Complete target and paid histograms each lose 192 rank-one entries; all
  other ranks match. The moment polynomial and surplus 1520 are unchanged.
  New totals: 23,050 productive fields and 117,846 paid calls. Including a
  separate 24,576-unit new lifecycle charge and both conservative recharges,
  the inherited conditional raw accounting is 811,461,936 < 10^9.

## Source pins and verification

Canonical base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`; #6937 source head
`a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`; #6936 native/comparison head
`03626137d0bd57f09b0bf9597376183ce6fa9683`. Every used source file has a
repository/commit/path, byte count, Git blob and SHA256 pin. The packet
contains proofs, exact profiles, all 192 typed expansions and complete PR text.

```sh
python3 -B scripts/research_package.py --package research/p104-qself-owned-lowering
```

Eight registered normal/optimized gates cover the formal identity, separate
covectors, source/phase/owned binding, exact invoice and 27 meaningful negative
controls. A separate 84-case metered scan audit executes unchanged lifecycle
INIT/COPY/CLEAR code and checks its derived constants, actual raw erasure,
head restoration and retained backing. The full Gaussian caller is not
claimed to have run physically. One proposed basis mutant is correctly
reported as equivalent, rather than counted as a rejected control.

## Scope and remaining obligations

The full operator theorem assumes commuting Q,D and Q^4=I; only the local
owned substitution holds for arbitrary completed A. All five selected
framework assumptions, plus the candidate's retained native/A6, odd-scalar
and BIT premises, remain. Exact token-to-provider/table dispatch and concrete
header export are unfinished. Physical provider closure, actual return
representability, compiled precision/stock substitution and rounded analytic
recovery are open. The historical scalar/pass tariff is kept distinct from
the new explicit physical scan bound. This does not adopt the candidate's
unreviewed κ or alter the accepted κ 0.003125804.

## Novelty and credit

The E-free root, caller, QSELF idea and reported original caller replay belong
to DreamingOfClouds, with Claude Opus assistance. The source README does not
specify whether its D variables remained formal; this package does not
claim that four q characters are insufficient or that the reported result
was wrong. It adds shipped unspecialized certificates and the explicit
owned/source/cost closure.

Prepared for **@CubeJerry** with substantial OpenAI assistance. Retain Romman,
the native/productive/compiler lineage, @CubeJerry's
CrocSwap/integer-mult-bounds#6912 and CrocSwap/integer-mult-bounds#6914,
unpaidmoon's CrocSwap/integer-mult-bounds#6930, icekylinx's
CrocSwap/integer-mult-bounds#104, and the pinned published lifecycle and
scalar/SWAP packages. Separate AI review is not independent human or
proof-kernel acceptance.
