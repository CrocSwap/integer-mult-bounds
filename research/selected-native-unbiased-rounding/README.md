# Unbiased reversible rounding at the selected first native MOVE

The selected PR6030 word's first native MOVE now has a source-bound integer
grid map with exact retained-seed inversion and zero conditional mean error.
One fresh fair bit serves every pair in a complete butterfly layer. Its
pointwise squared error is the minimum possible grid error: h^2 for each
odd-parity pair and zero otherwise. Each seed preserves the complex pair
sum and Gaussian phase covariance in the native pair coordinates.

For N=512^f and f fresh stage bits, the completed tensor map has exact mean
T_[21]^(tensor f), mean squared error at most f*N*h^2/2, and an exact literal
inverse with the retained bits in reverse stage order. This is a construction
and proof with finite corroboration, not a new kappa.

A reachable first-MOVE input has error/input norm ratio at least one under
every same-grid rule. Thus this map cannot fill a uniform relative allowance
u<1. The absolute-error caller join remains open. The [proof](PROOF.md),
[generated receipt](RESULT.json), [source pins](SOURCES.json) and
[scope record](TASK.json) state the contracts and limits.

## Source and evidence

Canonical base: 7c49fe32c55de02c2c873655c804b16e4c3fef0a; priority revision 8;
selected PR6030. Event 9896 is MOVE field 236 from empty frame 3 to frame 7
with basis [21]. The unchanged compiler and independent coordinate oracle
agree on all 512 columns. The new interpreter checks real and imaginary basis
inputs, signed dense inputs and every seed of a full 512^2 tensor input.
A separate reverse row and literal scalar replay check the first-MOVE witness.

The verifier checks all pairs with real components from -4 through 4, both
directions, all Gaussian unit phases and signed inputs including 2^1024-scale values.
It checks seed reuse bias, a wrong inverse seed, a biased fixed seed,
deterministic floor, a non-covariant center, invalid seeds, the relative-error
counterexample and source corruption. RESULT.json gives the exact counts.

## Reproduce

Use CPython 3.12 and the declared NumPy 2.3.4 dependency:

```sh
python3.12 -B scripts/research_package.py --package research/selected-native-unbiased-rounding
```

Both registered commands use isolated, warning-strict normal and optimized
modes. Expected markers: `PASS_SELECTED_NATIVE_UNBIASED_ROUNDING` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The source compiler and coordinate oracle
require assertions, so each mode runs them in an unchanged normal subprocess.
The new verifier's checks remain active under optimization.

## Complete scope and remaining work

The direct implementation uses f*N/2 pair calls, 2*f monomial passes and f
retained bits. The proof includes setup, arithmetic, routing, sufficient
integer widths, data movement and O(N) buffer storage. This is an indexed
integer implementation, not a reversible bit circuit or fixed multitape
schedule. Sampling, random-tape access, entropy recovery, physical cleanup,
accelerated recursive tariffs and full caller propagation are unpriced.
Data inversion does not prove additivity, graph consistency or cleanup after
arbitrary intervening arithmetic. All five assumptions remain open.

Selected cold replay, predecessor full scientific suites, native builds,
independent human review and proof-kernel review are unrun. See the PR for
publication and hosted status. A hosted pass verifies the registered commands,
not acceptance of the universal proof.

## Open next questions

The next question is a full absolute-error caller join with finite scalar
records and owned fresh randomness. First bind its completed native defects
to the selected suffix transfers. A physical supplier and full tape invoice
are the blockers. No next scope is reserved.

## Attribution and overlap

Prepared by Ali Romman with substantial OpenAI Codex assistance; no subagents.
[NOTICE](NOTICE) separates the prior deterministic center family in PR6509,
Nick Petalas's ensemble and reuse results, the selected word, and the consumed
native compiler/oracle lineage. Their sources remain unchanged.

Public open/closed PR and Discussion metadata was refreshed before the claim.
A second exact-main README/TASK search found no matching unbiased Gaussian or
butterfly description. Related PR6509, PR6438, PR6418, PR4017, PR6499 and PR6526
were inspected. This construction has a different numerical contract and an
actual selected native binding. Arbitrary diffs and unpublished work remain
search limits. No novelty certificate is claimed.
