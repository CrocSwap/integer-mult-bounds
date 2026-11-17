# Sharp two-for-one terminal exchange

Scoped written proof with exact finite corroboration, produced by Nick Petalas.

In the binary terminal-rank relaxation with n unmarked arrivals, b base marked
directions, s singleton marked directions and at most h changed unmarked
arrivals, the universal stock bound min(b+s,b+2h) is sharp for every even b.
One three-vector exchange earns two independent marked differences while
changing one unmarked arrival. Fixed libraries suffice for every budget.

For the synthetic 523+22 shape with b=12 and s=10, five changed unmarked
arrivals attain stock 22 and preserve terminal rank 545. The construction also
respects the base support partition 3+3+2+4. Consequently the dimension-only
argument in [ToikY #7258](https://github.com/CrocSwap/integer-mult-bounds/pull/7258)
cannot raise its five-arrival necessary condition. An obstruction beyond it must
use actual source libraries, donor projections, scheduling or costs.

These are synthetic libraries. No claim of stock 22 on the literal BIT word,
physical delivery, native admission, complete multiplication theorem or new
kappa follows. The selected frontier and its five assumptions are unchanged.

The [proof](PROOF.md) defines the relaxation, credits the predecessor upper bound,
and proves attainment. The standalone verifier constructs endpoints, checks full
rank and quotient rank, and exhausts every assignment in ten small singleton
models with an independent span oracle. It generates a receipt with source
hashes. No predecessor scientific verifier runs.

Local CPython 3.12.15 verification covers 825 small construction cases, six
545-dimensional witnesses and all 26,286 assignments in the ten complete models.
Four mathematical controls and three invalid-parameter controls pass.

## Reproduce

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error scripts/research_package.py --package research/bit-terminal-two-for-one
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/bit-terminal-two-for-one/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bit-terminal-two-for-one --check-modes --check-source-history
```

Registered normal and optimized checks have 120-second bounds. Direct verification
prints its generated hash-bound receipt. An optional `--receipt` path must be
outside the checkout. Runtime needs only the standard library and package files;
the source-history check additionally needs full Git history.

## Open next questions

Determine whether funded changed paths or expanded marked libraries can realize
even one three-vector gadget with the required shared U component and quotient
projection. Concurrent [#7260](https://github.com/CrocSwap/integer-mult-bounds/pull/7260)
studies actual old-source donor constraints, unlike this maximal-library relaxation.
Use its source-pinned donor map as a cited starting point rather than repeating
its census. A legal paid schedule, joint endpoint, ownership, restoration and
the complete invoice remain separate obligations.
The structured question is in [TASK.json](TASK.json).

## Credit and source context

The new exchange, sharpness theorem and verifier were produced by Nick Petalas.
Credit ToikY's #7258, exact head `90a63fbefcf79c3e0c0453ef0741dff8517b6167`,
for the 12+2h upper bound, singleton/base partition and altered-unmarked-arrival
route. Its census and prices are cited inputs, not deliverables rechecked here.
Credit Jerry Chen / CubeJerry #7001/#6726 and their retained contributors for the
BIT word motivating that route, and Clear1nsight #7244 for its complete comparison.
Binary elimination, rank-nullity and direct sums are classical methods.

[SOURCES.json](SOURCES.json) records immutable main provenance and the exact public
predecessor path and hash. There are no external runtime inputs. Independent human
and formal proof-kernel review are unclaimed. New work is Apache-2.0.
