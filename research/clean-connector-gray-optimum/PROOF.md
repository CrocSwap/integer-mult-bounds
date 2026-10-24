# Exact clean-row schedule and tariff

## Contract

There are n>=1 immutable source rows x_j and one target y_m for each nonzero
n-bit mask m. The requested update is y_m += A_m sum_(j in m) B_j x_j over F2.
All original rows can contain arbitrary data. The original dirty connector is
not used. Add one owned row c. Pay for allocation, its full zeroing pass and
release. After zeroing, the only map calls are B_j: c += B_j x_j and
A_m: y_m += A_m c. Each complete call restores its private scratch and heads.
Return c=0. The maps are arbitrary fixed linear maps and can be singular or
noncommuting. No output is read, no source is changed, and there is no hidden
observer between operations. A fixed finite word must work for all maps and
data. The word can depend on prices, but not on special map identities.

This is Cinna Davis's paid extra-row extension in PR1954. The new result
changes its schedule. It does not claim a new clean-row primitive or a new
Gray-code method. The stored map tables and row widths remain the same.

## Construction

Put g(k)=k XOR (k>>1), for 0<=k<2^n. Start c=0. For k=1,...,2^n-1, toggle the
one source bit on which g(k) differs from g(k-1), then call A_g(k) once. At
the last vertex g(2^n-1)=2^(n-1), toggle B_(n-1) to return c to zero.

The binary reflected Gray sequence visits every mask once; adjacent masks
differ in one bit. One direct proof is that its first half lists the
(n-1)-bit sequence and its second half lists that sequence in reverse order
with the top bit set. This proves the property by induction, including the
one-bit join and the final closing edge. At each vertex, induction on source
calls gives c=sum_(j in g(k)) B_j x_j. The one readout at that vertex gives
the required update. No rearrangement of A and B products is used. The
returned owned row is zero, and every other boundary is preserved.

The schedule has exactly 2^n source calls and 2^n-1 readouts. There are also
two explicit allocation/release actions. Program generation is exponential
in n, as is the requested output list. It is not a free physical compiler.

## Optimum over all finite legal words

Let every complete source call have price b>0 and every complete readout
have price a>=b. The exact map-call optimum is

```text
OPT = 2^n b + (2^n-1)a.
```

This statement does not require a bound on word length, a tour, one readout
per output, or a fixed source order. To prove necessity, specialize to scalar
identity maps with independent source bits. Let L count source calls and R
count readouts. Source parity is a walk from mask zero back to zero. It visits
at most L-1 distinct nonzero masks. Put N=2^n-1 and let k be the number of
visited nonzero masks, so k<=min(L-1,N). A valid word has L>=2. Every target
needs at least one readout. If its mask is not visited, one readout cannot
produce that target, so it needs at least two. Thus R>=2N-k.

If L<=N+1, then

```text
bL+aR >= b(N+1)+aN + (N+1-L)(a-b) >= b(N+1)+aN.
```

If L>=N+1, the simpler bounds L>=N+1 and R>=N give the same result.
The Gray cycle attains equality, which proves the formula. The identity
specialization is necessary for the generic all-map contract; it does not
prove a lower bound for a particular degenerate map assignment. If the
contract also requires pairwise-distinct maps at sufficient width, use a
common one-dimensional identity block and distinct maps on its complement.
The same source-bit argument then applies on the common block.

At n=5 with unit prices the optimum is 63 map calls. Uniform complete action
charges d can be included by replacing b,a with b+d,a+d. The comparison a>=b
is preserved. Fixed admission fees can be added afterward. Word-dependent
compiler, control or hosting fees need a separate analysis.

## The price restriction has an explicit counterexample

At n=3, the source sequence 0,1,2,0,1,2 visits prefixes 0,1,3,7,6,4,0.
Read each of 1,3,7,6,4 once. Read target 2 at prefixes 1 and 3, and target 5
at prefixes 1 and 4. These updates are correct for arbitrary maps by linearity.
This gives six source calls and nine readouts. At b=10,a=1 its bill is 69,
less than the Gray bill 87. Thus the theorem is not stated for a<b, and this
PR does not solve heterogeneous tariffs or the full call-profile frontier.

## Retained five-source root invoice

Use the PR1954 length-16 fixture: five source permutations and 31 distinct
output maps, each a 13-tap convolution after a permutation. Source price is
b=16, output price a=208 and per-action descriptor price d=13. The table below
keeps every line of its declared XOR/storage/scheduler tariff. These units
are not physical Turing-machine transitions or measured runtime.

| Item | Prior clean schedule | Gray clean schedule |
|---|---:|---:|
| Shared map tables | 26112 | 26112 |
| Shared row cells | 592 | 592 |
| Source updates | 2560 | 512 |
| Output updates | 6448 | 6448 |
| Action descriptors | 2483 | 819 |
| Mask-control descriptors | 403 | 403 |
| Allocation/release descriptors | 26 | 26 |
| Extra row cells | 16 | 16 |
| Zero writes | 16 | 16 |
| Total | 38656 | 34944 |

The saving is 128(b+d)=3712. The additional clean row is paid, not borrowed
as free zero data. The 31 mask-control descriptors and all cleanup charges
are retained. The lower bound optimizes complete map/action calls. It does
not optimize these admission terms over other implementation models.

The older named dirty comparator in PR1954 costs 41138 (10 B and 64 A), but
it is not the dirty-alphabet optimum. Adam Gall's PR2063 gives the exact
all-positive-price frontier for that original contract. Here complete prices
are b'=29 and a'=221. Its minimum is 12b'+62a'=14050, attained by the
source-surcharge profile. Add common 26704 to get 40754. The new paid-clean
bill therefore saves 5810 against the true dirty optimum in this fixture.
The verifier prices all 16 retained Pareto profiles, not only the old named
comparator. The PR2063 theorem supplies their completeness; its full census
is not reproved here.

## Verification and limits

The verifier checks formal source coefficients for n=1,...,12, and full-state
Dijkstra optima for n=1,2 under nine allowed price pairs each. Dijkstra visits
the finite coefficient-state graph and has no word-length cutoff. It checks
192 matrix/data cases, including singular maps, plus all 608 retained basis
columns and 64 mixed dirty states against the unchanged source and a separate
expanded target formula. Six word mutations fail. Nine unpaid invoice-line
controls fail. Source hashes and the typed exact receipt are mandatory.
These finite checks support the written proof; they do not establish its
unbounded quantifiers by sampling.

The paid root construction is complete only under its stated tariff and
complete-map premises. Recursive hosting, physical descriptor production,
map lowering, precision, a selected supplier caller and global contraction
remain open. No complete kappa value or selected frontier changes. Human
review and formal-kernel acceptance are not claimed.

New schedule analysis and verifier: Ali Romman with substantial OpenAI Codex
assistance, Apache-2.0. Cinna Davis retains credit for the paid clean-row
fixture and related borrowed-source Gray tour in PR2271. Ross Richardson
retains credit for the generic connector interface in PR943. Adam Gall
retains credit for the original dirty-alphabet price theorem in PR2063.
