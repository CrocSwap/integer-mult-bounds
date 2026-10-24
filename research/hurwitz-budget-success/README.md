# Sharp Hurwitz budget versus simultaneous success

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with exact finite corroboration.** For ten independent uniform
b-bit inputs in the fixed-support Hurwitz message model, the exact maximum
probability that every receiver decodes correctly at integer charge budget C is

    P_max = 2^(-max(0, 5b - floor(C/2))).

Each receiver knows its orthogonal mate's input. Messages may be arbitrary
nonlinear functions of their fixed source inputs, but supports and widths are
fixed, and every bit pays its inherited reader/source pairing rank. The
[proof](PROOF.md) also establishes the abstract matching-tariff formula with
5 replaced by any positive pair count m. It covers independent random coins
when every fixed-coin realization respects the same fixed-width budget.

At b=1, budgets 0 through 10 have exact optimum probabilities

    1/32, 1/32, 1/16, 1/16, 1/8, 1/8, 1/4, 1/4, 1/2, 1/2, 1.

Saving one unit below the zero-error floor already forces simultaneous failure
probability at least 1/2. A partial mate-parity code attains every step. This
is a sharp decoding-error extension, not a new supplier or kappa improvement.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/hurwitz-budget-success/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/hurwitz-budget-success/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/hurwitz-budget-success
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/hurwitz-budget-success --check-source-history
```

The marker is `PASS_HURWITZ_BUDGET_SUCCESS`. `RESULT.json` is a generated
receipt bound to the proof, verifier and metadata hashes. Direct replay checks
the entire receipt without modifying any file. `--write NEW_EXTERNAL_PATH`
generates a new receipt after all calculations; it never overwrites a receipt.

The first fixture exhausts every one-bit Boolean full broadcast on two mate
pairs. It constructs the receiver-observation conflict graph, computes exact
maximum independent sets for all 65,536 induced graphs, and then constructs
and literally executes optimal receiver decoders for all 65,536 encoders on
all 16 inputs. This is independent optimization of success sets, not a replay
of the theorem's formula or a predecessor's numbers.

The attaining-code census executes all input tuples for m=1,...,5 and b=0,...,3
with 2mb<=12, at every integer budget 0,...,2mb+2. The code sends selected
pair-coordinate parities and decodes all receivers. Controls distinguish
upward rounding of odd budgets, independent guesses instead of mate guesses,
omitted parity, conflicting successful inputs and invalid parameters. A
correlated-input boundary example succeeds with zero charge and explains why
input independence matters. Counts and the complete encoder histogram are in
the generated receipt. The written proof supplies the all-width result.

## Scope and predecessor credit

Alexander Templeton's merged [PR785](https://github.com/CrocSwap/integer-mult-bounds/pull/785)
supplies the fixed-support nonlinear model and zero-error transcript argument.
Douglas R. Colkitt's [PR703](https://github.com/CrocSwap/integer-mult-bounds/pull/703)
supplies the Hurwitz matching geometry, tariff and transversal accounting,
following Joel Pulikkan's [PR620](https://github.com/CrocSwap/integer-mult-bounds/pull/620).
Jerry Chen's [PR912](https://github.com/CrocSwap/integer-mult-bounds/pull/912)
treats paid adaptive headers and expected zero-error charge. It is a separate
boundary, not an input to this proof. Historical proofs are pinned as
provenance in `SOURCES.json`; no predecessor verifier or geometry is replayed.
No priority is claimed for the general successful-subset counting method.

Only the decoding-error premise changes. Uniform independent inputs, fixed
supports and widths, mate-only free side information, and additive per-bit
pricing remain essential. Expected-charge budgets, adaptive routing,
interactive relays, correlated inputs and additional side information are
outside scope. Physical encoding, decoding, cleanup, hosting and tape costs
remain unknown; no native operation is installed. There is no selected-frontier
change or complete multiplication theorem. Independent human and formal
proof-kernel review are unclaimed.

This is a changed-scope side result under `complex-rank-shape-decoder`.
The card's 5% supplier ceiling acceptance gate is not claimed passed. The
family expansion decision is to finish this sharp obstruction and stop;
no dependent construction campaign or selected cold replay is justified.
The base is `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.

## Open next questions

The structured questions in `TASK.json` concern individual receiver errors
and unequal paired widths. For the first, start with exact achievable error
vectors on two one-bit mate pairs. For the second, start with widths
(1,2,1,1) on two pairs. The present joint-success theorem and uniform
transversal dimensions do not settle these questions.

## Code verification limits

The verifier uses structured, nonrecursive loops. Its exhaustive Boolean
tables have 65,536 entries; literal witness inputs have at most 12 bits.
Managed Python allocations are an explicit Power of Ten deviation: lists,
integers and temporary tuples allocate during the scan, with live memory
bounded by those fixed domains. No callback dispatch, subprocess, network,
external source import or generated code occurs. Every function is under
60 physical lines. Checks use explicit exceptions and remain active under
optimized Python. Warning-strict normal and optimized execution are registered.
