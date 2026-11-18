# Sharp odd-difference image bounds and equality pools

For an irreducible collection of binary rank-one idempotents with nonzero
off-patterns, let k be the pattern dimension, nu the matrix-unit graph's
maximum matching size, and n the joint-image dimension.

The bound `2n<=3k+nu-1` is attained exactly when `k-nu=1 modulo 4`.
Every such equality pool consists of disjoint unit pairs, an even number
of normal triples and one fresh link. It has exactly n members and odd n.

When `k-nu=3 modulo 4`, the sharp bound is `2n<=3k+nu-3`.
Thus, for every odd positive k-nu, the maximum n is the largest odd integer
at most `(3k+nu-1)/2`. The even-difference maximum remains open.

Read [the proof](PROOF.md), [receipt](RESULT.json),
[exception certificates](EXCEPTIONS.json), [checker](verify.py) and
[credit](CREDITS.md). No paid word, native provider, complete invoice or
new kappa is supplied. All five selected assumptions remain.

With CPython 3.12 and its standard library, from the repository root:

```sh
python3.12 -I -W error -B research/edge-matching-equality-classification/verify.py
python3.12 -B scripts/research_package.py --package research/edge-matching-equality-classification
```

Expected: `PASS_EDGE_MATCHING_EQUALITY_CLASSIFICATION`, then
`PASS_REGISTERED_RESEARCH_PACKAGE` for the registered command.

The proof reduces two exceptions to finite widths three and four. All 868
unordered bases are checked; all 357 qualifying complete pools have a
recorded proper invariant subspace. Raw rank-one scans and separate pattern
lifts agree, and all nonzero-vector orbits are checked. The normal-triple
step is also repeated. There are 37 attaining fixtures with 23133 lifted
patterns, 1050 column-triple controls, odd-triple trace/kernel controls and
an irreducible even-image control away from equality.

Independent human and formal-kernel review are unclaimed. Selected cold
replay, full predecessor package replays, native, Lean and Docker checks
were not run. The all-dimension conclusion uses the written reduction and
its explicit finite exceptional certificates.

## Open next questions

Determine the even-difference maximum, or classify the lower odd-difference
attainers. A paid-word search must first account for the existing
orthogonal-basis single-link obstruction and the complete relation lattice.
