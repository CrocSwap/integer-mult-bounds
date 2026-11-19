# Inequivalent even maximizers with one matrix-unit edge

At pattern dimension `k=3` and matching number `ν=1`, two complete binary
projector pools attain the maximum joint-image dimension `n=4` and have
inequivalent actions. The new pool has two unordered pairs whose product has
trace one. The published maximizer has four. This is a scoped construction over
`F₂`.

## Model and construction

Write `P=xyᵀ` with `yᵀx=1`. Its pattern is the off-diagonal part of `P`.
For a pattern space `H`, the complete pool consists of all rank-one idempotents
whose patterns belong to `H \ {0}`. An edge `{i,j}` is present when `H` contains
`Eᵢⱼ` or `Eⱼᵢ`. The matching number is the maximum number of disjoint edges.
Equivalence of actions means simultaneous conjugacy by an invertible map on the
joint image, with the projectors allowed to be relabelled.

Use coordinates `a,b,f,g`, with corresponding unit vectors denoted by the same
letters. Take these four pairs of factors.

| Projector | Image `x` | Covector `y` |
| --- | --- | --- |
| `P` | `a` | `a+b` |
| `Q` | `a+b` | `b` |
| `R` | `a+f` | `a+g` |
| `S` | `a+b+g` | `b+f` |

Each pairing `yᵀx` is one. Put `H=span(E_ab, off(R), off(S))`. The patterns of
`P` and `Q` both equal `E_ab`. Partition the coordinates into `(a,b)` and
`(f,g)`. On the first two rows and last two columns, the patterns of `R` and
`S` restrict to `a gᵀ` and `(a+b) fᵀ`. In the reverse rectangle they restrict to
`f aᵀ` and `g bᵀ`. Both pairs of restrictions are independent. Every
pattern outside `span(E_ab)` therefore has a nonzero entry in each of the two
disjoint rectangles. It follows that `k=3` and `E_ab` is the sole matrix unit.

The only lifts of `E_ab` are `P` and `Q`. Indeed, the side conditions `x_a=1`
and `y_b=1` force all the other bits except `x_b,y_a` to vanish, and exactly one
of those two bits must be one. In the coset of `off(R)` modulo `span(E_ab)`,
the two nonzero cross rectangles uniquely fix `x` and `y` over `F₂`, yielding
`R`. The coset of `off(S)` gives `S` by the same argument. In the sum coset the
first rectangle has rank two, since `a` and `a+b` are independent. It cannot
be a rectangle of an outer product. This exhausts the nonzero pattern space.

The four images form a basis because `a` and `a+b` span the first two
coordinates and the other images have distinct fresh coordinates `f,g`.
The covectors are also a basis. Every nonzero invariant subspace must therefore
contain at least one of the four images, obtained by applying a projector to a
nonzero element of the subspace. Define an arrow `i → j` if `P_j x_i = x_j`.
The closed walk `P → R → S → Q → R → P` reaches all four images from each of its
vertices. Thus the action is irreducible, with `n=4`. The even maximum at these
parameters is four by the matching bound and its attainment in #7707.

## Inequivalence

For distinct projectors `P_i=x_i y_iᵀ` and `P_j=x_j y_jᵀ`,
`tr(P_i P_j)=(y_iᵀ x_j)(y_jᵀ x_i)`. The integer count of unordered pairs
with trace one is unchanged by simultaneous conjugation and relabelling.
The pairing matrix for the new pool, with entries `y_iᵀ x_j` and order
`P,Q,R,S`, is

```text
1 0 1 0
0 1 0 1
1 1 1 0
0 1 1 1
```

The trace-one pairs are `{P,R}` and `{Q,S}`. For the published maximizer,
#7707 uses `P,Q` with the two links `(b+f)(a+f)ᵀ` and `(b+g)(a+g)ᵀ`.
Each link has trace-one product with each of `P,Q`. The two links have
trace-zero product, as do `P,Q`. Its count is four, which separates the two
actions even under arbitrary linear changes of basis on the joint image.

## Reproduce

Run these from the repository root with CPython 3.12.15 and its standard library.

```sh
python3.12 -B research/even-one-edge-maximizer/verify.py
python3.12 -B -O research/even-one-edge-maximizer/verify.py
python3.12 -B scripts/research_package.py --package research/even-one-edge-maximizer
python3.12 -B scripts/check_research_commit.py --package research/even-one-edge-maximizer --check-source-history
```

The verifier scans all 120 width-four rank-one idempotents for the new pattern
space, checks all 15 nonzero starting vectors and reports the two trace-one
pairs. The written proof uses the published upper bound as a premise.

## Open next questions

- What are all action classes at `(k,ν,n)=(3,1,4)`? Start by enumerating spans
  of `E_ab` and two realized pattern classes at width four, then classify
  their complete pools up to conjugacy. Higher ambient widths require a
  separate reduction.
- Can the new alphabet realize a rank-saving paid word? Start by specifying
  a saturated exponent relation lattice and the full ambient endpoint. A
  word, dirty-state restoration, native implementation and the complete
  recursive invoice remain open. This construction supplies no new saving.

## Credit

The new construction and proof were produced by Nick Petalas. Ali Romman’s
[PR #7707](https://github.com/CrocSwap/integer-mult-bounds/pull/7707) supplies
its even-maximizer question, the baseline construction and the sharp value.
His [PR #7692](https://github.com/CrocSwap/integer-mult-bounds/pull/7692)
supplies the matching theorem and the two lifts of a matrix unit used in the
baseline. [TASK.json](TASK.json) identifies the exact predecessor proofs.
The new package is Apache-2.0.
