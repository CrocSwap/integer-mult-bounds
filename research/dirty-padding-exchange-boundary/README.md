# Borrowed dirty padding cannot isolate a uniform exchange

**Scoped negative result; no new supplier or kappa.** Arbitrarily dirty borrowed banks cannot replace fresh padded output
using only uniform
bank XORs, additive padding/restriction, and completed full padded exchanges.
For every aggregate rectangle `[P,Q,G,Q,S]` with `Q>=2` and nonempty binary
padding, this holds for any finite number of dirty banks and any finite word.
The program must restore all borrowed banks, including their padding coordinates.

[PROOF.md](PROOF.md) states the exact hypotheses and proves the obstruction.
On one genuine two-cycle and one padded two-cycle, group-ring determinants
count the same padded exchange calls. The desired endpoint requires different
determinants. A seven-gate swap-through-buffer word gives the correct useful
output but exchanges the borrowed padding. The proof excludes every repair
within the stated alphabet, not merely short repairs.

This is a changed ownership contract, not an error in ywz65's pending
[PR2636](https://github.com/CrocSwap/integer-mult-bounds/pull/2636). That work
explicitly requires fresh output and owned counters. Its predecessor
[PR2457](https://github.com/CrocSwap/integer-mult-bounds/pull/2457) supplies the
aggregate-padding reduction. Their completed-callee and caller-ownership
obligations remain open. Immutable head pins appear in
[PREDECESSORS.json](PREDECESSORS.json).

## Decision and scope

Do not implement a dirty-only adapter in this alphabet: it fails even when
all operations cost zero. Retain fresh ownership, or declare and price a new
operation, such as an exchange restricted to genuine cells. This reduces one
concrete interface search to a precise choice of changed assumption.

The theorem permits arbitrary uniform linear mixing within each bank type.
It grants additive scan gates; it does not claim that PR2636 implements them.
It excludes other coordinate permutations, masked exchanges, nonlinear or
payload-dependent control, erasure, and clean/disposable banks. It is not a
lower bound for arbitrary physical algorithms or recursive suppliers.
This package changes no selected construction, upstream source, or frontier.

## Reproduce and checking boundaries

```sh
python3.12 -I -B scripts/research_package.py --package research/dirty-padding-exchange-boundary
```

The primary marker is `PASS_DIRTY_PADDING_EXCHANGE_BOUNDARY`; the failure
controls print `PASS_DIRTY_PADDING_FAILURE_CONTROLS groups=4`. Python 3.15.0
also runs the standard-library code. Interpreter records accompany receipts.

The two models use different state representations and traversals:

* Literal coordinate bit matrices exhaust all reachable operators for four
  padded rectangles and one unpadded control. Each closure has 96 states and
  288 edges. No determinant or group-ring filter prunes these traversals.
  All input columns, including dirty padding, enter the matrix semantics.

* Generic bank matrices over `F2[t]/(t^2-1)` check 81 primitives, one empty word, and 160
  seeded words across six bank counts, up to two genuine and four padded
  banks. A direct Leibniz determinant checks the invariant. These are finite
  checks, not an exhaustive search for those larger bank counts.

An additional 500 shapes check the existence and invariance of the two
orbits.

The checks include a dirty basis-column counterexample, a no-padding
positive control, the `Q=1` exception, and a masked-exchange escape control.
Git-free subprocess controls reject an omitted exchange, omitted restriction,
and actual pinned-source corruption, with Python optimization enabled.

The all-length and all-bank-count statement follows from the written proof.
Finite replay alone does not prove that theorem. The two implementations
share this author; they are independent models, not independent reviewers.
We claim no human review, formal proof kernel, completed physical callee, full
selected cold replay, hosted CI pass, or multiplication theorem.

## Scope selection and prior work

OS seed 3 selected the bit-supplier track. The three candidates were PR2519's
one-buffer R439 routing bill, PR2652's mixed-width physical ports, and PR2636's
output ownership boundary. The first two already have their local identities;
this run selects the third. The source-bound card baseline passed.
[TASK.json](TASK.json) records the changed scope from the H2/K helper card;
this result is not an H2/K replacement or a supplier budget improvement.

PR677 section 4 already uses group-ring determinants for query boundaries.
This note credits that method and adds the simultaneous genuine/padding
invariant. PR679 already restores unused lanes with separate inverse calls;
that changed coordinate alphabet is outside this theorem. The larger complex
reciprocal-encoding and clean-subspace results concern different contracts.
Source hashes in [SOURCES.json](SOURCES.json) preserve the predecessor text.

Initial overlap covered 789 live open PR bodies, recent Discussion claims,
and local package notes. Later refreshes covered 775 and then 751 open PR bodies. The wider cached Discussion search is older; PREDECESSORS.json
records its coverage. No search is a novelty certificate.

## Open next questions

Can a concrete completed exchange fix the padding complement under a paid
physical contract? First name one exact callee and specify all padded cells,
head positions, scratch ownership, and caller parking. A selected physical
callee and its complete cost remain missing. A changed primitive must pass
that cost screen before further construction work.

## Credit and license

New paired-orbit argument and checks by Charles Bethin with substantial
OpenAI Codex assistance. Credit ywz65's PR2457/2636 scan lineage, commdata2338's PR677
group-ring method, Greer Guthrie's PR679 padding-restoration analysis, and
their retained predecessors. Apache-2.0. No predecessor implementation is
copied into this package.
