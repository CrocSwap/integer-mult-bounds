# Well-conditioned positive-definite circuit counterexamples

Every failed complete dirty linear identity over Q or Q(i), with independent
operator symbols, has a counterexample using real symmetric positive-definite
contractions. The construction has dimension D+1, where D is the largest
nonzero coefficient degree. Every spectrum lies in [1/2,1], so every generator
has condition number at most 2. A rational parameter also places all generators
arbitrarily close to I. [PROOF.md](PROOF.md) gives the quantified statement.

This strengthens the negative diagnostic in zxv's
[PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235).
Conditioning or positivity alone cannot repair a false independent-symbol
identity. Native inverse, commutation or Clifford relations can still exclude
the counterexample. The complete kappa calculation is unchanged.

[witness.py](witness.py) uses exact-length reachable spaces to find a top-degree
word without expanded words. [literal.py](literal.py) separately executes every
register operation under the prescribed matrices. It retains all dirty input
and returned roles, including self-source queries. It checks negative witnesses
only. Positive certificates retain the predecessor's separate checker.

## Evidence and replay

Requires CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/spd-dirty-circuit-witness
python3.12 -I -B research/spd-dirty-circuit-witness/witness.py research/spd-dirty-circuit-witness/wrong-order.json
```

Expected registered output: `PASS_SPD_DIRTY_WITNESS` in normal and optimized
modes. [RESULT.json](RESULT.json) records exact counts and source hashes.
The replay includes 240 expanded-word differential circuits over Q and Q(i),
literal matrix actions, 96 spectral-enclosure fixtures, fifteen control groups,
and the source's complete wrong-order echo. The (X+Y)^64 stress circuit has
2^64 top words; the adapter retains small exact-length spaces and returns a
65-dimensional rational witness. Finite checks support the written proof;
no independent human or formal proof-kernel acceptance is claimed.

The package starts at main ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority
revision 7. Two vendor files and the example are frozen copies from pending
head 48976daa4dce59b4867ef046da72a370e389925d. [SOURCES.json](SOURCES.json)
records original upstream locations and pins the exact retained copies in this
publication history. The original proof and attribution are retained with the
compiler. No pending upstream Git object is required by a fresh checkout.
The first hosted replay failed before mathematical execution because that
pending Git object was absent. The source-history repair preserves all bytes
and all mathematical checks. No dependency is promoted to main.
The full-history wrapper was not run in the shallow checkout. No selected cold
replay, native/Lean/Docker run, physical implementation or kappa change is claimed.

## Open next questions

Can a specified native child family realize one such witness while retaining
its extra relations? First write its exact relations and test the labelled path
against each one. This matters because the current theorem permits independent
symbols; it does not prove failure inside a restricted native family. No such
relation-preserving substitution is supplied here. The inverse-aware frontend
claimed separately in Discussion #5236 remains outside this work.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
See [NOTICE.md](NOTICE.md) for the unchanged zxv compiler and scalar code,
classical weighted-automata/PIT credit, and retained echo/tensor lineage.
