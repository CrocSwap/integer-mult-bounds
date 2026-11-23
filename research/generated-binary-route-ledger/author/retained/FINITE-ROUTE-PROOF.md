# Fixed dyadic route words for the selected nested differences

## 1. Result and boundary

The 513 distinct nested differences in the retained selected binary raw
catalogue admit explicit **prime-independent whole-job route words** over
`Z[1/2]`. Each difference is routed to the first complete basis of the same
rank in the authenticated catalogue. This includes 135 distinct differences
which are not raw frame projectors. It is a finite construction for the exact
2,380 distinct MOVE/helper endpoint pairs, not a claim that every generated
compiler matrix has these small words.

Every word and its inverse works over `Z/q^w Z` for every odd prime q and
every positive w. After paying ordinary swaps for every earlier-target
addition, each directed route on all 64 high address fields uses at most:

| Operation class | Catalogue maximum | #7840 Section 4 allowance at N=8 |
| --- | ---: | ---: |
| Completed ordinary high-coordinate interchanges | 472 | 1,024 |
| Ordered additions, including 64 carry translations | 496 | 512 |
| Fixed unit scalings | 64 | 64 |

The maxima need not occur in one word. Inverse routes receive their own full
bill. Expanding fixed scalings into the five coefficients of #5052 requires
at most **128 signed-dyadic scaling atoms per directed route**. This expanded
count is distinct from the 64 fixed-scaling count.

This supplies finite words and a checked interface to already paid physical
primitives. It does not supply a tape interpreter for the complete route,
a numeric price for ordinary swaps or low-controlled carry preparation, or
installation of complete streams in recursive owner banks. Owned erasure
and the native/compiler, precision, tape, stock, fine-prime and analytic
recovery obligations remain unchanged. There is no new multiplication
exponent or assumption-discharge claim.

#7840 already establishes generic full-GL routing, representative carry,
spectators and an N-dependent tariff using q-dependent unit pivots. The
selected dyadic-basis proof already establishes all-odd-prime algebraic
closure. The contribution here is the explicit q-independent factorization
and checked tariff of the finite difference catalogue, including non-raw
projectors with nonunit first rational pivots. Generic GL existence, carry
identities and elementary matrix facts are not claimed as new.

## 2. Authenticated complete bases and orientation

`INPUTS.json` authenticates the exact compressed native data, accepted
independent complete-basis catalogue and retained #7840 proof. The canonical
scientific source is `e54523517d0f03e58352e647c403a5af3e525a57`. The basis
file is a new review artifact, not claimed to exist at that canonical commit.
The dyadic author result has since been published in #8092 under
`research/dyadic-selected-compiler-bases`; the local accepted-package name in
the input provenance identifies where these exact review bytes were obtained.

For a raw frame a, reconstruct

\[
P_a=G_a E_{r_a}G_a^{-1},\qquad G_a=[B_a^t\;A_a^t],
\qquad E_r=\operatorname{diag}(I_r,0).
\]

Enumerate source MOVE and complete helper endpoint pairs, order each by
rank, and deduplicate exact difference matrices. For each of the 513
differences P, its retained complete basis B_P is independently checked:

\[
PB_P=B_PE_r,\quad B_PB_P^{-1}=I,\quad
B_P,B_P^{-1}\in M_8(\mathbb Z[1/2]).                 \tag{1}
\]

This checks image and full kernel. For each rank let Q be the first
difference of that rank in the exact enumeration, and put

\[
S=B_PB_Q^{-1}.                                      \tag{2}
\]

Then `S Q S^-1=P`, and the right address route `g -> gS` gives

\[
(gS)Q(gS)^{-1}=gPg^{-1}.                            \tag{3}
\]

This is a completed role-diagonal whole-job identity. It does not authorize
distinct routes on coupled raw query ports: #7840's common-route condition
at mixed-role scalar contacts still applies.

## 3. Explicit factorization and finite certificate

The producer reduces `S^t` to I by elementary row operations. At column j,
it seeks a remaining entry which is a dyadic unit, hence a signed power of
two. If none exists, it seeks two remaining rows i,l and
`c in {1,-1,2,-2}` such that `a_ij+c a_lj` is a dyadic unit, and performs that
row addition. It swaps this pivot into row j, scales it to one, and clears
the column in every other row.

This short-repair rule is **not asserted to succeed on arbitrary dyadic
invertible matrices**. On this catalogue it succeeds, with 16 repairs in
total. It fails closed if neither an entry nor this short repair exists.
An existing-unit-only rule fails on actual catalogue matrices; invertibility
alone is not used to justify skipping the repairs.

`CATALOGUE.json` records every matrix, pair, reference, operation and count.
Its SHA-256 is

`fd605374cfeb851d3306e6e1778afffc51de508f32658a3d58c523bf066b5054`.

Descriptors are `["swap",i,j]`, `["add",target,source,"coefficient"]`, and
`["scale",i,"coefficient"]`, with zero-based indices and exact rational
strings. If chronological elimination operations are `E_1,...,E_k`, exact
multiplication verifies

\[
E_k\cdots E_1 S^t=I.                               \tag{4}
\]

The forward high-row route is the chronological word
`E_k^-1,...,E_1^-1`, whose column-vector action is `S^t`; the inverse route
is the stored elimination word. The checker reconstructs (2) with its own
inverse engine and interprets both words without importing the producer.

All addition coefficients are dyadic, and all scales are signed powers of
two. Reduction through the ring homomorphism
`Z[1/2] -> Z/q^w Z` is defined for every odd q and preserves (1)--(4) and
every elementary inverse. The finite exact rational certificate therefore
proves these particular words work for all q,w. Finite modular checks are
corroboration, not the basis of the universal conclusion.

### A non-raw target with a forbidden first pivot

Choose `P=P266-P11`, of rank three, with reference `Q=P270-P2`.
P is not any raw frame projector. After clearing the first two columns of
`S^t`, the next first nonzero candidate is `3/4`, zero modulo three.
It cannot be used for fixed all-odd-prime elimination. Row six of the same
column contains `-1/4`, so the certificate swaps this dyadic unit into place.

Writing A_ij(c) for adding c times row j to row i, W_ij for a swap, and
D_i(c) for a scale, the chronological elimination word is

\[
\begin{aligned}
&A_{21}(1/4),A_{41}(1/4),A_{61}(1/4),A_{71}(1/2),W_{26},D_2(-4),\\
&A_{42}(-3/4),A_{62}(-3/4),A_{72}(-1/2),W_{34},D_3(-1),A_{63}(-1),\\
&W_{46},D_4(1/4),A_{24}(3),A_{34}(2),A_{74}(-2),W_{56},D_7(-1),\\
&A_{27}(-1/2),A_{47}(-1/2).
\end{aligned}                                      \tag{5}
\]

It has 13 additions, four earlier-target additions, four swaps and four
fixed scalings per high row. Its directed full route costs 96 ordinary
swaps, 168 ordered shifts including carry, and 32 fixed scalings, expanding
to 48 signed-dyadic atoms. The checker verifies the exact endpoint and the
actual third-column bad and replacement pivots.

## 4. Representative carry on all high fields

Use #7840's complete address decomposition

\[
g=g_0+qX,\quad g_0\in\operatorname{GL}_8(\mathbb F_q),
\quad X\in M_8(\mathbb Z/q^{w-1}\mathbb Z),
\]

with low representatives in `0,...,q-1`. Let h_0 use those representatives
for `g_0S mod q`, and define the **exact rational** carry

\[
C_S(g_0)=(g_0S-h_0)/q.                             \tag{6}
\]

This matrix lies in `M_8(Z[1/2])`: every numerator entry has a power-of-two
denominator and reduces to zero modulo q, so its integer numerator is
divisible by q. This is q-integrality, not necessarily ordinary integer
integrality. For `S=1/2`, `q=3`, `g0=1`, one gets `h0=2` and `C=-1/2`.
Integer floor is wrong; dividing by q inside `Z/q^w Z` is not defined.

Apply the forward word separately to **all eight complete high rows**, then
add all 64 entries of (6) modulo `q^(w-1)`. The result is

\[
\rho_S(g_0,X)=(h_0,XS+C_S(g_0)),                   \tag{7}
\]

and reconstruction gives `h0+q(XS+C_S)=gS mod q^w`. At w=1 the high cube
is a singleton and no high primitive, including a zero-width interchange,
is called; the low route remains a permutation.

If k_0 represents `h_0T mod q`, direct expansion gives

\[
C_{ST}(g_0)=C_S(g_0)T+C_T(h_0),                    \tag{8}
\]

and consequently

\[
C_{S^{-1}}(h_0)=-C_S(g_0)S^{-1},\qquad
\rho_{S^{-1}}\rho_S=\operatorname{id}.             \tag{9}
\]

The inverse recomputes carry from its own low representatives. Negating the
original carry without transport by `S^-1` is not justified. The checker
tests (9) over Q and independently compares reconstructed matrices mod q^w.

Prefixes, gaps, suffixes, ancestor fields and unused fresh coordinates are
additional independent coordinates on which (7) is identity. For each fixed
low type, (7) permutes the entire 64-field high cube. Tensoring this
bijection with the spectator identity transports any record without reading
or changing its payload; the inverse restores the original address and
complete record. This includes dirty data, zero bytes and correlated
fields. It does not prove private machine work has been erased: ownership
and cleanup remain contracts of the completed physical primitives called.

## 5. Pay the actual interfaces

An earlier-target addition `x_i <- x_i+c x_j` with i<j becomes
`swap(i,j)`, the ordered later-target addition into j from i, and
`swap(i,j)` again. Both swaps are paid completed ordinary interchanges.
This is the source boundary emphasized by #6950: zero explicit swaps in
an abstract word do not imply zero physical ordinary calls.

For a word with a additions, u earlier-target additions, t swaps and d
fixed scalings, its sufficient directed full-route bill is

\[
8(t+2u)\ \text{ordinary swaps},\quad
8a+64\ \text{ordered shifts},\quad
8d\ \text{fixed scalings}.                         \tag{10}
\]

All 64 carry translations are charged even if some coefficients are zero.
Reversal and inversion preserve a,u,t,d, so the inverse has its own same
bill. Taking maxima of complete bills over all 513 words gives Section 1.
Combining different words' separate row maxima would overstate the finite
ordinary maximum; the checker bills each whole word before maximizing.

A scale `+/-2^k` expands into |k| atoms of coefficient `+/-2` or `+/-1/2`,
placing any minus sign in one atom. A standalone negative sign uses one
`-1` atom. The length is `max(|k|,1_{negative})`. The maximum is 16 atoms
per high row and 128 per full route, unchanged by inversion.

#5052 supplies these five physical scaling interfaces on arbitrary complete
`[P] x [Q] x [S]` Boolean streams, with same-original-owner return and
restored private state. Its sufficient bounds are `2048 V_j` transitions
and `64 V_j` visited cells at site volume V_j. Once the caller's required
complete-stream representation is installed, scaling can therefore be
charged by `2048 sum_j V_j`, with sequentially reusable private capacity
`64 max_j V_j`. If all 128 possible sites have common volume V, sufficient
scaling-only bounds are `262144 V` transitions and `64 V` private capacity.
This is not a total route transition count, and complete-stream installation
and source-preserving output storage are not free.

Ordinary swaps, coefficient preparation, low selection/unselection, scans,
ordered-shift execution, low-controlled carries, descriptors, headers,
caller ownership and packet-layout conversion retain inherited costs.
#6950's ordinary-call audit and #5052's scale machine address different
operation classes. This appendix gives a finite invoice at their interfaces;
it does not independently execute a complete physical route machine.

## 6. Evidence, limits and remaining work

`route_words.py` produces descriptors. `verify_routes.py` imports neither it
nor the earlier dyadic computation engine. It checks input hashes and Git
blobs, rebuilds raw frames and all differences, verifies complete bases,
reconstructs (2), verifies both exact word matrices, lowers earlier-target
adds and recounts (10). It checks 20,520 modular basis rows. For the non-raw
witness it checks 192 complete 64-field cases at q=3,5,7,11 and w=1,2,3,4,
the entire `3^8` one-high-row cube, and 39,366 transported opaque records
with exterior spectators. Controls detect omitted carry, wrong inverse,
the nonunit pivot, integer-floor carry, omitted spectators, destroyed
payload and unpaid earlier-target swaps. Normal and optimized execution
must both pass; checks use explicit exceptions, not removable assertions.

The full `GL_8(Z/q^w Z)` cover is not materialized. Universal semantics follow
from exact identities and elementary bijections, with finite tests checking
the actual source and implementation. This is model-assisted checking, not
external human or proof-kernel acceptance. Independent peer-review receipts
are separate from this author checker.

The 472/496/64 bound is restricted to these 513 dimension-eight routes.
Generated compiler dimensions and coefficient heights may grow. Their
dyadic closure supplies all-odd-prime arithmetic validity, not these word
lengths or physical charges. A general q-independent dyadic elimination may
need more additions and scale atoms; #7840's q-dependent construction keeps
its own N-dependent interface at the actual generated dimension. Growing
outer fine-prime obligations remain separate from fixed compiler arithmetic.

Concrete remaining work is to install these descriptors in an actual
recursive owner bank; provide and price low selection and carry producers;
connect numeric ordered-shift and completed-swap charges; and derive a
separate size-dependent factorization ledger for generated nodes. None is
declared solved here.

## 7. Source and overlap credit

- [#7840](https://github.com/CrocSwap/integer-mult-bounds/pull/7840), pinned
  proof at `adf2e0aa6777977a280ce50f8938f4a0f4f19b76`, Section 4: full-GL
  routing, representative carry, spectators and tariff.
- [#8092](https://github.com/CrocSwap/integer-mult-bounds/pull/8092),
  `research/dyadic-selected-compiler-bases`: complete bases and carried
  compiler closure used here.
- [#5052](https://github.com/CrocSwap/integer-mult-bounds/pull/5052),
  JoyboyBrian, `02a3cedb301e072bc5d991c7e36086daa8cd5c40`: full physical
  signed-dyadic scale API and owner-return tariff.
- [#6950](https://github.com/CrocSwap/integer-mult-bounds/pull/6950),
  unpaidmoon, `eb35892026c56733ca223938153d9869381bbe5e`: ordered-interface
  hidden ordinary-swap census.
- [#6954](https://github.com/CrocSwap/integer-mult-bounds/pull/6954) and
  [#7092](https://github.com/CrocSwap/integer-mult-bounds/pull/7092) are
  related short-factorization and restricted-ring-floor work. No general
  short-word priority or duplicate helper462 mechanism is claimed.

Original source and contributor notices are retained in `NOTICE.md`.
