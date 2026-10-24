# SPD witnesses with true inverse calls

Every false complete rational dirty linear identity in the named-inverse
grammar has a constructive positive-definite witness in dimension at most
r+q. Generators can be arbitrarily close to identity. Both the generators
and their actual inverses have spectral condition number at most two.
The inverse operator norms can reach two; only the generators must be
contractions. All initial and returned roles remain in the contract.

The [proof](PROOF.md) uses a nonzero coefficient word of length D from the
[retained inverse frontend](vendor/UPSTREAM-PROOF.md). Put d=D+1. Symmetric
labelled paths give a nonzero rational endpoint function. Its numerator
has degree at most L=q+ + d q-, where q+ and q- count all forward and inverse
calls in both programs. At least one of L+1 explicit rational grid points
gives a nonzero endpoint. This handles cancellation from the infinite
inverse series, which the earlier highest-degree polynomial method does
not cover.

The pinned wrong-order inverse commutator has a dimension-three witness
with epsilon=1/4 and coordinate difference -1/35. Grid examples with
1,2,4,7 roots force acceptance only at the final allowed point. The full
[receipt](RESULT.json) records independent dense checks, small reduced-word
comparisons, dirty-helper deletions, exact inverse residuals and a compact
stress circuit with 2^32 lowest-degree words.

## Replay and use

From the repository root:

```sh
python3 -B scripts/research_package.py --package research/spd-inverse-circuit-witness
```

The registered Python 3.12 checks run normal and optimized modes. From this
package directory, generate and check a concrete witness:

```sh
python3 -I -B witness.py vendor/wrong-order.json --output /tmp/spd-inverse-witness.json
python3 -I -B check_witness.py vendor/wrong-order.json /tmp/spd-inverse-witness.json
```

The expected final markers are `PASS_SPD_INVERSE_WITNESS_PRODUCED` and
`PASS_SPD_INVERSE_WITNESS_CHECKED`. Use `--epsilon-cap 1/1099511627776` to
request a smaller generator distance from identity. Equivalent programs
raise `ValueError`; this adapter only constructs negative witnesses. Use
the predecessor for a positive equality certificate.

The implementation requires Q, square common-size generators and only
true inverses of named generators. It excludes extra native relations,
inverses of operator sums, numerical detection guarantees and physical
costs. It does not change the selected frontier or the complete kappa
calculation. See [validation](VALIDATION.md) for the checks and limits.

## Source and credit

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The inverse realization, syntax and scalar code are byte-exact from
@krzysztofwojt's
[PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262), source
`6f92ccf1e61c4668c8ee687bd1df8b42932b8759`. The retained
[README](vendor/UPSTREAM-README.md) and [proof](vendor/UPSTREAM-PROOF.md)
keep the credit to @zxv, classical rational-series/Magnus/weighted-automata
methods and the earlier dirty-echo, tensor and phase work.

Ali Romman's polynomial SPD construction in
[PR #5268](https://github.com/CrocSwap/integer-mult-bounds/pull/5268) is the
nearest conditioning predecessor. The new result supplies a finite
parameter search for inverse series. It does not claim a new general PIT
algorithm or global literature priority. [SOURCES.json](SOURCES.json)
binds the retained source bytes to this branch's published ancestry and
records their original commit and path.

## Open next questions

Bind one actual inverse-bearing native word to this grammar. First pin
its source and list every input, output and extra operator relation. The
current witness respects inverse and symmetry contracts, but it need not
respect any additional native-family relations. A native adapter and a
useful lower bound on the nonzero discrepancy remain open.
