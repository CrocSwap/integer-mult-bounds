# Two short rows cannot realize a unit coefficient in any characteristic

This contribution was produced by Nick Petalas. It extends the prime-modulus
row obstruction in [#4280](https://github.com/CrocSwap/integer-mult-bounds/pull/4280)
to every modulus, and gives a composite-characteristic family showing why the
unit-coefficient restriction matters.

Claim type: **scoped proof**, with finite executable checks. The new results are:

1. If a balanced depth-four chain word realizes a nonzero coefficient c with
   at most two short rows, each short-row length L satisfies `m | cL`.
   Equivalently, `m/gcd(m,c) | L`. In particular, every unit coefficient needs
   at least three short rows, including when m is composite.
2. For every integer t >= 1, at `m = 8t` and `c = 4t`, exactly two short rows
   suffice and the shortest word has **4m calls**. This is an infinite family,
   not an extrapolation from the finite checks.

The annihilator condition is necessary; sufficiency is not claimed. No new
kappa, supplier admission or complete multiplication theorem is supplied.

## Model and inherited criterion

The unsigned complete calls are `z_l += B_l z_(l-1)` for l = 1, 2, 3, 4.
The source x = z_0 is immutable; z_1, z_2, z_3 and y = z_4 initially hold
arbitrary dirty data. The maps B_l are arbitrary, with coefficients in a
nonzero unital ring of exact characteristic m. The word must restore the
intermediates and add `c B4 B3 B2 B1 x` to y. Each call is fully charged.

A balanced word uses each call exactly m times. The inherited interval-count
criterion of [#4249](https://github.com/CrocSwap/integer-mult-bounds/pull/4249)
gives a floor of 4m for every nonzero c. This package uses #4280's row model:

- The partition lambda lies in the m by m box and describes the 2/3 path.
  Its row lengths are L_q in nonincreasing order.
- The nonincreasing profile rho records the levels of the m calls 1.
- The nonincreasing profile beta records the levels of the m calls 4.
  Set `B(L) = beta(1) + ... + beta(L)`, with `B(0) = 0`.

Every such triple of profiles, with entries between 0 and m, comes from a
balanced word. By #4280, Lemma 2, it is correct exactly when

```text
sum L_q = sum rho_q = sum beta_p = 0                         (mod m),
sum rho_q L_q = sum B(L_q) = 0                              (mod m),
sum rho_q B(L_q) = -c                                      (mod m).
```

A short row has `0 < L_q < m`. Full and zero rows drop out of all displayed
congruences involving L_q, because `B(m) = sum beta_p = 0 (mod m)`.
They may still affect `sum rho_q`. These statements are inherited tools,
not new results or a re-verification of #4280's witness tables.

## Proof of the annihilator obstruction

With no short rows the target coefficient is zero. Exactly one short row
contradicts `sum L_q = 0 (mod m)`. With exactly two, let their lengths be
L_1 >= L_2 and their rho values be r_1 >= r_2. Their lengths satisfy
`L_1 + L_2 = m`, since each is strictly between 0 and m. The inherited
congruences reduce to

```text
(r_1 - r_2) L_1 = 0,
B(L_1) + B(L_2) = 0,
c = -(r_1 - r_2) B(L_1)                                   (mod m).
```

Multiply the first identity by `-B(L_1)` and use the third to obtain
`c L_1 = 0 (mod m)`. Since `L_2 = m - L_1`, also `c L_2 = 0 (mod m)`.
Writing `g = gcd(m,c)` and cancelling g in the integer divisibility relation
gives `m/g | L_i`. If c is a unit, this forces `m | L_i`, contrary to the
definition of a short row. This proves the result for every modulus.

For prime m every nonzero c is a unit, recovering #4280's Lemma 3 as a
special case. The new content is the all-modulus annihilator condition and
its restriction on unit coefficients in composite characteristic.

## A two-row family in every characteristic divisible by eight

Fix t >= 1 and m = 8t. Take the following profiles, padded with zeros:

```text
lambda = (m, 6t, 2t, 0, ..., 0),
rho    = (m-4, 4, 0, 0, ..., 0),
beta   = (5 repeated t times, 4 repeated t times,
          2 repeated 2t times, 1 repeated 3t times, 0 repeated t times).
```

They have m entries, are nonincreasing and lie in [0,m], because m >= 8.
There are exactly two short rows. The five sums that must vanish are

```text
sum L_q       = 16t = 2m,
sum rho_q     = m,
sum beta_p    = 16t = 2m,
sum rho_q L_q = (m-4)m + 24t = (m-1)m,
sum B(L_q)   = 16t + 15t + 9t = 40t = 5m.
```

The target sum is

```text
sum rho_q B(L_q) = (m-4)16t + 4(15t) = 16tm - 4t = -4t (mod m).
```

Thus the word realizes c = 4t, which is nonzero modulo 8t. The row-model
converse supplies a balanced word of length 4m, meeting the inherited
per-call floor. Fewer than two short rows cannot realize any nonzero target,
as proved above. Hence two is the exact minimum short-row count for this
family, and 4m is its exact minimum call count.

For example, t = 1 uses lambda = (8,6,2), rho = (4,4,0), and
beta = (5,4,2,2,1,1,1,0). Its 32-call word is
`44422222343442111133433234321111`. The verifier constructs the chronological
word from the profile definitions and checks the actual dirty action.

## Reproduce and evidence

From the repository root, using CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/depth4-two-row-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/depth4-two-row-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/depth4-two-row-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/depth4-two-row-obstruction --check-source-history
```

Any CPython 3.12 can replace the local interpreter path. The verifier imports
no predecessor code and writes no files. It prints a generated receipt bound
to every package file and live input hash, followed by
`PASS_DEPTH4_TWO_ROW_OBSTRUCTION`. It checks:

- The 64 new family words for t = 1..64, hence m = 8..512 in steps of eight.
  Every word has exactly m copies of each call, passes all ten chronological
  interval conditions and separately has UT5 product `I + c E_(1,5)`.
- Two literal dirty-register replays per word with 2 by 2 maps. The first
  two maps are a fixed noncommuting pair; the others and all initial registers
  use reproducible random data. All intermediates restore and y gains exactly
  the ordered four-map composition multiplied by c.
- Every residue triple `(L, delta, b)` with `2 <= m <= 96`,
  `ceil(m/2) <= L < m`, `0 <= delta,b < m` and `delta L = 0 (mod m)`.
  For `c = -delta b`, it checks the annihilator and divisibility conclusions
  and the exclusion of nonzero unit c. This is an algebraic relaxation;
  it does not claim the triples have realizable monotone profiles.
- Rejection of a wrong coefficient, dropped and extra calls, a changed rho
  profile and all detected action-changing adjacent swaps of the t = 1 word.

The written proofs carry the unbounded statements. The finite checks support
the construction and catch implementation or chronology errors.
The bounded algebra check enumerates 436,358 tuples, including 235,610 with
nonzero c. The replay reports 17 rejection controls. Both registered commands
ran locally in less than one second each.

## Limits and implementation constraints

This is a result about balanced unsigned depth-four words and their row-model
complexity. It does not classify all two-row nonunit coefficients, supply
three-row unit constructions, or settle the 4m conjecture for every m and c.
Admission, dispatch, routing, intermediate storage, precision, physical
compiler and recursive caller costs remain unpriced. The selected frontier
is unchanged. Independent human and formal proof-kernel review are unclaimed.

The replay has no recursion or unbounded retry. Its largest profiles have
512 entries and its largest word has 2,048 calls; the algebra loop bounds
are explicit in the code. Each function is below 60 lines. Internal and
input contracts use explicit exceptions, so optimized Python retains them.
The managed Python runtime allocates objects during the checks; fixed
allocation is unavailable here. Live storage is bounded by the fixed replay
domains and no run output is written into the checkout. A lower-level
fixed-capacity implementation is only needed if those domains become a
resource limit. Strict-warning normal and optimized replay are registered
in [VERIFY.json](VERIFY.json); no external static analyzer is required.

## Open next questions

The structured questions, relevance, first steps and blockers are in
[TASK.json](TASK.json).

1. Which nonzero coefficients admit exactly two short rows? Enumerate the
   monotone profiles for a fixed pair L and m-L. The annihilator condition
   prunes the domain but is not proved sufficient.
2. Can three short rows realize every unit coefficient for every m >= 6?
   The new obstruction proves necessity. Seek a uniform construction using
   the three-row examples in #4280 while retaining both profile budgets.

## Attribution and scope

The row model and its prime-modulus obstruction are from #4280, produced by
Nick Petalas. The chain model and interval-count floor come from #4249;
the three-interleaving formulation and the earlier depth-four witnesses
come from [#4263](https://github.com/CrocSwap/integer-mult-bounds/pull/4263).
Ross Richardson's [#943/#934 lineage](../universal-connector-boundary/README.md)
supplies the complete-call dirty-connector interface. Divisibility and
unitriangular matrices are classical tools. The new results here are the
all-modulus annihilator obstruction and the two-short-row family above.
Exact source pins are in [SOURCES.json](SOURCES.json).

The `connector-alphabet-change` card is explicitly changed to this scoped
successor question. The alphabet stays fixed. This is a small search-pruning
and construction result, with no inferred improvement to a complete supplier.
Apache-2.0.
