# Incident residuals and minimum local ranks

This note concerns the 692 completable radical-one source spans in the fixed
`ParitySide(10)` circuit. It is a local geometric result, not a compatible
assignment of frames to that circuit, a transfer primitive, an operation
invoice, or a multiplication-bound improvement. All dimensions and counts
below are exact over the binary field.

## Definitions and the finite domain

Let `V = F2^10` have its standard dot product, and let `j = 1023` be its
all-ones characteristic vector. Integer masks encode vectors. At an active
node, `S` is the set of actual ancestor source labels and `T` is the set of
actual descendant target labels. Set `A = span(S)` and `B = span(T)`.
Every label in `S` and `T` is a weight-three, hence norm-one, vector.

A separating frame is a nondegenerate subspace `U` with
`A subset U subset B-perp`. Its incident source residual at `s in S` is
`U intersect s-perp`. Its incident target residual at `t in T` is
`U-perp intersect t-perp`. These are the residuals from the source line to
`U`, and from the target line to the reverse-complement frame `U-perp`.
Call `U` incident-safe if each of these residuals is zero or nonalternating.
Nondegeneracy of the residuals follows from the norm-one lines and the
nondegeneracy of the containing frames.

The domain requires `A perpendicular B`, `A intersect B = {0}`, and
`dim rad(A) = 1`. It consists of 692 nodes, rather than 692 distinct source
subspaces: different nodes can have the same source span or different actual
incidences. The predecessor's two impossible sandwiches and 1,577
nondegenerate-source nodes are outside this domain.

The sandwich minimum theorem used below is established in ToikY's
[PR #972](https://github.com/CrocSwap/integer-mult-bounds/pull/972), pinned at
`f39f92a085fc95fe4245b06d4a695739d79763bc`. It gives the minimum separating
dimension `dim A + dim rad(A)`. The present note adds complete incident
residual tests and minimum incident-safe ranks on the stated radical-one
domain; it does not repeat that contribution's all-node census.

## Exhausting all minimum separating frames

Write `a = dim A`, `b = dim B`, and `rad(A) = span(r)` with `r != 0`.
Every minimum frame has the form

    U_z = A + span(z),  z in B-perp,  r dot z = 1.

To prove sufficiency, let `x = x_A + c*z` be in the radical of `U_z`.
Pairing with `r` forces `c = 0`. Pairing with `A` then places `x_A` in
`span(r)`, and pairing with `z` forces `x_A = 0`. Thus `U_z` is
nondegenerate and has dimension `a+1`.

Conversely, a nondegenerate `(a+1)`-dimensional frame containing `A` has
the displayed form, and its additional vector must pair nontrivially with
`r`; otherwise `r` would remain in its radical. This proves coverage, not
just a construction of some frames.

The functional `z -> r dot z` is nonzero on `B-perp`, since otherwise
`r` would lie in `(B-perp)-perp = B`, contrary to `A intersect B = {0}`.
There are therefore `2^(10-b-1)` permitted vectors `z`. Two such vectors
give the same frame exactly when they differ by an element of `A`:
the quotient `U_z/A` is a one-dimensional binary space, with a unique
nonzero coset. Each frame has exactly `2^a` representatives. Consequently
the exact number of distinct minimum frames at the node is

    2^(10-a-b-1).

Signs of scalar coefficients do not change binary source lines. Actual
label sets are essential; replacing them by all vectors of their spans
would impose additional, unrequested incidence conditions.

## Characteristic vectors give exact incident tests

For a nondegenerate space `E`, write `w_E` for its unique characteristic
vector, characterized by `w_E dot x = x dot x` for every `x in E`.
For a nondegenerate subspace `L` of `E`, the orthogonal decomposition
`E = L direct-sum (E intersect L-perp)` shows that the latter summand
is alternating exactly when `w_E in L`.

For a norm-one line `L = span(s)`, `w_E` cannot be zero, since it pairs
to one with `s`. Thus a **nonzero** residual `E intersect s-perp` is
alternating exactly when `w_E = s`. If `dim E = 1`, the residual is zero
and is accepted even though this equality holds. The zero-residual
exception must not be dropped.

The orthogonal decomposition `V = U direct-sum U-perp` gives

    w_(U-perp) = j + w_U.

Hence the complete incident test is:

* Reject at source `s` exactly when `dim U > 1` and `w_U = s`.
* Reject at target `t` exactly when `dim U-perp > 1` and `j + w_U = t`.

The characteristic vector of a minimum frame has an especially small
search domain. The vectors `w in A` satisfying

    w dot x = x dot x for every x in A

form a pair `{w0, w0+r}`. Existence follows because the linear functional
`x -> x dot x` vanishes on the radical, and the image of the bilinear map
`A -> A*` is precisely the annihilator of that radical. Its solution set
is a coset of the one-dimensional radical.

In any `U_z`, its characteristic vector belongs to `A`: write it as
`x_A + c*z` and pair with `r`; the required value is `r dot r = 0`, so
`c = 0`. Exactly one of the two candidates also satisfies
`w dot z = z dot z`, because the candidates differ by `r` and
`r dot z = 1`. Explicitly,

    w_(U_z) = w0          if (j+w0) dot z = 0,
              w0 + r      otherwise.

This selector is constant on each coset `z+A`, so it is a well-defined
test of the frame. The two possible characteristics need not both occur.
On the permitted affine set of `z`, the selector is constant exactly
when `j+w0` belongs to `B+span(r)`; otherwise both values occur equally
often. This follows by restricting the functional to the translation
space `B-perp intersect r-perp`, whose annihilator is `B+span(r)`.

## Exact minimum-frame census

Exhausting the described cosets gives 3,096 distinct minimum frames at
the 692 nodes. Exactly 2,538 frames pass every actual source-line and
target-line test. There are 158 source-only failures, 400 target-only
failures, and no frame failing both kinds of incidence.

| dim A | dim B | Minimum frames per node | Safe minimum frames per node | Nodes |
|---:|---:|---:|---:|---:|
| 2 | 4 | 8 | 0 | 10 |
| 2 | 5 | 4 | 0 | 2 |
| 3 | 1 | 32 | 32 | 16 |
| 3 | 5 | 2 | 2 | 2 |
| 4 | 4 | 2 | 1 | 50 |
| 4 | 4 | 2 | 2 | 80 |
| 4 | 5 | 1 | 0 | 20 |
| 4 | 5 | 1 | 1 | 2 |
| 5 | 1 | 8 | 8 | 170 |
| 5 | 2 | 4 | 4 | 20 |
| 5 | 3 | 2 | 2 | 40 |
| 6 | 1 | 4 | 0 | 100 |
| 6 | 2 | 2 | 2 | 10 |
| 7 | 1 | 2 | 2 | 100 |
| 8 | 1 | 1 | 1 | 70 |

Thus 560 nodes admit a safe minimum frame: 510 accept every minimum
frame and 50 accept some but not all. The other 132 accept none. These
counts were also obtained by an independent in-memory enumeration using
explicit XOR-closed sets and all 1,024 ambient masks. That cross-check
shared the scalar DAG generator, but did not use the producer's frame
enumerator. It is not independent human peer review.

## Minimum incident-safe dimensions, including larger frames

An even-dimensional nondegenerate `U` is automatically incident-safe
here. Indeed, both `U` and `U-perp` have even dimension because the
ambient dimension is ten; removing any contained norm-one line leaves
an odd-dimensional nondegenerate residual. An alternating nondegenerate
space has even dimension, so each such residual is nonalternating.
This observation does not assert that a frame of the next even dimension
exists.

For the 12 rejected nodes with `dim A = 2`, the minimum separating
dimension is three. Complete enumeration of dimension-four separating
frames gives 16 frames at each of the ten `dim B = 4` nodes and four
frames at each of the two `dim B = 5` nodes. Every one is incident-safe
by parity. Their minimum incident-safe dimension is therefore four.
There are 168 such dimension-four frames in total.

One complete way to enumerate these frames is to take every minimum
frame `U` and every norm-one vector
`q in U-perp intersect B-perp`, and form `U + span(q)`, deduplicating
subspaces. This is exhaustive: any nondegenerate frame `E` of dimension
`a+2` containing `A` contains a minimum frame `U`. Choose in `E` a
vector pairing to one with `r` to construct it. Then
`E intersect U-perp` is a nondegenerate line, and its unique nonzero
vector is one of the enumerated `q`.

The 100 rejected nodes with `dim A = 6` all have `B = span(t)` for one
actual norm-one target `t`. Every one of their four minimum
dimension-seven frames has characteristic `j+t`; equivalently, every
one fails at that target. No dimension-eight separating frame exists.
To see this, put `W = t-perp`. This is a nondegenerate
dimension-nine space with characteristic `j+t`. For any minimum `U`,
the plane `W intersect U-perp` is alternating, since `w_W = w_U`
belongs to `U`. A dimension-eight nondegenerate frame `E` containing
this `U` would require a nondegenerate line in that alternating plane,
which is impossible. Any proposed dimension-eight `E` containing `A`
would contain some minimum `U` by the partner argument above, so it
cannot avoid this obstruction by choosing different intermediate frames.

The frame `W` itself is incident-safe: its target residual is zero, and
its characteristic `j+t` has weight seven, hence cannot equal any
actual weight-three source label. The minimum incident-safe dimension
at these 100 nodes is therefore nine, two above the separating minimum.

At each of the 20 rejected nodes with `dim A = 4` and `dim B = 5`,
the only minimum frame already equals `B-perp`, of dimension five.
It fails a source incidence. Any nondegenerate frame containing `A`
has dimension at least five, while any separating frame has dimension
at most five. Thus **no incident-safe separating frame of any dimension
exists** at these 20 nodes.

Together with the 560 nodes already safe at the separating minimum,
this exhausts the original 692-node domain:

| Local conclusion | Nodes |
|---|---:|
| Safe at minimum separating dimension | 560 |
| First safe one dimension above minimum | 12 |
| First safe two dimensions above minimum | 100 |
| No incident-safe separating frame of any dimension | 20 |

Among the 672 locally feasible nodes, the minimum incident-safe
dimension histogram is `4:30, 5:132, 6:230, 7:10, 8:100, 9:170`.
These are geometric dimensions and node counts, not paid helper counts
or a recursive resource bound.

## Concrete witnesses and obstructions

At node **229**, `S = {38,49}`,
`A = span(49,23)`, and `B = span(896,448,192,64)`.
Its actual targets are `{448,704,832,896}`. Its radical generator is
23. Each of its eight dimension-three frames has characteristic 38 or
49, four frames of each type. Both characteristics are actual sources,
so every minimum frame fails. For example, partners `z=1` and `z=2`
produce characteristics 49 and 38 respectively. Its sixteen
dimension-four separating frames all pass.

At node **1217**,
`A = span(56,27,15,3)` and `B = span(515,259,131,67)`.
Its actual sources are `{35,44,52,56}`, and actual targets are
`{67,131,259,515}`. There are exactly two dimension-five minimum
frames. Partner `z=961` produces characteristic 35 and fails at the
actual source 35. Partner `z=965` produces characteristic 32 and
passes every actual incidence. This is a small example of why choosing
one arbitrary minimum completion does not decide existence of a safe one.

At node **818**,
`A = span(518,262,134,20,12,6)` and `B = span(97)`.
The radical generator is 30. The two characteristic solutions inside
`A` are 926 and 896, but only 926 occurs among the four minimum frames.
Because `926 = 1023+97` over the binary field, all four fail at target
97. No dimension-eight separating frame exists. The dimension-nine
frame `97-perp` is incident-safe, as proved above.

For an example of absolute incident impossibility, node **302** has
`A = span(896,352,224,96)` and `B = span(112,17,9,5,3)`.
Its sole minimum frame is `B-perp` and has characteristic 896, an
actual source. Its source residual has positive dimension and is
alternating. There is no larger separating frame.

## Why the tests are necessary for nested transfers

For a nested chain of nondegenerate spaces
`L = U0 subset U1 subset ... subset Uk = U`, there is an orthogonal
direct-sum decomposition

    U intersect L-perp
      = direct-sum over i=1,...,k of (Ui intersect Ui-1-perp).

It follows successively from `Ui = Ui-1 direct-sum
(Ui intersect Ui-1-perp)`. If every successive residual is zero or
nonalternating, a nonzero endpoint residual must be nonalternating:
some nonzero summand supplies a vector of norm one, which keeps that
norm in the full orthogonal sum. Therefore a nonzero alternating
endpoint residual cannot be repaired merely by subdividing that same
nested transfer into more intermediate frames.

Apply this argument along a source-to-node path, and along a
target-to-node path in the reversed complement frames. Every actual
source or target incidence must pass in a legal assignment under this
nested orthonormal-residual interface. The 20 absolute incident
obstructions therefore reject such assignments at these otherwise
completable source spans. They are additional local obstructions;
the predecessor's two impossible sandwiches already reject the
unchanged full circuit.

The converse is not proved and is not implied: safe choices at
individual nodes need not nest along an edge, and the intervening
edge residuals need not pass. Alternative topologies, copied carriers,
paid non-nested transport, and other phase interfaces are outside this
result. There is no claim that the locally feasible nodes form a legal
supplier, nor that local rank increments equal operation costs.

## Attribution

The historical signed parity circuit and its obstruction/repair analysis
are due to Douglas Colkitt. DreamingOfClouds' format-limits work supplied
the sandwich restriction and radical rank floor. ToikY's pinned PR #972
proved the constrained minimum-completion theorem and identified the
692-node radical-one domain. ArnavSwiggy's
[PR #920](https://github.com/CrocSwap/integer-mult-bounds/pull/920)
already emphasized the stronger incident-residual condition and supplied
an explicit alternating-residual counterexample. These predecessors
are the basis for this narrowly scoped extension; no priority is claimed
for the underlying bilinear-form or characteristic-vector facts.

Prepared with substantial OpenAI Codex assistance in the mathematical
derivations, enumeration, and independent computational cross-check.
