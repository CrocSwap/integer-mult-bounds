# An all-length transport floor for the 128 PR4470 receiver windows

**Result.** In each of the 128 windows defined below, no finite word of shears
on the same three persistent fields can lower the incumbent's paid transport
cost, provided frames grow monotonically and the entrance/exit frames stay
fixed. There is **no word-length or scalar-coefficient bound**. The result holds
for every nonnegative concave rank price `f` with `f(0)=0`, in particular
`f(r)=r^(1-C)` for every `0<C<1`. The incumbent attains the floor, so the
optimistic gain ceiling is exactly zero.

This is a source-bound, computer-assisted scoped obstruction with a written
containment argument. It is author-checked, not formal-kernel acceptance,
independent human review, a global supplier optimum or a new kappa.

## What this adds

[Chris R / Clear1nsight's #4546](https://github.com/CrocSwap/integer-mult-bounds/pull/4546)
at `55b8d34c82fc4df6499c5037e156db6e990b96fe` introduced the fixed-boundary
three-field relaxation and excluded length-at-most-four unit-shear rewrites in
twelve windows at `C=0.00302015`.
[Ryanson Jonathan's #4567](https://github.com/CrocSwap/integer-mult-bounds/pull/4567)
at `50fedd98cda709707e4291c542e20ead96bcc786` extended it to all 128 windows,
unit/nonunit finite alphabets and lengths five/six. That package explicitly
left its all-length explanation unproved. Its exact nonunit coverage is
`|c|<=2` through length six and `|c|<=3` through length five.

This package replaces word enumeration by a finite-state closure which forgets
coefficients, directions and most endpoint constraints. An exact concave-cost
comparison proves the floor for every accepted relaxed path. No search,
relaxation, price or acceptance function from either predecessor is imported.
Their model and interpretation are credited, not claimed as newly invented.

The submission refresh found concurrent investigations
[#4573](https://github.com/CrocSwap/integer-mult-bounds/discussions/4573),
[#4574](https://github.com/CrocSwap/integer-mult-bounds/discussions/4574) and
[#4577](https://github.com/CrocSwap/integer-mult-bounds/discussions/4577), all
under the same donor account. This package is **independent corroboration and
a separately reviewable certificate**, with no exclusive novelty or priority
claim. Its code and proof were developed before reading those claims. #4577
reports a directed-dependency graph with 1,303 states; the present more
permissive bidirectional propagation has 1,496 states and the same 239 terminal
profiles. The separate integer Dijkstra checks add an algorithmically distinct
check of the cost floor. No concurrent artifact is imported or certified here.

Canonical base is `f626db5c3a3d781d8f7695038776c621651f75e1`, priority revision 7.
The selected record there is still `23/10000`. The constructor source is
[Cinna Davis's #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470),
head `b9a13c1673e0e9697de410de16e8bbf3207a7363`, retained on main.
Seven exact constructor inputs are authenticated by Git blob and SHA256 in
`SOURCES.json` and declared in `VERIFY.json`. The constructor only supplies
the instance; all window extraction and cost reasoning are implemented here.

## Contract

Each window replaces consecutive persistent-field additions
`a += ca*x; b += cb*x`, where `ca,cb` are nonzero unit coefficients and
`a,b,x` are distinct arbitrary-input fields. Eligibility is exactly the #4546
contract: forward phase `B` or `cleanup_tail`, adjacency after removing emitted
`climb` records, and no intervening scalar or warp. There are 123 windows in
phase B and five in cleanup_tail.

The entrance frame is the field's frame before the transports into the first
contact. Its exit is the frame required by its next scalar contact or warp
entry, or its final frame if it has no later use. `RESULT.json` records each
window's index, roles, signs, entrance/exit bases, original contacts, paid gaps
and full relaxed profile set. The inherited native endpoint/physical validity
of the whole #4470 supplier is not replayed here.

A competitor is any finite word `y_i += c*y_j`, `i!=j`, on these three fields,
with the same arbitrary-input endpoint. Coefficients can be arbitrary rational
numbers (indeed the dependence argument does not need a bound on their size).
Every contact uses one common binary frame for its two operands. Along each
field, frames only grow by inclusion from its fixed entrance `S_i` to its
fixed exit `E_i`. Each positive frame-dimension increase `r` pays `f(r)`;
terminal moves into the required exits are included. Scalar-height, scalar
execution and other nonnegative charges are omitted in the competitor's favour.
The conclusion is about this transport invoice; it does not price a complete
changed supplier or rule out savings in other cost categories.

## Proof of the relaxation and the all-length conclusion

**1. Static contact bounds.** At a contact between fields `i,j`, its actual
frame `F` contains `S_i+S_j` and lies inside `E_i intersect E_j`. If the former
is not contained in the latter, that pair cannot contact at all. Otherwise put
`l_ij=dim(S_i+S_j)` and `u_ij=dim(E_i intersect E_j)`. With current dimensions
`d_i,d_j`, the contact dimension lies between `max(l_ij,d_i,d_j)` and `u_ij`.
The relaxation enforces only these dimensions and static inclusions, discarding
the stronger simultaneous geometric conditions. Thus it can admit spurious
paths, but cannot exclude a legal contact sequence.

**2. Chronological source dependence.** Initially only field `x` depends on
the arbitrary initial value of `x`. Mark it reached. At every contact, mark
both operands reached if either was reached before it. Actual propagation is
directed and can cancel; this rule deliberately overestimates it. Inductively,
every field with an actual nonzero dependence on the initial `x` is marked.
The required endpoint has nonzero dependence on `x` in all three fields, so
every valid final state must mark all three. An undirected connected contact
graph alone is insufficient: contacting `a,b` before `b` obtains `x` does not
retroactively deliver `x` to `a`.

**3. States and charges.** A state consists of the three current dimensions,
the reached mask, and the sorted multiset of positive transport gaps already
paid. It starts at `(dim(S), {x}, empty)`. A contact of height `h` replaces
both operand dimensions by `h`, adds their positive gaps to the multiset and
updates the reached mask. Any state with all three fields reached can finish
by adding the three positive gaps from its current dimensions to `dim(E)`.

Every actual contact sequence maps to this graph. If an actual implementation
splits a move between consecutive contacts into several monotone moves, the
graph merges these gaps. Concavity and `f(0)=0` give
`f(r_1+...+r_t) <= f(r_1)+...+f(r_t)`, so this merging only lowers the relaxed
cost. Scalar steps without a frame increase are retained as zero-cost edges.
The relaxed completed profile therefore costs no more than the actual path.

**4. Finite closure covers every finite length.** Every dimension is an
integer in its fixed entrance/exit interval; the reached mask has only eight
values. At every state the sum of paid gaps is exactly the increase in the
sum of dimensions, bounded by `sum_i(dim(E_i)-dim(S_i))`. Only finitely many
integer multisets have such mass. Hence the state space is finite, including
zero-cost cycles. The worklist starts at the initial state and continues until
there is no unseen successor. A separate pass verifies closure under every
allowed transition. Induction on word length then puts every finite path in
the computed set. There is no depth limit, numerical stopping tolerance or
coefficient alphabet in this computation.

**5. Exact comparison for all concave costs.** Let `v` be a completed rank
multiset and `T_k(v)=sum_{r in v} min(r,k)`. Every completed profile has the same
total rank mass. For every relaxed profile `v`, the verifier checks exactly

`T_k(incumbent) <= T_k(v)` for all integer `1 <= k < max_rank`.

To see why this suffices without evaluating a real power, put
`s_j=f(j)-f(j-1)`. Concavity says `s_j-s_(j+1)>=0`, and for ranks at most `m`,

`sum f(r) = s_m * sum r + sum_{k=1}^{m-1} (s_k-s_(k+1)) * T_k(v)`.

The common mass cancels. Each remaining coefficient is nonnegative, giving
`cost(incumbent) <= cost(v) <= cost(actual competitor)`. The original two
contacts form a legal path and their exact profile is admitted in every
window, proving attainment and a zero gain ceiling. The zero-mass case is
immediate; absent ranks can be padded by zero since `f(0)=0`.

## Evidence and reproduction

Run from the repository root, Python 3.12, standard library only:

```sh
python -B scripts/research_package.py --package research/receiver-window-all-length-floor --check-only
python -B scripts/research_package.py --package research/receiver-window-all-length-floor
python -I -O -B research/receiver-window-all-length-floor/verify.py --self-test
```

The registered replay authenticates the source closure, runs only the inherited
constructor in an isolated subprocess with a fresh bytecode-cache namespace,
extracts the windows, computes every closure and compares every committed
receipt field. It does not write artifacts. `--write` is a separate authoring
option. The calculation uses integer arithmetic and exact rational sign checks;
no floating-point logarithms, solver or root enclosure is needed.

The receipt contains **128 windows, 1,496 reachable states, 4,730 transition
edges and 239 terminal profiles** (summed separately per window). The count of
profiles per window is `1:93, 2:9, 3:6, 4:2, 5:13, 7:4, 9:1`. This agrees with
the finite-profile histogram reported by #4567, but that agreement is not an
input or premise of the proof.

A separate Dijkstra implementation discards the entire paid-profile history,
rebuilds the scalar transition costs, and minimizes `sum min(r,k)` directly.
All 248 such shortest-path computations attain exactly the incumbent values.
This corroborates the profile enumeration by a second algorithm; it is not an
independently launched agent or an external review.

Controls check 894 actual geometric prefixes (496 accepting) over every
monotone boundary triple in F2^1 and all contact/frame sequences through length
three. They also test zero-cost self-loops, incompatible exits, a genuinely
cheaper rank-coalescing example, reversal of the concave order, omitted terminal
charges and the chronological-dependence mutation. In the last example,
entrance dimensions `(0,0,1)` and exits `(2,1,1)` have valid profile `(1,1,1)`;
omitting the reach requirement admits the false cheaper profile `(2,1)`.
These small tests support implementation correctness; the arbitrary-length
argument is steps 1–5, not an extrapolation from the tests.
Another 22,621 exact directed unit-shear prefixes through length four check
that scalar cancellation never creates an unmarked dependence on `x`.

The registered replay and optimized self-tests passed locally on Windows with
CPython 3.12.0, using only the standard library. The registered computation
takes a few seconds here. Maintainer scientific review and hosted CI are
separate from this local evidence.

## Scope, coordination and limitations

The result is local to each fixed three-field window. It does not cover extra
owned/borrowed fields, frame decreases or resets, changed boundaries, changed
warp words, larger/nonadjacent windows, or joint rewrites. Overlapping window
results cannot be added. A negative result in this model is not a universal
barrier for integer multiplication. No complete supplier, precision, stock,
physical endpoint or selected cold replay was run.

Handoff-first selection followed #4567's explicitly remaining all-length
question. The `independent-moment` card is refined to that obligation;
`TASK.json` preserves its original card and the rationale. The optional family
decision is **narrow**: prove or falsify this missing implication, then stop;
do not expand another finite-word census. All required transport and exit costs
are present; actual geometry is relaxed, and scalar/physical/compiler costs
remain outside this local invoice rather than being declared free in a supplier.

[Discussion #4572](https://github.com/CrocSwap/integer-mult-bounds/discussions/4572)
is the canonical claim/result thread, with a short reply to the #1166 handoff.
The initial overlap helper paginated 355 open PRs and 3,470 Discussion records;
it reported incomplete local notes in this sparse checkout. Relevant #4470,
#4546/#4567 source, README and ledger context were inspected separately. This
does not establish exhaustive novelty. The generic selected baseline was
attempted but could not inspect omitted `research/kappa-0023-productive-jobs`
inputs in the sparse checkout; it is not reported as passing. This package
authenticates its own complete seven-file input closure instead.

Before submission, canonical main was fetched again and remained the base
above. #4567 had advanced to `5ac594d1bc1e6d91f20ef8157f38bb9b29768bfd`, adding
88 nonadjacent pairs with untouched intervening fields and single-contact
retiming checks; its all-length explanation was still explicitly unproved.
Those additions are distinct from the present closure of the 128 adjacent
windows. The older head above is the proposal inspected when this task began;
neither predecessor checker is a runtime input here.
The refreshed overlap corpus completed 355 open PRs and 3,486 Discussion
records at 08:04 UTC and exposed the concurrent claims credited above. Local
note coverage remains incomplete. This is the basis for the independent
corroboration framing, rather than an assertion of unique new coverage.

## Open next questions

1. **Can an extra owned field change the floor with its complete allocation and
   cleanup bill?** This changes the number of fields, outside the theorem, and
   could create contacts unavailable in this graph. First specify one window's
   fourth-field entrance, exit and allocation contract and derive the optimistic
   transport/cleanup state space. A favourable relaxed profile would still need
   exact endpoint, geometric and physical validation. No such allowance is
   supplied here.
2. **Does a joint window with a shared boundary admit a cheaper paid profile?**
   Fixing each window's exits may prevent savings across them. First select two
   overlapping windows, remove only their internal boundary requirement and
   derive the combined arbitrary-input endpoint and full external invoice.
   This is blocked on that changed caller contract, not on a longer three-field
   search within the present boundaries.

Credit Chris R / Clear1nsight (#4546 and #4543), Ryanson Jonathan (#4567),
Cinna Davis (#4470 and its retained predecessors), zxv's productive-helper,
receiver-sharing and native work, Jacob Alan Sussman, and the retained scalar,
Clifford, geometry and outer-ledger authors. Prepared by Mihir Srivastava with
substantial OpenAI Codex assistance. Apache-2.0. Frozen predecessors and the
selected frontier are unchanged.
