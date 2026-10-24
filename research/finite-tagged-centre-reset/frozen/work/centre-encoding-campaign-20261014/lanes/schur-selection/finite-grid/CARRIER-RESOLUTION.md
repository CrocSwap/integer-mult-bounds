# Relative resolution at a fixed nonzero coarse centre

This addendum strengthens the absolute-resolution witness in the frozen
`GRID-RESET-PROOF.md`. A zero coarse value can give a small carrier that
permits relative normalization. The following witness keeps the coarse
carrier nonzero. It uses the same actual minor, whose exact Gram check
is in `REDUNDANT-GRID-CHECK.json`.

Let e0 be one coordinate vector in the payload coefficient space. Put
`h0=e0/8`. Choose eight independent dyadic scalars s_k in `[-1/8,1/8]`
and put `v_k=s_k e0`. Set

    y_A=R_A^T v,    y_other=0,    u_k=h0-v_k.

Every input component has magnitude at most one half. Since
`R_A R_A^T=4I`, the query is `Ry/4=v`. The untagged centre is h0 for
every k, and the tagged physical centre is

    z_k(s_k) = (1/8+delta s_k) B_k e0.

Here B_k is the actual invertible native centre frame. There is no
assumption that e0 or the constant vector is a frame eigenvector.

For `0<delta<=1/2`, the scalar multiplier in this expression lies
between `1/16` and `3/16`. If adjacent allowed s values differ by
`2^-g`, their relative carrier separation is

    delta 2^-g / |1/8+delta s|.

It therefore lies between `(16/3) delta 2^-g` and
`16 delta 2^-g`. The common nonzero vector `B_k e0` cancels from this
ratio. A decoder that must return the exact grid value `B_k u_k` cannot
accept arbitrary relative error larger than half an adjacent separation:
the error balls around two distinct inputs would intersect.

Thus this particular mixed-carrier decoder needs relative error
`O(delta 2^-g)`. For `g=t+O(e)` and `delta=2^(-t-O(e))`, its leading
accuracy coefficient is two. If only absolute accuracy `2^-t` is
required at the decoded output, use query values spaced by
`2^-t 2^O(e)` instead. The inverse frame norm gives a sufficient
factor that is independent of t. The same leading coefficient follows
when t exceeds the fixed dimension guard. Additive `O(e)` guard terms
do not change that coefficient.

This statement is local to decoding the packed carrier under arbitrary
relative error. It is not a native-query lower bound. A new algorithm
can change other data access, use correlations between child errors,
or retain separate data channels. Such an algorithm is outside this
witness. The cost of each native job still requires the separate exact
response and input analysis; this witness does not supply that census.

The addendum preserves the original proof and receipt bytes. It does
not change their exact local word or their negative complete invoice.
OpenAI Codex supplied this clarification. Publication is on hold.
