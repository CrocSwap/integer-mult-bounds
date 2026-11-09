# Exact nonempty-interior admission at every original target window

Prepared for **@CubeJerry** with substantial OpenAI assistance. Apache-2.0.
**Source-bound geometry theorem; no new kappa.** Base:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## 1. Obligation, source and predecessor boundary

The actual common rational Reference defines selected coordinates by

`phi(j)=floor(e*j/S+1/2)`, `q(j)=j+phi(j)`, `0<=j<S`,

where S is the original source period, e its positive excess, `0<e<S`, and
`N=S+e` the target period. The other target coordinates are identity holes.
These are the literal `Reference.__init__`, `Coordinates` and
`SelectedAddresses` rules in `research/rational-unitary-fft/gaussian_reference.py`.
No phase is recomputed after translating a target window.

The literal `Core.partition` walks the original target window. Every hole
becomes a boundary singleton. It divides selected coordinates into maximal
consecutive source runs of one original phase, then invokes the authenticated
capped `carve(m,W,cap)` on each run. That body is
`research/capped-phase-fusion/evidence/gaussian_fast_ultra/check_capped_gauges.py`.
It returns only boundary when `m<=6W`; otherwise its loop immediately creates
an interior. The original complete Core's source and numerical contracts
remain in force; this theorem supplies one geometric admission.

Nick Petalas's CrocSwap/integer-mult-bounds#6259 already proves the source-phase
cut formulas, endpoint half-cell lengths and a constant-size boundary count
for Jose Manuel's **different 4w physical-source carve**. The capped-interior
lineage already proves the dyadic cap, W-separation and asymptotic boundary
density. We cite those facts and do not claim a new density order, phase-floor
identity, Gaussian inverse, or Schur-bandwidth bound.

The present result is the exact decision at the actual **target-coordinate
window with identity holes** and the current **6W capped carve**, followed by a
sharp finite uniform admission of every original start. Its hypothesis is
weaker than requiring both endpoint half-cells to be long. Earlier density
estimates already suggest eventual nonemptiness; the contribution is an exact
source-specific finite guard and its literal production-body check.

## 2. Exact largest selected phase run, without enumerating cells

Consider an ordinary window `[a,b)` with integer `0<=a<b<=N`. Let `L=b-a`.
Because j is integral, `q(j)=floor(N*j/S+1/2)`. Thus `a<=q(j)<b` is equivalent to

`S(2a-1)/(2N) <= j < S(2b-1)/(2N)`.

The selected source indices in the target window are exactly `[j0,j1)`, where

`j0=ceil(S(2a-1)/(2N))`, `j1=ceil(S(2b-1)/(2N))`.           (1)

The ordinary-window domain gives `0<=j0<=j1<=S`, including a=0, b=N and a
window consisting only of a hole. This inverse image is not `[a,b)` in source
coordinates; deleting holes without changing the endpoints is invalid.

Use the credited exact source-phase cuts

`A_0=0`, `A_(e+1)=S`,
`A_c=ceil(S(2c-1)/(2e))` for `1<=c<=e`.                  (2)

Phase c occupies `[A_c,A_(c+1))`. Its first and last phase lengths are
`ceil(S/(2e))` and `floor(S/(2e))`. An internal phase length is either
`h=floor(S/e)` or `h+1`; the latter disappears if S/e is integral. Empty
endpoint phases are harmless in the general formula.

If j0=j1, the largest selected phase run has length `M=0`. Otherwise set

`c0=floor(e*j0/S+1/2)`, `c1=floor(e*(j1-1)/S+1/2)`.

When c0=c1, `M=j1-j0`. When c0<c1, the two clipped endpoint runs have lengths

`u=A_(c0+1)-j0`, `v=j1-A_c1`.                            (3)

There are `m=c1-c0-1` complete middle cells, all internal source phases. If
m=0 then `M=max(u,v)`. If m>0, put `D=A_c1-A_(c0+1)`. Since these m lengths
are h or h+1, their maximum is exactly `h+[D>m*h]`. Consequently

`M=max(u,v,h+[D>m*h])` when m>0.                         (4)

Equations (1)--(4) use a fixed number of integer operations independent of S,
e, N, L and the number of cells. Within a source phase, q(j+1)-q(j)=1; a phase
increase creates one hole and breaks the target run. Hence M is exactly the
maximum piece length passed to the original capped carve by `Core.partition`.
The exact total D detects whether any h+1 middle cell occurs; inspecting an
arbitrary representative middle cell would be insufficient.

## 3. Exact admission for the unchanged capped carve

Assume integer W>=1 and a positive dyadic cap with `2 cap<=S`, as required by
the source's dyadic interior interface. For a selected run of length m:

* If `m<=6W`, the literal carve returns one boundary piece.
* If `m>6W`, its initial remaining length is `R=m-2W>4W`. Its first interior
  length is `min(cap,2^floor(log2(R-W)))`, a positive dyadic integer at most
  cap. The loop therefore produces at least one interior.

For every ordinary target window in Section 2,

`I is nonempty iff M>6W`.                                (5)

There is no substitute interior or change to the source partition. The source
`Reference.interior` is invoked at the actual retained start and checks the
same phase and contiguous selected coordinates. The bound `2cap<=S` supplies
its source-size admission for every subblock. The first and last W selected
vertices of a long run remain boundary, so (5) also gives `|J|>=2W>0` and
`0<|I|<L`. Existing separation and matrix-support arguments are inherited;
(5) does not prove their numerical consequences.

## 4. A uniform guard for every original start

**Theorem.** Suppose the domain above holds, and

`S >= e(6W+1)`, `L >= 12W+2`, `L<=N`.                    (6)

Then every ordinary original target window of length L has a nonempty interior
and a nonempty boundary under the literal production carve.

**Proof.** Every complete **internal** source phase cell has length at least
`floor(S/e)>=6W+1`. The two endpoint half-cells may be short. Also
`e/S<=1/(6W+1)<1/2`, so the first selected coordinate is 0, the last is N-1,
and all holes are singletons between successive nonempty phase cells.

Suppose a window had no selected run longer than 6W. It cannot meet three
selected phase cells: the middle one would be a complete internal cell, whose
length is at least 6W+1. If it meets two cells and starts or ends on an external
hole, the adjacent selected cell is complete and internal, again a
contradiction. Otherwise those two clipped runs contribute at most 6W vertices
each, with one hole between them, giving length at most `12W+1`.

If it meets only one selected cell, it cannot include both neighboring holes,
because that would make the cell a complete internal cell. Its length is at
most `6W+1`. A window with no selected coordinate contains at most one hole.
These alternatives all contradict `L>=12W+2`. Thus M>6W; Section 3 proves the
assertion. ∎

Requiring `floor(S/(2e))>=6W+1` would also suffice, but unnecessarily requires
both original half-cells to be long. Equation (6) avoids that factor of two
while preserving clipped endpoint phases and identity holes.

### Both integer thresholds have exact adverse families

For each W>=1 choose `S=18W+3`, e=3, `a=3W+3`, `L=12W+1`. The two internal
phase cells both have length 6W+1, with one target hole between them. The window
clips one selected coordinate from each end of their union, leaving lengths
6W and 6W and that hole. The source-ratio guard holds with equality but I is
empty. Moreover `N-L=6W+5>=W`. Thus the ordinary-window length threshold cannot
be lowered by one even with the complementary-gap guard retained.

Conversely choose `S=18W+2`, e=3, a=0 and `L=12W+2`. Then
`S=e(6W+1)-1`, N=18W+5, and the first two phase lengths are 3W+1 and 6W.
The window includes a prefix of 3W-1 selected coordinates from the next phase,
with two holes in total. Its largest selected run is 6W, so I is empty.
Here `N-L=6W+3>=W`. Thus the source-ratio threshold cannot be lowered by one
while retaining the length and complementary-gap guards.

These are sharpness statements in the **ordinary-window/complementary-gap domain**. Their L
need not be dyadic. No separately optimal threshold for the narrower dyadic
aligned Core family is claimed; that family may use (6) or exact decision (5).

## 5. Conservative complete-Core family and surviving admissions

The [complete Core's source family](https://github.com/CubeJerry/integer-mult-bounds/blob/6fb9ab776b7d0956b8bcc2d3cfde0f3034421630/research/complete-core-physical-join/NUMERICS.md)
binds the unchanged `Core.partition` source to ordinary
original windows. Its additional admissions include dyadic side and cap,
original alignment, `2cap<=S`, the complementary gap `N-L>=W`, exact source
accuracy and norm certificates. These are preserved. Suppose its retained
conservative regime has uniform constants with

`theta=e/S <= p^-2`, `W=O(sqrt(p) polylog p)`,
`L=2^ceil(400 log2 p)`.

Then `theta(6W+1)->0` and `(12W+2)/L->0`, so both inequalities (6) hold for
all sufficiently large p. Every original Core start on every active axis
therefore has a nonempty interior and boundary. There is no separate
nonemptiness assumption for its K contexts. The conclusion is uniform in K
and the original positions, including the first and last complete sections.

This removes only the empty-interior case in that stated asymptotic source
family. It neither supplies the theta or W bounds nor proves row gap,
conditioning, matrix/Schur formation, uniform precision, compiler, native
stock, owner lifecycle, whole halo delivery or final recovery. Short finite
families outside (6) retain exact classifier (5); an empty classification is
not an implementation of a missing zero-dimensional solver.

The parameter family is a cited conditional source contract, supplied by the
complete-Core and global-cohort predecessors. The geometric statement does
not depend on their unpublished data, modified code or acceptance status:
its three executable inputs are already pinned on canonical main.

## 6. Full added cost and model boundary

The guard reads input-independent source descriptors S,e,W,L,cap. Let d be the
maximum of their binary lengths and the original endpoint lengths. The uniform
guard uses a fixed number of comparisons, shifts, additions and products,
including dyadic-cap validation. Exact single-window decision (1)--(4) adds a
fixed number of integer divisions. Ordinary binary arithmetic supplies
O(d^2) bit work and O(d) scratch for either calculation. This is not constant
bit time. Input access, produced descriptors and disposal have O(d) size and
are included in the bound.

When each axis has the same S,e,W,L,cap descriptors across all K contexts,
the uniform guard is checked once per actual axis, costing O(g d^2) without
scanning or materializing contexts. Every distinct descriptor must otherwise
be checked and charged; heterogeneous families may require K g checks. If
a caller instead uses the exact local test at every context and axis, its full
extra setup is O(K g d^2). All existing coefficient, catalogue, route, backing,
payload and native bills are retained. This is source setup: there is no new
payload pass, floating-point computation, numerical error or supplier gain.

These checks fit the cited complete-Core preparation envelope
`K 2^(O(ell_original)) poly(p)` with its full K factor retained. No new saving
in the dominant online bill follows. The finite-domain geometry theorem is
unconditional; the whole multiplication construction remains conditional on
every other source and physical premise.

The verifier compiles only the authenticated Reference **geometry prefix**,
its original `interior` method, and unchanged `Core.partition` and capped
`carve` bodies. It excludes the constructor continuation that makes exponential
intervals and Gaussian values. This is a transparent source projection for
the geometric theorem, not an actual numerical Gaussian or native-tape run.
The decision formula is independent of that source projection.

## 7. Evidence and remaining work

The independent coordinate oracle covers all 772,850 ordinary windows for
every `2<=S<=40`, `1<=e<S`, original start and positive window length. It
constructs rational phases by independent nearest-half-up comparison and walks
target coordinates literally, including holes. All closed-form answers agree,
including 10,660 hole-only windows and 63,180 physical-endpoint windows.

The original source geometry/partition/carve bodies check 77,793 finite
configurations, including 855 admitted by the uniform guard. In the complete
N=128, L=64 two-window example S=127,e=1,W=4,cap=4, both original windows have
five interior blocks, 20 interior rows and 44 boundary rows. These are source
geometry outputs, not numerical Core outputs.

Sixteen W values corroborate each sharp adverse family. Controls detect
target/source-coordinate confusion, origin rebasing, substitution of a smaller
width for the actual carve width, wrong tie-to-even rounding, invalid
windows/caps/widths and corruption of each actual source input. Descriptors of
64, 257 and 1024 bits exercise the fixed-size formula without enumerating
their exponentially large periods. Written Sections 2--6, not finite counts,
establish the universal claims.

Open questions are threading this finite guard into the actual uniform source
constructor with its remaining matrix/precision certificates, optimizing the
narrower dyadic-aligned admission, and implementing genuinely empty short
windows at the full native interface. None is answered by replacing a missing
solver with an identity or treating finite geometry checks as analytic recovery.
