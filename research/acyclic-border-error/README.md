# A sharp error cutoff for bounded acyclic decoder rows

Scoped proof with exact finite corroboration. No new kappa.

For n>=2 and L>=1, define a_n(L) as the first positive root of

    e sum_{k=0}^{n-1} (1+L-e)^k = 1.

An n by n complex matrix whose diagonal error and lower entries have
magnitude at most e, and whose upper entries have magnitude at most L,
is nonsingular whenever e<a_n(L). An explicit real boundary matrix has
rank n-1, so the envelope is sharp. Rational boundary examples exist for
every n. The cutoff satisfies a_n(L) L^{n-1}->1 for fixed n as L grows.

This extends the acyclic generalized Lemma B rank rows used in
[DreamingOfClouds's PR5559](https://github.com/CrocSwap/integer-mult-bounds/pull/5559)
to approximate masked decoders under a bound on the paid subtotal's selected
unmasked entries. That package explicitly excludes border cost. Its exact
decoder floors and computations are cited predecessors, not replay targets.

For eight rows and L=1, the cutoff lies strictly between 1/256 and 1/250.
A separate exact boundary has e=1/255, L=256/255 and rank seven.
For a deficient row with error at most 2^-p and L<=2^b, necessarily
p<n+(n-1)b. Unbounded coefficient growth can escape this obstruction.

[PROOF.md](PROOF.md) gives the all-dimension argument, rational attaining
family, factor-magnitude consequence and transfer contract. Sharpness is
over directed triangular envelopes, not an asserted P112 decoder optimum.
Bounds on the final decoder total cannot replace bounds on the paid
subtotal. An exact example demonstrates cancellation by an omitted free term.

## Reproduction

From the repository root, with the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/acyclic-border-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/acyclic-border-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/acyclic-border-error
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/acyclic-border-error --check-source-history
```

Substitute another CPython 3.12 path elsewhere. Expected markers are
`PASS_ACYCLIC_BORDER_ERROR`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. The standalone verifier has no network, Git,
solver or dependency requirement. It writes only a generated JSON receipt
and marker to stdout. The receipt hashes all seven package files.

Finite evidence consists of 75 literal determinant identities, all 1,056
real sign vertices of four two/three-dimensional boxes, 60 independently
eliminated rational boundary matrices through dimension sixteen, 60 rejected
wrap omissions and 15 named domain or semantic controls.
These finite checks corroborate the written proof; they do not exhaust the
complex matrix domain or constitute proof-kernel verification.

## Scope and implementation bounds

The actual selected record at base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a` reports conditional kappa
0.003125804. The source-binding baseline passed; no selected scientific
replay was run. TASK.json changes the `complex-rank-shape-decoder` card to
this quantitative side result. SOURCES.json pins the original card,
selected record and PR5559 proof as historical provenance. No predecessor
scientific program is imported and no live external input is needed.

The mathematical theorem allows arbitrary finite n and real L>=1. The
certificate API limits n to 32, parameter numerator/denominator height to
4096 bits, and bisection to 128 rounds. The fixed verifier uses n<=16,
permutation determinants only through n=5, and sign enumeration only
through n=3. Functions are below 60 lines; all loops have fixed or
input-bounded domains. API domain violations raise ValueError. Exact
internal assertions are corroborated by explicit checks that survive -O.

Power of Ten rule 3 has a managed-runtime deviation in both Python files.
Fraction and Python container allocations are dynamic. Input dimensions,
heights, iteration limits and seven receipt inputs of at most 1 MiB bound
live state. The largest sign box has 512 vertices, processed one at a time;
matrices have at most 1024 entries. No child processes, callbacks, dynamic
evaluation, global mutable state or persistent file writes occur.
Normal/optimized warning-strict replay supplies interpreted-code diagnostics.
No separate static analyzer is configured for this isolated package. A
fixed-capacity implementation is a follow-up if these domains are expanded.

No unrestricted border-cost floor, COPY64 theorem, P112 attaining decoder,
complete paid invoice, native coefficient implementation, precision or tape
cost, stock, restoration or supplier admission is claimed. The five selected
framework assumptions remain. Independent human and formal proof-kernel
review are unclaimed.

## Open next questions

1. Derive the sharper threshold for one actual P112 selector with its exact
   zero cells. Start from its comparison matrix and a positive-weight
   certificate. An actual paid-subtotal magnitude contract is still needed.
2. Price a complete approximate decoder after the required factor growth.
   Start with one native paid word and include coefficient delivery, rounding
   and restoration. These physical obligations remain open.

The structured questions and their relevance are in TASK.json.

## Credit and overlap

This contribution was produced by Nick Petalas. Credit DreamingOfClouds
for PR5559's exact acyclic rank rows and explicit border-cost caveat, Cinna
Davis for the P112 dictionary/decoder setting, and all predecessors retained
there. Classical interval-matrix comparison and scaled diagonal dominance
retain their credit; [Jiri Rohn's survey](https://journals.uwyo.edu/index.php/ela/article/view/655)
records the general regularity framework. The explicit envelope and decoder
transfer are the contribution here. No global literature-priority claim is
made. Predecessor files and attribution are unchanged. Apache-2.0.

Overlap checks covered live PR metadata and Discussion claims, local batch
reservations, the card's cached overlap report, and distinctive Git searches
over main's complete README inventory. The cache's sparse local-note coverage
was incomplete; unpublished work and arbitrary historical code diffs remain
outside the search. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19440631)
states the scope. No other checked result supplied this bounded approximate
transfer. This observation is limited to the inspected coverage.
