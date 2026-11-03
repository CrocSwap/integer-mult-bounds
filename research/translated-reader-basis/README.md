# Save 32 coefficient ADDs with a translated reader basis

This contribution is produced by Nick Petalas. Apache-2.0.
Claim type: finite explicit translation-kernel construction with a scoped
algebraic proof. No new kappa is claimed.

The actual rank-30 Gaussian reader of Ali Romman's
[PR5646](https://github.com/CrocSwap/integer-mult-bounds/pull/5646) admits this
dyadic basis change, with zero-based mode indices:

    L4 += 2 tau_258 L1,        J1 -= 2 tau_258 J4.

Here tau_258 is the XOR translation on axis bits 1 and 8. It reduces the
complete four-shear coefficient bill from 20352 to 20320 ADDs and preserves
the common denominator 960. The word still has four cross-bank shears and
thirty arbitrary exactly restored dirty coordinates. The new step escapes
the source's constant-coefficient dyadic local minimum by using a basis over
the translation ring. [PROOF.md](PROOF.md) gives the all-input argument.

The scatter support rises from 208 to 220 while gather support falls from
9968 to 9940. The exact axis-by-axis translation invoice falls from 92036 to
91924 units before return routing. Every translation application is charged.
The largest coefficient rises from 1 to 9/8; the scatter/gather infinity-norm
bounds rise to 43/16 and 72. Rational arithmetic, physical routing, precision
and the complete caller remain unpriced. A coefficient saving alone does
not establish a complete physical or recursive-cost saving.

Nick Petalas's older [PR5919](https://github.com/CrocSwap/integer-mult-bounds/pull/5919)
gives a different rational 3/40 escape costing 20344 ADDs at denominator 1200.
This construction saves 24 more coefficient instructions than that published
count while retaining denominator 960. No global optimum is claimed.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/translated-reader-basis/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/translated-reader-basis/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/translated-reader-basis
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/translated-reader-basis --check-source-history
```

Any CPython 3.12 path can substitute. Direct replay prints a generated JSON
receipt with `PASS_TRANSLATED_READER_BASIS`, actual counts and package hashes.
It writes no files. The registered replay executes both normal and optimized
commands, each with a 120-second limit. Sources are pinned by exact Git blobs
and SHA256 in [SOURCES.json](SOURCES.json). Source formulas are reconstructed
as inputs; predecessor rank, inverse, local-optimum and native suites are
not rerun as this contribution.

The replay checks the changed pair's complete kernel product, inverse basis,
untouched factor vectors, all actual coefficient/routing counts and magnitude
bounds. It executes both complete words on one dense 512-address payload,
compares every data output and dirty-bank coordinate, and rejects six controls.
The finite payload checks instruction order; the written proof covers arbitrary
inputs and any representation of the commuting translations.

## Open next questions

- Does this support and routing-unit saving survive a complete arithmetic
  backend with coefficients up to 9/8 and the larger norm bounds? Start by
  pricing both factors in the same rounded kernel, including source-layout
  return, storage and every coefficient multiplication. No such caller is
  supplied here.
- Can a translation-dependent basis improve the complete physical bill
  further? Start from this explicit changed pair and a fixed priced objective.
  The present single witness establishes no local or global optimum and
  reserves no follow-up.

Structured questions and scope are in [TASK.json](TASK.json).

## Credit and scope

Ali Romman #5646 supplies the actual factors, ten constant dyadic operations
and the explicit broader-basis question. David Ganz / Dugongue #5634 supplies
the reader substitution, four-shear identity and section conjugacy. Ali Romman
#5640 supplies the dirty-space tariff. Nick Petalas #5919 supplies the retained
factor-reconstruction code adapted in kernels.py and the earlier rational
escape. Centre-code-services, reciprocal-native-responses, native-centre-capture,
centre-metric-encoders, PR3133, PR3148, PR2588, PR2226 and their source-specific
native, numerical and compiler contributors retain credit. Predecessor files
and credit lines are unchanged. Independent human and formal proof-kernel
review are unclaimed.

Base main is 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8,
selected PR6030. This changes complex-new-helper-inventory to a scoped ordinary
reader-interface result. It does not supply new productive credit or improve
the selected recursive invoice. The binding-only first example passed. Live
PR/account lists, active Discussions, handoffs, main object/formula searches,
merged general-form searches and reservations were checked before the
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19380523).
The cache covered 626 open PRs and 6742 Discussion records; its local note
coverage was sparse. Unpublished work and arbitrary diffs remain outside
that coverage. Search stopped at the first verified translated improvement.

## Implementation and verification limits

Only this package changes. The fixed reconstruction has 112 ports, thirty
modes, 512 addresses, ten supplied basis operations and one new operation.
Each kernel vector has at most 57344 entries. All loops have these fixed
finite domains; functions stay within sixty physical lines. Exceptions remain
enabled under optimization. There is no recursion, subprocess, network use,
dynamic code evaluation or mutable global research state in the new verifier.

Power of Ten rule 3 has a managed-runtime deviation. Python requires dynamic
integers, Fractions, dictionaries and lists. Authenticated source files and
decoded JSON are bounded to 16 MiB each; kernel dimensions and payload arrays
are fixed. No fixed-allocation pool or byte-exact heap bound is claimed.
The literal word keeps one exact integer scale per shear and at most 142
arrays of 512 coordinates per logical state. A future variable-size native
backend must supply its own storage and cleanup contract. Warning-strict
normal/optimized checks and syntax inspection provide available diagnostics;
no separate static analyzer or proof kernel is claimed.

The new precision and route invoices are explicit logical bounds. Physical
layout, primitive-interior rounding, complete native/outer admission, selected
cold replay, Lean, Docker and a materialized rounded multiplier are unrun.
All five selected framework assumptions remain.
