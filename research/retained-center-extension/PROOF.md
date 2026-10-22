# Exact interface and remaining cost obligation

## Source and boundary

Use PR4610 head `1eb8da6cfb35512c0cc2533413e5ca42f48e13c6`, specifically
`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`. This is its stronger
round-three word, not its round-two artifact. Exact compressed bytes, blob
and SHA-256 are pinned in SOURCES.json. Scientific base main is
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`; selected conditional kappa is
0.00302015. No selected files or frozen sources change.

The source has 632 persistent arbitrary fields and an owned temporary reused
eight times. Each lifetime clears the temporary, copies a persistent field
in an eight-dimensional chart, transports the temporary to the empty chart,
scatters it into data fields, and clears it. Eight paid rank-eight transforms
are included in its full invoice. The source persistent fields are not clean
scratch.

Give lifetime j a distinct arbitrary field z_j in its actual copy-input chart.
Delete its clears and replace `z_j := source` by `z_j += source`. Leave all
source scalars, transports, native warps and persistent boundaries unchanged.
The output z_j remains at the empty chart after its existing paid transform.
There are 640 independent inputs and outputs. Allocation is a finite extra
input/role contract; scalar additions, monomial routes and storage still have
finite volume-linear work. The change has no new owned erasure premise.

Every modified scalar gate is invertible, the transports and native monomial
warps are invertible, and there are no clears or copies left. Thus the new
word is invertible at every width satisfying the retained native contract.
Each scalar retains its actual common chart. Its additional scalar cost is
bounded by eight unit complex additions per invocation; removed copies and
clears do not fund unlisted recursive work. All original recursive calls
remain. This package does not assert a practical time or storage improvement.

## Exact block endpoint

On the original variables x=(X,Y,H), the source's normalized endpoint is
A x=(X,Y+X,H). Linearity gives the new endpoint

```
x' = A x + B z,
z' = R x + z.
```

The verifier derives B and R from the literal word rather than assuming them.
All 640 columns are represented as sparse rational sums of independent input
symbols with free noncommuting warp words. Adjacent inverse warp letters
cancel; all remaining words cancel at the endpoint. The old-input columns
are compared separately with a fresh baseline replay that retains the owned
copies. B and R in ABI.json are the actual derived constants.

B is zero outside Y rows. R reads only X and original helper inputs. Hence,
writing S=A-I, we have S^2=0, SB=0, RS=0 and RB=0. Direct rational elimination
gives rank(B)=rank(R)=8. Also B^T B=(7/2)I_8. In particular B is injective and
R is surjective, so BR has rank eight.

For K=M-I, block multiplication gives

```
K   = [[S, B], [R, 0]],
K^2 = [[BR,0], [0,0]],
K^3 = 0.
```

Thus K^2 is nonzero and M^-1=I-K+K^2. Exact sparse multiplication verifies
both inverse identities. This is a unipotent endpoint whose off-identity part
has nilpotence index three, with a central square term. It does not classify realizable Gaussian
controllers or imply a larger exponent.

## The actual raw inverse transpose

For a product T_k ... T_1, inverse transpose is T_k^-T ... T_1^-T. Therefore
use the **same chronological order** and inverse-transpose every elementary
gate. An addition `d += a s` becomes `s -= a d`; a scale becomes its reciprocal;
each native monomial and Gaussian transport becomes its inverse transpose.

If the primal chart is C_F, use C_F^-T as the dual chart. A primal transition
T=C_G C_F^-1 then satisfies T^-T C_F^-T=C_G^-T. The same chart labels and
Gaussian ranks apply. Monomial inverse transposes are still monomial. This
argument retains actual phases/operators under inverse transpose; it does
not replace them by rank-only identities. It invokes the authenticated source
operators, rather than independently relowering their Clifford recipes.

The verifier separately emits and replays this dual word, using distinct free
warp symbols, and compares its complete rational endpoint with
`(I-K+K^2)^T`. It also checks the exact primal/dual pairing. The original
source backward word is not substituted for the new raw dual. Both emitted
words have exactly the complete source paid profile.

## Why this is not eight new productive jobs

The formal self-residual z_j has rank eight between nested endpoint charts.
It is accompanied by R_j x. Each R_j has 100--104 nonzero original-input
terms. Furthermore Bz changes every Y output. For example arbitrary z_0
affects 56 old outputs with nonzero coefficients. Those are independent input
columns; setting them to zero would change the contract.

Even in stripped scalar coordinates the tempting elimination is

```
[[I,-B],[0,I]] M [[I,0],[-R,I]] = diag(A-BR,I_8).
```

It gives A-BR, not A. Moreover its output shear mixes empty-chart center
outputs with eight-dimensional Y outputs, and its input shear mixes centers
in eight-dimensional charts with X/helper inputs in other charts. Actual
Gaussian/frame implementation costs are unknown. This elimination is not a
free physical decoder and supplies no independent rank-eight target credit.

## Complete obligation ledger and expansion decision

* Proved in the stated native model: 640 arbitrary-input reversible word;
  scalar/frame legality; exact normalized endpoint; all eight center data
  retained; inverse-transpose word; unchanged recursive paid profile.
* Constructively bounded: finite additional roles/storage and scalar work;
  no new recursive call is introduced by this extension itself.
* Retained premises: source all-column/all-width native and monomial/phase
  contracts, numerical precision and movement model. No fresh physical phase
  audit is claimed.
* Unknown: independent productive-output consumer; its Gaussian requests,
  lost targets, routing and precision; completion and uniform compiler; BIT
  supplier counterpart and the full outer transfer.

Decision: preserve this changed interface as a bounded construction checkpoint,
then test a small exact consumer of this endpoint and its dual.
Stop if its fully charged target/paid moment is not positive. A hypothetical
64-rank-unit per-call center credit is a planning relaxation only. Further
root digits or an invoice that sets either B or R to zero cannot admit it.

CACHE.md and the updated registered replay provide a second kernel accepting
the explicit relation c=Rx. Its two-sided operator and raw dual are proved,
but the direct complete caller is more expensive than the original. The first
p16 scalar-span cache recycling screen also fails in its stated model. Neither
check supplies the unknown profitable consumer or removes the expansion gate.

The existing PR4359 embedded logger also retains dirty data and requires a
consumer. This extension instead replaces **all eight owned center lifetimes**
on the pinned round-three word, with no extra recursive call, and supplies the
complete 640-field block endpoint and its actual raw dual. The logger's input
and output contracts are not implicitly inherited as an admission theorem.

Credit and AI disclosure are in README.md. This is a finite exact interface
construction under retained source premises, not a multiplication theorem,
selected frontier change, or complete proof audit.
