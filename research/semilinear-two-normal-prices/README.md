# Exact weighted tariff for two normal semilinear targets

**Scoped written proof with exact finite corroboration; no new kappa.**
For every odd prime p, two nonidentity normal targets in
F2[F_(2^p)* semidirect C_p] have exact price

    2 min(a, 2b),

when every normal call costs a>0 and every outside call costs b>0.
The theorem permits repeated target labels, arbitrary finite restored dirty
workspace and free binary scalar mixing. Paid factors are rank-one
idempotents, and the endpoint is the complete formal group-algebra operator.

This settles the two-normal-target first experiment in Open next question 1
of [Krzysztof Wojt's PR5242](https://github.com/CrocSwap/integer-mult-bounds/pull/5242).
The new step excludes three outside calls. In the quotient character,
a three-call identity forces all three binary projectors to coincide;
one shared projector cannot deliver two independent nonidentity outputs.
Four outside calls attain the target, by factoring each normal label into
two outside labels. The [written proof](PROOF.md) combines that obstruction
with PR5242's credited natural-rank budget to settle every mixture and price.
Josie Elliston's [PR6048](https://github.com/CrocSwap/integer-mult-bounds/pull/6048)
already excludes three calls for distinct pair targets in every group when
no paid label is itself a target. That prior distinct-label floor is credited.
The new quotient-loop rigidity also treats repeated labels, which PR6048
explicitly excludes, and yields the weighted tariff above. No new
distinct-pair unit-price floor is claimed. No predecessor census is rerun
as a deliverable.

## Exact finite evidence

The deterministic verifier checks the new three-factor lemma over F4 and
F8, with one to three roles. It enumerates 32,840 ordered factor pairs and
all 1,120 resulting three-factor loops; every loop has one common projector.
It also checks 4,116 literal three-outside-call words in the full order-21
algebra and 144 attaining words for all 36 ordered pairs of normal targets,
including their arbitrary third dirty role. Each full endpoint comparison
checks every formal coefficient. A 13,203-case bounded count/price screen
corroborates the written unbounded case split. Eleven rejection controls and
an explicit nonbinary three-projector counterexample check the hypotheses.
A separate direct triple loop checks all 1,728 F4 two-role triples, without
the pair/inverse lookup used by the main finite census.
The finite fields and sizes do not prove the universal quantifiers.

The verifier prints a freshly generated JSON receipt with hashes of all
package files. It writes no files and has no external runtime inputs.
[SOURCES.json](SOURCES.json) pins the original question and cited proof as
provenance, alongside the catalogue and selected record at canonical main
7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8.
The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360644)
records the target before substantial work.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/semilinear-two-normal-prices/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/semilinear-two-normal-prices/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/semilinear-two-normal-prices
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/semilinear-two-normal-prices --check-source-history
```

Another CPython 3.12 path works. The registered normal and optimized commands
have a 60-second bound each. The direct checker also runs without Git in an
export containing this package. Package and publication checks authenticate
bytes and source history separately from the mathematical argument.

## Scope and remaining obligations

This is a formal weighted tariff, not an implemented physical supplier.
Native address operations, hosting/owners, physical restoration, movement,
precision, stock/compiler and a complete recursive/outer bill are unknown.
No new kappa, selected-frontier change or multiplication theorem is claimed.
Independent human and formal proof-kernel review are unclaimed. Lean, Docker
and the selected scientific cold replay are not part of this package.

## Open next questions

- Does a joint saving become possible for three normal targets with unequal
  type prices? The three-call loop lemma does not classify longer quotient
  identities. Start with the cheapest outside-only counts allowed by the
  natural-rank inequality and prove their full formal endpoint, rather than
  treating the rank relaxation as attainable. The blocker is a longer-word
  structure theorem or an explicit sharing construction.
- Can one actual native caller realize the two-outside factorization with
  a physical price below its normal call? First price both outside maps,
  binary role changes, routing and restoration at one named boundary.
  A legal source-bound physical interface is missing.

These questions are unreserved and structured in [TASK.json](TASK.json).
The result is shipped at this first proved improvement.

## Credit

This contribution was produced by Nick Petalas. Krzysztof Wojt / PR5242
supplies the question, quotient-character method and natural-rank premise;
Nick Petalas / PR5202 supplies the normal-C7 theorem; Cinna Davis / PR2011
and PR3893 supply the semilinear model and representation precedent;
Josie Elliston / PR6048 supplies the distinct-label short-word obstruction,
building on Nick Petalas / PR6038; eumemic / PR288 and the retained
register-model lineage keep their credit.
No predecessor files or credit lines are changed. Apache-2.0.
