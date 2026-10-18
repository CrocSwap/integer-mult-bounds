# Sharp finite transport of errors at actual leaf destinations

For PR628's reserved-depth balanced dirty word, an error injected into the
actual destination immediately after a complete leaf has the following exact
worst transport to any later complete-leaf cut, in the maximum register norm:

| Number of factors n | Sharp envelope |
|---|---:|
| 1..3 | 1 |
| 4..7 | 2 |
| 8..15 | 3 |
| 16..31 | 4 |
| 32 | 5 |

This covers **8,120,332 intervals**, both positive and inverse chronological
words, and arbitrary norm-at-most-one operator factors. Every reported maximum
is attained by scalar factors in {-1,+1}. At n=16 the destination-supported
maximum is 4, whereas the predecessor's arbitrary joint-disturbance interval
maximum is 14. The two results concern different input support and do not conflict.

This completes the bounded first experiment requested by
`dirty-interval-coefficient-boundary`'s destination-supported follow-up. It is
a finite exact result. The observed formula `max(1,floor(log2 n))` is **not
claimed for n>32**, and no new production precision or kappa follows.

## Domain and proof of each finite bound

A leaf is the ideal shear `register_y += sign*A_j register_x`; its source
and destination differ. Use the inherited four-phase balanced composition
`U,V,U^-1,V^-1`, one scratch role per depth shared by sibling calls, and
floor/ceiling split for unbalanced n. The inverse word reverses chronological
order and negates leaf signs. The complete emitted sequence is checked against
the actual pinned `compose` source via the retained source-event extractor.

At every cut immediately after leaf a, put a unit error only in that leaf's
destination. Start its formal column with polynomial 1 there and zero in all
other registers. Replay every subsequent leaf by **left-concatenating** its
factor symbol and adding signed coefficients in the free noncommutative algebra.
Repeated symbols are retained; no squarefree, commutative or involutive
quotient is imposed. At every later cut, the absolute coefficient sum of each
entry bounds that operator entry's norm, because every monomial is a product
of contractions. The largest entry bounds a single supported error in the
maximum register norm. Unchanged rows retain their previous bound; only the
updated row needs recounting. Immediate cuts, whose map is the identity, count too.

The loop enumerates all preceding leaves and every later cut of both words
for every n=1..32. Thus these are complete finite upper envelopes, not a
sample over cuts, signs or input values. A binary linear system assigns scalar
factor signs making every monomial in an attaining entry have the same sign.
The resulting exact scalar column attains its coefficient sum. Consequently
the upper envelope is the actual finite operator-norm maximum in this domain.

The bound transports one ideal additive perturbation after a complete leaf.
It does not cover internal leaf intermediates, cumulative multiple errors,
noncontractive factors, aliasing, an arbitrary joint error vector, or an
actual deterministic rounding failure. Factors with additional cyclic-kernel
constraints may not realize these generic scalar-isometry witnesses.

## Reproduce and inspect

```
python -I -O -B research/leaf-destination-transport/verify.py
python scripts/research_package.py --package research/leaf-destination-transport
```

RESULT.json contains each n's interval count and an exact attaining witness:
orientation, cuts, actual injected destination, output row, ordered polynomial,
scalar signs and resulting column. The new column engine imports no predecessor
bound or matrix-census implementation. For each witness it compares literal
scalar execution with the retained separately represented recursive prefix and
inverse-prefix oracle; that oracle and source extractor are reused and credited.
All scalar sign assignments and cuts for n=1..6 are also replayed directly.

Controls reject the wrong support, a pre-word injection and a noncontractive
factor. The source-bound n=4 joint witness with factors `(1,1,-1,1)` and cuts
`[2,6)` has norm 6, exceeding the supported bound 2, so support cannot be
dropped. The n=16 attaining column rejects an understated bound of 3.
Normal replay compares the complete receipt and writes nothing; `--write` is
explicit authoring mode. Direct hashes and registered Git provenance are checked.

No Lean, native leaf, selected cold replay, physical caller, error accumulation,
precision/tape or full multiplication theorem is proved here. The outcome is
marked partial relative to the catalogue's all-size objective.

## Open next questions

Does `max(1,floor(log2 n))` hold for every n? Start an induction through the
four recursive phases, retaining the preceding leaf's exact destination and
the shared depth scratch. The missing all-size column invariant is the blocker.
Even such an invariant would leave internal leaf growth and accumulation of
multiple rounding errors separate. See the structured question in TASK.json.

## Credit and provenance

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; revision 3 nonce
`71ae411736f0ac0cacb745e46faf3dec`. SOURCES.json pins every consumed source.
Credit Arham Tahir's `dirty-interval-coefficient-boundary` for its explicit
supported-error question, joint-norm theorem and independent prefix oracle;
Chafik Boukhalfa's PR628 composition; and the retained Hanson Sun, Charles Bethin,
Philipp/mightyOil, Gareth Davidson and 0xkilgore precision/restoration lineage.
Their joint-envelope counts and proofs are not new results of this package.
Prepared by woklerx with substantial OpenAI Codex assistance. Apache-2.0.
