# Forward B/C input-gauge thresholds are 31 and 23

Claim type: scoped written proof with exact finite corroboration. This
contribution was produced by Nick Petalas. No new kappa.

Allow a forward seven-axis B/C whole call a free odd power of its central
Gaussian on at most q of its 224 main input fields. Retain its cited paid
profile, separate helpers and the ordinary coordinate caller contract.
The exact maximum of its integrated sign-cut capacity is

    K_B(t,q) = K(t) + d*(a(q)+b(q)),
    K_C(t,q) = K(t) + ((1+d)/2)*a(q) + d*b(q),

where 0<t<1, d=8^t-7^t, K(t)=28+140*7^t+84*8^t,
a(q)=min(q,56), and b(q)=min(56,floor(max(q-56,0)/2)). The budget is
an upper bound. Gauge exceptional pairs first, then both inputs of A
pairs. Single-input A gauging loses capacity.

At saving 17/5000, one whole B call's optimistic signed bill is still
negative with 30 such free gauges; 31 is the first positive upper bound.
For C the corresponding budgets are 22 and 23. The last failing and
first passing margins are:

| Type | Last failing margin | First passing margin |
|---|---|---|
| B | q=30: (-0.582842,-0.582841) | q=31: (0.406957,0.406958) |
| C | q=22: (-0.771171,-0.771170) | q=23: (0.223728,0.223729) |

These thresholds are exact for this capacity relaxation. A positive
upper bound does not construct independent productive outputs. Gauges
are counted at every call occurrence, including reused prepared fields.
For mixed calls the complete bound is the sum of each call's capacity
gain minus its cited ungauged deficit. There is no universal integer
per-call threshold for such mixtures.

[PROOF.md](PROOF.md) gives the complete 12-choice local classification,
the optimal allocation, the all-caller implication under the stated
contract, and the exact threshold certificates. This takes the
odd-input-gauge direction in Open next question 2 of unpaidmoon's
[PR6639](https://github.com/CrocSwap/integer-mult-bounds/pull/6639).
Ali Romman's [capacity theorem](../complementary-caller-capacity-gate/PROOF.md)
and its paid/helper profiles are cited inputs. Their native producer,
counts and scientific suite are not replayed.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -X dev -W error -B research/bc-central-input-gauge-budget/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -X dev -W error -O -B research/bc-central-input-gauge-budget/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bc-central-input-gauge-budget
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bc-central-input-gauge-budget --check-source-history
```

Another CPython 3.12 path can replace the displayed local interpreter.
Direct replay emits a freshly generated JSON receipt with package hashes
and `PASS_BC_CENTRAL_INPUT_GAUGE_BUDGET B=31 C=23 no_new_kappa`.
It writes no files. The registered hook runs normal and optimized modes.

The checker enumerates 384 literal rational matrix rank cases, 3,072 sign
mask cases and 29,700 complete-budget comparisons against a separate
dynamic program. The written proof supplies the continuous exponent
quantifier. Integer-power inequalities certify the numerical margins;
Decimal arithmetic only proposes endpoints. Controls distinguish B and
C, one and two A gauges, and reject an undercharged A option.

## Scope and credit

Only forward A/B/C main blocks with central input gauges are covered.
The assumed helper contract must survive any actual producer change.
Output gauges, changed axes, inverse/transposed placements, shared
helper/main resources and different native profiles require new work.
No physical gauge producer, profitable caller, supplier admission,
compiler/hosting/precision/tape theorem, selected cold replay,
independent human review or proof-kernel review is claimed. The selected
frontier and all five framework assumptions remain unchanged.

Base main is 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8.
The baseline resolves selected #6030. Source pins are in
[SOURCES.json](SOURCES.json), and the exact original card and scope change
are in [TASK.json](TASK.json). No predecessor package is modified.

Credit Ali Romman for the capacity proof and retained P/H profiles;
unpaidmoon for PR6639's question; Dugongue, Cao Yifan/intqwq, Chris
R/Clear1nsight and the retained B/C source lineage. Dugongue's
[constructive gauge incidences](../fine-gap-gaussian-boundaries/consumer.md)
and fully priced alternating schedule concern a different question.
The local capacity classification, budget optimum and threshold
certificates are the new step here. Apache-2.0.

## Open next questions

Can a source-compatible producer supply the required odd-gauged main
inputs for less than their separate H1 fees, while retaining the exact
independent helper targets? First exhibit one all-input producer and
its full preparation/restoration bill, then insert its actual gauge
occurrence budgets in the proved envelope. Charging one H1 per gauge
already consumes more than its capacity gain. A favorable capacity
bound alone does not justify another caller search.

## Verification design

Build the Lever led to the independent finite-budget optimizer. Prove It
Works led to literal matrix and sign-mask computations and exact integer
power checks. The Autonomous local run playbook stops at this first
verified scope; no larger mechanism is claimed.

Power of Ten review covers verify.py. All functions have fewer than 60
lines and no recursion. Mathematical domains are fixed at 12 choices,
256 masks, 112 pairs and 225 budget states. The power checks use eight
fixed ranks, denominator 5000 and scale 10^12. Exception-based checks
remain active under optimized Python. CPython, Fraction, Decimal, JSON
and integer arithmetic allocate dynamically, a rule 3 deviation; these
fixed domains and a 16 MiB cited-source limit bound live state. The
only persistent output is stdout. Warning-strict development-mode
normal and optimized runs provide the available interpreter diagnostics.
