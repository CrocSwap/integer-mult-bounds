# Exact helper capacity under odd-denominator budgets

Scoped written algebraic proof with exact finite corroboration, produced by
Nick Petalas. For a dyadic helper-cut pairing K with positive odd Smith
factors h_1 | ... | h_r and prescribed positive odd integers a,b,

```text
max { t : X K Y=I_t, aX and bY dyadic } = #{ i : h_i divides ab }.
least common odd denominator for t channels = product_p p^ceil(v_p(h_t)/2).
```

Every feasible common denominator is a multiple of the displayed integer.
This extends Ali Romman's [#5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615)
dyadic-only boundary, the case a=b=1. It measures the finite exact-division
debt needed to remove that obstruction. These are denominator divisibility
budgets, not numerical denominator-size or norm budgets. No new kappa,
physical supplier or selected-frontier change is claimed.

For factors (1,27,675), the exact common-denominator thresholds are 1,9,45.
A common denominator 15 still admits just one channel. Budgets (9,3) admit
two and (9,75) admit three. [PROOF.md](PROOF.md) proves the criterion in every
finite rectangular dimension with a prime-local kernel argument and explicit
attaining maps. [capacity.py](capacity.py) validates a supplied dyadic Smith
chart and constructs those maps and a prime obstruction.

## Evidence and reproduction

The [verifier](verify.py) checks non-diagonal dyadic charts, every pair from a
finite budget menu, least-common-denominator attainers and indispensable primes.
A separate exhaustive residue-ring factorization oracle searches right factors
and every left row modulo 9. Complete scalar searches include deeper prime
powers at 3 and 5. A control excludes a two-channel boundary missed by
determinant divisibility alone. Invalid charts, budgets and altered witnesses
must reject. No predecessor scientific code or census is imported or rerun.

Run from the repository root with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/odd-budget-helper-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/odd-budget-helper-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/odd-budget-helper-capacity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/odd-budget-helper-capacity --check-source-history
```

Another CPython 3.12 path may be substituted. The verifier prints a computed
JSON receipt with `PASS_ODD_BUDGET_HELPER_CAPACITY`, counts and SHA256 hashes
of all eight package files and its declared proof input. It writes no files.
The runner prints `PASS_REGISTERED_RESEARCH_PACKAGE`; the committed-byte
preflight prints `PASS_RESEARCH_COMMIT_BYTES`. Checks remain active with `-O`.
Exact measured coverage and local command times are in the PR body.

[SOURCES.json](SOURCES.json) binds the catalogue, selected record and credited
proof input to base e54523517d0f03e58352e647c403a5af3e525a57. The catalogue
context is older than selected #7000; the source-bound baseline was used for
orientation. The changed card scope is in [TASK.json](TASK.json).

## Limitations

The universal theorem has a written proof. The executable accepts supplied
Smith charts with at most six rows/columns, 256-bit dyadic input entries and
positive odd factors and budgets below 2^20. It does not compute Smith charts.
Runtime bounds and deviations are in [SAFETY.md](SAFETY.md).

This supplies no actual selected prefix/suffix modules, physical carriers,
common charts, legal productive-target completions, dirty restoration or an
implementation of the odd divisions. Basis synthesis, coefficient magnitude,
precision, storage, movement and the complete paid/target and outer invoice
remain unpriced. The five framework assumptions retain their status. Selected
cold replay, native execution, Lean and Docker were not run. Independent human
and formal proof-kernel review are unclaimed.

## Open next questions

1. At one named source cut with a failed dyadic pairing, what odd denominator
   is necessary and implementable under its exact scalar service? Extract full
   saturated modules and a Smith chart first, then price the boundary maps and
   restore every arbitrary input. Source availability and the complete physical
   bill are the missing obligations.
2. Can an attaining boundary satisfy a prescribed coefficient norm or growth
   bound? Begin with the three-factor example and a stated norm budget.
   Denominator feasibility alone supplies no magnitude guarantee.

## Credit and scope

The new bounded-denominator criterion, maps, prime-power proof and checker were
produced by Nick Petalas. Credit Ali Romman #5615 for the helper-cut interface,
#5599/#5602 helper splitting, #5609 pairing, #5611 completion, Nick Petalas #5115
row preparation and their retained native/controller/compiler lineage. Smith
normal form, localization and valuation arithmetic are classical. No
literature-wide priority for these methods is claimed. New work is Apache-2.0;
predecessor files and credit are unchanged.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19542451).
