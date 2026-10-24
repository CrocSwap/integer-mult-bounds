# Exact nonidentity scalar-pivot header counts

This package answers the header-frequency question in Nick Petalas's
[PR #4785](https://github.com/CrocSwap/integer-mult-bounds/pull/4785).
It gives exact complete-header counts for every nonzero common scalar pivot,
including the three-shift generic case and both shift-collision cases.
The named F5 caller has 442368000 sharp splits at H=J2(3), and 42577920000
sharp splits over its full profile. Each split has |GL5(F5)| completions.

[PROOF.md](PROOF.md) states the ensemble, weights, proof and predecessor
credit. [counts.py](counts.py) evaluates the exact law. [RESULT.json](RESULT.json)
records the checks and full integers. The actual F4 split/Schur oracle checks
4032 pairs and gives 4860 complete headers, with probability 3/112.
Five nonidentity matrix contexts include F4 and F8. The generic q=4,d=12
case uses 455 strata for a space of 2^288 compressed matrices.

```sh
python3.12 -B scripts/research_package.py --package research/scalar-pivot-header-counts
```

Both registered Python3.12 modes print `PASS_SCALAR_PIVOT_HEADER_COUNTS`.
The checks also retain 25291 two-shift matrix cases, 11527 factor pairs,
382 product targets, five binary source comparisons and 20160 literal
binary headers. The standard library suffices. The checker verifies source
bytes and the complete typed receipt. Prime-power q and the scalar equality
class are supplied premises of the integer-only count API.

The scalar criterion, two-shift and multi-shift incidence laws, factor counts
and completion factor are credited predecessor results. This contribution
binds them to the missing nonidentity weights and the actual named caller.
It does not change kappa, price a physical cover or prove later-guard survival.
Lean, Docker, selected cold replay and full-history validation were not run.

## Open next questions

Can these exact nonbinary masses support one state-aware second Schur step?
Start with the complete F4 split domain here. Preserve the ordered residual
pair; its two matrices need not commute. A nullity-only repeated transition
is not justified. Physical selection and emission need a separate paid proof.

## Coordination and credit

Base 7c472563474e60185e6ca101a17622133d047e56, priority 7.
[SOURCES.json](SOURCES.json) pins the retained source files. The public
[multi-shift proof](https://github.com/CrocSwap/integer-mult-bounds/discussions/5261)
is also retained as an explicit predecessor. See PROOF.md for source links.

A separate general-H gluing artifact was shared as corroboration for Mihir
Srivastava's concurrent claim. It is not part of this PR. A deeper overlap
check also found that the two-shift shortcut was already complete. This
package makes no new claim for either result. Current PR and Discussion
bodies and relevant main notes were checked; arbitrary historical diffs and
unpublished work remain outside that coverage.

Ali Romman with substantial OpenAI Codex assistance in derivation,
implementation, review and verification. Apache-2.0. Source notices remain
unchanged. Independent human and proof-kernel review remain open.
