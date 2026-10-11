# Sufficient construction and complete cost composition

## Response-space synthesis

Let K be the final target-by-helper response of the complete raw local word. Each selected pivot p has explicit rational coefficients satisfying K_p + sum_d c_pd K_d = 0. The entrance additions h_d += c_pd h_p therefore make its response identically zero. The groups have disjoint pivot/donor role sets; no pivot is a donor. Their shear matrix is S = I + N with N squared zero. Reconstructing every column verifies M_new = M_old diag(I,I,S), not merely agreement on clean inputs.

The fixed witness contains 119 pivots, 143 donors, 26 new F2 subspaces, and 240 literal unit-numerator gates with denominator 1 or 2. Each entrance lies in the first required frame of every involved helper. All 4,082 frame transitions are checked nested. Entrance dimensions sum to 265; the local histogram delta is {1:+169,2:+91,3:-43,4:+15,5:+10,6:-96,7:-3}, with rank-mass delta -265. Old response, cleanup, retained-centre work, literal scalar expansion and endpoint adapters remain charged.

## Arbitrary entrance spaces without an orthogonal-complement assumption

For entrance E, its actual phase-sensitive chart is T_E, not an assumed coordinate or orthogonal chart. The exposed helper residual is J_E = F T_E^-1. Exact Clifford lowering gives J_E = L C_(9-dim E) R, with explicit rank-zero monomial unitaries L,R. Surround the COMPLETE dirty invocation by R^-1 before old response and L^-1 after cleanup. The local endpoint is block diagonal with the gauged helper independently restored, so the new residual is exactly C_(9-dim E), while the data is unchanged.

Zero response alone would not justify this wrapper. The local checker separately establishes the needed block-diagonal endpoint on every dirty column with a distinct symbolic entrance token for each E, in both orientations. The Gaussian checker verifies the exact phase of every address column. Neither adapter is commuted through internal scalar gates. Chronological inverse-adjoint is multiplicative and fixes unitary address adapters; the same physical wrapper is valid in the backward convention. See `frames/PROOF.md` for the full argument.

## Explicit heterogeneous banks

Eight replicas per stage produce residual inventory {4:120,5:208,7:64,8:560,9:5296}. The fixed integer patterns place all 6,248 residuals into 748 banks of width 73. Coordinate slots are disjoint and cover every bank after padding: 482 rank-one pads and one rank-ten pad per stage. Every helper has an explicit coordinate permutation and its literal inverse owner route. There are nine stages and 72 complete local invocations.

The template emits both boundary adapters for each gauged helper in each invocation: 17,136 explicit rank-zero adapters. Private centre, tableau and coefficient namespaces are separated. The inherited data-stage/idle chronology and cover corrections are retained, with all bank family indices, padding and final translations rebuilt for the new stock. Independent readback checks the emitted assignments, profiles and finite cost bounds.

Live stock is 14,412, physical stock 15,203, paid child count 316,107, maximum child rank 48, and deficit 73*14,412 - rank_mass = 2,496. The finite invoice includes scalar expansion, all boundary/routing adapters, old-response/cleanup work, padding, cover correction and private workspace. No gain is obtained by omitting a charged child or treating an unimplemented route as free.

## Conditional exponent

The actual emitted profile feeds two independent exact rational moment engines. The complex coarse lower bound is 507169363968149971159 / 500000000000000000000000, below the unchanged bit bound 255384852701747 / 250000000000000000. Six fixed ordinary bootstrap levels, eta=beta=10^-18 and a 10^-24 backoff feed all 47 strict outer inequalities. They give kappa = 101331088745971 / 100000000000000000.

The conclusion is conditional on the inherited all-size compressed-window lift, arbitrary correlated dirty-bank semantics, recursive compiler, ordinary-call/fixed-tape/restored-row, precision and analytic contracts stated by the inherited assembly. Finite column, phase, template and inequality checks do not prove those all-size interfaces. This document supplies a sufficient composition for the changed finite witness and its conditional price, not an unconditional integer-multiplication theorem or Lean certification.

The public PR399 padding-fusion bracket is different and is not applied here. No independent gains are added. Discovery solver objectives nominate witnesses; exact reconstruction, integer packing and final pricing establish the reported finite result. No bounded search establishes optimality.
