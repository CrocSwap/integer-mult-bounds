# Exact owner reuse and concave-cost matching

## 1. Objects and interface assumptions

The parent controller has 72 ordered calls, 112 source ports, 112 target ports,
and 492 helper roles per call. The ambient dimension is 73. A pending-child
group is a triple

$$
g=(\text{owner replica},\text{child},\text{port}).
$$

The parent window catalogue gives group capacity $C_g$, together with the call
times at which its physical stream is idle. The map from a group to its
physical family is

$$
F(g)=896\,\text{owner replica}
  +112(2\,\text{pair(child)}+\text{side(child)})+\text{port}.
$$

At every call in this particular parent geometry, at most one pending child of
a physical family is eligible. Both the matcher and the independent frozen
audit check this condition. They also exclude both active data families of the
call. Consequently, injective assignment to eligible groups is equivalent to
assignment to distinct idle physical families at that call.

Helper $h$ requests an integer width $w_h$, read afresh from the new local
word as the final-frame dimension minus the start-frame dimension. Native
program profiles are also recomputed from their paid edges. The finite local
compiler supplies the normalized helper chart and verifies its warm-start
semantics. A hosted width is a reservation in the pending child's address
coordinates on an existing physical stream; it is not a new physical stream.

This proof concerns the discrete assignment and its moment contribution. It
uses the parent windows as input. Independent global admission must verify
those windows against the actual controller and construct the actual
73-column charts for the fresh native local word.

## 2. Feasible shrinking on the original families

For one call, sort the old slot widths and the new helper widths increasingly,
breaking ties by the old or new helper number. Suppose the new width in each
position is no larger than its matched old width. Assign that helper to the
matched old slot.

This operation preserves the call time, stage, replica, pending child, port,
owner replica, and physical family. It preserves the set of 492 distinct
helper-owner families at the call, so the old window and active-data
exclusions still hold. In each pending-child group, the sum of new widths is
no larger than the old sum, hence remains within capacity.

Now order the assignments in each group consistently and replace their
offsets by consecutive prefix sums. The occupied sets become pairwise
disjoint intervals whose union is exactly a prefix of length
$U_g=\sum w_h\le C_g$. The idle child retains rank $C_g-U_g$, with pending
offset $U_g$. Thus the shrinking operation has a direct capacity proof; it
requires neither an owner solver nor any change to the controller.

The seed constructor applies this termwise argument to the 71 former `jp8`
calls. It keeps the remaining `ck` call provisionally unchanged. Two optional
fixed-family assignment passes redistribute the available capacity before
freezing the seed. Their result is audited using the same integer constraints.

## 3. One call with all other calls fixed

Fix one call $t$. Remove its existing assignments while keeping every other
call fixed. For each eligible group, define the available capacity

$$
c_g=C_g-\sum_{\substack{\text{assignments in }g\\\text{from calls other than }t}}w.
$$

The call must assign each of its 492 widths to a distinct eligible group with
$w\le c_g$. Unused groups can be viewed as receiving a dummy width zero.
After the assignment, group $g$'s idle rank is $c_g-w_g$. For any function
$\phi$, the portion of the idle objective affected by the call is exactly

$$
\sum_{g\text{ eligible at }t}\phi(c_g-w_g).
$$

All other idle contributions, and all local paid-edge contributions, are
constant in this single-call problem.

### Greedy rule

Sort eligible capacities increasingly. At each capacity, assign the largest
remaining helper width that fits; assign zero if none fits. Continue through
the remaining capacities.

This rule has no floating parameter. Equal-capacity tie choices are used only
to limit changes to physical owners and make the artifact deterministic.

### Exchange lemma

Take two capacities $c_1\le c_2$ and two widths $w_1\le w_2\le c_1$. The
assignment of $w_1$ to $c_1$ and $w_2$ to $c_2$ has residual pair

$$
(c_1-w_1,\ c_2-w_2).
$$

Exchange the widths. Feasibility is preserved, and the new pair is

$$
(c_1-w_2,\ c_2-w_1).
$$

The total is unchanged. The first new component is no larger than either old
component, and the second is no smaller than either old component. Therefore
the new pair majorizes the old pair. Every concave $\phi$ has weakly smaller
sum on the new pair.

### Consequence: feasibility and optimality

Start from any feasible complete assignment. At the smallest remaining
capacity, its assigned width is no larger than the largest remaining width
that fits. The greedy width occurs at some later capacity. If the two differ,
the exchange lemma moves that width to the current capacity while preserving
feasibility and weakly decreasing every concave objective. Fix this first
position and repeat on the suffix. Dummy zero widths cover unused groups.

Thus the greedy procedure succeeds whenever a feasible assignment exists, and
its remainder vector majorizes that of every feasible assignment. It
simultaneously minimizes every concave remainder objective for this call.
This proof depends on the absence of any eligibility restriction beyond the
capacity and the already fixed call window; that property is explicitly
checked for the present geometry.

## 4. Exact majorization receipts

Let $a_r$ and $b_r$ be the old and new remainder histograms for one update,
including zero remainders. When the helper-width multiset is unchanged, their
total numbers of groups and total ranks agree. Every remainder lies between
0 and 48. The implementation checks, with integers, that for each
$k=0,1,\ldots,48$,

$$
\sum_r b_r\max(r-k,0)
\;\ge\;
\sum_r a_r\max(r-k,0).
$$

These are the stored stop-loss margins. Between integer breakpoints the
difference is linear, so checking all integer breakpoints checks every real
threshold. With equal sums and equal lengths, the inequalities are the
standard majorization criterion: the new vector majorizes the old one.

The transcript contains 288 such equal-width updates: four passes through 72
calls. A single preceding update replaces the seed's last `ck` width multiset.
That bootstrap has different total width, so it is checked for exact
feasibility and is not represented as an equal-sum majorization step.

`reproduce.py` reruns every update and compares the full transcript's semantic
hash. Independently, `audit_frozen.py` removes each final call in turn, computes
all available capacities directly from the frozen owner map, runs a separate
histogram-only greedy calculation, and verifies that it returns exactly the
existing remainder histogram. This checks all 72 final coordinate optima
without relying on the transcript or the discovery seed.

## 5. Relation to the global moment

For ambient dimension $M=73$, define

$$
\phi_b(r)=r\bigl((73/r)^b-1\bigr)
          =73^b r^{1-b}-r,\qquad \phi_b(0)=0.
$$

For $0<b<1$, this function is continuous at zero and strictly concave on
positive ranks, because

$$
\phi_b''(r)=-b(1-b)73^b r^{-b-1}<0.
$$

Once all calls use the new provider, the local paid profile is fixed and every
accepted owner update preserves the global paid rank mass. The exchange and
majorization arguments therefore weakly decrease the global moment pressure
for every $b\in(0,1)$ simultaneously. A strict histogram majorization strictly
decreases that pressure. No estimated root, derivative, or floating cost is
needed to establish the improvement of these updates.

For the frozen map, the exact paid rank mass is 520704, so

$$
73\cdot7168-520704=2560.
$$

The final profile is recomputed from 72 copies of the new local paid profile
and from the actual remaining rank in every pending-child group. Numerical
roots printed by the matcher are screens only. Exact moment bounds and their
combination with the bit supplier are performed by the package's admitted
global pipeline.

## 6. Determinism and fixed-point scope

The implementation keeps the parent call order, alternating a forward pass
and a reverse pass. Within equal-capacity groups, it first prefers the old
assigned width, then other previously used owners, and finally physical-family
order. It retains an old helper number when possible and otherwise takes the
smallest unassigned helper number of the required width. These tie rules
affect the frozen map, but not the single-call optimum remainder histogram.

The recorded run has three passes with strict improvements. Its fourth pass
has zero strict changes and zero changed helper owners. Hence the recorded map
is a fixed point of the implemented call update. The separate final audit
also establishes the stronger cost-level statement that every individual call
already minimizes every concave remainder objective with the other calls
fixed.

Calls share capacities. Simultaneously changing two or more calls could
possibly improve on a coordinate fixed point. The argument makes **no claim
of joint global optimality**, and the frozen artifact does not depend on such
a claim.

## 7. Fields to regenerate for actual global admission

| Field or object | Required action |
| --- | --- |
| Call `stage`, `replica`, `time` and parent windows | Preserve the parent controller |
| Helper number and width | Read the new local signature and use the nominated assignment |
| `owner_replica`, `child`, `port` | Use the final legal group selected by the matcher |
| `copy`, `family` | Recompute from the selected group, then check uniqueness and active-data exclusion |
| Helper `offset` | Compact all widths in each group into a disjoint prefix |
| Idle `rank`, `hosted`, `pending_offset` | Recompute from the actual occupied prefix |
| Per-call width lists and global paid profile | Recompute from the fresh local programs and actual cells |
| Provider bindings, center carriers and program hashes | Bind the freshly checked provider; do not retain stale parent IDs or hashes |
| Actual 73-column owner charts and their digests | Generate afresh from the selected child, port, offset, width and spectator coordinates |

The new construction uses different center carrier registers, including source
registers. Its ordered center frames and checked operator, rather than old
carrier numbers, are the semantic interface. The hosting proof does not waive
that interface check. The signature-only intermediate PLAN produced during
replay is explicitly marked as such and is never a substitute for fresh
provider binding or global phase admission.
