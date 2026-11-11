# Exact Boolean-host charge of excluded clique X0 (no κ)

Result and claim type: **exhaustive finite census** of a finite domain, together
with direct evaluation of one host. The census proves a scoped exact minimum.
It is not a heuristic search, not a signed invoice, and not a selected-frontier
change. The selected κ remains **363005817/100000000000**.

This package answers the X0 half of open question 1 in
[PR #7167](https://github.com/CrocSwap/integer-mult-bounds/pull/7167): a
coset-leader lower bound for excluded clique X0, whose supplied host has
charge 7. The minimum over the other fourteen odd 8-cliques stays open. The
degree-at-most-4 branch-and-bound suggested beside it was not needed, because
the census below covers every degree.

## Hypotheses

Coordinates are the simple-root chart `x0..x7` on `F_2^8`, with the E8 line
map of #6933 as used by #7031. The quadratic form is

```text
Q(x) = wt(x) + x0 x2 + x1 x3 + x2 x3 + x3 x4 + x4 x5 + x5 x6 + x6 x7
```

over `F_2`. The 120 root lines are exactly `{Q = 1}`. A *host* of a clique is
a Boolean function that equals the clique indicator on those 120 points. Values
on `{Q = 0}` are free. The *charge* is the number of monomials of degree at
least 2 in the algebraic normal form. Affine monomials are not counted. They
are not free parameters of the function: they still have to match the indicator.

X0 is the first excluded odd 8-clique of the #7014 partition vendored by
#7167, ports `(7, 25, 42, 52, 76, 82, 97, 127)`. The file
`data/frames.json` is those bytes, sha256
`c75915c18fc06ac19cc90fb9911209517c071862fdf401b998d5075efc0cda0d`. X0 is not
one of the 13 P104 frames, and the 104-line scope is not used.

## Theorem

Every Boolean host of X0 has charge at least 7. The indicator of the 5-flat
`a + W^⊥` has charge 7, so the minimum is exactly 7. That indicator is

```text
(1 + x0)(1 + x5)(1 + x3 + x6)
```

with charged monomials

```text
x0 x3, x0 x5, x0 x6, x3 x5, x5 x6, x0 x3 x5, x0 x5 x6.
```

These seven monomials are distinct, so the expansion has charge 7 with no
`F_2` cancellation. The same twelve monomials, affine terms included, are the
charge-7 host recorded for row 13 of #7167.

## Why the flat is a host

X0 is a coset `a + W` of a 3-dimensional subspace `W`. The polar form of `Q`
has `dim W^⊥ = 5`, and `(a + W^⊥) ∩ {Q = 1} = X0`. The indicator of that
32-point flat is therefore a host. The verifier checks the dimension, the
intersection, the factored evaluation on all 256 points, polynomial expansion,
and the subset-sum transform. It also evaluates the host on every root line.

## Why no host has charge at most 6

After the nine affine monomials are eliminated, a charged coefficient vector
`d ∈ F_2^{247}` is the high-degree part of a host if and only if `H d = s`.
Here `H` is a 111-by-247 matrix over `F_2` and `s` is a nonzero syndrome. The
111 comes from 120 independent line constraints minus the 9 independent affine
columns. The minimum charge is the minimum Hamming weight of a solution, the
coset-leader weight of `s`.

There are exactly `304181752291` vectors of weight at most 6. They are not
sampled. The 247 columns are split into contiguous blocks of sizes 83, 82 and
82. For a support with block weights `x ≥ y ≥ z` and `x + y + z ≤ 6`:

| shape | what is enumerated |
|---|---|
| `x ≤ 2` | every triple of supports of weight at most 2 |
| `x = 3`, `y ≤ 2` | the weight-3 block, and every complementary pair of weight at most 2 whose weights sum to at most 3 |
| `x = y = 3`, so `z = 0` | the two weight-3 blocks |
| `x ≥ 4`, so `y + z ≤ 2` | that exact heavy weight, by every split across one halving of the heavy block, against every light support of weight at most `6 - x` |

Every composition of an integer at most 6 into three parts falls into one row.
Within the heavy block, `itertools.combinations` lists every left/right split
of the exact weight. If several supports share a syndrome, the search keeps a
lightest one. That cannot hide a legal solution: whenever a heavier support
fits under the cap, the lighter support of the same syndrome also fits.

The same census is repeated after reordering columns by `(index mod 5, index)`,
which induces a different three-block partition. Both partitions return no
solution. Therefore no charged support of size at most 6 is a host, and the
minimum charge is exactly 7.

An independent 120-by-9 affine solver, which never builds `H`, accepts the
charge-7 host and rejects both a 6-monomial subset of that host and the first
six charged monomials. The two solvers agree on those three supports. Agreement
on three supports does not replace the census.

## Enumerator self-test

On 18 basis columns, every one of the `31180` targets of weight at most 6 has
a unique support, and the search returns that support. A weight-7 basis target
is rejected. Eight further unique patterns on 90 basis columns, including a
weight-6 block at the end of a part and the shapes `(3,3,0)`, `(4,2,0)`,
`(5,1,0)` and `(2,2,2)`, are recovered exactly. On the real column set, the search finds a support
for column 0 alone and for the XOR of the first six columns, so an empty
return is not hard-coded. Deleting the monomial `x0 x3` from the charge-7 host
makes direct evaluation fail.

## Evidence and reproduction

Python 3.12, standard library only. From the repository root:

```sh
python3 -I -B research/p104-x0-boolean-host-floor/verify.py
python3 -B scripts/research_package.py --package research/p104-x0-boolean-host-floor
python3 -B scripts/check_research_commit.py --package research/p104-x0-boolean-host-floor --check-source-history
```

The verifier prints `PASS_X0_BOOLEAN_HOST_FLOOR` with `minimum=7` and
`kappa_claim=none`. One local CPython 3.12 run of the registered command took
about one minute, including both partitions, the basis self-test and the
planted supports. That time is machine-dependent and is not part of the claim.

Overlap at the 2026-11-11 cached snapshot: the phrase "excluded clique X0" and
the phrase "unrestricted Boolean" occur in open PR #7167 and in its #1166
finding, which both state that the unrestricted minimum is open. No other open
PR in that snapshot states an X0 host-charge lower bound. Search coverage is
not a proof that no later parallel claim exists.

## Limitations

- The exact minimum is for X0 on the 120-line scope only. It says nothing about
  frames F0–F12 or about excluded clique X1. A named-class minimum from #7167
  is not an unrestricted minimum for those rows.
- The charge is an ANF monomial count in this chart. It is not a gate count, a
  signed invoice, or a selected-frontier quantity. No selected cold replay,
  Lean proof, Docker run, or independent human review is claimed.
- The lower bound is a complete enumeration with a written case split, not a
  short hand-checkable identity. A reviewer confirms the case split and reruns
  the verifier.
- #7167's package is not imported or replayed. This verifier recomputes the X0
  flat from the same frame bytes and the on-main line map, and checks that the
  resulting monomials are the charge-7 host published there.
- Questions 2 and 3 of #7167, the joint thirteen-row union and the invoice
  naming, are not taken. Question 3 is κ-adjacent.

## Open next questions

Structured copies are in [TASK.json](TASK.json).

1. **Frame 5.** What is the exact unrestricted charge of P104 frame 5? #7167
   gives an explicit host of charge 6, below that row's named-class minima.
   First step: build the same 111-by-247 system for frame 5 and run this census
   through weight 5. Absence would prove the minimum is 6; a hit would be a
   smaller host. The X0 syndrome does not answer this row.
2. **Short certificate.** Do seven pairwise disjoint odd parity checks exist
   for this `H` and `s`? Such checks would certify charge at least 7 without
   enumerating supports. First step: search the row space for syndrome-odd
   vectors with disjoint column supports. Nothing in the census produces them,
   and a packing of seven supports is tight if the minimum distance is near 30.

## Credit

Prepared by unpaidmoon with substantial Cursor Grok assistance. Predecessors,
cited and not replayed as executables: Nick Petalas, #7167 (the open question,
the charge-7 X0 host, and the coset description of the odd 8-cliques);
unpaidmoon, #7014 (the frame partition), #7031 (the chart and the charge model)
and #7047 (affine sums of letters are not a general host); DreamingOfClouds,
#6933 (the E8 line map, merged). The frame bytes are the #7167 vendored copy of
the #7014 witness. New work is Apache-2.0.
