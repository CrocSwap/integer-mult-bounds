# Independent implementation review

This review and `independent.py` were produced by a separately tasked OpenAI
Codex agent. This is independent implementation and reasoning within the same
assisted contribution, not external peer review. The oracle does not import
`program.py` or `verify.py`; callers pass it emitted instruction values.

## Result and useful scope

The sharp complete-query bound is sound in the stated free unit-generator
alphabet: `4m + 2k`, with weighted optimum
`4 sum_j c_Bj + 2 sum_i c_Ai` for positive prices independent of ports and sign.
For every source `j`, track the integer coefficient `h[t,j]` of the degree-one
term `b_j X_j` in each output `t`. Only `B_j` queries change it. At least two
rows must have nonzero histories, since an output cannot read itself through
its own `A_i` query. Each history begins and ends at zero, costing at least
two unit `B_j` queries. Separately, the coefficient of `a_i Y_t` is the signed
number of `A_i` queries reading row `t`, and must cancel. Each `A_i` is needed
and thus costs at least two queries. Higher-degree feedback cannot cancel
these degree-one coefficients or create the missing degree-two source term.

This is a direct rectangular extension of the credited dirty-commutator
construction. Its useful addition is simultaneous batching over two axes,
plus a sharp interface theorem and a new complete two-source minimum census.
It saves `2(m-1) sum_i C(A_i)` against separate-source batching and
`2(k-2) sum_j C(B_j)` against separate-output batching. Both savings are strict
when `m > 1`, `k > 2`, and all complete-operator prices are positive. At either
boundary, the corresponding saving is zero. The dedicated-connector batch
still wins work by `2 sum_j C(B_j)` and uses one additional length-L row.
Usefulness therefore depends on a binding storage constraint; no application
embedding or unconditional end-to-end advantage is established here.

The `182` leaf count is an attained cost of the chosen factor trees, not a
lower bound for all possible leaf words. The query theorem excludes direct
product queries, coefficient preprocessing, scalar copies, writeable sources,
and extra rows. Port-dependent routing prices need a separate optimization.
Rounded or nonlinear children do not satisfy the exact linear argument.

## Independent checks

`evaluate` uses direct matrix-vector arithmetic with unbounded Python integers.
`expected` evaluates `y_i + A_i sum_j B_j x_j` directly. `product_matrix`
independently composes factors by their action on basis vectors. No symbolic
normalization, schedule structure, emitter inverse, or leaf recurrence enters
the dense comparison. The evaluator records scalar products, partial dot
accumulators, and all row values for the signed-width check. Complete reversal
is constructed locally from the supplied instruction list.

`check` runs all four schedules for dimensions 1, 2, and 3 and seeds 54, 154,
and 254. The latter two fixtures deliberately include zero and singular
factors. Hand-computable checks also distinguish two noncommuting singular
matrices. The seed fixture gives 36 forward-and-inverse cases. Calling the
same checker on the 16 `(m,k)` grid points gives 576 cases, superseding the
initial exploratory 192-case run. All these checks passed.

For the tape invoice, a separate closed formula eliminates individual head
steps. For one leaf, let `L` be row length, `C` the matrix's first tape slot,
`S` the source row's first slot, and `T` the target row's first slot. Since
coefficients follow every data row, the literal specified travel equals

```
2 L^2 C + L^3(L-1) - L(2L-1)S + (2-L)T
  + (L-1)(L+4)/2 + sum_{i=0}^{L-1} |T-S-L+1+i|.
```

Summing this expression agrees with the emitter's traced invoice. For the
seed fixture at `L=3`, the travel totals are 388364 borrowed, 707540
separate-output, 527460 separate-source, and 229160 dedicated word slots.
These are exact prices of the specified trace, not physical timing results.

## Complete two-source/two-output census

At minimum length 12, the lower bound fixes the multiset: each `B_j` has one
positive and one negative call into each output, and each `A_i` has one call
of each sign reading the other output. The twelve queries are distinct.

Delete the four queries for either source from a candidate word. Linearity
and immutable sources imply that the two resulting eight-query projections
must each solve their one-source problem, and the converse holds. Both
projections must retain the same order of four `A` queries. For a fixed pair
of projections, count all compatible words by multiplying the binomial
shuffle counts in the five gaps before, between, and after those `A` queries.
This is a bijective decomposition of the full `12!` candidate domain.

An independent sparse free-polynomial evaluator checks all `8! = 40320`
one-source words and finds 224 solutions, grouped into 8 `A` orders and 104
gap patterns. The projection/shuffle count gives **76032** two-source
minimum words, with 9504 for each admissible `A` order. As a separate coverage
check, applying the same shuffle formula to *all* one-source projections
recovers exactly `12! = 479001600` candidates. The checker explicitly rejects
any changed count. It performs exact complete counting without enumerating
479 million words or treating operators as commuting.

## Reproduction

The package verifier calls the independent functions. The standalone census
and hand checks can also run with optimized Python; no check relies on
`assert`:

```sh
python3 -O research/rectangular-output-borrowing/independent.py
```

The 576-case grid is independently reproducible from the repository root:

```sh
python3 - <<'PY'
import sys
sys.path.insert(0, 'research/rectangular-output-borrowing')
import independent as oracle
import verify
total = 0
for m in range(1, 5):
    for k in range(2, 6):
        lengths = {**{f'B{j}': 1 + (j+m) % 4 for j in range(m)},
                   **{f'A{i}': 1 + (i+k) % 4 for i in range(k)}}
        factors, cases = verify.check_case(m, k, lengths)
        result = oracle.check(cases, factors, m, k)
        total += result['expanded_dense_forward_inverse_cases']
if total != 576:
    raise ValueError(total)
print('PASS independent dense forward/inverse cases:', total)
PY
```

The generator supplies the words in this harness; the independent oracle
supplies their numerical semantics and expected mathematical result. Finite
dense tests are adverse implementation evidence. The free identity and
degree argument, not these tests, establish the general exact theorem.
