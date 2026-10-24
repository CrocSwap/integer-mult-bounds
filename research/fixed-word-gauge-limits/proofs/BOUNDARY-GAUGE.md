# Boundary gauges that preserve the physical supplier

This note gives a larger search class for the pinned local supplier. It
does not state that this class reduces its cost.

Let each wire segment have an invertible native frame `T_v`. The physical
value on the segment is `T_v z_v`, where `z_v` is its scalar content. A
native edge from segment `u` to segment `v` applies `T_v T_u^-1`. A scalar
ADD can combine segments with the same frame. All operators below include
their scalar phases and act on the full array, at the required tensor
power.

Choose an invertible operator `G_v` on each segment. Require the same
`G_v` on the two live values of each scalar ADD or COPY. No relation is
required across a CLEAR that removes an old value. Replace the frame by
`T_v G_v` and the native edge by

    T_v G_v G_u^-1 T_u^-1.

The same scalar program is then legal. If its scalar endpoint is `P`, its
physical endpoint is

    diag(T_out) diag(G_out) P diag(G_in)^-1 diag(T_in)^-1.

It is the old physical endpoint if and only if

    diag(G_out) P = P diag(G_in).

This equality, rather than a fixed zero boundary gauge, is the exact
boundary constraint. Necessity and sufficiency follow by multiplication by
the invertible outer frames. They do not require the frames to commute.

For the original forward local shear, the scalar endpoint has
`x_p'=x_p`, `y_p'=y_p+x_p`, and `h_i'=h_i`. Thus it is sufficient to use one
common gauge on the four endpoints of each pair `(x_p,y_p)`, and one common
gauge on the two endpoints of each helper `h_i`. Distinct pairs and helpers
can use distinct gauges. The backward shear has the same constraints.
Private output rows are zero. A cleared private input has no endpoint
constraint from `P`; its actual scalar accesses still impose constraints.

For the two-valued search `G_v=C_a^epsilon_v`, union the required scalar
access components. Then union each helper's input and output, and each
data pair's four endpoints. No such component needs a fixed value merely
because it is external. Price every native edge and wrapper after this
union. A change in a printed frame identifier alone is not an operation.

The construction preserves arbitrary borrowed inputs. It also preserves
each helper's complete physical residual, because

    T_out G (T_in G)^-1 = T_out T_in^-1.

The claim is valid at every tensor power: apply the same proof to the
tensor operators. Before admission, a candidate still needs exact native
lowering, phase checks, a full child profile, scalar and wrapper cost, and
an independent replay of the unchanged physical endpoint.

This note was prepared with OpenAI Codex assistance.
