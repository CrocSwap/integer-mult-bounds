# Total phase convention

This note clarifies Section 7 of `STREAM.md`, SHA256
`1351e6171fc7b9ac778363dc208665aa83e9176f84213c8aac34326cd71ad12e`.
The original proof is preserved.

The intended complete physical frame is

    O_i = i^(gamma_i) (X_(delta_i) C_(U_i))^(tensor lambda).

Thus `gamma_i` is the total phase of the whole tensor operator. With
`lambda=2f`, its scalar on the projector range is

    eta_i = i^(gamma_i+r_i f) (-1)^(f omega_n.delta_i).

If a record instead supplies a one-column phase `gamma_i^(1)`, then
use `gamma_i=lambda gamma_i^(1) mod 4` in this formula. The displayed
phase in the original proof must not be tensorized a second time.

## Dependency guard for recursive use

Section 6 needs an explicit condition on the dependency graph. Suppose
the resulting recursive word has a valid path envelope with

    sum_j (e_j/e)^rho <= theta < 1,  rho>1,

for every possible child path at an internal width `e`. Let its local
depth, including the new projector layers, be at most `E+c e`. Thus

    A(e) <= max_paths sum_j A(e_j) + E+c e.

Assume the inherited stopping rule `e<d^beta` and its leaf-size bound.
Use a constant `C` at least as large as the inherited leaf coefficient
and `(E+c)/(1-theta)`. Strong induction gives

    A(e) <= C d^(-beta(rho-1)) e^rho.

At an internal node, `e>=d^beta`, so
`d^(-beta(rho-1)) e^rho >= e`. The gap after the child terms is at least
`(1-theta)C e >= E+c e`, since `e>=1`. The leaf step is the inherited
leaf inequality with the enlarged `C`. The outer guard construction
therefore keeps the same exponent and changes its fixed constant.
The pinned `notes/bulk-complex-guard.tex` gives this induction for the
old constant local term; this paragraph supplies the new linear term.

A new internal cross-owner operation can change which old child
events one dependency path reaches. Zero added children alone does
not prove that the old `theta` still applies. A use inside a changed
controller must establish a path envelope for that controller.
For the separate `OWNER-BINDING.md` boundary conjugation, the old
internal path classes do remain unchanged: a path starts in any old
role, crosses the old provider, and then crosses only the new output
layer. In that case the displayed induction applies to the old valid
path envelope with the added boundary term.

These clarifications came from the independent review. They do not
change the stream graph, its exact finite replay, or its arithmetic
invoice. They limit the recursive claim to its required hypotheses.
