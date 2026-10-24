# Exact parity bookkeeping for a typed seven-axis consumer

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

This note is a sufficient consumer construction after the quotient word's ACTUAL typed normal forms and monomial wrappers have been independently established. It does not infer those types from frame dimensions. Use the corrected physical-row convention: X is the first 112-role bank and Y the second. A type-B extra central transform is on physical Y, in both orientations.

Let Q be the retained symmetric one-axis central Gaussian operator, Q^T=Q, with Q^2 an explicitly known monomial, and D_s a symmetric seven-axis Gaussian on disjoint fresh axes, D_s^T=D_s and D_s² monomial. Hence Q commutes with every D_s. Forward typed local operators are

    A_s = diag(D_s,D_s) S_y(Q^-1),
    B_s = diag(D_s,Q D_s) S_y(Q^-1).

Their retained backward-dual forms are

    A_s^dual = diag(D_s^-T,D_s^-T) S_x(-Q^-1),
    B_s^dual = diag(D_s^-T,Q^-1 D_s^-T) S_x(-Q^-1).

These are the raw inverse transposes, using Q^T=Q. To obtain the retained controller shear S_x(-Q), explicitly apply input-Y Q² and output-Y Q^-2; then apply D_s² on both output rows to convert D_s^-T=D_s^-1 into D_s. These are paid volume-linear monomial wrappers, checked with absolute phases. Explicitly set R=diag(I,Q²), L=diag(I,Q^-2), and P=diag(D_s²,D_s²). Direct block multiplication gives

    P L A_s^dual R = diag(D_s,D_s) S_x(-Q),
    P L B_s^dual R = diag(D_s,Q^-1 D_s) S_x(-Q).

The rightmost input wrapper R acts first; the leftmost output wrapper P acts last. Both equations retain their exact even powers and phases. The inverse exponent in B_s^dual does not change the parity flip: it is still physical Y. These formulas are subject to the exact typed normal-form certificate. A previous provisional X/Y assignment was incorrect and must not be used as evidence.

## Row gauges and their exact meaning

Put Q^a on a controller row, a an integer. For a logical shear that adds epsilon Q^k times source row j into target row i, conjugation by row gauges gives physical coefficient

    epsilon Q^(k+a_i-a_j).

This is an exact operator equation. Reduce exponents modulo two only for the Fourier-rank invoice; retain every even exponent as its explicit monomial Q^(2m). Signs and those monomial wrappers remain in the actual circuit. An odd central exponent costs one rank-one Gaussian job; an even exponent is monomial. No exact statement Q^2=I is assumed.

Therefore:

- a plain ADD, k=0, is scalar/monomial when row parities agree and costs a rank-one job when they differ;
- a QUERY shear, k odd, is scalar/monomial when row parities differ and costs a rank-one job when they agree;
- a signed swap carries row gauges along with its swapped rows; a swap is not permission to relabel a physical Y extra as an X extra.

A paid rank-one shear coefficient can be implemented with one owned temporary: COPY the source, apply the central Q or Q^-1 Gaussian job with its exact even-power monomial, add the result to the target, then CLEAR the owned temporary. All four stages are charged by the native implementation. The original source remains intact. This uses the admitted owned-erasure convention; it cannot be applied to dirty borrowed storage.

## Local type incidence constraints

To consume A_s or B_s as the retained logical A_s under row gauges without an additional corrective Gaussian, require equal input parities on X and Y. Type A carries both parities through unchanged. Type B carries X through unchanged and flips Y. The same incidence rule holds in the controller-compatible backward orientation only after the explicit monomial wrappers above, with its actual S_x shear and inverse central exponent. The raw inverse transpose alone has shear -Q^-1 and must not be relabelled -Q.

These constraints follow by conjugating the complete two-row operator, not by observing a changed main chart. If the two input parities disagree, either an explicitly priced central gauge change or an explicitly priced corrective shear is needed. A consumer may optimize those choices, but may not impose the free incidence rule and silently ignore incompatible events.

## Productive target credit

For a diagonal output row whose retained logical endpoint is

    Q^m product_s D_s^(e_s),

the actual endpoint with final row gauge Q^a is Q^(m+a) product_s D_s^(e_s). If the e_s are the retained 0/1 fresh-slot exponents, its exact Gaussian rank is

    7 sum_s e_s + ((m+a) mod 2).

All signs, inverse orientations and even powers belong to explicit monomial normalizers. A final parity bit alone is not a productive credit. In particular when m is odd, final parity one REMOVES the central productive rank; it does not add one. Initial main gauges are fixed to preserve the requested input ABI. If an optimizer changes helper entrance gauges, the independent-helper zero cross-block condition must be retained as in the phase-flow theorem.

## Complete admission

A candidate parity schedule must reconstruct every chronological LOCAL, IDLE, ADD, QUERY and signed swap, include every extra central child and every final productive central rank, then check the resulting exact matrix endpoints. The ambient block is seven, not eight: an unused local coordinate does not earn an eight-axis ladder or diagonal credit. Any extra central primitive, transport, owned copy and monomial wrapper is actually emitted and paid. The full target/paid moment, compiler, precision and outer native assembly must then be certified anew.

This is a constructive sufficient consumer interface and a precise optimizer specification. It reports no profitable parity schedule, no admission of a malformed quotient warp, and no new kappa. Credit the actual typed quotient normalizer, Cinna Davis's local supplier/controller lineage, the query-thinned controller authors, Dugongue's native Word RAM/phase-gauge construction, and the retained Gaussian/Clifford/whole-job compiler sources.

## Equivalent type-B factorization

The corrected forward type B also has the exact identity

    diag(1,Q) S_y(Q^-1) = S_y(1) diag(1,Q).

Both sides send (X,Y) to (X,X+QY). Thus the extra central Q may be viewed as an input-Y transform followed by a plain scalar ADD. This is an operator identity including signs and inverse powers as written, not a free replacement of Q by I. It may help a new controller derivation, but the complete chronological controller polynomial and all output central exponents still have to be recomputed.
