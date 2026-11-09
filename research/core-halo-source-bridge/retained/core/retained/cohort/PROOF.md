# Actual Core interiors in one complete global field

Prepared for **@CubeJerry**, with substantial OpenAI Codex assistance.
Apache-2.0. Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The byte-pinned global caller dependency is the published commit
`d51859e7816771f627033b23db0f9786ada863f8`; see
[GLOBAL-DEPENDENCY.json](GLOBAL-DEPENDENCY.json). **No new κ.**

## 1. The precise new interface

This construction prepares the **complete interior stage** of actual
`Core.partition` windows and delivers its globally rounded execution to the
published Full physical service. The exact reference is identity on the
boundary of each complete core. The actual rounded execution has a proved
whole-field error, including those boundary coordinates. Bitwise boundary
preservation is not asserted.

The source results retained from #4253, #4786, #5018 and #5104 already give
the local Full/RawGaussian words, anchored gauges, common reference and
source grid binding. They do not create the present in-place disjoint union,
admit that non-Toeplitz union through the generic native compiler, or gather
arbitrarily selected axes of a larger original field into the new global
consumer. Conversely, we do not replace their numerical lemmas, #4178's
fresh suffix theorem, or the physical native and ownership premises of the
published consumer. Neither complete `Core.execute`, Schur/halo assembly,
nor the final multiplication/recovery theorem is established here.

Fix all original axis address widths `ell_i >= 1`, including unselected axes,
and an ordered tuple of distinct selected axes `a_0,...,a_(g-1)`. Put

```
n = sum_i ell_i,     T = 2^n,     L = 2^m >= 2,
ell_(a_j) >= m,      K = T/L^g.
```

For each selected axis supply the actual canonical `Reference` of target
length `2^ell_(a_j)`, its narrow/broad family, the admissible dyadic interior
cap, and physical band width. A direction, forward or stored inverse, is
provided for every complete packed coarse label and selected axis. Directions
may differ across labels. All ordinary full-field vectors are allowed; no
separability of their data is assumed.

The theorem is conditional on successful exact source admissions, the
retained Full/RawGaussian prefix and linear approximation theorems, and the
published global physical service's explicit integer, native, internal-stock
and owned-return contracts. It proves a source-specific composition of those
contracts, not an unconditional admission of the selected supplier.

## 2. The source-only partition producer

`Partition` supplies exactly the attributes used by the unchanged
`Core.load_carve` and `Core.partition` bodies: `raw`, `reference`, `n`,
`coordinates`, `width`, `cap`, then the authenticated `carve` and `carve_ast`.
The shell is not presented as an invocation of `Core.__init__`. In particular,
no unused Schur, block-boundary or LU pages are constructed or subsequently
charged as though they had been executed.

The explicit entry predicates are: an actual canonical `Reference` object;
the narrow or broad family; integer, aligned original start `first`; dyadic
`L>=2` and dyadic cap `B>=1`; `0<=first<first+L<=reference.target_size`;
`first mod L=0`; complementary gap at least `width`; `2B<=source_size`; and
an integer band at least `max(1,2*source_halfwidth+2)` in the narrow family,
or `max(1,target_halfwidth)` in the broad family. The `Reference` constructor
itself retains its source-size, excess, rational coordinate, truncation and
error admissions. These are the geometry predicates needed by these two
inherited methods; conditions used only to construct or solve the unused
Schur boundary are not silently invoked.

The source carve returns interior index tuples `I_j` in the **original
L-wire window**, including physical holes and post-hole shifts. For each
cell its `source_start` is passed unchanged to the bound RawGaussian
constructor; its actual reference matrix is
`Reference.window(kind, tuple(first+i for i in I_j))`. No independently
padded interior payload is allocated. The exact inverse used for admission
is an ordinary source exact solve of that same matrix, not its transpose
or adjoint. All setup, including these solves, is paid in Section 8.

Let `J` be the complement of the disjoint sets `I_j`. In direction `s` the
requested single-axis reference is

\[
D_{ca}=I_J\oplus\bigoplus_j A_j^{(s)},\qquad
A_j^{(0)}=A_j,\quad A_j^{(1)}=A_j^{-1}.                 \tag{1}
\]

The direct sum is embedded at the actual `I_j`, not contiguous relabelings.
Empty interior families are supported: (1) is the complete identity, and
the producer supplies one genuine empty logical matching. Gather, the
compiled idle word and its roundings are still paid.

The producer seals source geometry, description, carve, pieces, cells,
derived indices, complement, exact matrices and inverse pages. Validation
regenerates the unchanged partition and rechecks the same reference windows.
The authenticated loader rejects a preloaded cached interval module before
opening the source. Trusted exact serialization covers the entire new
preparation and hash boundary and restores Python's original decimal digit
limit even on failure; this removes no arithmetic or source admission.

## 3. A linear RawGaussian defect and a direct-sum prefix maximum

Each actual RawGaussian is constructed at radius one and a strengthened
source target `t_s`; its exact stored Full child and direct/inverse gate
words are retained. Denote its gauge bound by G, middle norm bound by H,
stored gauge/reciprocal error by eta, normalized inverse allowance by qbar,
reference error by epsilon, and raw inverse allowance by Qraw. Let eF be
the actual Full builder's `coefficient_error`, and ek the normalized
Gaussian `kernel_error`. These are **linear endpoint errors**. The source's
local `forward_error`/`inverse_error` also contain local data roundings and
are not substituted as linear defects of a new global execution.

Both stored gauges and their stored exact reciprocals approximate the
appropriate ideal gauges within eta. A three-factor telescope gives

\[
\begin{split}
e_+&=(G+\eta)^2(e_F+e_k)+H\eta(2G+\eta)+\epsilon,\\
e_-&=(G+\eta)^2(e_F+2\bar q^2e_k)
                         +H\eta(2G+\eta)+2Q_{raw}^2\epsilon.       \tag{2}
\end{split}
\]

This follows by comparing the middle factor first, then replacing one gauge
at a time. The inverse reference term is the retained resolvent comparison
to the same rounded reference. The source `Reference.errors[kind]` bounds
both row and column errors for these constant-phase unperiodized windows;
this is not a substitution of a differently periodized matrix.

The code requires `eta<=1` and `max(e_+,e_-)<=2^-t_s`. These are exact checks.
They are uniformly feasible with the retained source allocation, subject
to its reference-accuracy admission: write tau_s=`2^-t_s`. At radius one,
`Rmid=4G`, `tau_mid<=tau_s/(16G)` and both the Full coefficient and the
inverse kernel contributions are at most
`tau_mid/[4(Rmid+1)]`. Thus the inverse middle contribution before the
gauges is at most `tau_s/(128G^2)`. Also
`eta=tau_s/(48GH)`, `G+eta<=2G`, and the source reference admission gives
`2Qraw^2 epsilon<=tau_s/8`. Consequently

```
e_- <= tau_s/32 + tau_s/16 + tau_s/8 = 7 tau_s/32;
e_+ <= 5 tau_s/32.
```

Let PiF be the Full builder's `execution_bound`. The retained Full prefix
theorem covers prefixes, suffixes and inverses, hence both stored directions.
The two outer gauge layers yield

\[
\Pi_j=(G_j+1)^2\Pi_{F,j}.                                      \tag{3}
\]

At logical level k the new producer unions the k-th actual child matching
on all `I_j`; a shorter completed child is idle. Distinct cells cannot share
a wire. At every cut the complete L-wire prefix is an orthogonal direct sum
of child prefixes/completed endpoints and identity on J. Therefore

\[
\Pi_{ca}=\max(1,\max_j\Pi_j),\quad
e_{ca}=\max_j e_{j,s},\quad
\lambda_{ca}=\max(1,\max_j\|A_j^{(s)}\|_2),\quad
E_{ca}=\lambda_{ca}+e_{ca}.                                    \tag{4}
\]

The implementation uses the source certified norm upper bound for lambda.
There is no multiplier for the number of interiors. Arbitrary spectator
data remain covered by these operator statements.

## 4. Generic complete-core lowering, rather than Toeplitz admission

The direct sum (1) generally is not Toeplitz and is never passed to
`FullRoot`'s Toeplitz admission. Instead `CoreRoot.lower` supplies the actual
complete logical word, Pi from (4), endpoint E and linear upstream error e
to the unchanged **generic** `NativeProgram` constructor of #4253.

Every embedded child gate is a gate from the actual source grammar: scalar,
upper/lower shear, diagonal, swap or the admitted rational unitary forms.
The exact RawGaussian gauge layers are scalar gates. `NativeProgram`
validates each actual gate and its fixed word; arbitrary invertible 2x2
matrices are not admitted by this argument. Relabeling a gate onto its
original disjoint indices does not alter its type or values.

Put Gamma=`2^ceil(log2 Pi^2)`. The source gate quotient and prefix argument
gives the compensated primitive bound `C=2^14 Gamma Pi`. At a primitive
cut the prefix factors into a fragment of the **current** lowered matching
and the completed logical prefix. The fragment bound is paid once at that
cut; it is not multiplied once for every completed matching. This is why
the direct-sum Pi in (4) applies to the whole lowered word. Its complete
return routes and normalization factors are preserved.

For L=`2^m`, every actual logical layer, including an idle one, lowers to
`16m+5` primitives, with `8m+2` raw-H calls and `8m+3` diagonal calls. The
source raw-H conversion changes a compensated prefix by at most a scalar
two at any cut, immediately compensated by its next diagonal. Thus `2C`
bounds both raw prefixes and inverse prefixes. These bounds apply also
inside identity padding, where nontrivial routing and H work still occur.

Write d for the maximum actual logical depth over all labels and axes.
The global source therefore has exactly

```
J=d(16m+5),       Hc=d(8m+2),       Dc=d(8m+3).                  (5)
```

The source coefficient-independent polylogarithmic Full depth, with the
two gauge layers, bounds d by a polylogarithm of B. Unequal actual depths
are synchronized using the compiler's genuine complete idle words.
The generic constructor also prepares its original local rounded receipt;
the global caller consumes only its exact raw word and prefix contract.
That unused local rounded trajectory is not composed into the new error
bound, and its actual preparation remains in the setup charge.

## 5. Complete original-coordinate layout

Let `s_i=sum_(h<i) ell_h` be the actual axis starts. The selected low bits
are `S=(s_(a_j)+b : j=0,...,g-1; b=0,...,m-1)`. The ordered target list is
`U=(0,...,gm-1)`. Map S to U in that order and complete the permutation by
mapping the sorted difference `U\S` to the sorted difference `S\U`.
Outside their union every bit is fixed. This is a permutation with support
at most `2gm`; fixed points in its encoded support are harmless.

Let sigma be its address action. Packed label c corresponds to original
base `sigma^-1(c*L^g)`. The original selected coordinates extracted from
this address are the exact aligned starts passed to Section 2. All other
coordinates, including every unselected axis and all selected high bits,
are represented by c. In particular n is the **whole** field address width,
not merely the width of the currently selected group. Sorted coarse bits
cannot be guessed to be a particular high-axis tuple after completion.

In packed coordinates, axis zero is fastest. The exact target is the direct
sum over c of `D_c,g-1 tensor ... tensor D_c,0`. In original coordinates it
is conjugated by sigma. At each diagonal event the factors use that exact
c and those exact source roots; at each H event the mask is
`{a*m+b : a=0,...,g-1}` for the actual source stage bit b.
Identity on the complement is a per-axis assertion: an entry whose first
coordinate is a boundary value can still be transformed along another axis.

## 6. The global grid and exact source adapter

The published `FullTensor.__init__` hardcodes a single Toeplitz `FullRoot`
per axis. `core_caller.py` replaces only that root-creation interface. It
extracts the unique complete source suffix beginning with `self.depths`,
including allocation, complete-word synchronization and validation, without
altering its authenticated bytes. The new roots implement `lower`,
`validate`, `record`, context seals and the same linear endpoint contract.
The unchanged methods `events` and `execute` are then inherited. This is a
specific authenticated interface adaptation, not a general Python verifier.

Let R=`2^r`, tau=`2^-t` and Lambda=`max lambda_ca`. Set

\[
t_s=t+\lceil\log_2(8gR(\Lambda+1)^{g-1})\rceil.                 \tag{6}
\]

By (2)--(4), every e is at most `2^-t_s`. The exact source telescope is

\[
R\max_c\sum_a e_{ca}\prod_{b<a}E_{cb}\prod_{b>a}\lambda_{cb}
\le\tau/8.                                                     \tag{7}
\]

The unchanged suffix evaluates (7) exactly and rejects an unfunded source.
Increasing the final arithmetic grid cannot repair (7). A supplied reference
that is insufficiently accurate for (6) is rejected by the actual RawGaussian
constructor. Source reference preparation and any stronger original entry
precision remain paid parts of the interface.

Set `A=max_c product_a(2C_ca)`, `E=max_c product_a E_ca`. Let b be one plus
an integer upper bound for the l1 norm of **all actual raw factor entries**,
including padding, and `V2=2^ceil(n/2)`. The frozen caller uses common F with

\[
[8ED_cA^2g b^{g-1}R+4EA D_cV2]2^{-F}\le\tau/4,\qquad F\ge F_0. \tag{8}
\]

It proves this for the fresh rounded coefficient suffix followed by one
complete complex data multiplication and component truncation. The exact
physical H return adds no data rounding. The sum of the realized residuals
is propagated through linear suffixes; there is no false Lipschitz assertion
about a nonlinear rounder. Equations (7)--(8) give total whole-field error
at most `3tau/8<tau` relative to (1), conjugated by sigma. Boundary entries
are included in the full `V2` rounding term.

The component amplitude, factor, cache and raw product widths are exactly
the frozen caller's allocations. In particular `W=F+ceil(log2(4A(R+1)))+2`.
All source and width seals remain checked. Host fresh products in the
independent finite oracle are verification, not the physical arithmetic
algorithm.

## 7. Paid physical gather, consumer and original-coordinate return

`PreparedOuter` encodes both support permutations and every complete source
H/D event through the unchanged `PreparedFull`. Its constructor is source
preparation, with full controls paid before execution. It drops its decoded
program reference after encoding. At runtime only borrowed encoded data,
controls and encoded Count metadata enter `CohortPhysical.run`.

The wrapper copies the complete original input to its own protected port,
calls the authentic `GlobalBoundary.gather` with sigma, suspends its owning
scope while `FullPhysical` consumes that distinct port, consumes the
protected returned result, and calls the same authentic router with
sigma inverse. The first gather carries W0-bit incoming components and the
second W-bit final components, but **both use P=W+g** for routing admission.
The service then exposes the complete original-coordinate result.

This wrapper owns distinct ports from the child. Its alias guard excludes
all private H/scalar/grid/router and child ports, and separates borrowed
payload, program, both permutation tapes and metadata. Both routing code
heads and every other borrowed head are rewound on return. Old current
fields are retired only after replacement, and every temporary body and
owned marker is erased. A protected output must be consumed before reuse.
Passive production call counters are fixed-key null maps, so repeated calls
do not accumulate unbounded diagnostic host integers. The underlying
emulator's observation layer and opt-in finite fixture counters remain
observations, not numerical inputs or branch controls.

The source radius is permutation invariant. The physical consumer still
executes its full exact squared-radius admission, common-grid lift, all
whole-field H and D events and width checks. None is bypassed because a
partition has large boundary or idle regions. Both gathers are exact data
permutations, so (7)--(8) apply unchanged after returning to original order.

These statements compose the actual caller protocols with the inherited
successful-call/owned-return contracts. Arbitrary asynchronous interruption
recovery is not a new claim. The finite physical witness in Section 10
executes the wrapper and one actual H event, not every event of the large
Core fixture.

## 8. Complete time, setup, controls and storage

Let `mu(u)=O(u^nu)`, `nu=log2(3)`, be the retained exact all-width Karatsuba
word product. Write U for the maximum of final data, factor, cache and raw
product widths. Let `C_H(n,W+g,g)` be the published complete raw-H cost and
`C_route(n,W+g,k,w)` the authentic sparse-permutation cost on complete T
complex records of width w, with k encoded support entries. The general
invoice for this new wrapper is

```
S_prepare + S_encode + S_constructor
 + C_route(n,W+g,k,W0) + C_route(n,W+g,k,W)
 + Hc C_H(n,W+g,g)
 + O(T mu(W0+n+1) + T U + Dc T [mu(U)+U]
       + poly(n+log(U+2)+log(J+2))).                            (9)
```

`S_prepare` includes Reference preparation at the needed accuracy, exact
partition windows and inverses, actual RawGaussian/Full construction, every
whole-core gate lowering and real idle word, source/root/plan/page validation,
the strengthened source allocation, all exact-to-F conversions and disposal
of prepared objects. `S_encode` includes **all** source events and both
permutation tapes, not an unpriced callback during execution.
`S_constructor` retains the physical dependency's explicit fixed native
owner construction and private-port inventory cost. The actual #3627
`production_layer` takes no p/n arguments: it fixes the two native owners,
q, dimension, rank, topology/catalogue and program before varying precision.
Conditional on that inherited source construction and its admissions, this
graph and private-port inventory cost is an `O_source(1)` constant, possibly
astronomical. We retain it in (9), rather than assert a practical production
construction or independently discharge its catalogue. The variable width,
stock, field and routing metadata stay in the complete runtime tariffs.

The radius term pays 2T physical real squares and their exact running sum.
The diagonal term includes complete complex products, fresh suffix tables,
all copies, rewinds, control, truncations, stale-table disposal and final
output exposure, as proved in the frozen physical dependency. The two new
gathers include their own complete metadata, staging, stock, original-frame
return and retirement costs. Their additional wrapper copies and erasures
cost O(TU), already shown in (9). The forward gather's lower W0 does not
reduce the precision P chosen for its route plan.

If `bpos=max(1,ceil(log2 n))`, the exact stored Full code length is inherited:

```
2(J+1) + Hc g bpos + 2 Dc K g L Wfactor.
```

The two new permutation tapes add `4k bpos` bits, and finite encoded
metadata adds its actual cardinality-word sizes. General total space retains
this all-stage code, `O(TU)` owned work, the inherited H-owner inventory,
every prepared exact source/cache object still retained by the caller and
the largest historical blank backing. Source objects may be explicitly
released after encoding; neither `PreparedFull` nor `PreparedOuter` retains
the decoded source program. With reuse, the bound uses maximum prior call
extents plus entry backing, not just the latest smaller live input. Clearing
a tape does not make its old allocated backing disappear.

### 8.1 A conservative sequential source-preparation bound

We do not assume constant-cost Python dictionaries or arbitrary-precision
arithmetic as tape operations. Let ell be the largest selected original
axis address width, Hoff a bound on original exact coefficient bit heights,
and h a bound on all subsequent rational construction heights. The actual
source uses lazy coordinate and selected-address descriptions: a single
partition inspects O(L) coordinates and O(LB) window entries. Nevertheless,
the same `Reference` objects persist across labels. Their memo dictionaries
can accumulate a number of entries comparable with the original source
size or its square. A claim of per-label polynomial cost merely because
the constructor has no eager full-source loop would be unjustified.

A safe refinement represents these finite dictionaries as sequential key/
value lists, scans them on each access, and charges their full accumulated
length. The universe of selected coordinates, matrix-entry pairs and source
weights is bounded by `2^O(ell)`. Each source interval computation and exact
rational operation has polynomial cost in its argument and result bit
heights by the retained interval and Full height theorems. Exact matrix
solves can use the literal reduced-rational elimination: their entries are
ratios of bounded-order minors, so their height is polynomial in B and the
input heights. Copies, division, gcd and comparisons can all use ordinary
polynomial-time sequential integer arithmetic at setup.

The new cross-label loops are serialized in their actual lexicographic order.
For stage-major event preparation, scan the stored complete source words
and select the required stage, paying their length again at each stage.
This may add a polynomial factor in L and J; it does not require a random
access across K different roots. All nested array loops, sealing and
validation can likewise scan their stated finite tables. Loop/cardinality
counters cost polynomial(n), and output control serialization is charged
above. Thus a conservative bound is

\[
S_{prepare}+S_{encode}
 \le K g\,2^{O(\ell)}\operatorname{poly}(L,B,n,t_s,F,H_{off},h,J), \tag{10}
\]

including repeated regeneration/validation and full reference caches. The
polynomial and exponential constants are uniform fixed source constants;
they cannot depend on runtime g, K or payload values. Their exact degree is
not optimized. In unrestricted parameter regimes (10) remains a possibly
expensive setup term. The physical runtime does not invoke this host source
preparation as a free service.

## 9. One favorable admitted interior-stage family

This section shows that the new source join need not lose the existing
global-service saving to per-interior padding, source setup, or the exact
Karatsuba scalar. It is not a second standalone retuning contribution and
does not admit the remaining outer stages.
The inherited Gaussian source regime is
`theta in [1/(4p^2),1/p^2]` and
`alpha=ceil(sqrt((4/pi)log(16p)))`; primality and the other outer stages are
separate source obligations, not inferred from an interior fixture.

Use the dyadic complete-core side from `unconditional-batched-crt/GAUSSIAN.md`,
`L=2^ceil(400 log2 p)`. Give the original field `d=Theta(p^epsilon)` axes,
each with `ell=Theta(p^(1-epsilon))` bits, where the retained near-one choice
is `epsilon=1-10^-30`; hence full n=Theta(p). Choose

```
beta=39/40,       g=Theta(p^beta),       xi=15/16,
B=2^floor(xi log2 p),                   F0,t,log R=O(p).
```

Apply the finite source admissions in Sections 1--3. The selected-axis
target lengths are dyadic, and eventually ell exceeds log2 L, so complete
cores partition each selected coordinate without independent per-axis data
padding. Partition d axes into groups whose sizes lie between g and 2g
when d>=2g; grouping a remainder with another group introduces no dummy
axes or tiny last group. The number of such groups is O(d/g).

The inherited anchored gauge and normalized Full bounds give
`log Pi=O(polylog(p)+p^(2xi-2))` with the retained source constants and the
corresponding inverse allowance. Across g axes their logarithmic contribution
is O(g polylog(p)+p^(beta+2xi-2) polylog(p)). Here
`beta+2xi-2=17/20<1`. Equations (6)--(8), full n=Theta(p), and the source
height theorem therefore give F=Theta(p) and U=O(p). Offline original
weight tables may instead need O(p^2 log p) bits; that bound is included in
Hoff and (10), not forced into an online record before conversion.

In this regime L, B, J, F and the retained exact construction heights are
polynomial(p). Moreover ell=o(g log L). Dividing (10) by `T=K L^g`,

```
g 2^O(ell) poly(p) / L^g -> 0.
```

This proves absorption of the conservative source/cache and encoded-control
bill, including the full K multiplier, into the complete field volume.
It does not assert this absorption for constant g.

Let `V=Theta(Tp)`, alpha=`99827101/100000000` and
eta=`332353/332929`. The authentic H and support-route rate hypotheses yield
the following non-setup part of (9), up to fixed logarithmic powers:

```
O(V [Hc g^alpha log p + Hc (g+1)^eta (log p)^(1+eta)
     + Dc p^(nu-1) + (gm)^eta polylog(p) + polylog(p)]).          (11)
```

Here `gm=O(p^.975 log p)<=P^.997` eventually, with `P=W+g=Theta(p)`.
The actual router has additional finite guards: `n>ell_route`,
`n-ell_route>=10 floor(k/2) G`, and a free `ell_route`-bit block, with
`G=4 ceil(log2 P)+6` and `Kroute=64G`. Its retained theorem proves the
fast route eventually under the long-field geometry; literal fallback
is retained in (9) outside that domain. No finite q2 fixture establishes
this asymptotic rate.

The scalar comparison is strict without approximate logarithms:
`3^5<2^8` gives `nu-1<3/5`, whereas
`beta*alpha=.97331423475>3/5`. Both Hc and Dc contain the same actual
depth and have bounded ratio. Thus exact Karatsuba is subordinate to the
native term for this family. After O(d/g) groups the dense native exponent
above V is `epsilon-(1-alpha)beta<.99831423475`; the analogous route
exponent is `epsilon-(1-eta)beta<.998313153856`. The scalar and scanning
powers are respectively less than .625 and .025. Every retained native
constructor term in (9) is still an explicit inherited admission charge.

This favorable interior-stage bill neither funds an unimplemented boundary
restore nor supplies Schur, halo, CRT, prime-supply or final recovery.
Those remaining composition obligations prevent any new κ assertion.

## 10. What the checks establish

The complete finite source replay executes all authentic matching layers,
lowered events, coefficient pages and global rounding sites, then compares
with an independent original-reference direct sum/tensor oracle. The
physical attachment witness instead executes the actual original-coordinate
gather, **one authentic first H event**, and the inverse gather, at the
unchanged source F/W. Its receipt records both the complete source stage
count and the executed prefix length. It uses the inherited disclosed
reduced q2 native fixture and certified finite metadata floor constants;
it does not claim a complete physical Core replay or production rate.

Meaningful negative controls target original supports, label order, both
gauges, stored inverse versus adjoint, complete idle words, source accuracy,
source/module authentication, immutable geometry and numerical allocation.
These finite checks corroborate the construction and fail-closed source
binding. The universal direct-sum, layout, error, ownership composition and
cost arguments are the written proofs above together with the explicitly
pinned predecessor theorems, not extrapolations from fixture timing.

## Open next questions

1. Can the remaining complete Core boundary and halo word consume this
   original-coordinate error contract without a bitwise boundary restore?
   First check its exact intermediate radius/error budget; do not infer this
   from the identity complement of the unrounded reference.
2. Can a bounded-cache source producer remove the conservative `2^O(ell)`
   factor in (10), preserving the same reference and all validation seals?
   It is unnecessary for the displayed growing-g family, but matters for
   smaller source geometries and repeated partial cohorts.
3. Can a priced streaming control producer replace all-stage encoded pages
   when g is constant? The current complete code and retained backing are
   intentionally present in the general space bill.
