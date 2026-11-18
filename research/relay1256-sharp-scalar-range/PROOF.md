# Sharp normalized scalar ranges

## Contract and result

Fix the candidate graph from Clear1nsight's
[PR #7704](https://github.com/CrocSwap/integer-mult-bounds/pull/7704),
at `e29a5ae8591243c1178067727f12ce4abefa0b93`.
Its decompressed SHA-256 is
`8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf`.
Keep its 1501 independent entrances, all scalar coefficients, the row
schedule and the increasing donor order within each row. A paid move is
the identity in these normalized scalar coordinates. This contract does
not identify a physical chart map with the identity.

For independent real entrances with absolute value at most one, the exact
largest absolute values are as follows. A term number starts at one.

| Quantity | Sharp maximum | Row | Term | Extra signed bits |
|---|---:|---:|---:|---:|
| Completed row or entrance | `2140811/96` | 101894 | 4 | 15 |
| Ordered partial sum | `53895757/256` | 156140 | 11 | 18 |
| Separate rational product | `4340699/24` | 156140 | 3 | 18 |
| Integer numerator before division | `36262265/32` | 100773 | 9 | 21 |

The numerator uses the coefficient in reduced form `a/b`, with `b>0`.
Its value is `a` times the donor, before division by `b`. The last row
of the table comes from donor 93930 and coefficient `7345/16`.

The source's sum of separate absolute product bounds is `13819451/16`.
This is the source receipt's `27984388275/16` divided by its odd scale
2025. The exact prefix bound is smaller by the factor
`221111216/53895757`. This is a tighter bound, not an error in the source.
The large prefix occurs in terminal row 156140. Its completed value is
exactly entrance 1372, so a bound on completed values alone misses the
temporary growth.

For integer entrances that are multiples of 921600 and fit a signed
W-bit word, `W+21` signed data bits suffice for the stated normalized
scalar arithmetic, for all `W>=2`. A 32-bit entrance fixture needs all
21 extra bits. This does not replace the source's physical `W+26`
service contract: its W measures a different domain of chart-valued
donors and inherited root states.

## Linear forms give both bounds and witnesses

Let `c(v)` be the rational coefficient vector of any intermediate v in
the independent entrances. Each entrance has its unit vector. If the
literal terms of a row are `q_j v_j`, then its prefix after t terms has
coefficient vector

```text
c(prefix_t) = sum_(j=1)^t q_j c(v_j).
c(product_j) = q_j c(v_j).
c(numerator_j) = numerator(q_j) c(v_j).
```

These identities follow by induction in the source schedule. They do
not assume independent donors within a row. All appearances of the same
entrance must first be combined. The stored row uses the complete sum.

For a real vector x with every `|x_i|<=1`, the triangle inequality gives
`|c dot x| <= sum_i |c_i|`. Set `x_i=sign(c_i)` at each nonzero
coefficient, and set all other entries to one. This input attains the
bound. Thus the coefficient l1 norm is the exact range of each linear
form. The largest such norm over a finite set of forms is also attained.
This proves the all-input statement; the finite computation only has to
enumerate the fixed source forms correctly.

The checker represents `921600*c(v)` by integers. Every basis product
divides exactly. It updates the prefix norm by `|old+product|-|old|`
at each affected entrance. After each complete donor term, it checks
that prefix against the maximum. It also checks every separate product,
every numerator, all completed rows and all initial unit vectors.
The enumeration covers 7644 rows, 172414 ordered prefixes and 9044092
nonzero basis products. Source hashes, schedule completeness, unique
donor order, causality and donor charts are checked before this pass.

The receipt gives the negative entrance columns of each attaining input.
All other signs are one. Four complete scalar replays use these inputs
with rational arithmetic, without coefficient vectors or the norm update.
Each attains its listed maximum and stays within all four bounds.
Four further complete scalar replays use the integer fixtures below.

## Integer range and sharp bit counts

If all entrance integers are multiples of G=921600, the integer basis
pass proves that every product and stored value is integral. Prefixes
are sums of those integral products. No rounding occurs. Let C be one
of the four exact unit-input bounds. Signed W-bit entrances have absolute
value at most `2^(W-1)`, so the corresponding intermediates have absolute
value at most `C*2^(W-1)`.

For the four rows of the table, respectively,

```text
2^14 < 2140811/96 < 2^15
2^17 < 53895757/256 < 2^18
2^17 < 4340699/24 < 2^18
2^20 < 36262265/32 < 2^21.
```

The strict upper inequalities imply the stated signed widths. To check
that one fewer bit does not work uniformly, set W=32 and set every
entrance to its attaining sign times
`M=921600*floor((2^31-1)/921600)=2147328000`. Both signs fit W bits.
Every intermediate remains integral. The resulting target values are:

| Quantity | Attained integer | Largest positive value with one fewer bit |
|---|---:|---:|
| Completed row | 47885660448000 | 35184372088831 |
| Ordered partial sum | 452077609716000 | 281474976710655 |
| Separate product | 388371020928000 | 281474976710655 |
| Numerator | 2433343030560000 | 2251799813685247 |

These are reachable values of the actual graph, rather than independent
choices for donors that may share entrances. In particular, checking only
product and prefix bounds would suggest 18 extra bits and miss the
numerator requirement. The 20-bit numerator allowance also fails.

A signed shift-and-add multiplication can form `a*v` with no absolute
partial product larger than `|a*v|`: operate on the absolute values,
then apply the sign. In binary long division by positive b, every
quotient prefix is at most the absolute numerator. Before each possible
subtraction, the remainder is less than `2b`. The source has `b<=384`,
so these remainders are less than 768. These values fit `W+21` for
`W>=2`. Products, sum operands and sums have the bounds above. This
gives an arithmetic data-width construction. It does not price a tape
implementation, descriptor service, child workspace or bank traversal.

## Verification limits

The sharp values apply to one fixed normalized scalar graph and its
literal donor order. Different ordering, coefficients, graph or entrance
contract require a new check. The full source endpoint theorem is not
reproved here; the range theorem is about the supplied graph itself.
The terminal identity at the prefix peak is checked as a control.

Physical inputs on different charts involve the operators
`T_current * inverse(T_input)`. Their norms, paid-child internal states,
root scaling and precision recurrence remain separate. The present
scalar bounds cannot be substituted for those obligations without a
proof. No paid profile, caller invoice, complete kappa, selected record
or inherited assumption changes. No independent human or formal-kernel
review is claimed.
