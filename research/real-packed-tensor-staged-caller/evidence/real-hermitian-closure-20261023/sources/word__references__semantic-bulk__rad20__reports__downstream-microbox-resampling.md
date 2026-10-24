# Local principal inverses for bulk resampling

This is a fresh analytic construction with a positive
[independent conditional transfer review](review-bulk-resampling.md).
It uses the accepted phase-cell inverse to process polynomial-size windows
independently and compares only their core outputs with the global
Gaussian resampling map. The locality and arithmetic bounds below have a
direct proof. The [complete tape schedule](bulk-resampling-tape-transfer.md)
for gathering, fractional reshaping, halos and assembly has received the
same positive review. Strict numerical assembly is a separate dependency;
no larger kappa is promoted by this report alone.

The campaign started 2026-10-07T22:25:21Z, with historical original
deadline 2026-10-08T08:25:21Z. The user subsequently extended the same
campaign to 2026-10-08T10:00:00Z; completed protocols retain their
historical identities. The original input is CrocSwap/integer-mult-bounds
at bcd4ebde8692383539f8a48734e5fbf3a18a32c2; the separate compact-control
input is 6e564879f51ae16f23d392e9e196c605f36d90df.
The retained scalar definitions are in the original input's
`upstream/build/sections/07-resampling.tex`. The completed numerical
interfaces come from [the phase inverse proof](downstream-phase-cell-inverse.md)
and its [independent review](review-phase-cell-inverse.md).

## One fixed global rounded matrix

For each axis retain N=C T D, rho=t/s=1+theta, the increasing nearest
indices q_j=floor(rho*j+1/2), u=alpha^2 and
w=ceil(sqrt(16p/u))+2. The accepted construction fixes one matrix H:
its diagonal is exactly one, entries beyond cyclic distance w vanish,
within-cell entries are exactly a_hat_j G_hat_(j-l)/a_hat_l, and cross-cell
entries are the accepted directed approximations. All a_hat and G_hat
values are computed once for the global axis. Every local matrix below
is an exact principal restriction of that same H. A window does not
recompute its weights or round its coefficients again.

The accepted estimates, for p>100, are

```
||H-N|| < e_p := p*2^(16p+7)*eta + 2^(-46p),
eta=2^(-32768p), gap(H)>=1/(8p), ||H||<2, ||H^-1||<=8p.
```

Because H_jj=1, F=H-I has row norm at most 1-g with
g=1/(16p). Removing off-diagonal entries only improves this bound.
The Neumann argument concerns H and its principal matrices, before Schur
elimination. The Schur diagonal is generally not one and is not used in
this argument. A matrix with a different diagonal would first require
explicit diagonal normalization; diagonal dominance alone would not
justify using H-I.

## A principal-window locality lemma

Let I be an unwrapped interval with s-|I|>w, let H_I be its
principal matrix, and let a core row j be more than Jw steps from either
artificial endpoint. Let P_I restrict an input and R select core rows.
The extensions use zero outside I only for the local comparison.

For 0<=k<J, every contributing path in the row of F^k moves by at most
kw, so it remains in I. Thus the core rows of F^k and F_I^k agree
exactly after extending the latter by zero. Summing the two Neumann tails
gives the operator bound

```
||R H^-1 - R H_I^-1 P_I||
 <= 2*(1-g)^J/g
 <= 32p * 2^(-J/(16p)).
```

This is an absolute row-norm statement for arbitrary signed complex
inputs; it does not assume positive coefficients or numerical
cancellation. Take J=512p^2. For p>100 the bound is below 2^(-16p), since
32p*2^(-32p)<2^(-16p). The required source halo is at most
Jw<=512p^3. The same statement remains true when I crosses the periodic
seam: lift its indices to one increasing integer interval and reduce
them modulo s only when looking up global coefficients. No vertex is
repeated because |I|<s. The stronger complement condition ensures cyclic
width-w edges become ordinary width-w
edges on that lift. The relations beta_(j+s)=beta_j and
q_(j+s)=q_j+t retain all seam selections and weights. No artificial
coupling is introduced between the two ends of I.

The complement condition is necessary for this noncyclic statement.
The independent review supplied s=20, w=3, I=[1,20): indices 1 and19
have cyclic distance2 but unwrapped distance18, despite |I|<s. Our
polynomial windows satisfy the much stronger eventual condition
s>2(L+2A+2w), because s exceeds every fixed polynomial in p. Without
that condition a wrap correction must be retained. This qualification
repairs the initial written endpoint assumption; it changes no tested
window or asymptotic exponent.

The perturbation to the true inverse is independently bounded by

```
||H^-1-N^-1|| <= 32p^2 e_p.
```

It is much smaller than the locality allowance and follows from the
resolvent identity with the accepted ||N^-1||<=4p.

## Local phase cells, clipped endpoints and cost

Intersect I with the globally fixed phase cells. A complete cell retains
its accepted length between d-2 and 4d+1. A clipped endpoint piece of
length at most 4w is entirely boundary; it has no local interior. Every
other piece has its first and last w vertices designated boundary. Empty
interiors are skipped. There are at most two clipped pieces, including
when I crosses the physical seam; the physical seam cells themselves
remain globally separate and have the same retained minimum length.
In particular, insert each lifted ORIGINAL physical period cut as a cell
boundary, even if the unwrapped values of q_j-j would merge its two
adjacent cells. Their cross-cut coefficients retain the original directed
rounding in H. A window shorter than one period has at most one such
cut, adding only O(w) boundary vertices within the bound below.

Every interior block is still exactly similar to a symmetric truncated
Toeplitz matrix using the same global weights. Distances beyond w remain
zero. No two different cell interiors interact. Eliminating interiors
preserves the original row diagonal-dominance gap and never increases
the Schur row norm, by the accepted Schur induction. The inherited
ordered boundary matrix is noncyclic banded with bandwidth O(w): fill
can join the two boundary groups of one cell and pre-existing entries
can join adjacent cell groups. The artificial endpoints have no wrap
correction. A harmless constant-width cyclic solver could also be used
with zero wrap entries, but is unnecessary.

For M=|I| and eventual d>4w, a loose useful bound is

```
n_boundary <= 4 M w/d + 12w.
```

The complete cells contribute two groups of w; all short clipped pieces
together contribute at most 8w. The extra 12w includes endpoint cell
counting. The accepted local Gohberg-Semencul and boundary LU residual
proofs apply unchanged to principal restrictions: gap is still at least
1/(8p), local norms are at most 8p, coefficient precision is the same,
and the Schur gap after its directed rounding is at least 1/(16p).
No error factor grows with M or with the number of cells. The completed
local inverse error remains bounded by

```
2^(64p)*p^64*eta * max(1,||input||).
```

Its per-line cost is

```
O((M + M w^2/d + w^2)*p^(1+delta)).
```

The final term is the artificial-boundary cost. All convolutions have
length at most 4d+1, with O(p)-bit retained factors. The complexity uses
the already cited unconditional short integer multiplier, never the
stronger multiplication bound being proved. Exact window precomputation
may have longer rational determinant records, but costs polynomial in
t and p over all origins and all d axes. Because t=n^o(1), this is still
n^o(1). Online factors retain O(p)-bit records.

The factor bank must be accessed sequentially. If the outer box order is
`[A] x [k_i] x [B]` followed by a complete inner microbox, scan the axis-i
catalogue in increasing k_i for each fixed A, copy the current page onto
work tapes, and reuse it throughout B and the inner line scans. Rewind
the catalogue once at the next A. A page has
O((M+M*w^2/d+w^2)*p) retained bits: local weights and GS generators use
O(M) records, while couplings and noncyclic boundary LU use O(n_boundary*w).
Its scans and resets per inner line are included in the displayed solve
cost. Copying whole pages per (A,k_i), and even polynomial metadata per
page, costs O(V) because the complete inner microbox has at least
L^(d-1) records, exceeding every fixed polynomial in p. This uses neither
random table access nor a permutation of the large outer field.
Polynomial-time factor regeneration once per complete microbox would be
another valid amortization, but regeneration per line is not claimed.

## Fractional cores and generous halos

Choose the dyadic tile side L=2^ceil(8 log2 p) and the integer halo
A=4096p^3. Require the eventual size condition
s>2(L+2A+2w) for every axis. Since t is a power of two
and exceeds every fixed polynomial in p, L divides t. Tile the target
indices into complete cores T_k=[kL,(k+1)L). Corresponding source cores
are

```
J_k=[floor(kL/rho), floor((k+1)L/rho)).
```

They partition [0,s) exactly, including both physical ends. Their lengths
are floor(L/rho) or ceil(L/rho); in particular they are at least L/2-1.
For compression, provide the complete target halo interval
T_k^+=[kL-A,(k+1)L+A), interpreted periodically. Let I_k be the source
indices whose q_j belong to this interval. Its endpoints are monotone
and have at most constant rounding discrepancy from rho^-1 T_k^+.
Every j in J_k is at source distance at least A/2-3 from its artificial
endpoints. This exceeds 512p^3 for p>100. Its local C selection uses
only supplied target halo records and preserves increasing order.

The near-one interval constraint provides useful padding headroom:
theta>1/(4d), rho<2 imply

```
L-|J_k| >= L/(8d)-1.
```

At L>=64dA, the complete source halo I_k also fits in L slots, with
room for endpoint discrepancies. This condition follows from d<=p and
p>100 with the chosen L. Source halos can therefore be padded to the
same dyadic L within each tile. The resulting global padded volume is
exactly T, and the retained tensor-size inequality T/S<2 controls it.
Padding these near-one source intervals does not introduce 2^d volume.

For expansion, the normalized S/2 row at a target core coordinate uses
source centers within J_k up to a constant endpoint discrepancy. The
source halo contains the existing Gaussian radius, at most O(p), with
enormous room. Its omitted periodic Gaussian tails are below 2^(-p-10)
under the accepted blocked-evaluation estimate. Only target core rows
are needed; expansion need not produce an extra target halo.

The total target input-halo volume for compression is

```
T * (1+2A/L)^d <= T*exp(2dA/L),
```

so it is bounded by a fixed constant times T. Intermediate source padded
fields have length L; target halo fields have length L+2A. Sequentially
processing axes only reduces this volume. If an internal field exchange
requires dyadic lengths, padding the two participating polynomial fields
temporarily costs a constant factor in that call; it is removed before
the next call. Simultaneously padding every target halo field to 2L
would cost 2^d and is not permitted.

## Tensor core error requires no halo refresh

Set j_scale=ceil(log2(32p)), D_normalized=D/2^(2u).
Each exact principal map

```
B_k = D_normalized H_(I_k)^-1 C_(I_k,T_k^+) / 2^j_scale
```

has row norm at most 1/4, as does its core restriction. The corresponding
true global compression is D_normalized N^-1 C/2^j_scale, with norm at
most 1/8. Their core-row difference, after embedding input halo windows
in the global input space, is bounded by the locality and perturbation
allowances above. Normalization only decreases those allowances.

An initially gathered tensor halo box is processed once along each axis.
For each axis the completed local inverse may compute its full source
window and immediately discard noncore rows. The exact final core map
is the tensor product of these restricted one-axis maps. Repeated use
of the tensor product identity and contraction bounds gives total core
error at most the sum of the d one-axis row-error bounds. There is no
volume or line-length factor in the sup norm. Incorrect global values
near the artificial cuts of a local window are never separately fed
back as purported global halo values. Thus no global halo refresh is
required between axes.

The same argument applies to expansion, whose normalized restricted
positive Gaussian maps have norm below 3/4. Intermediate exact maps
remain contractions; directed p-grid component truncation retains the
disk output, and its error adds at most sqrt(2)*2^-p per axis. Combining
accepted blocked evaluation, principal inverse arithmetic, locality and
perturbation preserves the original loose d*p^2*2^-p tensor interface.
The scalar normalization and total exponent
gamma=d(2u+j_scale+1) remain unchanged. No locality argument replaces
the retained exact global Fourier identity; the computed local maps
are approximations to its same normalized analytic maps.

## Complete fixed-tape transfer and its review

The intended schedule gathers the low log2 L bits of every padded axis
into a common microbox suffix by one independently reviewed global bit
router. The retained padded box is dyadic with volume T. A fractional
source reshape can then move one inner log2 L-bit field adjacent to its
outer field, split the increasing j stream at J_k boundaries, emit each
complete suffix block with zero padding to L, and return the inner field
to the suffix. Every partial padded tensor has volume at most T. Its
row counters and nearest/interval boundaries have O(p) bits and can be
generated by additions and comparisons; polynomial setup per complete
microbox record is absorbed by its superpolynomial size.

The all-size tape proof establishes initial halo duplication without
copying an unbounded number of coarse boxes, stable order across the
other coarse fields, and final periodic boundary/crop assembly. Its
explicit construction is in the [complete tape report](bulk-resampling-tape-transfer.md).
The inner-field moves cost O(V d polylog p), not
O(V d ell^tau), because each moved field has O(log p) bits. Source interval
padding uses near-one T/S<2; compression's target halo duplication uses
the separate displayed overlap bound. The scheduler must not merge
these two arguments into an uncharged arbitrary mixed-radix transpose.

With this schedule and the separately accepted general router, total
arithmetic retains the phase cost

```
O(T*p^(1+delta)*(d+w^2+d*w^2/L)),
```

and exposures would cost O(Tp*d*polylog p) after one O(Tp*p^tau*polylog p)
global layout call. For epsilon<tau the former movement is lower order.
This replaces the old resampling-axis margin a(1-epsilon) by a as a
conditional consequence of the reviewed construction. It is not an
independently complete multiplication claim. Finite prototypes test locality,
fractional boundaries, clipped cells and tensor core error. They cannot
by themselves certify the fixed-tape time bound.

The [independent bulk review](review-bulk-resampling.md) accepts the full
written analytic and fixed-tape transfer after the complement-gap and
physical-period-cut qualifications. Its own joined stream experiment
checks 84824 output records in six two/three-axis schedules, including
mixed-radix moves, fractional intervals, wrapping halos, sequential
factor pages and final row order. Its separate boundary negatives retain
the four invalid variants: insufficient complement gap, merging original
period cells, cropping an unprocessed axis and simultaneous dyadic padding.
The producer source and original certificate bytes remain unchanged.
