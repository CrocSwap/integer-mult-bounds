# Exact Boolean-host charge of P104 frame 5 (no κ)

Result and claim type: **exhaustive finite census** of a finite domain, together
with direct evaluation of one host. The census proves a scoped exact minimum.
It is not a heuristic search, not a signed invoice, and not a selected-frontier
change. The selected κ remains **363005817/100000000000**.

This package answers open question 1 of the X0 Boolean-host census
([PR #7235](https://github.com/CrocSwap/integer-mult-bounds/pull/7235)): the
exact unrestricted charge of P104 frame 5, whose explicit host in
[PR #7167](https://github.com/CrocSwap/integer-mult-bounds/pull/7167) has
charge 6. The X0 minimum does not transfer. The 104-line system, the joint
thirteen-row union, and invoice-primitive naming are not taken.

## Hypotheses

Coordinates are the simple-root chart `x0..x7` on `F_2^8`, with the E8 line
map of #6933 as used by #7031. The quadratic form is

```text
Q(x) = wt(x) + x0 x2 + x1 x3 + x2 x3 + x3 x4 + x4 x5 + x5 x6 + x6 x7
```

over `F_2`. The 120 root lines are exactly `{Q = 1}`. A *host* of frame 5 is
a Boolean function that equals the frame indicator on those 120 points. Values
on `{Q = 0}` are free. The *charge* is the number of monomials of degree at
least 2 in the algebraic normal form. Affine monomials are not counted. They
are not free parameters of the function: they still have to match the indicator.

Frame 5 is the sixth of the 13 P104 frames in the #7014 partition vendored by
#7167, ports `(28, 49, 133, 168, 265, 292, 400, 445)`. The file
`data/frames.json` is those bytes, sha256
`c75915c18fc06ac19cc90fb9911209517c071862fdf401b998d5075efc0cda0d`. Frame 5 is
one of the 104 P104 ports. The census itself uses all 120 root lines.

## Theorem

Every Boolean host of frame 5 on the 120 root lines has charge at least 6.
The product

```text
x0 x5 (x3 + x1 x3 + x3 x6 + x2 x7 + x1 x3 x7 + x4 x7)
```

has charge 6, so the minimum is exactly 6. Its six charged monomials are

```text
x0 x3 x5, x0 x1 x3 x5, x0 x3 x5 x6, x0 x2 x5 x7, x0 x1 x3 x5 x7, x0 x4 x5 x7.
```

There is no affine term and no `F_2` cancellation: the six factors of the
parenthesis are disjoint from `x0` and `x5` and distinct from each other, so
the product has six monomials. These are the six masks
`(41, 43, 105, 165, 171, 177)` recorded for row 5 in #7167. This verifier
re-expands the product and evaluates it; it does not replay that search.

## Why the product is a host

The verifier multiplies the algebraic normal forms, checks that the subset-sum
transform is an involution on the result, and evaluates the ANF at every root
line. The factored reading `x0 x5 g` agrees with that evaluation at every
line. An independent Gaussian elimination on the nine affine columns, which
never builds the 247-column syndrome matrix, accepts this support.

Deleting `x0 x3 x5` leaves a charge-5 polynomial. Direct evaluation and both
solvers reject it. The first five charged monomials, in mask order, are also
rejected, and the two solvers agree on that rejection. Agreement on these
supports does not replace the census.

## Why no host has charge at most 5

After the nine affine monomials are eliminated, a charged coefficient vector
`d ∈ F_2^{247}` is the high-degree part of a host if and only if `H d = s`.
Here `H` is a 111-by-247 matrix over `F_2` and `s` is a nonzero syndrome. The
111 comes from 120 independent line constraints minus the 9 independent affine
columns. The coefficient matrix does not depend on which clique is being
hosted; the frame-5 indicator supplies `s`. The X0 syndrome is a different
right-hand side and is not used. The minimum charge is the minimum Hamming
weight of a solution.

There are exactly `7509373288` vectors of weight at most 5. They are not
sampled. The 247 columns are split into contiguous blocks of sizes 83, 82 and
82. For a support with sorted block weights `x ≥ y ≥ z` and `x + y + z ≤ 5`,
exactly one of the following holds. There are 16 such sorted triples.

| shape | what is enumerated |
|---|---|
| `x ≤ 2` | every triple of supports of weight at most 2 whose weights sum to at most 5 |
| `x = 3`, so `y + z ≤ 2` | the weight-3 block, and every complementary pair of weight at most 2 whose weights sum to at most 2 |
| `x ≥ 4`, so `y + z ≤ 5 - x` | that exact heavy weight, by every split across one halving of the heavy block, against every light support of weight at most `5 - x` |

`(3, 3, 0)` and `(4, 1, 1)` sum to 6, so they are outside this cap. The
verifier checks that each of the 16 sorted triples falls into exactly one row
and that those two weight-6 triples fall into none. Within the heavy block,
every left/right split of the exact weight is listed. If several supports
share a syndrome, the search keeps a lightest one. That cannot hide a legal
solution: whenever a heavier support fits under the cap, the lighter support
of the same syndrome also fits.

The same census is repeated after reordering columns by `(index mod 5, index)`,
which induces a different three-block partition. Both partitions return no
solution. Therefore no charged support of size at most 5 is a host, and the
minimum charge is exactly 6.

## Enumerator self-test

On 15 basis columns, every one of the `4944` targets of weight at most 5 has
a unique support, and the search returns that support. A weight-6 basis target
is rejected. Nine further unique patterns on 90 basis columns, including a
weight-5 block at the end of a part and the shapes `(2,2,1)`, `(3,2,0)`,
`(3,1,1)`, `(4,1,0)` and `(5,0,0)`, are recovered exactly. A repeated column
has two legal weight-1 supports; the search returns one of them, and it
returns the empty support for the zero target. On the real column set, the
search finds a support for column 0 alone and for four planted weight-5
supports, including one that meets a block boundary. The strided partition
likewise finds its first column and the XOR of its first five columns, so an
empty return is not hard-coded.

## Evidence and reproduction

Python 3.12, standard library only. From the repository root:

```sh
python3 -I -B research/p104-frame5-boolean-host-floor/verify.py
python3 -B scripts/research_package.py --package research/p104-frame5-boolean-host-floor
python3 -B scripts/check_research_commit.py --package research/p104-frame5-boolean-host-floor --check-source-history
```

The verifier prints `PASS_P104_FRAME5_BOOLEAN_HOST_FLOOR` with `minimum=6` and
`kappa_claim=none`. One local CPython 3.12 run, and a second run under
`python3 -O`, each finished in about 17 seconds, including both partitions,
the basis self-test and the planted supports. That time is machine-dependent
and is not part of the claim.

Overlap against open upstream PR titles and bodies found the charge-6 host and
the open question in #7167 and #7235, and no statement that the unrestricted
frame-5 minimum had already been settled. Search coverage is not a proof that
no later parallel claim exists.

## Limitations

- The exact minimum is for frame 5 on the 120-line scope only. It says nothing
  about the other twelve P104 frames or about either excluded clique. A
  named-class minimum from #7167 is not this unrestricted minimum. #7167
  records frame 5's invariant minimum as 10 and its cubic minimum as 18; those
  class censuses are not replayed here.
- The same six monomials also match frame 5 on the 104 P104 lines, so that
  weaker scope has charge at most 6. Its minimum may be smaller. This census
  does not decide it.
- The charge is an ANF monomial count in this chart. It is not a gate count, a
  signed invoice, or a selected-frontier quantity. No selected cold replay,
  Lean proof, Docker run, or independent human review is claimed.
- The lower bound is a complete enumeration with a written case split, not a
  short hand-checkable identity. A reviewer confirms the case split and reruns
  the verifier.
- #7167 and #7235 are not imported or replayed. This verifier rebuilds the
  chart from the on-main line map and the vendored frame bytes, and checks
  that the resulting monomials are the charge-6 host published for row 5.
- The joint thirteen-row union and the invoice naming in #7167 are not taken.
  The seven-check question for the X0 syndrome is not taken either.

## Open next questions

Structured copies are in [TASK.json](TASK.json).

1. **104-line scope.** What is the exact unrestricted charge of frame 5 when
   the host is required only on the 104 P104 lines? The product above is still
   an upper bound of 6. First step: eliminate the affine columns on those 104
   lines and run this census through weight 5. The rank-111 matrix is the
   wrong system for that scope.
2. **Short certificate.** Do six pairwise disjoint odd parity checks exist for
   this frame-5 `H` and `s`? Such checks would certify charge at least 6
   without enumerating supports. First step: search the row space for
   syndrome-odd vectors with disjoint column supports. Nothing in the census
   produces them. This is a different right-hand side from the seven-check
   question left open for X0.

## Credit

Prepared by unpaidmoon with substantial Cursor Grok assistance. Predecessors,
cited and not replayed as executables: Nick Petalas, #7167 (the charge-6
frame-5 host and the unrestricted-charge question); unpaidmoon, #7235 (the
three-block census for X0, which left frame 5 open), #7014 (the frame
partition), #7031 (the chart and the charge model) and #7047 (affine sums of
letters are not a general host); DreamingOfClouds, #6933 (the E8 line map,
merged). The frame bytes are the #7167 vendored copy of the #7014 witness.
New work is Apache-2.0.
