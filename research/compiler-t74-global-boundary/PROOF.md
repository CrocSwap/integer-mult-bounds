# A source-emitted global switch through the physical T74 owner

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.

This is a source-relative composition theorem. It connects the actual routing
prefix emitted by `local_layer` in
`research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_tensor_compiler.py`
to `ComposedRoot.run` from CrocSwap/integer-mult-bounds#3627. The Beneš identity,
the local fixed-H compiler and the physical root are credited predecessors.
The new object is their executing global boundary, including its nonconstant
diagonal, original coordinate labels, exact grid conversion and return contract.

The theorem retains the universal native, hosting, machine-refinement, exact
endpoint and cost premises in the authenticated exports of #3627. It does not
replace that source by the selected #6030 supplier. **No new κ.**

## 1. Quantified input and result

Let there be `g>=1` original binary address axes of lengths
`ell_a>=m>=1`. Number bit positions from the least significant end and put

    n = sum_a ell_a,    N = 2^m,    L = 2^(n-gm),    A = 2^n.

The low `m` bits of every axis are its local coordinate. The remaining bits
form a complete coarse label. For every one of the `L` coarse labels and every
axis, supply a permutation of the complete `N` local coordinates. The ordering
of these supplied tables is the packed coarse-label ordering defined in §2,
not an unstated ordering on a subset of labels.

The numerical input is the complete `C` by `A` rectangle, with `r` Gaussian
coefficients per address, `C,r>=1`. Each real and imaginary numerator is a
signed `w`-bit integer, `w>=2`, interpreted on the same external `p`-grid,
`0<=p<=w`. Define

    V = 2 w C r A,       P_* = w+g.

The caller owns disjoint input, control and canonical Count ports. The physical
boundary returns the specified product of local permutations on the **original
address axes**, with the same `w`-bit components and the same external `p`-grid.
The result is exact. The boundary preserves the borrowed packet, controls and
Counts, consumes its child returns, and restores the inherited successful-input
owned-work baselines. Its distinct protected output must be consumed before
reuse. No interruption-recovery claim is added.

For the following rate statement fix positive constants `c,C0,B,D,M` and require

    c P_* <= n <= C0 P_*,        g <= D w,
    g m <= floor(P_*^(997/1000)),
    m <= M log2(P_*+2),         log2(r+1) <= B P_*.

The stronger **`gm`** condition pays the initial and final gather. The H
supplier's condition on `g` alone does not justify that gather.

Put

    alpha = 99827101/100000000,      tau = 332353/332929,
    F(P,g) = g^alpha log2 P + (g+1)^tau (log2 P)^(1+tau).

The complete time, including control preparation, is

    O(S_prepare
      + V m (F(P_*,g)+1)
      + V (gm+1)^tau (log2 P_*)^(1+tau)),                  (1)

where the separately charged conservative preparation bound is

    S_prepare = O(L g N^2 (P_*+2)^7
                  + poly(P_*+log2(C+1)+log2(r+1))).        (2)

Section 6 gives a sequential construction behind (2), and states when that
term is absorbed. It is not replaced by one polynomial in `P_*` independently
of the number of coarse labels. Fresh occupied workspace is `O(V)+F_q` under
the retained source contracts. For reused simulator backing, the honest bound
includes entry history, as in §7.

Outside this rate domain the functional composition remains valid whenever
the source calls accept their inputs. Formula (1) is not asserted there.

## 2. Actual source events and original coordinates

For a desired local permutation `pi`, form the matching

    (pi^-1(0),pi^-1(1)), ..., (pi^-1(N-2),pi^-1(N-1)).

The source's `matching_permutation` is exactly `pi`. Call its actual
`local_layer` with that matching and its actual identity `gateword`. The first
`4(2m-1)` operations are the forward Beneš routing prefix. Each source switch
is emitted as

    H, D_sign, H, D_half,

where the selected bit follows the common schedule
`0,1,...,m-1,...,1,0`, the diagonal has entries `+1` or `-1`, and every entry of
`D_half` is `1/2`. Different local permutations and coarse labels retain the
same H schedule. `compile_route` reads and validates these actual returned
operations; it does not accept a separate list of H supports. The arbitrary
central gate word and the inverse routing suffix of `local_layer` are not
claimed as executed by this package.

For completeness, the source recursion has the usual Beneš invariant. On
input wires its two edge sets pair `i` with `i xor 1` and with
`pi^-1(pi(i) xor 1)`. They are perfect matchings, so their union has even
alternating cycles. The source coloring therefore gives one wire of each
color in every input pair and every output pair. The first switch sends a
color to its corresponding half-lane. For each color the induced map
`i//2 -> pi(i)//2` is a permutation; the recursive calls route these two maps.
The last switch sends each colored preimage to its prescribed output. The
two-wire base case is immediate. This also proves the common bit schedule by
induction. It is the credited routing lemma applied to the actual source
operations, not a new Beneš construction.

Let `s_a=sum_{b<a} ell_b`. The original local-bit set is

    S = {s_a+j : 0<=a<g, 0<=j<m};

the packed target is `T={0,...,gm-1}`. Map the ordered S list to T, map sorted
`T\S` to sorted `S\T`, and fix the complement. This is a coordinate
permutation `pi_gather`, supported on at most `2gm` listed positions. Listed
fixed points are permitted by the physical router. The frontend exports both
directions in canonical source order.

The complete global packet is gathered once. In the packed frame, local axis
`a` occupies positions `am,...,am+m-1`, and a source H at local bit `j` selects
`am+j`. It acts on every coarse label and all `C*r` replicated coefficient
streams in **one** global supplier invocation. It is not a call on an isolated
`N^g` microbox.

For a packed coarse prefix `c`, its original label is obtained by applying
`pi_gather^-1` to the address `c*2^(gm)` and extracting the original high
parts of all axes. Local low bits cannot change this label. This is precisely
`Layout.coarse_label`; it also handles the rearrangement of coarse bits caused
by the sparse complement extension. Replacing this map by a guessed coarse
ordering can apply another label's nonconstant diagonal.

At stage t the global diagonal is

    d_t(c,k_0,...,k_(g-1)) = product_a d_(t,c,a)(k_a),

using the actual source tables for that original label. The supplier restores
its own temporary exposure before this scan. Thus the diagonal is applied in
the caller's packed original-label frame. At the end of the whole routing
prefix the initial gather is inverted exactly once.

## 3. C, H0 and an exact raw-H port

The retained root performs its Gaussian C computation, phase sweeps and scalar
normalization. Its public endpoint is

    Q_P(H0_S x),            H0 = [[1,1],[1,-1]]/2,

with componentwise truncation toward zero on the P-grid. It is exact if the
ideal endpoint lies on that grid. This exact-grid statement comes from #3627's
common-grid/final-only-truncation argument, not merely from its Euclidean error
estimate. In the underlying Gaussian convention,

    C = [[1+i,1-i],[1-i,1+i]]/2,
    S = diag(1,i),          b = (1-i)/2,
    b S C S = H0.

The wrapper therefore must not treat a C return, a normalized H0 return and a
raw H return as interchangeable.

Suppose the current physical component width is `u>=2`. Let its integer
numerators be `a+ib`, and set `P=u+g`. Since

    |a+ib| <= sqrt(2)*2^(u-1) < 2^u,

the P-grid packet obtained by appending `g` low zero bits represents
`(a+ib)/2^u` in the strict complex unit disk. `GridBoundary.expand` also adds
two high sign bits, producing exactly `P+2` physical bits per component.
The source H0 endpoint has numerator

    2^P * 2^-g * sum_sigma (+/-) (a_sigma+ib_sigma)/2^u
      = sum_sigma (+/-) (a_sigma+ib_sigma).

It is an integer on the P-grid, so the callee's final truncation is exact.
Reinterpret that same returned numerator at the external p-grid. It is the
raw `H^tensor g` output, with width `u+g+2`; no additional arithmetic scaling
or rounding has been assumed.

This uses one width bound for the complex modulus. The weaker condition that
the two components are separately at most one would not supply the unit disk.
The external p-grid is preserved semantically; it is not substituted for the
callee's online precision P.

The first raw call of a switch has precision `P_*=w+g`. Its returned width is
`w+g+2`. The second has precision `w+2g+2<=2P_*` and returns width
`w+2g+4`. Both satisfy the retained H domain and `n=Theta(P)` with changed fixed
constants. The width ratio remains bounded by a constant depending on D.

## 4. The nonconstant phase and completed-switch reset

For one source switch, `H D_sign H /2` is the identity or the selected wire
swap according to the source flip bit. Tensoring the g axis stages gives

    2^-g H_global D_product H_global = P_switch.           (3)

Here the product diagonal may depend on the **entire original coarse label**
and on each local coordinate. This is the actual compiler switch identity,
not an assertion about a constant sign in a newly chosen frame.

`product_signs` builds this mask in physical sequential order. For each coarse
label it starts with the one-bit zero mask. At axis a, for each of the N source
sign bits it copies the previous prefix, XORing that bit. Since axis zero is
least significant, this is exactly the packed tensor order. The prefix lengths
are `N,N^2,...,N^g`, whose sum is less than `2N^g`; also `gN<=N^g`.
The complete mask therefore costs `O(A)` bit traversal after its small encoded
setup. It is reused over the C complete rows and r coefficients per address.
Signed multiplication by ±1 uses a binary complement and one-bit carry in
`signed_component`, including a signed-overflow rejection. Complete phase
application costs `O(V)` at the current constant-factor-expanded widths.

The source normalization is the product of g `1/2` tables. After the second
raw call, (3) says every numerator equals `2^g` times a permuted original
numerator. `exact_divide` physically checks that all g discarded low bits of
every component are zero, then uses the retained grid codec to divide and
return to **the original w-bit width**. The codec separately rejects discarded
high bits that are not sign extension. This is exact division, not truncation
used to conceal a violated compiler invariant.

Consequently every completed switch restores the original amplitude range and
external p-grid. Induction over `2m-1` switches proves the whole prefix and
shows that the guard does not grow with network depth. This argument establishes
the endpoint for arbitrary signed inputs; the finite input patterns are only
controls. No general rational or complex diagonal product is executed here.

## 5. Complete stock, protected suffix and callee ownership

The wrapper calls the actual `ComposedRoot`, not a reference Walsh oracle.
On its composed branch at online precision P the inherited producer computes

    ell = ceil(log2 P)^2,       K_root = floor(g^(1/500)),
    T_root = {ell+j K_root : 0<=j<g}.

It constructs the selected-support extension, finds an untouched complete
ell-bit block U, physically exchanges U with the low suffix E, and retains
`r_eff=2^ell r` actual coefficients throughout the root call. The root receives
the complete prefix with

    left = n-ell-g K_root, right = 0,
    selected = g, precision = P, coefficients = r_eff, outer_rows = C.

Its actual active-width plan computes

    G_root = 4 ceil(log2 P)+6, H_root = g G_root,
    q0 = depth * ceil(log2(level_divisor)),
    qF = ceil(2H_root/K_root), qB = ceil(H_root/K_root).

On the recursive branch it produces stock `level_divisor^depth` and pads the
complete complex row count to a multiple of that stock. These fields are not
filled into an unrelated synthetic spectator plan by the frontend.

Each nested BIT call uses the retained `Ordinary.run`, which calls its encoded
selector with the actual incoming width and the retuned `Profile(1,577)`.
Its fitted path passes **that plan's stock** to `outer.interchange`; the latter
funds, pads, calls, restricts and cleans before returning. Its fallback is also
inside the same complete contract. Thus this composition uses the internally
funded BIT-stock alternative: the enclosing compiler does not assert that the
maximum individual stock, or the complex stock alone, supplies a simultaneous
nested stock product. The internal BIT contract and its universal source
premises remain inherited, not independently admitted by these finite tests.

The H exposure and inverse receive only the prefix as address bits, leaving E
inside the opaque coefficient records. Their router's own temporary grouping
stays within that prefix. After the exact root return, the inverse exposure,
ungrouping and inverse U/E exchange restore the incoming complete coordinate
frame and field boundaries before the adjacent diagonal is evaluated.

The router's reservations are a separate object:

    G_router = 4 ceil(log2 P)+6, K_router = 64 G_router,
    H_router = floor(k/2) G_router.

Its three reservoirs, guarded XOR batches, tail work and suffix restoration
are included in the retained router tariff. They are not identified with the
root's K or H. The source's literal branches are also retained and paid by its
explicit bounded-geometry fallback argument; this package does not price a
direct O(Vg) implementation as an accelerated call.

`production_boundary` binds the unchanged source production factory, which
constructs two fresh native owners in one authenticated runtime cohort. The
finite fixtures below do not instantiate those enormous fixed compilations.

## 6. Complete preparation and execution cost

### Control preparation

There are L complete coarse labels, not one. The input permutation tables have
`LgNm` bits up to delimiters. With the identity central word fixed, one source
`local_layer` uses `O(N(m+1)^2)` elementary indexed operations and
`O(N(m+1)^2)` bits of local address/array state; all source diagonal values in
the retained prefix are constants. These loose bounds include the recursive
cycle coloring, local inverse permutation, layer collection and validation.

A fixed-tape sequential implementation can represent those local arrays with
explicit m-bit indices and perform each indexed access by a full scan. Bit
arithmetic on the indices and a recursion stack add a fixed polynomial in m.
For example `O(N^2(m+1)^6)` time is a conservative allowance. No scan crosses
another coarse label's table while evaluating this one local circuit.

To emit stage-major controls, make `4(2m-1)` sequential passes over the complete
permutation-table input. On each pass regenerate one local source prefix at a
time and emit only the current stage. `encode_controls` implements that order;
it does not assume constant-time lookup into a global coarse-label array.
The initial validation pass and the reference stage summary can be produced
by the same passes. Coarse-label decoding and descriptor setup cost at most a
further `O(L poly(n,g,m))`. With `n,m,g=O(P_*)`, (2) is a safe complete bound.
The displayed seventh power deliberately leaves room for the extra stage
passes and local bit arithmetic; it is not an optimized compiler claim.

The tests execute the actual retained Python source to generate controls.
The cost argument above describes its sequential finite-tape implementation;
CPython elapsed time is not a tape-operation invoice. This preparation is
charged separately from the already physical online bridge.

For g=1 or a small fixed g, (2) need not fit the H tariff and is retained
explicitly in (1). In the family `g=Theta(P_*^beta)`, any fixed
`0<beta<997/1000`, and `m=O(log P_*)`, the gm-domain holds eventually. Moreover

    LgN^2(P_*+2)^7 / V
      = O(g (P_*+2)^7 / (w C r N^(g-2))) = o(1).

Since `N>=2` and `w=Theta(P_*)`, the exponential denominator in g dominates
every fixed polynomial. This is an explicit admissible amortization family,
not a transfer of the selected supplier's grouping exponent or an integer
multiplication result.

### Initial/final gather and all H calls

The authenticated `physical-support-router/PROOF.md` inside the router export
states correctness for arbitrary `k<=n` and its accelerated tariff specifically
for `k<=2 P^(997/1000)`. The initial/final descriptors have
`k<=2gm<=2P_*^(997/1000)`. Their actual record width is `2wr`, whose logarithm
is `O(P_*)`. Their complete two-direction cost is therefore

    O(V (gm+1)^tau (log2 P_*)^(1+tau)).

These two gathers occur once per program, in addition to every H callee's own
support exposure and inverse. No gather is counted as a mere relabeling.

There are exactly `2(2m-1)` complete raw-H calls. Their online precisions lie
between P_* and 2P_*, all their expanded volumes are `O(V)`, and the global
address width n remains comparable to each online precision. Applying #3627's
**two-term** bound to every call gives `O(Vm F(P_*,g))`. Low-zero insertion,
return copying and disposal, the product signs and exact switch quotients cost
`O(Vm)`. The encoded Count setup and traversal obey the inherited amortized
counter bounds; any fixed-degree global setup in `log C` is paid by the complete
factor C, not repeated per data bit. This proves (1).

In particular, `n=Theta(P)` is a real whole-field hypothesis. A small local
matrix with logarithmic address width cannot use this tariff independently.

## 7. Space, lifecycle and finite verification boundary

The new owner has a fixed pool of 128 roles, one protected output and one
GridBoundary. At most a constant number of full packets and masks coexist.
The source code tables and the local simulation fit `O(V)` in the stated
domain: `LgN<=A`, `m=O(log P_*)`, `w=Theta(P_*)`, and the local evaluator's
polynomial index space is absorbed by N or by w. Child pools and the two fixed
native compilations are charged through the source space contract.

Every child is called with a suspended enclosing allocation scope and borrowed
views. Its distinct output is copied to an owned packet, consumed and erased
before the old packet is discarded. Children must be closed and have consumed
outputs before another call. Success restores borrowed origins and bytes and
erases wrapper bodies and markers. The output is protected until the caller
consumes it. Finite checks inspect actual source plan fields and ownership
state; observers never select a runtime branch or supply a missing stock.
Per-coefficient diagnostic counters are optional fixture callbacks with ignored
return values. The production boundary leaves that observer unset, so its
arbitrary-C invoice does not include an unbounded host counter per payload bit.

For previously used simulator objects, clearing a tape does not shrink backing
storage. The retained-history statement is

    K_after <= K_entry + O(max_i V_i) + F_q,

over the program's constant-factor-expanded packets, including the actual
entry allocation history. A current-live-payload-only backing bound is not
claimed.

The bounded physical fixtures use the predecessor's q=2 native and reduced
root guards. The recursive fixture additionally declares reduced reservations
and a one-bit external suffix; it is not a production GL64/O(73,2) execution.
The costly floor-power metadata helper is exactly constant-folded on the finite
set `1..32` at exponents `997/1000` and `1/500`. Every cached value r is certified
by `r^den<=x^num<(r+1)^den`; incorrect entries are rejected. Other values delegate
to the unchanged helper. Receipts list every used fold. The actual plan
producers, payload/root/router calls and ownership operations still execute.
No measured time or tape count for this folded fixture is used in (1).

The finite tests compare complete physical output with a separate original-axis
permutation oracle, not another H/D interpreter. Longer schedules are also
checked with independent exact rational algebra. Neither kind of finite replay
proves the inherited universal source premises. This package closes a scoped
compiler/physical-boundary implication; it does not discharge all five global
assumptions, execute the general central complex gate words, or lower the full
integer multiplication bound.
