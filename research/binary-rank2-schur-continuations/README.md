# Complete binary rank-two Schur continuations

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

**Finite exact certificate with a scoped counting proof. No new kappa.**
For every ordered pair of rank-two idempotents `P,Q` on `F2^4`, this package
supplies every next-pivot transition multiplicity and the exact number of
complete headers passing both leading guards of orders one and two.
It adds **23 continuation rows** to the seven source-specific parent rows
already covered by codyw912 / PR4735 and Mihir Srivastava / PR4689.
The classification into thirty parent orbits is MatShep / PR4762's result.
Those classifications and seven existing continuations are not new claims.

A sharp consequence of the complete table is

```text
Q = I + P:  no common first guard, hence no common full guard;
Q != I + P: at least 144 of 20160 complete headers pass both guards.
Minimum positive full-guard probability = 144/20160 = 1/140.
```

Equality occurs in exactly two simultaneous-conjugacy classes. With
`P=diag(1,1,0,0)`, their canonical `Q` rows are `(0,0,4,9)` and `(0,4,4,8)`.
Each has nine partners for this fixed P. The table below supplies their literal
split distributions and every other case. These are complete, equally weighted
`GL4(F2)` headers, not an arbitrary restricted or weighted cover.

## Exact contract and proof of coverage

For an ordered invertible header `M`, put `A=M^-1 P M` and `B=M^-1 Q M`.
A full success means that the leading principal minors of **both** matrices
at orders one and two equal one. No third or fourth minor is required.
`H(P,Q)` counts these headers out of `|GL4(F2)|=20160`.

Simultaneous conjugation bijects complete headers and preserves H. Every
rank-two idempotent is conjugate to `P=diag(I2,0)`. Its centralizer is exactly
`GL2(F2) x GL2(F2)`, preserving its image and kernel, with 36 elements.
There are 560 rank-two partner idempotents. Quotienting them by that block
action gives the thirty credited parent classes. The primary code enumerates
all 65536 binary matrices, retains precisely the rank-two idempotents and
partitions them into disjoint block orbits. The oracle independently obtains
the same complete partner domain from `M P M^-1` over all full headers.
Thus no ordered pair is omitted, including noncommuting pairs.

For a first column `a` and inverse first row `beta`, admission requires

```text
beta(a) = beta(Pa) = beta(Qa) = 1.
```

There are 120 possible `(a,beta)` splits before imposing the two guards.
Let `W=ker(beta)`. codyw912's credited intrinsic Schur recurrence gives

```text
P'(x) = Px + Pa beta(Px),  Q'(x) = Qx + Qa beta(Qx), x in W.
```

The residuals are rank-one idempotents on the three-dimensional W. Their
ordered type is the sufficient PR4735 invariant
`([u=v],[phi=psi],phi(v),psi(u))` for `P'=u phi`, `Q'=v psi`.
Its seven types and terminal split counts g, all inherited, are

| Type | 1111 | 1011 | 0111 | 0000 | 0001 | 0010 | 0011 |
|---|---:|---:|---:|---:|---:|---:|---:|
| g | 10 | 6 | 6 | 1 | 3 | 3 | 4 |

Write `N_t` for the number of first admitted splits with residual type t.
Each first split has `|GL3|=168` complete-header extensions; after an admitted
second split there are `|GL2|=6`. Consequently

```text
first-guard headers = 168 sum_t N_t,
full-guard headers H = 6 sum_t N_t g_t,
exact depths 0,1,2 = (20160 - 168 sum N_t, 168 sum N_t - H, H).
```

This is an application of the cited recurrence, not a new Schur identity.
The new work computes its complete thirty-row input, including the 23 parents
outside the earlier seven-state source ensemble. Exhausting that finite input
proves the stated sharp minimum. The complementary case also follows directly:
`beta(Qa)=beta(a)+beta(Pa)=0`, contradicting first admission.

## Complete table

Rows are binary row masks, bit j denoting column j. Canonical Q is the
lexicographically smallest row tuple in its fixed-P block orbit. Orbit size
counts partners of fixed P, not full simultaneous-pair orbits or header weights.
The `inherited` marker identifies exactly the seven PR4735 parent classes,
transported from its `diag(0,0,1,1)` convention. Their continuations retain that
source's credit even though this complete table includes them for usability.
The two ordered equality flags are kept separate.

| Q rows | Orbit | 1111 | 1011 | 0111 | 0000 | 0001 | 0010 | 0011 | H | Row credit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `0,0,4,8` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | new |
| `0,0,4,9` | 9 | 0 | 0 | 0 | 12 | 4 | 0 | 0 | 144 | new |
| `0,0,5,10` | 6 | 0 | 0 | 0 | 6 | 18 | 0 | 0 | 360 | new |
| `0,2,0,8` | 36 | 1 | 1 | 1 | 21 | 3 | 3 | 0 | 366 | inherited |
| `0,2,0,9` | 36 | 3 | 3 | 3 | 3 | 21 | 0 | 1 | 816 | inherited |
| `0,2,2,8` | 36 | 0 | 0 | 2 | 16 | 4 | 4 | 0 | 312 | new |
| `0,2,2,9` | 36 | 0 | 0 | 6 | 4 | 16 | 1 | 3 | 618 | new |
| `0,4,4,8` | 9 | 0 | 0 | 0 | 12 | 0 | 4 | 0 | 144 | new |
| `0,4,4,9` | 9 | 0 | 0 | 0 | 0 | 12 | 12 | 0 | 432 | new |
| `0,4,4,14` | 18 | 0 | 0 | 0 | 10 | 6 | 6 | 2 | 324 | new |
| `0,5,5,8` | 18 | 0 | 0 | 0 | 10 | 6 | 6 | 2 | 324 | new |
| `0,5,5,14` | 18 | 0 | 0 | 0 | 6 | 14 | 2 | 6 | 468 | new |
| `0,6,0,8` | 36 | 0 | 2 | 0 | 16 | 4 | 4 | 0 | 312 | new |
| `0,6,0,9` | 36 | 0 | 6 | 0 | 4 | 16 | 1 | 3 | 618 | new |
| `1,2,0,0` | 1 | 60 | 0 | 0 | 0 | 0 | 0 | 0 | 3600 | inherited |
| `1,2,0,1` | 9 | 12 | 0 | 32 | 0 | 0 | 0 | 0 | 1872 | inherited |
| `1,2,1,2` | 6 | 0 | 0 | 36 | 0 | 0 | 0 | 0 | 1296 | new |
| `1,4,4,0` | 36 | 3 | 3 | 3 | 3 | 0 | 21 | 1 | 816 | inherited |
| `1,4,4,1` | 36 | 0 | 0 | 6 | 4 | 1 | 16 | 3 | 618 | new |
| `1,6,0,0` | 9 | 12 | 32 | 0 | 0 | 0 | 0 | 0 | 1872 | inherited |
| `1,6,0,1` | 9 | 0 | 12 | 12 | 4 | 0 | 0 | 8 | 1080 | inherited |
| `1,6,0,6` | 18 | 4 | 4 | 4 | 0 | 2 | 2 | 20 | 1080 | new |
| `1,7,1,0` | 18 | 0 | 12 | 12 | 0 | 6 | 6 | 0 | 1080 | new |
| `1,7,1,6` | 18 | 0 | 0 | 8 | 0 | 6 | 6 | 12 | 792 | new |
| `4,8,4,8` | 6 | 0 | 0 | 0 | 6 | 0 | 18 | 0 | 360 | new |
| `4,9,4,13` | 18 | 0 | 0 | 0 | 6 | 2 | 14 | 6 | 468 | new |
| `4,10,4,0` | 36 | 0 | 6 | 0 | 4 | 1 | 16 | 3 | 618 | new |
| `5,10,0,0` | 6 | 0 | 36 | 0 | 0 | 0 | 0 | 0 | 1296 | new |
| `5,11,0,5` | 18 | 0 | 8 | 0 | 0 | 6 | 6 | 12 | 792 | new |
| `6,11,13,6` | 12 | 0 | 0 | 0 | 0 | 9 | 9 | 12 | 612 | new |

[RESULT.json](RESULT.json) contains the same generated table, all three depth
counts, a concrete `(a,beta)` witness for every nonempty cell and source hashes.
No receipt or table entry was handwritten.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/binary-rank2-schur-continuations/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/binary-rank2-schur-continuations/oracle.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/binary-rank2-schur-continuations
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/binary-rank2-schur-continuations --check-source-history
```

Any CPython 3.12 installation can replace the displayed local interpreter.
VERIFY.json registers both scripts in warning-strict normal and optimized
modes, with separate 120-second limits. Direct runs write only to stdout.
Regenerate a receipt outside the checkout with `verify.py --emit`; compare it
with the committed RESULT.json. The receipt binds all six other package files.

The packed primary checker enumerates intrinsic splits. The independent dense
oracle imports neither primary nor predecessor code. It enumerates all 20160
actual headers for each of the thirty parent representatives, for **604800
parent/header pairs**. It evaluates the two leading minors directly, without
using the terminal g table or recurrence to count full successes. It also
independently constructs literal block Schur residuals at all **900 distinct
admitted representative splits**, comparing every transition cell and witness.
It checks complete disjoint orbit coverage using dense conjugation.

Five rejection controls cover changed first-guard count, changed full-guard
count, changed transition count, changed orbit size and a singular inverse.
The primary checks residual rank/idempotency, complement membership, ordered
type distinction and exact nonnegative depth mass. Explicit exceptions remain
active under `-O`. Publication validation and hosted CI state are recorded in
the PR; hosted success is not inferred from a local run.

## Scope and credit

The question is Open next question 1 of MatShep's
[PR4762](https://github.com/CrocSwap/integer-mult-bounds/pull/4762), exact
`3b4e0449262b0b1e07b80e009ef71cc0ca5bf816`,
[complete factor invariant](../idempotent-factor-invariant/README.md).
The recurrence, terminal invariant, terminal g values and seven original
continuations are codyw912's
[PR4735](https://github.com/CrocSwap/integer-mult-bounds/pull/4735), exact
`4afbea22e79e19d1d65702eb4090d454ee39d967`,
[Schur transitions](../schur-invariant-transitions/README.md).
Mihir Srivastava / `mihir-s-05`,
[PR4689](https://github.com/CrocSwap/integer-mult-bounds/pull/4689), exact
`3a72fbad148294aa9ca7f900a48dbb10e64232be`, supplies the earlier seven-state
and source-specific guard numbers. Their scientific suites were not replayed.
The new enumerations are needed to produce the extended table, not an audit
or independent-review deliverable for any predecessor.

Nick Petalas's older [PR4915](https://github.com/CrocSwap/integer-mult-bounds/pull/4915)
counts general stabilizer fibers but leaves split incidence open; its formula
is not used. The older [PR4817](https://github.com/CrocSwap/integer-mult-bounds/pull/4817)
counts only the first generic binary pivot, not its successor distribution.
Its quarter-law is background; this result supplies complete two-guard
continuations. Credit codyw912's inclusion/observation lineage, ssafwann's
Schur/header work, Ryanson Jonathan, lee-phys, Cinna Davis and the retained
normalizer sources. Classical binary elimination, idempotent conjugacy and
orbit-stabilizer methods are background.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
The selected binding orientation passed for PR6030 at `781451/250000000`.
That command authenticates metadata only. The formal-interface-lemma card is
explicitly changed to this finite algebraic side result. The
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370194)
followed live handoff, recent-account, reservation and main/merged searches.
A cached refresh covered 506 open PR bodies, 6500 Discussion records and all
8917 tracked local notes at the base. Arbitrary historical diffs and unpublished
work remain unsearched. Search absence is not proof of novelty.

This is restricted to two rank-two idempotents on F2^4 and complete equally
weighted headers. Larger dimensions, odd fields, restricted covers, header
selection/emission, physical reads, dirty restoration, native alignment,
stock, precision/tape and the complete paid consumer are outside the result.
It does not furnish a native supplier, a useful physical header cover or a
complete multiplication theorem. All five selected framework assumptions
remain. No selected cold replay, Lean, Docker or formal proof-kernel run is
needed or claimed. Family decision: finish this finite table, then stop.

## Open next questions

- Can factor-data invariants give these transition rows without enumerating
  binary 4x4 partners? Start with an incidence derivation of the two sharp
  1/140 rows, keeping all ordered terminal types. A scalable symbolic
  successor law is still missing.
- Can an actual caller exploit simultaneous-header probabilities after every
  cost is charged? First pin a producer's payload field and two independent
  rank-two requests, then specify selection, emission, access and restored
  outputs. This finite algebraic certificate supplies none of that physical
  contract or the odd-field transfer.

## Implementation limits

Both scripts have acyclic direct calls, no recursion, executable source loading,
network access, subprocesses or solver. The primary matrix domain has 65536
members, block group 36 and at most 120 legal split pairs per parent. All
linear algebra has dimension at most four. The oracle considers exactly
15*14*13*12=32760 candidate ordered distinct columns, retaining 20160 full
headers. It holds at most those headers, 560 projector matrices and 120 split
entries for one row. Functions remain below 60 physical lines.

Power of Ten rule 3 deviation: Python integers, tuples, dictionaries and JSON
allocate dynamically during these bounded finite checks. The dimensions,
header inventory and package input sizes bound the retained state; the oracle
checks those capacities and both scripts release their local state on exit.
No fixed-pool runtime implementation is claimed. A fixed-capacity native
replacement would be required before making that claim. Warning-strict normal
and optimized execution and in-memory syntax inspection provide diagnostics;
no separate unavailable type checker, linter or proof kernel is claimed.
