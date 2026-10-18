# Exact E8 puncture thresholds and a star-decoder exclusion

**Result:** among all punctures of at most 35 of the 120 real E8 root lines,
no bit-side label decoder with star copy accounting improves the copy-cost / live-port
ratio **63/111**. Nine linearly independent punctured labels attain that ratio.
This is an exhaustive geometric bound, not a randomized search.

A second result makes the previously sampled mixed-port obstruction exact:
a rational normal not proportional to an E8 root needs **at least 14 punctures**
to be compatible with any nonzero decoder label. The bound is sharp, including
for odd labels. Its D7 equality example has star copy cost 64 on 106 surviving
root ports, so that puncture itself is worse than 63/111.

**No new supplier word, supplier exponent, or κ is claimed.** The current bit
supplier is already above the complex bottleneck. A smaller helper network can
still improve a word even if its copy ratio does not improve.

## Reproduce

From the repository root, using Python 3.9 or later and no external packages:

```sh
python3 research/e8-continuation-20261013/punctures/verify.py --negative-controls
python3 research/e8-continuation-20261013/punctures/verify.py --write /tmp/e8-puncture-results.json
cmp research/e8-continuation-20261013/punctures/results.json /tmp/e8-puncture-results.json
```

The verifier uses exact integers and rational arithmetic. On the development
machine it runs in under one second. The JSON contains every standard parabolic
flat tested and explicit punctures witnessing all eight sharp rank thresholds.
Optimized Python (`-O` or `PYTHONOPTIMIZE`) is explicitly refused before any file
write. The optional negative controls inject corrupt root geometry, label parity
and a flat containing an extra independent root, and check rejection at the
corresponding structural invariants. They also check that `-O` writes no receipt.
Root indices use this package's doubled standard coordinates, **not** the
Hamming-coordinate numbering in #620 or the shipped word.

## Definitions and exhaustive reduction

Let L be one representative of each of the 120 E8 root lines, in doubled standard
coordinates with squared norm 8. Put G_st = L_s·L_t / 4 and B = (J+G) mod 2.
The binary matrix B has rank nine. For a label functional p, its reader set R(p)
is the support of the corresponding nonzero word in rowspace(B). There are 511
such words. Their weights are 56 (255 words), 64 (255), and 120 (one).
For a puncture set P define

    s_P(p) = dim_Q span{L_t : t in R(p) minus P}.

In the star label-decoder model used by #620's `bitp.py`, the optimum copy cost
is the minimum total weight of a basis of the nine-dimensional binary label
space, with weight s_P. Matroid greedy computes it exactly. Allowing extra
nonnegative-cost star totals cannot improve the minimum-basis cost: their source
functionals must span and therefore contain a basis.

It suffices to test the 255 proper subsets I of a fixed simple system of E8.
Here is the coverage argument, which is part of the proof rather than a claim
that the program enumerates every flat individually. For a root-spanned proper
subspace F, choose a generic normal vector in F-perp, so exactly the roots in F
are perpendicular to it. Move this normal to the closed fundamental Weyl chamber.
Every positive root has nonnegative simple-root coordinates. A root is
perpendicular to the normal precisely when its support lies in the set I of
simple roots perpendicular to it. Thus the roots of F become exactly the roots
in the span of I. This is the usual parabolic-flat argument; see, for example,
the opening of Section 4 of [Baumeister et al., *On the Hurwitz action in finite Coxeter groups*](https://arxiv.org/html/1512.04764v1#S4).

The verifier checks integrality and common-sign positivity of all simple-root
coordinates. It also checks that each of the eight simple reflections preserves
the 512 reader words and their self-pairing parity. Because these reflections
generate the Weyl group, taking minima over all reader words on these standard
flats covers every conjugate flat without enumerating the Weyl group.

## Sharp rank-loss thresholds

For d=0,...,7 let delta_d be the smallest number of roots that can be deleted
from any nonzero reader R(p) so its surviving Q-span has dimension at most d.
For each standard d-dimensional flat H, the required deletion count is
|R(p) minus H|. Minimize this over its 511 reader words and over all standard
flats of dimension d. Every lower-dimensional flat extends to one of dimension
d, so this also covers "at most d". The program checks that each minimizing
witness actually retains rank d.

| d | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| delta_d | 56 | 55 | 53 | 50 | 44 | 36 | 26 | 1 |

In particular, **25 punctures cannot produce any reader of rank six**, and
**35 punctures cannot produce any reader of rank five**.

## Star-ratio theorem

A sharper statement holds for |P| <= 13:

    C_star(P) = 72 - rank_F2{u_t : t in P}.

To see this, the seven non-root-normal maximal parabolic hyperplanes need at
least 14 deletions for any reader to fit. For the remaining E7 hyperplane,
exactly one reader fits after fewer than 14 deletions: the reader of its normal
root, and the root itself must be deleted. Therefore the only cheap functionals
are the labels of punctured roots. They have weight seven; all others have
weight eight. No reader has smaller rank, since delta_6=26. The minimum-weight
basis takes a maximum independent subset of the cheap functionals, proving the
formula. The live binary labels still span dimension nine: a rank loss would
require deleting an entire nonzero reader, hence at least 56 ports.

Now write p=|P|, v=120-p. The preceding facts imply:

| punctures p | lower bound for star copy cost C | consequence |
|---|---:|---|
| 0,...,8 | 72-p | (72-p)/(120-p) > 63/111 |
| 9,...,25 | 63 | C/v >= 63/111, equality possible at p=9 |
| 26,...,35 | 54 | C/v >= 54/94 = 27/47 > 63/111 |

The second and third rows use that any spanning set contains nine independent
functionals, each of rank at least seven or six, respectively. The verifier
supplies a nine-puncture control with independent labels and exact star cost 63.
This proves the asserted optimum over **all** punctures of size at most 35.

For the fixed bit-side stage window h=8, the format ceiling in #595/#602 is
monotone in C/v, so this excludes improving that ceiling by such punctures within
the same star model. It does not compare full supplier words: helper counts,
frame changes, idle windows, hosting and outer assembly still have to be priced.

## Sharp non-root-port obstruction

The maximal parabolic hyperplanes have the following exact reader-deletion minima.
The odd-label minimum agrees with the unrestricted minimum in every row.

| root subsystem | root lines in hyperplane | minimum deletions |
|---|---:|---:|
| E7 | 63 | 1 |
| D7 | 42 | 14 |
| E6+A1 | 37 | 27 |
| A7 | 28 | 28 |
| D5+A2 | 23 | 33 |
| A6+A1 | 22 | 35 |
| A4+A3 | 16 | 40 |
| A4+A2+A1 | 14 | 43 |

For any non-root normal n, move n into the fundamental chamber. Its vanishing
simple roots form a proper subset I. If exactly the E7 node is missing, n is a
root normal, contrary to the premise. Otherwise I is contained in at least one
of the other seven maximal subsets. Its root section is contained in that
non-root hyperplane. Consequently every nonzero reader has at least 14 roots
outside n-perp.

A compatible new bit-side port (physical vector n, nonzero binary label z)
requires every surviving root with z·u_t=1 to lie in n-perp. Hence all the roots
in R(z) outside n-perp must be punctured. This proves the universal lower bound
14, rather than only a bound on sampled or root-spanned normals.

Equality occurs at the D7 normal e8. The unique minimizing reader deletes the
14 integer root lines involving coordinate eight. Its label has odd norm, so
it satisfies the added port's label self-pairing requirement. After puncturing
these lines, the reader-rank histogram is {7:15, 8:496}; their cheap functionals
have binary span dimension eight. The exact star optimum is therefore 64, not
63 or 62. This is a control for the root-only puncture, not a fully costed
mixed-port supplier construction.

## Scope and next direction

This closes a sizeable star-puncture search range. It does **not** lower-bound
Theorem C's general pairing-rank cost: two seven-dimensional reader/source
spans can have a pairing block of rank six. It also does not handle a new
non-label decoder, multiple added ports, or a helper-saving tradeoff at worse
copy ratio.

A non-star construction is therefore a more relevant next test than further
star annealing among <=35 punctures. Alternatively, 36 is the first puncture
count at which the coarse rank thresholds here stop ruling out improvement;
that is a necessary opening, not evidence that nine cheap independent
functionals or an economical full word exist.

## Provenance and assistance

This work follows the questions and conventions in GamingPuzzled's #620,
`research/e8-decoder-floors-and-cold14-notes/s2-decoder/{bitp.py,sa_bit.py,hyper.py,addports.py}`;
DreamingOfClouds' #595/#602, `research/format-limits-corrected/`; and eumemic's
#543, `research/e8-bit-r420/`. The reader-rank census, exhaustive reduction and
<=35-puncture consequence are supplied here; no novelty outside this repository
is asserted. The mathematical coverage argument is stated explicitly and all
finite arithmetic is independently regenerated from roots by this package.
Base source pin: `17ce0c79b7b51c2634b439ea5a2b754f09909693`, with immutable references:

- [#620 decoder and puncture notes](https://github.com/CrocSwap/integer-mult-bounds/tree/17ce0c79b7b51c2634b439ea5a2b754f09909693/research/e8-decoder-floors-and-cold14-notes/s2-decoder)
- [#595/#602 corrected format limits](https://github.com/CrocSwap/integer-mult-bounds/tree/17ce0c79b7b51c2634b439ea5a2b754f09909693/research/format-limits-corrected)
- [#543 bit supplier](https://github.com/CrocSwap/integer-mult-bounds/tree/17ce0c79b7b51c2634b439ea5a2b754f09909693/research/e8-bit-r420)

Prepared by **Chi Zhao**, with **substantial OpenAI Codex assistance**.
Licensed under **Apache-2.0**, consistent with the repository.
No archived source was modified.
