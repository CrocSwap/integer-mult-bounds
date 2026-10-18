# A single existing phase child cannot absorb this idle-axis defect

This is a source-bound obstruction to a precise proposed cost change. It is
not a barrier to changed words or arbitrary encodings, and gives no new kappa.

## 1. The replacement interface

Use the retained PR3148 T740 allocation and the literal source recipe at
owner replica zero, port zero. The independent stream inputs are arbitrary
complex arrays on `F2^73`, including arbitrary entering dirt. Transfer axis
`v=16` from residual child 10 to residual child 12. Their ranks change from
`48,48` to `47,49`. All hosted calls, other residuals, interactions, translations
and the exact target operator stay fixed.

Permit replacing exactly one of the twenty residual phase-child positions.
At that position the new completed child is Fourier diagonal and acts on
one scalar stream. Its eigenvalue `z(x)` at character `x` can be *any* nonzero
complex number. This grants more freedom than a legitimate quarter-turn
phase child, regardless of its new address axes or rank.

Before and after that child, grant arbitrary invertible constant scalar
stream matrices, at zero cost. Their action is explicitly
`L_stream tensor I_address` and `R_stream tensor I_address`: they apply the
same stream map at every address and do not mix addresses with stream labels.
They need not be reciprocal before normalization. Arbitrary constant global
phases and arbitrary dirty spectator streams restored exactly are allowed.
The one-child operator, rather than its private recursive implementation,
is the interface being replaced.

This assumption is essential. A character-dependent controlled permutation,
an address-changing chart, two child uses or two changed sites belongs to a
different interface. Scalar coefficients alone do not imply stream-only action.
No such broader encoding is excluded or assigned a zero implementation cost.

## 2. A common projector is necessary

Let `E=e_s e_s^T` select the child's stream. With a choice of adapter order,
the local replacement at character `x` is

```
R(x) = L [I+(z(x)-1)E] K.
```

At character zero the required local operator is `R(0)=I`. Since `z(0)!=0`,
the bracket is invertible, so

```
K = [I+(z(0)-1)E]^-1 L^-1,
R(x) = I + (z(x)/z(0)-1) P,
P = L E L^-1,   P^2=P,   rank(P)=1.
```

The normalization also removes a constant global phase. In particular:

1. `rank(R(x)-I)<=1` at every character;
2. all nonzero flattened matrices `R(x)-I` span the same one-dimensional
   space, because the same `P` is used at every character;
3. a nonzero rank-one defect has nonzero trace, since its trace is the scalar
   multiplying `P`. A nonzero rank-one nilpotent is insufficient.

Conversely, on any supplied finite character set containing zero, rank at
most one, common one-dimensional span, nonzero trace for nonzero defects,
and `1+trace(R(x)-I)!=0` characterize this favorable interface on that set.
For a nonzero rank-one matrix `D`, `D^2=trace(D)D`, so
`P=D/trace(D)` is the required idempotent. Every rank-one idempotent is similar
to `E`. If all defects vanish, choose any `P` and all eigenvalues one.
The converse is a useful control; no finite passing set proves a full-domain
replacement or a legal physical implementation.

Adding arbitrary dirty restored scalar spectator streams cannot avoid the
necessary condition. On the extended space the same argument gives a rank-one
projector. The full required endpoint is `R(x) direct-sum I_spectator`; any
nonzero defect therefore forces that projector to vanish on, and have no
cross terms with, all spectator rows and columns. Restriction to the eight
visible streams gives the same condition. A clean ancillary subspace or
unrestored garbage is a different promise.

## 3. Bind the condition to literal cuts

All matrices below are in the Fourier-character representation; global phase
is retained. At a candidate site, write the altered chronological word as
`B(x) D_site(x) A(x)`, with earlier factors on the right. Omit only that site's
residual child phase. Retain its separate address translation, the other
child at the same event, every hosted phase and every other literal event.
The required replacement is unique:

```
R_site(x) = B(x)^-1 T(x) A(x)^-1,
T(x) = i^popcount(x) I_8.
```

Both checkers verify `B D_site A` equals the altered word and
`B R_site A=T` at the tested cuts. At character zero all twenty required
replacements equal identity. The original unaltered source word equals `T`
at each character used for a witness. Thus each finite witness is an exact
counterexample to a necessary full-domain identity, not an extrapolation from
sampling.

For nineteen sites, `x=16` alone gives a nonzero two-by-two minor of
`R_site(16)-I`. Their row/column indices and exact determinants are in
`RESULT.json`; every determinant is `2` or `-2`. This excludes all one-stream
phase replacements at those sites, even with free oblique scalar encoding.

Site 12 exposes why checking each character separately is too weak. With
zero-based matrix indices, the exact required defects are

```
R_12(16)-I       = (i-1)(E_(6,4)+E_(6,6)),
R_12(33554432)-I = (i-1)E_(0,0).
```

Each parenthesized matrix is a rank-one idempotent. They are different,
and even commute (both products are zero). Flattening positions `(6,4)` and
`(0,0)` across those two character defects gives determinant
`(i-1)^2=-2i`, which is nonzero. They cannot share one fixed projector.
This excludes the remaining site. Commutativity alone would not have sufficed.

The finite computation covers exactly these twenty sites for this one
transfer, owner and port. The algebraic exclusion quantifies over every
nonzero eigenvalue function, every invertible *stream-only* scalar adapter
and every proposed child rank, because none can pass the necessary witnesses.
It does not quantify over other transfers or changed intervening words.

## 4. Why this tests recursive cost

Let `p=1-a`, `0<a<1`. Holding every other invoice term, width and stock
normalization fixed, strict concavity gives

```
(47/73)^p+(49/73)^p < 2(48/73)^p.
```

Thus the proposed transfer has a favorable *recursive child* profile at
unchanged call count and rank mass. PR3220 ruled out a separately added
whole repair child under its bounded fixed-mass tariff. This proposal instead
tries to replace an existing call and avoid that added tariff; PR3229's
abstract direct-sum shared-repair premise does not settle it.

The optimistic test here grants the replacement arbitrary eigenvalues and
all adapter, movement, source-access, helper, restoration, precision and stock
costs free within the stated stream-only interface; no additional address
operator is granted. It already fails exact operator equality at every site. Hence no
implementation within this one-site stream-only contract can realize the
claimed profile saving. This is an algebraic rejection of the stated proposal,
not a runtime lower bound, a universal cost obstruction or a stronger kappa.
A passing broader construction would need its own complete invoice and
both supplier/outer interfaces; unknown costs are not zero.

## 5. Evidence, controls and credit

`verify.py` authenticates the retained input bytes and executes the exact
hashed interpreter source via `compile(..., optimize=0)`, bypassing bytecode
caches. It reuses that source's data-event interpreter, with separate
Gaussian-rational prefix/suffix inversion. It authenticates all 2,717,280 T740
fill rows, reconstructs the actual owner-zero/port-zero residuals, and finds
all witnesses after 27 deterministic characters.

`independent.py` is a separate elementary-matrix reconstruction and reverse
factor inverse implementation. It reuses only authenticated source/data
parsing, not the retained `run_data_event` or `replay` functions, and checks a
larger explicitly declared finite character domain. Its receipt is separate.
These are independently tasked AI-assisted implementations, not independent
human review. `VERIFY.json` declares both complete local commands.

Controls include an accepted non-coordinate projector, an unchanged literal
child, a pair of individually valid but inconsistent projectors, a nonzero
rank-one nilpotent and a rank-two defect. The actual receiver witness is also
a source-bound counterexample to accepting only per-character rank. Full
arbitrary stream input columns and exact phase are retained.

Credit remains with Rohan Arun's idle-axis proposal, Gonzalo-Mier's PR3199
physical interpreter/census, Nick Petalas's PR3187 physical counterexample,
Gareth Davidson's PR1387 obstruction, Jeremy Diviney's PR3148 allocation,
and the retained dcharb78, Marius-Paul Dumitrean, Jeremy Kothe, geometry/native
and selected-supplier lineage. Ross Richardson's PR3220 motivated absorption;
PR3229's abstract shared-repair follow-up is explicitly distinguished rather
than repeated. Actual runtime source bytes and base are pinned in `SOURCES.json`.
This proof, the one-site test and its separate oracle were prepared by Ross
Richardson with substantial OpenAI Codex assistance. New material Apache-2.0;
source archives and notices are unchanged. No formal proof kernel, full native
supplier, complete outer multiplication theorem or new selected result is claimed.
