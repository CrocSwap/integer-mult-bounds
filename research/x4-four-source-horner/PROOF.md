# Shared Horner work for at most four immutable sources

This is a finite scalar-circuit construction on the pinned historical PR799
X4 backward program. It extends Ross Richardson's PR945 pair mechanism to
three and four sources, using the existing PR696 copy/unit lowering as the
baseline. The exact repository base is
`007664306fff84fbb1c9a1b4053b69f439764034`; input byte and Git-object bindings
are recorded in `SOURCES.json`. It does not change the selected certificate or
claim a new kappa.

## Eligibility and complete boundary identity

A candidate is a consecutive window of two, three or four scalar ADD events

`T <- T + q_i S_i`,

with one identical positive, nonzero frame label. Every `q_i` is a nonzero
dyadic rational. All sources are distinct, none is the target, and neither
the target nor any source is the private coefficient register `W`. No scale,
copy, clear, phase, centre, climb, adapter or other event may intervene.
Consequently every source is immutable throughout the window. Repeated-source
aggregation, source mutation, frame changes and nonconsecutive grouping are
outside this candidate class.

Write `q_i = sign_i a_i / 2^d_i` in reduced form, with `a_i > 0`. Define

`k = max_i d_i`, `A_i = a_i 2^(k-d_i)`,
`b = max_i bit_length(A_i)` and `P = sum_i popcount(A_i)`.

Choose the first source whose `A_i` has its top bit set. Let `sigma` be that
coefficient's sign and initialize `W` by a charged COPY from that source.
Process all remaining set bits in descending bit position. Between positions,
double `W`; for each set bit, add or subtract its source according to
`sigma * sign_i`. After the last bit, the invariant is

`W = sigma sum_i sign_i A_i S_i = sigma 2^k sum_i q_i S_i`.

Apply `k` halvings, accumulate `sigma W` into `T`, and clear `W`. Choosing the
leading coefficient's sign as the common sign avoids an extra negation even
when every highest-position contribution is negative. The complete map is

`(T, S_1, ..., S_m, W) -> (T + sum_i q_i S_i, S_1, ..., S_m, 0)`.

The entry value of `W` may be arbitrary: COPY overwrites it. The final CLEAR
is charged and erases private work; it does not restore private dirt. The
target may also be arbitrary, and no source is changed. The identity is over
the rationals and applies separately to real and imaginary components.

The old sequence has the same map and clears `W` after each ADD. The candidate
clears it at the end of the whole window. The states agree at that boundary,
but need not agree at the removed internal macro boundaries. Substitution is
valid in the scalar event projection because no intervening event observes
those internal boundaries. Repeating this argument over disjoint windows
preserves the final scalar map.

## Full arithmetic price and source access

The exact count per real component is

| Operation | Count |
| --- | ---: |
| Initial source COPY | 1 |
| Doublings between bit positions | `b - 1` |
| Other signed source additions | `P - 1` |
| Halvings | `k` |
| Signed target accumulation | 1 |
| Final private CLEAR | 1 |
| **Total** | **`b + P + k + 1`** |

Each source access is explicit: there are `P` reads of source operands in
this word, including the initializing COPY. Shifting a numerator to align
denominators does not change its popcount. Thus grouping preserves the number
of nonwork source-operand occurrences from the corresponding PR696 words.
It saves shared shifts, target accumulations and clears; it does not obtain
free source access. No new helper or second coefficient register is used.
The complex count is twice the per-component count.

For the complete backward scalar projection, the recorded count changes
from 71,837 to 60,813 per component, or **143,674 to 121,626** across both
components. The explicit source-operand count remains **19,723** per component.
Counting one read for COPY and unary operations, two for ADD/SUBTRACT and zero
for CLEAR, total operand reads change from **73,196 to 65,431**. These are
literal arithmetic operand occurrences, not a physical source-access or
memory-movement invoice.

All non-scalar events remain identical and in order. In particular the recorded
paid child profile remains `{1:2548, 2:338, 3:430, 4:194, 5:56, 8:8}`. This
retains the declared child, centre, phase and frame schedule; it does not
independently admit the replacement to the native or hosted supplier compiler.

## A strict separation from pair partitions

Zero-based backward program events **9519 through 9522** have frame **37**,
target `L227`, sources `L224, L81, L57, L92`, and coefficients

`(-1/2, +1/2, -1/2, +1/2)`.

The four-source word has `b=1`, `P=4`, `k=1`, so costs **7** primitives per
component. A PR696 singleton costs 4, while any shared-Horner pair of these
terms costs 5. Even allowing every partition into arbitrary singles and pairs,
and deleting every intermediate work clear between groups, the minimum is
`5 + 5 - 1 = 9`. A pair with two singletons costs at least 11, and all
singletons cost 13 under the same generous clear discount. The quartet is
therefore strictly better than every partition in that pair/singleton class.
The first three events similarly cost 6 jointly versus at least 8 for pairs
and singletons after clear discounts. These are examples of the larger
candidate class; they are not claims that the optimal global recipe selects
these particular overlapping windows, or lower bounds for arbitrary circuits.

## Exact selection within a stated finite class

The complete census contains **16,431** compatible windows: 6,112 pairs,
5,455 triples and 4,864 quartets. The stopping rule is completion of this
census and one exact interval optimization; there is no stochastic circuit
search. The OS assignment seed 22 chose this object and the fan-in cap four.

Let `g(i,m)` be the PR696 primitive price of the original length-`m` window
starting at event `i`, minus the joint word's price. Admit only windows with
`g(i,m) > m-1`, so their saving strictly exceeds the saving from merely
omitting the window's `m-1` internal work clears. All events outside selected
windows retain the baseline lowering. For suffix optimum `F(i)`,

`F(i) = max(F(i+1), max_admitted_m [g(i,m) + F(i+m)])`,

with zero after the final event. Every legal disjoint selection either skips
event `i` or starts one admitted window there, which proves the recurrence by
backward induction. Ties deterministically skip, then prefer the shorter
starting window. The selected recipe has **1,174** windows: 58 pairs, 147
triples and 969 quartets, saving **11,024** primitives per component.

This proves optimal disjoint selection only among the admitted windows with
the unchanged lowering elsewhere. It does not prove unrestricted optimality
for fan-in four, arbitrary rescheduling, signed-digit synthesis, general
circuits, or a combined pass that also removes every other redundant clear.

The same domain and recurrence restricted to pairs produce PR945's **13,072**
two-component saving. This construction saves **22,048**, an additional
**8,976** in the backward orientation. These are alternative recipes, not
additive passes. The retained forward orientation costs **143,658**. The
orientation maximum consequently falls only from **143,674 to 143,658**;
PR945 already achieves that maximum. The additional backward reduction gives
no further improvement to the maximum and no new recurrence exponent.

## Grid containment and magnitude are separate obligations

Consider exact symbolic rows in the common formal input basis at a window's
entry. At every integer Horner prefix, `W` is an integer linear combination
of immutable source rows. Its dyadic denominator depth is therefore no
greater than the largest source-row denominator depth. After the full integer
numerator is formed, the value after `h` halvings, for `0 <= h <= k`, is

`W = sigma 2^(k-h) sum_i q_i S_i`.

Each summand is an integer multiple, up to sign, of the old per-source final
work value `q_i S_i`. For unit coefficients the source itself supplies the
same grid bound. Sums of dyadic rows cannot have a finer denominator than the
finest summand. The target is untouched until its final update, which equals
the old complete-window target. The arbitrary entry `W` also appears in the
old entry state. Thus the largest exact row-coefficient denominator depth
does not increase under substitution.

This does **not** establish containment of magnitudes in the old prefix
trace. Joint work can sum several source magnitudes, and common-denominator
alignment can create larger integer intermediates. PR696's single-source
prefix-subsequence proof cannot be reused for this purpose. A positive work
envelope is bounded locally by `sum_i A_i B_i`, where `B_i` bounds source `i`,
and the target endpoint envelope is `B_T + sum_i abs(q_i) B_i`; these must be
checked in the actual program, not assumed smaller.

The complete exact scalar replay includes **737** formal columns: 728 logical
registers, eight arbitrary private centre inputs and arbitrary `W`. Both the
baseline and candidate attain exact maximum row L1 norm **5,338,828** and
maximum dyadic denominator exponent **19**. The separately implemented
integer-row replay agrees. Its positive scalar-prefix envelope is also
unchanged at **48,299,247,699,832,632,898,063 / 16**. Exact row norm and the
positive envelope are different quantities; both account for coefficient-work
intermediates. The replay verifies the backward shear, restoration of the
504 public dirty helpers, and erasure of the nine private inputs at exit.

These are exact-arithmetic scalar facts. They do not prove a 192-bit runtime
payload admission, a rounding-error budget, or the all-size precision/tape
theorem. In particular, equal global maxima do not say every individual new
work row occurs in the old trace.

## Remaining interfaces and provenance

Every primitive is emitted with the window's common frame label, and no source
is written. This avoids an explicit frame transition inside a replacement.
It does not by itself prove the physical realization, common-label access,
mutable-source contract, or native/hosted source-access pricing. The inherited
emitter advertised private clearing after each scalar macro; the new typed
group would instead advertise clearing after each joint window. Production
integration must represent and admit that changed boundary before treating
the word as a drop-in supplier replacement.

The abstract non-scalar profile, helper allocation and schedule are retained;
whole-call hosting, physical/frame/phase admission, global invoices, uniform
compilation, rounding/tape and analytic transfer remain unresolved by this
package. A finite all-column replay is not a formal proof of the complete
multiplication theorem. No current frontier, native supplier implementation,
or `upstream/` file is changed.

Credit goes to Ross Richardson's PR945 for shared pair Horner work, Sagar
Thakrar's PR696 for the copy/unit lowering, icekylinx's scalar primitive and
coefficient-stream lineage, Jeremy Kothe's PR799 X4 program and its retained
construction ancestry. Prepared for ToikY with substantial OpenAI Codex
assistance, including separate implementation and mathematical review.
Apache-2.0; no independent human review is claimed.
