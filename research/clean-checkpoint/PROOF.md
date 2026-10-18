# One paid clean checkpoint at the root

This note changes only the root interface of the balanced dirty product-shear
recursion in [PR628's pinned proof](vendor/pr628-DIRTY-PROOF.md) and
[dispatcher](vendor/pr628-dirty.py). It uses the exact dirty recurrence and
restoration argument recorded independently in [PR663](vendor/pr663-README.md).
The new resource is one explicitly supplied zero-filled length-`L` array.
All subtrees retain the balanced dirty recursion. Optimality below concerns
the root split in this family, with unit leaf-call prices.

## Interface and identity

Arrays belong to an abelian group, such as complex dyadic arrays under exact
addition. A leaf adds a deterministic function of its source to its target,
restores its source, and has a target-independent increment. It is also
zero-preserving: its increment at source zero is exactly zero. Its negative
call implements its exact inverse. Coefficients, phases, rounding rules and
other read-only parameters remain fixed between paired calls. All source,
target, checkpoint and borrowed arrays are distinct; no ancestor source or
target may serve as deeper scratch.
The phase array is also distinct from every mutable array. This explicit root
guard follows @androolloyd's concurrent PR673 admission finding: initial unit
modulus alone does not imply read-only phase access when Python objects alias.
The pinned original repair is retained in `vendor/pr673-phase-alias-guard.patch`.

For a dirty child, write `B(x;t)` for its increment, where `t` contains the
initial deeper scratch. The usual parent with checkpoint dirt `z0` executes

```text
z += B(x;t)
y += A(z;t)
z -= B(x;t)
y -= A(z;t)
```

Inductively each child restores its source and deeper scratch. The two `B`
calls therefore see identical inputs, restoring `z` exactly. The increment is

\[
 A(z_0+B(x;t);t)-A(z_0;t).
\]

This proves restoration and target independence without assuming linearity.
It also proves zero preservation inductively: `B(0;t)=0` makes the displayed
difference zero for every `z0,t`. Thus arbitrary deeper dirt is allowed even
though the increment can depend on that dirt.

Now supply `z0=0` and omit the last call. The remaining word is

```text
U:     z += B(x;t)
V:     y += A(z;t)
U^-1:  z -= B(x;t)
```

It restores `x,z,t` and adds `A(B(x;t);t)` to `y`. The omitted call would have
source zero; since `A(0;t)=0`, it leaves every data array unchanged. Consequently
the three-call and four-call words **at the same root split** have identical
final data arrays, including bitwise equality on a fixed dyadic grid. The
negative word is the reverse sequence of inverse calls, chronologically
`U, V^-1, U^-1`; each child's inverse must itself reverse its instruction word.
This yields exact whole-word inversion on the allowed zero-checkpoint states.

PR628's rounded leaf has zero increment at source zero: every causal state,
closure numerator, closure seed and final multiplied value is then zero.
Its stable denominator remains governed by the inherited leaf assumptions.
This observation does not independently re-prove its nonzero-source accuracy.

For linear ideal leaves the increment is the ordered product of all factors,
with the first factor in the list applied first. No commutation is needed.
Changing the root split can change the nonlinear rounded increment; it preserves
the ideal ordered product, not necessarily the rounded output of the original
balanced-root program.

Cleanliness is essential. For identity children, `x=0,z0=1`, the three-call
word increments `y` by one while restoring `z0=1`; the intended product is zero.
Supplying a zero array is a stronger storage assumption than borrowing arbitrary
dirt. Neither the identity nor this implementation erases borrowed information.

## Exact counts and the optimal root split

Count every positive and inverse leaf invocation, including invocations whose
net effect happens to be zero. The balanced dirty count is

\[
 D(1)=1,\qquad D(m)=2D(\lfloor m/2\rfloor)+2D(\lceil m/2\rceil).
\]

For `p=2^floor(log2(m))`, PR663's formula is

\[
 D(m)=3pm-2p^2.
\]

Indeed the ordinary balanced factor tree has `2p-m` leaves at depth `log2(p)`
and `2m-2p` at the next depth; each descent doubles execution multiplicity.
For a root split `k+(n-k)`, with `1<=k<n`, the clean count is therefore

\[
 F_n(k)=2D(k)+D(n-k).
\]

**Theorem.** For `n>=3`, let `q` be the unique power of two satisfying
`3q<=n<6q`. All minimizing splits are the integers in

\[
 \boxed{\max(q,n-4q)\le k\le\min(2q,n-2q)},
\]

and their common count is

\[
 \boxed{N(n)=6q(n-2q)}.
\]

For `n=2`, the sole split is `k=1` and `N(2)=3`.

To prove the theorem, the count formula gives

\[
 D(m+1)-D(m)=3\,2^{\lfloor\log_2m\rfloor}.
\]

Hence `F_n(k+1)-F_n(k)` is nondecreasing in `k`: it is twice this slope at
`k`, minus the slope at `n-k-1`. The objective is discretely convex.
On the stated interval, `q<=k<=2q` and `2q<=n-k<=4q`, so

\[
 2D(k)+D(n-k)
 =2(3qk-2q^2)+(6q(n-k)-8q^2)=6q(n-2q).
\]

The formula for `D` is valid at these closed dyadic endpoints. If the interval
has a left neighbor, its slope into the interval is strictly negative: either
`k` has just reached `q`, or `n-k` has just dropped to `4q`. If it has a right
neighbor, the outgoing slope is strictly positive: either `k` has reached
`2q`, or `n-k` has dropped to `2q`. Convexity excludes every other minimizer.

Let `k*=min(2q,n-2q)`, the largest minimizing split. All the minimizing splits
have `k<=n/2`, so this choice minimizes the largest child size. With
`h(m)=ceil(log2(m))` and `h(1)=0`, scratch consists of

\[
 1\text{ clean array}+h(\max(k,n-k))\text{ dirty arrays}.
\]

The children run sequentially and restore the same dirty pool before reuse.
For `3q<=n<=4q`, `n-k*=2q`, so the total is `1+log2(2q)=h(n)`.
For `4q<n<6q`, `2q<n-k*=n-2q<4q`, so the total is again `h(n)`.
The `n=2` case has one clean array and no dirty arrays. Thus the chosen optimum
replaces one dirty array with a clean array without increasing the total array
count. Some other cost-optimal splits require one more total array; the tie
break matters.

The relative count has the uniform bounds

\[
 \frac35\le\frac{N(n)}{D(n)}\le\frac34\qquad(n\ge2).
\]

For `3q<=n<=4q`, compare `N=6qn-12q^2` with `D=6qn-8q^2`; their ratio
increases from `3/5` to `3/4`. For `4q<=n<6q`, use `D=12qn-32q^2`;
the ratio decreases from `3/4` toward `3/5`. Equality at the lower bound
occurs at `n=3*2^j`, and at the upper bound at powers of two, including `n=2`.
These are leaf-call savings, not automatically wall-clock or precision savings
by the same percentage.

At the seed-selected generic case `n=54`, `q=16` and all optimal splits have
`16<=k<=22`. Choosing `22+32` gives `D(22)=544`, `D(32)=1024`, and

| Root and subtree policy | Leaf calls | Clean arrays | Dirty arrays |
| --- | ---: | ---: | ---: |
| Balanced dirty, `27+27` | 3136 | 0 | 6 |
| Clean root, balanced `27+27` | 2352 | 1 | 5 |
| Clean root, optimal `22+32` | 2112 | 1 | 5 |

The final row saves 1024 calls against the dirty baseline, or `16/49`
(approximately 32.653%), and another 240 against the balanced clean root.
This is a generic factor-count example, not a claimed prime-power kernel at
radix 55.

## Charged work and storage

The unit recurrence alone is not a complete machine cost. For each factor `j`,
let `t_j` bound the cost of **either signed leaf** at the selected precision
and trajectory magnitude. It must include the causal, output and restoration
passes; source/target grid scans; coefficient stability validation; scalar
arithmetic; and every phase/coefficient access performed inside that leaf.
The inherited prototype's three arithmetic passes give `3L` scalar steps per
leaf, but its additional validation scans must also be charged.

For a contiguous factor list `I`, define the weighted leaf charge

\[
 T_D([j])=t_j,\qquad
 T_D(I)=2T_D(I_{\rm left})+2T_D(I_{\rm right}),\qquad
 T_C(I,k)=2T_D(I[:k])+T_D(I[k:]).
\]

This counts both executions of the left subtree, including uncomputation.
With common leaf price `t`, it becomes `T_C=N t`. For unequal `t_j`, the
displayed recurrence still charges the work, but the unit-count split theorem
does not assert a weighted-time optimum. If signed prices differ, one may use
their maximum for `t_j`, or sum the actual signed invocation prices instead.

Dispatch costs are separate. Let `g(I,h)` charge an invocation's array-alias
and length checks, its own full unit-phase scan, factor slicing, descriptors,
counters and recursive control; let `g_C` charge the clean adapter's analogous
work apart from the separately listed zero check. The complete recursive
upper charge can be written without suppressing these costs:

\[
\begin{aligned}
 R_D([j],h)&=t_j+g([j],h),\\
 R_D(I,h)&=2R_D(I_{\rm left},h-1)
          +2R_D(I_{\rm right},h-1)+g(I,h),\\
 R_C(I,k,h)&=2R_D(I[:k],h)+R_D(I[k:],h)+g_C.
\end{aligned}
\]

Here `h` is the supplied dirty-pool depth; leaves may receive unused remaining
arrays. With `N` leaves there are exactly `4N/3` recursive invocations including
the clean root: that root has three children and every other internal node has
four. In particular, repeated dispatch phase scans cost `O(NL)` phase-validation
operations rather than a single uncharged scan. A conservative bound for the
prototype's descriptor, list and controller operations is `O(N log n)` word
operations; this is additional to arithmetic, phase access and data movement.

The full charge is

\[
 P_{\rm factors}+P_{\rm phases}+Z_{\rm provision}+Z_{\rm verify}
 +R_C+R_{\rm routing},
\]

where preparation, enclosure certification and phase generation/storage retain
their supplier costs. `Z_provision` pays for obtaining a genuinely clean length-`L`
array; if ordinary allocation and explicit initialization are available, this
includes `L` word writes. The adapter's zero verification is another length-`L`
scan. Such writes do not establish reversible erasure of arbitrary borrowed
data, and a model lacking clean-array provisioning does not meet this contract.
Routing includes actual phase/source/target access and any charged stride or
layout movement not already counted inside the leaf or preparation price; count
each cost once, and assume no free global phase table or free routing.

Besides the input and target, mutable data-array storage is `L` clean words
plus `L*h(max(k,n-k))` dirty words. At the selected optimum this has the same
total array count as the dirty baseline, but a stronger cleanliness requirement.
One also pays the inherited scalar arithmetic workspace (including the chosen
multiplication routine's workspace), indexing and recursive controller storage,
and read-only factor/phase descriptions. A materialized length-`L` phase table,
as accepted by the prototype, is additional read-only storage. Its allocation
and preparation do not disappear from the cost by calling it a parameter.
Factor lists can be described by intervals; the Python prototype instead copies
lists and retains ordinary recursion frames, whose storage and work remain paid.
An interval dispatcher uses `O(log n)` frames with `O(log n+log L)` indexing
bits per frame. With the minimal supplied dirty pool, the prototype additionally
retains `O(n+log^2 n)` list references along the active stack. Supplying extra
unused dirty arrays increases both their allocated storage and the array-check
costs; the stated array counts use the minimal pool. Precision-`w` scalar words
must also include the integer magnitude bits allowed by the inherited trajectory
bound, not just `w` fractional bits.

## Conditional pathwise execution-error bound

Retain the inherited estimates for both signs of every leaf: the ideal linear
map has norm at most `K=r/beta`, and the local rounding error is at most
`a*u*(B+1)` when the source norm is at most `B`, where

\[
 a=13(r+1)/\beta^3,\quad u=2^{-w},\quad G=2+K.
\]

Let `D0` bound all initial array norms, including the zero checkpoint, and let
`M_j` be the largest norm after `j` completed leaves. Assuming `a*u<=1`,

\[
 M_{j+1}\le(1+K)M_j+au(M_j+1),\qquad
 M_j+1\le G^j(D_0+1).
\]

In the second inequality `M_j+1` means one plus `M_j`. Compare the complete
computed instruction word with the corresponding ideal word from the same
initial arrays. If `e_j` is their completed-leaf state error, then

\[
 e_{j+1}\le(1+K)e_j+auG^j(D_0+1),\qquad
 e_N\le Na(D_0+1)uG^{N-1}.
\]

This is a pathwise estimate, so it applies to the changed root word with its
**actual** `N=2D(k)+D(n-k)`. The ideal clean word computes the ordered product
and cancels all borrowed initial dirt. A sufficient execution precision is

\[
 w\ge p+1+\left\lceil\log_2(Na(D_0+1))\right\rceil
       +(N-1)\left\lceil\log_2G\right\rceil,
\]

together with `a*u<=1` and `u<=beta^2/2`. It yields execution error at most
`2^(-p-1)`. Coefficient/phase preparation must independently supply the other
half of the error budget, scaled to the original source norm as in PR628.
No independence of rounded output from deeper dirt is asserted. Reduced leaf
count permits substitution of a smaller `N` in this inherited sufficient bound;
it does not change its asymptotic precision order or independently establish
the supplier's leaf-accuracy assumptions or fast-arithmetic implementation.

## Scope of the result

This is an algebraic root-interface result with explicit storage and cost
obligations, supported by a written all-`n` argument and finite executable
checks. The requested `n=2..256` enumeration is bounded verification of the
split theorem, not an unrestricted search. Mathematical review here was by
another Codex agent; no human review or formal proof-assistant certification
is claimed. There is no new kappa, common-label Clifford realization,
bit-reversible arithmetic compiler, complete multiplication reduction, or
all-size fixed-tape theorem. The clean-array supply, physical routing and
inherited analytic interfaces remain explicit obligations.
