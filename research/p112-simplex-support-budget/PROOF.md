# Four P112 exclusions from root-simplex support spectra

## Statement

Let `r_t` be the pinned 112 E8 root-line representatives, with binary labels
`ell(t)`. Over a characteristic-zero field `K`, put

```
C = {c_h : c_h(t)=<r_t,h>, h in K^8},
w(q) = rank_F2 {ell(t) : q(t) != 0}.
```

For each `b=6,7`, no `b+4` independent pieces spanning `T` can have
`dim(T intersect C) >= b` with either weight profile

```
3,5,5,6^(b+1)    or    4,4,5,6^(b+1).
```

The notation bounds each weight from above. These are four actual profiles
in PR3154's TWOSIDE `(b,t)=(6,4),(7,4)` residues. The conclusion is a scoped
piece theorem, not full C5, `C(P112)>=64`, supplier admission or a new kappa.

The new ingredient is a support-sum bound for root simplices. It counts the
most frequent evaluation value, rather than bounding each coordinate's
number of nonzero edges. All counts below are exact.

## Retained geometric premises

The source-bound [root-simplex proof](vendor/ROOT-SIMPLEX-PROOF.md) and
[larger-simplex proof](vendor/LARGER-SIMPLEX-PROOF.md) give:

- Weight `3,4,5,6` supports contain at most `4,8,12,20` live lines.
- `C` has dimension eight and minimum support size 53.
- A nonzero codeword supported on fewer than 70 live lines is proportional
  to a root codeword.
- Independent root directions whose pair differences are also root
  directions can be written `h_i=z alpha_i`, for one nonzero scalar `z`
  and signed roots with `<alpha_i,alpha_j>=1`, squared norm two.

The replay reconstructs the 120 root lines and the P112 frame deletion,
all 4,097,782 five/six-flat kernels, 960 simple reflections and 7,140 root
planes. The general root-direction classification uses the standard
Weyl-chamber theorem, not just these finite tests. Its extension to `K`
uses the rational one-dimensional kernel of the perpendicular roots.
These are inherited written proof obligations, not a new formalization.

The executable scales every root by two. Its squared norms are eight and
its distinct star-root inner products are four. This scaling does not
change support or equality multiplicity.

## Quotient normalization

Choose the three small pieces, of weights `3,5,5` or `4,4,5`.
Their support union `S` has size at most 28. Every remaining piece `q_i`
has support size at most 20. There are `n=b+1` such pieces.

Let `D=T intersect C` and `lambda:T -> T/D`. The quotient dimension is at
most four. The three small pieces together with any `q_i` have union size
at most `28+20=48<53`. Their images are independent: any dependence would
be a nonzero codeword supported on fewer than 53 lines, since the original
pieces are independent. Thus the quotient dimension is exactly four.
Modulo the three small images, all remaining pieces have nonzero images
in a one-dimensional quotient.

Rescale the `q_i` to have equal images there. For suitable combinations
`a_i` of the small pieces,

```
c_0=0,    c_i=q_i-q_0-a_i in D, i=1,...,b.
```

The `c_i` are independent by their separate coefficients on `q_1,...,q_b`.
Every nonzero difference `c_i-c_j` has support at most
`28+20+20=68<70`, so is a root direction. The retained root-plane argument
therefore identifies these vertices with one scaled affine root simplex
`0,z alpha_1,...,z alpha_b`. Outside `S`, its coordinate values differ
from the endpoint values `q_0(t),...,q_b(t)` by one common shift.

## Complete star coverage by small stabilizer orbits

An ordered root star is a tuple of signed roots with all distinct inner
products equal to one. To classify its next root, enumerate every signed
root having inner product one with the prefix. Reflections in roots
perpendicular to the whole prefix fix that prefix pointwise and act on
this finite candidate set. Partition the set into orbits of these
reflections, retaining one representative per orbit.

This subgroup need not be the whole stabilizer. Retaining every subgroup
orbit is sufficient for coverage. Inductively, every ordered star can be
moved to a retained prefix by root reflections. For its extension, the
subgroup then moves the next root to one of the retained representatives.
No probabilistic search, assumed transitivity or table of embeddings is
used. Each reflection is checked against the complete candidate set.

The exact partition through rank seven is:

| Prefix rank | Perpendicular root lines | Extension roots | Orbit sizes |
|---|---|---|---|
| 0 | 120 | 240 | 240 |
| 1 | 63 | 56 | 56 |
| 2 | 36 | 27 | 27 |
| 3 | 20 | 16 | 16 |
| 4 | 10 | 10 | 10 |
| 5 | 4 | 6 | 6 |
| 6 | 1 | 3 | 2, 1 |

Hence rank-six stars have one representative; rank-seven stars need two.
Their differing spectra below show why dropping the second branch is
unsound. The proof of orbit coverage is an induction on at most seven
roots, supported by the complete finite partitions in `model.py`.

## Minimum nonzeros after a common shift

For `n` coordinate values `v_0,...,v_(n-1)`, the smallest possible number
of nonzeros after adding one common scalar is

```
k = n - max_a #{i : v_i=a}.
```

A shift can make zero only one equality class. Choosing the largest class
attains the minimum. This statement holds over `K` and is invariant under
nonzero common rescaling.

For each star representative, evaluate the vertices `0,alpha_1,...,alpha_b`
on all 120 root lines. Root reflections permute the lines, up to sign;
sign changes preserve equality multiplicity. Thus the following histograms
cover every star, over every characteristic-zero field:

| Star | Number of coordinates at each minimum nonzero count |
|---|---|
| rank six | `0:1, 1:21, 2:63, 3:35` |
| rank seven, first branch | `1:8, 2:56, 3:56` |
| rank seven, second branch | `0:1, 2:84, 4:35` |

Remove the eight frame lines and at most 28 live lines of `S`. This deletes
at most 36 entries of the full spectrum. Even allowing arbitrary deletion
of the 36 largest costs, the surviving sum is at least

```
rank six:                 21 + 62*2 = 145,
rank seven, first branch:  8 + 56*2 + 20*3 = 180,
rank seven, second branch:     83*2 = 166.
```

No assertion about frame placement or containment of `S` in a binary flat
is required. Allowing arbitrary deletions and arbitrary coordinate shifts
is a relaxation, so its lower bound applies to the actual pieces.
Outside `S`, sum this lower bound over endpoint supports. The whole endpoint
support sum is bounded above by `20n`. This gives the contradictions

| b | n | Required endpoint support | Endpoint allowance | Margin |
|---|---|---|---|---|
| 6 | 7 | 145 | 140 | 5 |
| 7 | 8 | 166 | 160 | 6 |

Each row applies to both stated profiles. All four are impossible.

## Actual residue and predecessor boundary

The unchanged `vendor/bk2b.py` reproduces all 24 original TWOSIDE cell
counts. A separate transcription checks inclusion of both profiles among
the original 69 and 154 survivors in the two target cells. Completeness
of the original decoder reduction is inherited, not proved by this check.

PR3173's coordinate inequality would require

```
53*n*(n-1)/2 <= 112 + (M_n-1)*28 + (n-2)*20*n,
M_n=max(2*n-3,floor(n*n/4)).
```

It has margins `-7,-8` here and does not contradict either cell.
Its earlier applications have one fewer weight-six endpoint and an
additional weight-five piece; they are not the four profiles proved here.

Every four-piece quotient basis certified by the weight capacities alone
is checked against all two-six-flat packings with paid line cuts. For the
first profile its only weight multiset is `3,5,5,6`; for the second it is
`4,4,5,6`. Both have minimum certified cut allowance 16 and only weight-six
pieces left over. Thus the pinned eight/ten-cut theorems and the twelve-cut
rank-four-anchor result do not certify these applications by this route.
This is an overlap boundary, not a lower bound on the actual number of
needed cuts. More economical covers using actual support overlap are not
excluded. Other independent arguments may exist.
