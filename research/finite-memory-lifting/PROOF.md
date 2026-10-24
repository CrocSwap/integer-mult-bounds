# Finite-memory lifting and the limits of column routing

**Status:** local written proof with exact finite calibration, awaiting independent mathematical review. The weighted-automata and matrix-product foundations are classical. The contribution is their concrete physical-column contract for native protocols, its positive-width and complete-return treatment, an explicit source adapter, and the routing/approximation boundaries below. No new κ, physical supplier, general automata algorithm or global literature priority is claimed.

## 1. A concrete family, rather than independent operator letters

Fix a field K, a local column dimension d, a transfer dimension D, p output roles and q independent input roles. Supply fixed matrices

`F ∈ K^(p×D), B ∈ K^(D×q), T_(y,x) ∈ K^(D×D)`,

for every pair `0<=y,x<d`. At positive width f define the complete endpoint P_f by

`(P_f)_(i,y_1…y_f ; j,x_1…x_f) = [F T_(y_1,x_1) … T_(y_f,x_f) B]_(i,j)`.

The tables and boundaries are fixed across widths. Omitted pairs in an explicitly sparse table mean zero matrices. They do not mean untested pairs. The role indices occur only in the boundaries: an exterior scalar/register coefficient is applied once, whereas a local phase is encountered at every column.

P_f is a linear operator on payloads. Its local address permutations can be nonlinear, and its columns can interact through the transfer state. This does not include arbitrary nonlinear arithmetic on payload values. D is a representation dimension; it is not automatically a number of owned fields, physical bits, Gaussian calls or tape cells.

For any word w of physical pairs, write T_w for its ordered transition product. All p×q endpoint blocks are compared. A borrowed dirty role is an independent input with its required returned identity block in the reference. Dropping that block changes the problem.

## 2. Exact all-positive-width certificate theorem

Let V_k be the row span of `e_i^T F T_w` for `1<=|w|<=k` and all output roles i. Put `r1=dim(V_1)`.

**Theorem A.** If r1=0 then every P_f is zero. Otherwise the following are equivalent:

1. `P_f=0` at every positive width.
2. `P_f=0` for every width `1<=f<=D-r1+1`.
3. There are at most D rows forming a matrix R and matrices E_s,C_s such that, for every physical symbol s,

   `F T_s = E_s R`, `R T_s = C_s R`, and `R B = 0`.

In particular, every false identity has a literal nonzero physical matrix entry at some width at most D. Comparing families of transfer dimensions D_A,D_B uses a direct-sum residual of dimension D_A+D_B.

**Proof.** The spaces satisfy

`V_(k+1) = V_k + Σ_s V_k T_s`.

Once two consecutive spaces agree, the common space is invariant under every transition and contains every later reachable row. Starting with r1 dimensions, at most D-r1 strict increases are possible. Thus V_(D-r1+1) is the entire positive reachable space. Vanishing through this width means B annihilates that space, hence every later coefficient too. If V_1 is zero, every positive product already begins with a zero row.

For a zero family choose R as any basis of the positive reachable space. Its containment and invariance give E_s,C_s, and all its rows annihilate B. Conversely, start a positive word with F T_s=E_sR, repeatedly apply R T_t=C_tR, and finally use RB=0. This proves every complete endpoint coefficient is zero. The empty word is deliberately absent: an identity can hold at every positive width while FB is nonzero. ∎

The reachable-space argument is classical; see [Kiefer and coauthors, Proposition 3.1](https://people.mpi-sws.org/~joel/publications/Q_weighted_automata13.pdf), [Tzeng](https://doi.org/10.1137/0221017), and the existing independent/inverse register certificates [#5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235) and [#5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262). Here the alphabet consists of **concrete physical input/output column pairs**, not independent formal operators. Relations and absolute phases are already present in the entries.

**Sharp positive-width bound.** In dimension D take one local symbol with cyclic-shift transition S_D and boundaries e_0^T,e_0. Its coefficient is one precisely at positive multiples of D. Widths 1,…,D−1 all pass, but width D fails. The same example can multiply the identity at any local dimension by putting S_D at every diagonal physical pair. No smaller bound depending only on D works for positive-width families.

**Exact producer and checker.** Breadth-first reachability retains original independent path rows and their output-role/word labels. At most D rows survive. A nonzero boundary value produces an actual physical word; dependence pruning preserves existence of a witness no longer than the bound above. Otherwise elimination supplies the closure coordinates. The checker needs only the three displayed equations; independence or minimality of R is unnecessary. Its reported seed rank is diagnostic, not a separately checked rank certificate.

Arithmetic is polynomial in the explicit transition-table size, D,p,q, in field operations. Exact rational implementations also admit polynomial bit bounds by common-denominator scaling and pivot-minor estimates, as in [#5352](https://github.com/CrocSwap/integer-mult-bounds/pull/5352). This package does not claim a faster algorithm or a new optimal bit bound. A compact native program can have an exponentially larger extracted table or transfer dimension, so this is not a polynomial bound in arbitrary source-program length.

## 3. Composition, real inverses and controlled width dependence

The matrix-product/weighted-automata correspondence is classical; see [Crosswhite and Bacon](https://arxiv.org/abs/0708.1221). For scalar endpoint blocks, the following constructions prove closure directly.

**Sum.** Direct-sum the virtual spaces, transitions and boundaries. Dimensions add. Exterior coefficients multiply a boundary once.

**Composition.** If A acts after H, use

`T^AH_(y,x) = Σ_z T^A_(y,z) ⊗ T^H_(z,x)`

and tensor the left and right boundaries. Dimensions multiply. Expanding a width-f product distributes the independent intermediate indices z_1,…,z_f, giving exactly the physical matrix product A_f H_f. For owner matrices this construction is applied **blockwise**, with a separate sum over the intermediate owner role. That owner sum is global, not an independent choice at each column. In particular,

`D_(i,j)(AH) <= Σ_h D_(i,h)(A) D_(h,j)(H)`.

**Inverses and return.** There is no assertion that the inverse of an arbitrary finite-memory family has bounded dimension. Supply an inverse representation and certify both compositions, or use an independently proved inverse frontend. Local permutation/phase inverses are actual inverses of their concrete one-column tables. An inverse-name annotation by itself supplies no relation. Full input and return blocks must still be retained.

**Recurrence coefficients.** A scalar `c_f = a G^f b` with k recurrence states multiplies any endpoint family by replacing

`T_s → T_s ⊗ G`, `F → F ⊗ a`, `B → B ⊗ b`.

The dimension becomes Dk. This covers polynomial coefficients through Jordan blocks, exponential coefficients, periodic phases and their finite sums/products. Constant exterior c uses transition 1 and a boundary c; it is not replaced by c^f. For example, the unnormalized Hadamard W satisfies `(W^⊗f)^2=2^f I`, while replacing 2^f by the exterior scalar 2 passes width one and fails width two.

**Regular restrictions.** A finite automaton recognizing allowed physical words can be tensored with the transitions in the same way. The resulting zero theorem is restricted to those words. A length filter for multiples of four can make i^f=1 valid on that subsequence; it does not certify every positive width. Restrictions on input values are new contracts and cannot silently replace arbitrary independent inputs.

These constructions permit fixed finite control schedules, a fixed number of represented sweeps and supplied recurrent coefficients. Their combined state dimensions must be included in D. An unrepresented width counter or position-dependent schedule is not free.

## 4. A genuine column-mixing family and a pinned native adapter

**Prefix XOR.** On f binary columns, let

`y_j = x_1 xor … xor x_j`.

Use two transfer states s∈{0,1}, initial state zero, and accept either final state. The local transition permits exactly

`y=x xor s`, `s_next=y`.

Every input has one path, with the stated output. The map is a permutation, with inverse `x_1=y_1`, `x_j=y_j xor y_(j−1)`. Swapping physical input/output labels therefore represents its inverse with the same two states. The composition construction certifies its inverse identity with residual dimension five.

This is outside sums of identical one-column tensor powers: every `Σ_i c_i A_i^⊗f` commutes with every column permutation, while prefix XOR at width two does not. For example, input 10 maps to 11 and input 01 maps to 01. It is an explicit semantic extension beyond [#5436](https://github.com/CrocSwap/integer-mult-bounds/pull/5436)'s columnwise support contract. The two-state virtual description does not grant a free native implementation.

A two-by-two middle-cut coefficient minor is the identity: take left physical pairs (0,0),(1,1) and right pairs (0,0),(1,0). Thus transfer dimension at least two is necessary, and the construction is exact at this boundary.

**Native fixture.** The byte-exact source is [the nine-axis, two-role conjugation word](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/native-tensor-cutoff/examples/source-conjugation.json) retained by [#5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369), from the [#2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250) recipe lineage. Its local identity is `G Z G^-1=R`; the eight-instruction complete register word adds that image and then subtracts the actual R query, restoring the original first role and the arbitrary second role.

The frontend composes literal local permutation/phase tables, transports the exterior register scalars once, and checks all four owner/input blocks against the complete reference. No free-word independence assumption is used. Independent literal phase evaluation covers all 512 addresses. Removing R's constant phase fails at width one. Applying the prefix-XOR basis change on source axis four to the shear residual gives an eight-state cross-column representation with a two-row invariant certificate. The general composition theorem and the separately checked prefix inverse justify the corresponding uniform conjugated identity.

This is a small source-bound algebraic adapter. It is not the 112-owner provider, the selected caller, its physical raw dual, a paid-word compiler or a new implementation of any free alphabet.

## 5. Cut-rank obstructions, including operator-norm approximation

At any cut after s columns of a width f=s+t endpoint, form the coefficient unfolding H with rows `(output role, y_left, x_left)` and columns `(input role, y_right, x_right)`. Its entries factor as

`H_(i,u ; j,v) = (e_i^T F T_u)(T_v B e_j)`.

**Theorem B.** Every such unfolding has rank at most D. A nonzero r-by-r minor is a finite lower certificate D>=r for any representation of that endpoint. This is the classical matrix-product cut-rank obstruction, here applied to the complete physical endpoint. It also applies to position-dependent tables at a fixed width, although those do not inherit Theorem A's all-width cutoff.

**Half-swap.** Let f=2k, local dimension d, and let S swap the two k-column halves. Put `N=d^(2k)`, the physical Hilbert-space dimension. At the middle cut its unfolding is the N-by-N permutation matrix

`H_(yL,xL ; yR,xR) = [yL=xR][yR=xL]`.

Therefore exact representation requires `D>=d^(2k)`. Over C, every approximant A with cut rank at most D satisfies

`||A-S||_op² >= max(0, 1-D/d^(2k))`.

**Proof of the robust bound.** Let Q project onto the column space of H(A), of rank r<=D. Since H(S) is unitary,

`||H(A)-H(S)||_F² >= ||(I-Q)H(S)||_F² = N-r >= N-D`.

Unfolding preserves the Frobenius norm. For an N-dimensional physical operator, `||E||_F²<=N||E||_op²`. Divide by N. ∎

**Nonlocal quadratic phase.** Over C, on two k-bit halves let

`V|a,b> = (-1)^(a dot b)|a,b>`.

The nonzero part of its middle unfolding is the `2^k`-dimensional Walsh matrix W, with `WW*=2^k I`. Consequently

`D>=2^k` exactly, and `||A-V||_op²>=max(0,1-D/2^k)` for any cut-rank-D approximant.

For the robust statement, with M=2^k the discarded squared Frobenius energy is at least `M(M-D)` and the physical Hilbert-space dimension is M². The same projection argument gives the bound. Thus even this phase-only Clifford family cannot have a uniformly bounded transfer dimension in the fixed column order.

The bits label the address basis; the coefficients here are complex. In characteristic two the signs coincide and this phase obstruction disappears. It is not an F2/BIT lower bound.

For a product of scalar-block layers with dimensions b_1,…,b_h, composition gives `D<=Π b_j`. The half-swap therefore requires `Π b_j >= (1-ε²)d^(2k)` to reach operator error ε<1; the paired phase requires `Π b_j >= (1-ε²)2^k`. Owner sums, physical memory conversions and routing direction must be accounted for separately. These are representation bounds, not native paid-call or tape-time lower bounds. Changing the column order changes the cut and can remove the obstruction.

## 6. Essential limits of finite testing

**Bounded bond at individual widths is insufficient.** A one-state family with width-dependent left boundary equal to zero through any chosen M and one afterwards passes those M tests but fails later. Arbitrary unrepresented position dependence gives the same problem. A fixed transfer table, or an explicit finite controller included in D, is essential.

**Tolerance is not equality.** Even a fixed one-state unitary per instance can have small early errors and large late errors. Let `α_N=(N+i)/(N-i)` and compare `α_N^f I` with I. For f<=M,

`|α_N^f-1| <= f|α_N-1| <= 2M/N`.

Write `θ=2 arctan(1/N)>0`. At an integer f nearest π/θ, the phase is within θ/2 of π, so `|α_N^f-1|>=2 cos(θ/4)>=sqrt(2)` for N>=1. Hence no D-only finite-width **tolerance** test certifies a uniform small error, even for a two-state comparison of fixed unitary families. The exact algorithm sees a nonzero discrepancy immediately; numerical resolution and a recovery-safe error budget are separate obligations.

The theorem decides equality after a valid fixed finite representation has been supplied. Extracting that representation from an actual program, pricing it, and proving its precision/tape/recursive admissibility remain independent research tasks.

## Open next questions

1. Extract the smallest useful physical transfer tables for one currently investigated provider/consumer, preserving all source versions and dirty returns. Table/bond growth, not a missing equivalence algorithm, is the first obstacle.
2. Build a real cross-column native adapter for the prefix construction and price its complete inverse, storage and movement. The virtual two-state description is not that implementation.
3. Derive source-specific cut minors for an actual observation or routing obligation; account for legal column reorderings before calling it a barrier.
4. Extend exact certificates to a uniform approximation criterion with proven contraction/conditioning assumptions. Small early-width errors alone are insufficient.
5. Use the bit-bound methods of [#5352](https://github.com/CrocSwap/integer-mult-bounds/pull/5352) to optimize this concrete table format and quantify practical extraction limits; symbolic succinctness and explicit-table bit complexity are different questions.
