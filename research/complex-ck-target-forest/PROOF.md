# Signed target-forest factorization and its exact price

This is a finite rational circuit argument for the pinned #626 CK compensation
panel, selected at the recorded base and historical after the concurrent #741
integration. It does not discharge the all-size multiplication theorem.

## Interface

Write the 112 target values as `y` and the 254 source helper values read by
the panel as `h`. All these registers start in frame zero. The selected panel
is `y <- y + C h`, with `h` unchanged and entries of `C` in `(1/4) Z`.
The target and source sets are disjoint. These properties, the precise matrix
entries, and their selected-SPEC binding are checked from the original word.
The earlier precondition is retained verbatim, so this argument permits
arbitrary inputs even when target values already contain preconditioned dirt.

For each nonroot target `t`, choose one parent `p(t)` and sign `s(t)` in
`{-1,+1}`. Require the directed parent graph to be a rooted forest. Define
`T` by `(T y)_t = y_t - s(t) y_p(t)` at nonroots and `(T y)_t = y_t` at roots.
Ordering targets by depth makes `T` triangular with unit diagonal, so it is
invertible over the rationals.

## Executable schedule and arbitrary-input restoration

Apply `y_t -= s(t) y_p(t)` in decreasing depth order. Each parent still holds
its original value when a child reads it. The resulting state is exactly
`T y`; merely iterating these gates in increasing depth would implement a
different matrix. Next add each nonzero entry of `T C` using the unchanged
helpers. Finally reverse the preparation list and negate every coefficient.
This realizes

```text
T^-1 (T y + (T C) h) = y + C h.
```

Thus every arbitrary target input is restored apart from its prescribed
correction. The forward circuit never writes any helper. No scratch register,
recursive child, copy of a live target, frame change or endpoint restoration
outside these charged gates is needed. The same frame-zero scalar interface
admits every added basis operation. The original precondition, subsequent
adapters, native frames, center operations and wrappers remain literal.

For an addition matrix `E = I + q e_t e_s^T` with `t != s`, its inverse
transpose is `E^-T = I - q e_s e_t^T`. Applying these dual gates in the same
chronological order gives the inverse transpose of the entire panel: the map
`M -> M^-T` preserves multiplication order. Equality of the complete forward
matrix therefore implies equality in the inherited backward convention.
Both directions are also replayed on all 716 arbitrary input columns, and
the unchanged native checker verifies the surrounding complete programs.

## Full scalar price

For nonzero reduced `q = a / 2^d`, the retained Horner implementation clears
one private coefficient-work stream, builds `|a|` times the source by binary
doublings and additions, halves it `d` times, accumulates it with the required
sign, and clears the work stream again. The exact complex-component price is

```text
p(q) = 3 + floor(log2 |a|) + popcount(|a|) + d.
```

Set `p(0)=0` because no gate is emitted. Both source accesses and all private
initial/final clearing are included. One unit target-basis addition has price
four, and preparation plus restoration therefore cost eight per forest edge.
The code literally replays all 206 coefficients on independent target/source/
work symbols and checks their operation counts. Arbitrary private-work input
is erased at each original macro boundary, as in the retained interface.
Real-component prices are twice complex-component prices.

Let `P(r) = sum_j p(r_j)` for a coefficient row. A root `t` costs `P(C_t)`;
a nonroot with parent `u` and sign `s` costs

```text
w(t,u,s) = 8 + P(C_t - s C_u).
```

This charges every residual coefficient operation and both basis gates.
Since `C_u - s C_t = -s (C_t - s C_u)` and `p(q)=p(-q)`, the edge price is
independent of its eventual orientation. This symmetry is specific to unit
signs and the retained sign-symmetric coefficient price.

## Exact forest-class optimum

Introduce a superroot `*`, with edge `(*,t)` of price `P(C_t)` for each
target. Between each unordered pair of targets retain both signed edges.
Each target forest extends to a spanning tree by connecting its roots to
`*`. Conversely, remove `*` from a spanning tree and orient each remaining
component away from its unique former neighbor of `*`. These operations
preserve both the recipe class and its exact total price.

Consequently the least price in this explicitly defined signed-unit forest
class is a minimum spanning tree of the 113-vertex multigraph. The complete
domain has `112 + 2 * binom(112,2) = 12,544` edges. Kruskal constructs a tree,
with SHA-256 of seed 39 and each edge breaking equal-weight ties. No stochastic
search, timeout, or broader circuit optimality is involved.

For every graph edge `(a,b,w)`, the certificate checks that `w` is at least the
largest tree-edge weight on the unique tree path from `a` to `b`. This is the
standard spanning-tree cycle criterion. To see sufficiency directly, add any
edge of a competing tree to the certified tree. A removable edge on its
fundamental cycle has no greater weight. Repeating exchanges toward the
competitor shows that the certified tree cannot be more expensive. Necessity
follows by replacing a heavier path edge with a violating cheaper edge.
The checker includes both signs and all root edges. A separate Prim
implementation, with independently calculated dyadic costs, finds the same
total without using the constructor's ordering or tie-breaking code.

The certified minimum is **16,364 complex primitives**. Its six components
have 106 target edges and maximum depth nine. The circuit contains
`106 + 3130 + 106 = 3342` additions. The original panel costs 49,624 complex
primitives, so each full local orientation saves
`2 * (49624 - 16364) = 66520` real primitives.

This floor applies only to the described target forests with separately
lowered entries. It does not bound non-unit parent shears, general target
matrices, helper transformations, coefficient sharing or other primitive sets.

## Prefix and recursive accounting

Maintain a positive row-norm envelope, initially one for each logical input.
An addition updates `N_t <- N_t + |q| N_s`. During its coefficient preparation,
the envelope also includes `|a| N_s`, because binary Horner's positive
intermediates do not exceed `|a|`. Scaling, copying and clearing update the
envelopes directly. This bounds every real-component scalar prefix by the
triangle inequality, including work preparation before halving.

The complete replacement forward maximum is `920709848294` (40 bits); the
backward maximum is `599514829020946429949/32` (65 bits). Both are below
`2^192`. The independent inherited native audit computes identical envelopes.
The backward increase from 62 to 65 bits is included, rather than inferred
away from the final matrix equality.

All non-scalar events are byte-for-byte equal as parsed JSON, including the
native paid histogram

```text
H = {1:2596, 2:552, 3:304, 4:160, 5:70, 6:8, 8:8}.
```

The scalar macros outside compensation, all helper/source accesses within
them, copies, wrapper calls and recursive children retain their original
costs. There are no new helpers or frame changes. The local adapter bound
`16*(macros + children + 716 + 8) + 64*73` would decrease from 426,400 to
340,608 because 5,362 macros are removed and the 3,698 children are unchanged.
This is a local arithmetic consequence, not an issued global invoice. The
JP8 provider and the selected assembly are untouched.

In particular the changed constant scalar/adapter work does not change the
paid recursive moment or its exponent. No improved kappa is claimed. Adopting
this alternative compensation syntax into the strict production constructor
and regenerating bindings and global receipts remain future work.
