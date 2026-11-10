# Integral Fourier squares lower the D16 spinor cap to 316

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped mathematical proof with exact finite corroboration.**
Every antipodal binary length-sixteen code whose nonzero distances belong to
`{2,6,8,10,14,16}` has at most **632 words, or 316 antipodal pairs**.
Consequently, the roots-plus-spinors family of DreamingOfClouds's
[PR2244](https://github.com/CrocSwap/integer-mult-bounds/pull/2244) has at most
**240 + 316 = 556 lines**, improving its upper bound of 557 by one.
Attainment of 316 spinor lines is not asserted.

The new step answers the integrality question in Nick Petalas's older
[PR5206](https://github.com/CrocSwap/integer-mult-bounds/pull/5206).
Its real two-point optimum and dual identity are cited predecessors.
No predecessor scientific executable is imported or replayed. The new proof
uses the fact that, with 317 antipodal pairs, every even-weight character sum
is twice an odd integer. Its square is at least four. The inherited weighted
dual identity then requires the same sum of squares to be both at least
146,992 and exactly 116,656. The contradiction gap is 30,336.
[PROOF.md](PROOF.md) gives a self-contained derivation.

## Reproduction and evidence

From the worktree root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/spinor-integral-cap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/spinor-integral-cap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/spinor-integral-cap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/spinor-integral-cap --check-source-history
```

Another CPython 3.12 path may replace the local interpreter path. The direct
checker prints a generated receipt bound to all six package files, followed by

```text
PASS_SPINOR_INTEGRAL_CAP spinor_lines=316 roots_plus_spinors=556 gap=30336 no_new_kappa
```

The checker enumerates all 20,998 character masks at weights two, six and eight.
Literal character evaluation corroborates the seven entries of the weighted
kernel table, separately from its binomial calculation. It checks 25,440
possible sign counts for odd pair counts up to 317. Fifteen actual small
antipodal codes supply 314,970 character evaluations and 320 ordered pairs;
167,984 of those character evaluations have odd pair count. These fixture
families overlap and are not a census of codes of size 634.

Seven rejecting controls cover altered dual coefficients, forbidden distance,
duplicate words, out-of-range words and missing antipodes. Three further
discriminators show why even pair counts, missing antipodality and omission of
the square's factor four do not give the contradiction. Every check remains
active under optimized execution. No receipt is hand-written or stored.

The universal code-size bound follows from the written parity argument and
character identity. Finite execution corroborates those identities and arithmetic;
it is not an enumeration of all large codes or a formal proof-kernel check.

## Scope and credit

PR2244 supplies the D16+ roots-plus-spinors distance model and original
317-spinor-line cap, with its PR2228, PR2125, PR968 and lattice/decoder lineage.
PR5206 supplies the exact antipodal real relaxation and its three-multiplier
dual identity. Both remain unchanged and retain their credit. Classical
character orthogonality, Krawtchouk polynomials and parity refinements of code
bounds retain their credit; no general literature-priority claim is made.

This is a geometric side result under `complex-rank-shape-decoder`, with the
scope change recorded in TASK.json. The current selected-baseline binding
command passed at selected PR6030, kappa `781451/250000000`. No physical
decoder, compensation, native realization, routing, restoration, compiler,
precision/tape, stock, supplier admission or new kappa follows. The five
selected framework assumptions remain. Independent human and formal
proof-kernel review are unclaimed. Selected cold replay, Lean and Docker are
unrun. This package stops at the first proved improvement.

## Open next questions

Can the even pair count 316 be excluded or attained? Its even-weight character
sums can vanish, so the odd-pair square floor used here does not settle it.
A first step is an integral or triple-distance feasibility test at exactly
632 words, before a larger construction search. Neither that test nor a
632-word construction is supplied or reserved. TASK.json records the relevance
and blocker.

## Verifier resource contract

The verifier has no arguments, recursion, subprocesses, network access or
predecessor imports. It enumerates at most 65,536 candidate masks, stores
20,998 selected masks and uses at most eight words in each positive code
fixture. Each helper accepts at most sixteen fixture words. Nested bounds are
explicit; no code space is searched. All functions are under sixty lines.
Receipts read six fixed regular files, each at most 1 MiB, one at a time.
Warning-strict normal and optimized runs provide interpreter diagnostics;
repository-wide configuration is unchanged.

Power of Ten rule 3 has a managed-runtime deviation in `verify.py`: Python
allocates exact integers, tuples and dictionaries during checking. The fixed
domains above bound live state, and receipt buffers are released after each
file. A fixed-buffer port is the follow-up if allocation-free execution is
required. No unbounded service, callback dispatch or dynamic code generation
is introduced.

## Overlap and provenance

The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19372180)
records the target before packaging. Live handoffs, active Discussions, open
PRs, recent account work, main README formulas and merged spinor work were
searched. PR5206 was published October 23, outside the seven-day restriction.
It is the question's source; no other active local reservation used that source.
Main and merged searches found the predecessor cap and real optimum, with no
identified 316-spinor-line bound. Sparse notes, arbitrary historical diffs and
unpublished work remain search limits. SOURCES.json binds the two predecessor
notes and the historical task/selected context to canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
