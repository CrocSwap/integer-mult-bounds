# Chronological width in the multiplicative rank

For the fixed default-height chronological compiler of
[codyw912's PR #4638](https://github.com/CrocSwap/integer-mult-bounds/pull/4638),
let d count primes dividing target or paid ranks, and let r be the rational
rank of their prime-valuation vectors. The same width sequence satisfies

```
Previous upper bound: log B_N = O((log N)^(d+1))
New upper bound:      log B_N = O((log N)^(r+1)),  r <= d.
```

This answers the exponent-lattice refinement in #4638's first Open next
question. A projection to r independent prime coordinates is injective on
the rank semigroup. Its selected-prime exponent box therefore bounds the
number of source-count plateaus. [PROOF.md](PROOF.md) gives the quantified
argument and the resulting explicit integer bit envelope.

This is a **scoped conditional all-rank proof**, with finite exact
corroboration. It changes neither the compiler nor its width sequence.
It gives a strictly smaller upper-bound degree when r<d; it does not prove
that either bound is tight. No new leaf exponent or kappa is claimed.

For the abstract target pattern {6:1,36:1} and paid pattern {1:1,6:1},
d=2 and r=1. The proved logarithmic degree decreases from three to two.
The semigroup is exactly {6^j:j>=0}. No physical native supplier for this
pattern is asserted. The finite checker at cap 46656 finds its seven
semigroup elements. The generic selected-prime box has 16 points, and the
explicit conservative width exponent is 22464. These are different quantities.

## Evidence and scope

The independently written standard-library checker imports no predecessor
program and replays no predecessor census. It checks:

- Every one-, two- and three-element subset of {1,...,12}, at caps 1, 7, 64
  and 257, plus four larger discriminating fixtures at cap 46656.
- Exact semigroup equality between bounded generator multiplication and an
  independent integer-by-integer divisibility oracle, projection injectivity,
  the selected-prime box bound and the full-prime comparison.
- Rational elimination ranks against independent nonzero-minor enumeration
  using the Leibniz determinant formula, for every fixture.
- Thirteen rejecting controls and two further semantic comparisons, including
  a rank-deficient coordinate choice, omitting a paid-rank prime and an
  actual collision under an insufficient projection.

Executed output on CPython 3.12.15:

```
PASS_SEMIGROUP_RANK_WIDTH
fixtures=1196 enumerated_members=7641 strict_rank_reductions=186 controls=15
```

The member count sums occurrences across fixtures; it is not a count of
distinct integers across the whole run. The 186 counts fixtures with r<d.
Normal and optimized modes run the same explicit checks without Python
assertions. Finite checks corroborate the new counting lemma; the all-rank
conclusion follows from the written proof and the cited #4638 premises.
The predecessor's flow, batching policy, source bound and all-prime width
divisor are used as published results and were not audited here. Both timed
registered commands completed in about 0.13 seconds locally. Three disposable
optimized-code mutations reject: an insufficient coordinate set, omitted
semigroup products and an incorrect width charge.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/semigroup-rank-width
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/semigroup-rank-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/semigroup-rank-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/semigroup-rank-width --check-source-history
```

Substitute a local CPython 3.12 path on another machine. Each registered
check has a 120-second timeout. The direct checker works without Git or
network access and normally writes nothing. To create a new receipt, add
`--record /absolute/scratch/path/receipt.json`. It refuses to overwrite an
existing file and generates the results, interpreter version and SHA256
hashes of all six package files. No receipt is hand-written.

[SOURCES.json](SOURCES.json) pins historical source documents and task
provenance. There are no external executable or data inputs. The source
README is cited as provenance, not dynamically imported. Hosted CI and
independent mathematical acceptance are separate from local checks.

## Limitations and open obligations

This is a compiler-size side result under the precise default-height
recurrence. The selected baseline orientation passed; no selected supplier
or historical scientific replay was run. No actual selected inventory is
claimed to have r<d. Native semantics, physical allocation, dirty restoration,
fixed-tape movement, precision, stock, all-size implementation and outer
transfer remain inherited obligations. The five selected framework assumptions
and selected frontier are unchanged. Independent human and formal proof-kernel
review are unclaimed.

The proof has no generator-size limit. The executable helper bounds its
alphabet to 16 entries, each at most 1000000, and cap to 65536; the exhaustive
minor oracle is used only for at most three distinct generators. Python
allocates managed objects during execution; input capacities bound live
collections. The fixed local control table uses thirteen bounded callbacks.
No recursion or dynamic code generation is used. Warning-strict execution and
in-memory Python compilation pass; no external Python linter was available.

## Open next questions

1. Does the same multiplicative-rank refinement sharpen #4638's adaptive
   theorem after adjoining its height base M to the alphabet? First isolate
   its level-LCM count and prove the required shell bound. The changed-height
   decrement and nonemptiness hypotheses must be retained.
2. Can source valuations or actual gcd cancellation reduce the remaining
   logarithmic factor for a named default-height rule? First derive an exact
   valuation recurrence for that rule. The semigroup count alone gives no
   matching lower bound for its widths.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
No further construction or search was undertaken after this refinement.

## Credit and coordination

This contribution was produced by Nick Petalas. The new step is the
independent-coordinate counting lemma and its application to the inherited
chronological width divisor. The projection argument uses elementary
linear algebra and unique prime factorization; no historical priority for
those tools is claimed. New work is Apache-2.0.

codyw912 #4638 supplies the d+1 theorem, the bounded plateau visits and the
explicit exponent-lattice question. Mihir Srivastava #4507 supplies least
chronological batching, zxv #4436/#4483 and Jacob Alan Sussman supply the
compiler and flow, and Ryanson Jonathan and Cinna Davis retain their
credited flow/width and native-construction lineage. Mihir Srivastava #4586
and Ryanson Jonathan #4588 supply earlier growth and finite-check context.
Nick Petalas #4892 concerns global divisibility minimality for a fixed
batch library, a distinct result with no new growth-degree bound.

Base: canonical main 19fdb086ea96af9a9f87936a2b888e10af4ed810, priority
revision 8. The formal-interface-lemma card is explicitly changed to this
written compiler-size lemma, not a proof-assistant formalization. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19221421)
records the bounded target. Live open/account PRs, merged term searches,
main's README text, active Discussions and the latest handoff comments were
checked. The overlap cache searched 341 open PRs and 5519 Discussion records
with reported complete pagination, but only 214 of 8136 local note records
were materialized; separate Git searches covered omitted main README files.
This is bounded overlap evidence, not a proof of novelty.
