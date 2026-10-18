# Saturating one coordinate-CNOT label forces the direct bill

This is a written theorem for the formal register model of commdata2338's
PR1414/1491 and Cinna Davis's PR1541. The finite checks corroborate the
argument; they are not its all-register justification. No physical supplier
or multiplication exponent is claimed.

## Model and statement

Let `G=GL_2(F2)`, with `a=[[1,1],[0,1]]`, `b=[[1,0],[1,1]]` and
`s=aba=bab=[[0,1],[1,0]]`. For finite `r>=t>=1`, work in the **formal**
algebra `M_r(F2[G])`. One paid unit is

`D_N(g)=I+([g]+1)N`, where `g` is only `a` or `b`, `N=uv^T`, and `v^T u=1`.

Free scalar `GL_r(F2)` basis changes are allowed. Every address call,
including an undo, costs one. No other address maps, copies, erasures,
overwrites or clean allocation are available. The complete target is

`T=I+([s]+1)P`, with `P=diag(I_t,0)`.

All inputs are arbitrary. Every extra register is restored and may not leak
into active outputs. Equality is in the group algebra, not merely its
natural two-dimensional address representation. The direct bill is `3t`:
use `bab` or `aba` on each active coordinate projector.

**Label-saturation theorem.** Write `n_a,n_b` for the paid label counts.
Every such word has `n_a,n_b>=t`. If `n_a=t`, then `n_b>=2t`; symmetrically,
if `n_b=t`, then `n_a>=2t`. At equality `(t,2t)` or `(2t,t)`, every normalized
paid projector satisfies `PN=N=NP`: the paid factors do not couple the
restored dirty complement. This last claim concerns normalized paid factors,
not the original placement of free scalar operations.

## 1. Credited reductions

Move all scalar basis changes to the right, conjugating each projector.
Augmentation `[g]->1` sends each paid factor and the target to `I`, so the
remaining scalar factor is `I`. Rank-one idempotence is preserved. This is
the normalization used by Gareth Davidson's PR1333 and the later CNOT work.

The sign quotient `G=S3 -> C2`, over
`F2[C2]=F2[epsilon]/(epsilon^2)`, sends each `a,b,s` to `1+epsilon`.
The normalized formal identity therefore gives

`sum_all N_i=P`, and hence `n_a+n_b = t (mod 2)`.

The matrix-sum identity is stronger than its trace consequence and is needed
below. This is the sign argument of PR1414, reused with credit.

Order coordinates by the two address components in the natural
representation. Chronological **left** multiplication gives

`a: [[I,N],[0,I]]`, `b: [[I,0],[N,I]]`,

and the target is `[[I+P,P],[P,I+P]]`. Only an `a` call changes the top block
row, with image in its vector `u`; only a `b` call changes the bottom block
row. The two final off-diagonal blocks `P` imply

`im P <= span(u_a)` and `im P <= span(u_b)`.

Thus each label occurs at least `t` times. This is the image-span step of
PR1541. A formal identity implies the represented identity; the converse is
not assumed.

## 2. Exactly t a calls make the top block row rigid

Suppose `n_a=t`. The `t` vectors `u_a` are a basis of `im P`. Conjugate by a
scalar basis change on `im P`, extended by the identity on `ker P`, so that
the image vectors, in occurrence order, are `e_1,...,e_t`. This conjugation
commutes with `P` and does not change the target or either count.

Write the running natural matrix as `[[A,B],[C,D]]`. Each active top row
is changed by exactly one call; all other top rows are unchanged. Top row
`i` is initially `[e_i^T,0]` and finally `[0,e_i^T]`. Before its unique call
it equals its initial row, and after that call it equals its final row.
Both have the same row sum. Consequently

`A+B=I` at **every** chronological cut.

A `b` call with projector `N_j` changes `C+D` by
`N_j(A+B)=N_j`. Initially and finally `C+D=I`, so

`sum_b N_j=0`.

Combine this with the full sign identity to obtain `sum_a N_i=P`. But
`N_i=e_i v_i^T`, so comparison of its distinct rows gives `v_i=e_i`.
Every `a` projector is therefore precisely `E_ii` in this basis.

At the unique `a` call on row `i`, the needed top-row change is
`[e_i^T,e_i^T]`. Since its covector is `e_i`, bottom row `i` at that instant
is exactly this row. Its two block halves sum to zero. On the other hand,

`C+D=I+sum_(b before a_i) N_j`.

Taking row `i` gives

`e_i^T = sum_(b before a_i) e_i^T N_j`.

Each summand is a scalar multiple of `v_j^T`. Thus **every active coordinate
covector belongs to the span of the b covectors**. This chronological step,
together with the zero sum, is the additional ingredient.

## 3. A zero rank-one sum must pay for both spans

Let `m=n_b`, let `U` be the `r by m` matrix with columns `u_j`, and let `V`
be the `m by r` matrix with rows `v_j^T`, over the `b` calls. We have

`UV=sum_b N_j=0`, `rank U>=t`, and `rank V>=t`.

Since `im V` is contained in `ker U`, rank-nullity gives

`m >= rank U + rank V >= 2t`.

This proves saturation. Exchanging the two address coordinates exchanges
`a` and `b` while fixing `s`, giving the symmetric statement.

If `m=2t`, both ranks are exactly `t`. Their column and row spans contain,
respectively, the active coordinate space and its covector space, so those
spans equal the active spaces. Each `b` image and covector has no dirty
component. The `a` projectors are already `E_ii`. Undoing the scalar change
that commutes with `P` gives `PN=N=NP` for every normalized paid factor.

The proof uses no upper bound on `r` or `t`, no finite search, and no
assumption that different projectors commute.

## 4. Consequences and the unresolved case

* **Three swaps cost nine with arbitrary finite dirty workspace.** A word
  below nine has odd length and at least three of each label, so only seven
  remains, with counts `(3,4)` or `(4,3)`. Saturation rules both out. Three
  direct `bab` words attain nine in the full formal algebra. This is an
  analytic alternative proof of PR1541's theorem; that predecessor retains
  priority for the arbitrary-workspace result and its checked SAT proof.
* **Four swaps need at least ten.** Below twelve, parity and the label floor
  leave totals eight or ten. Saturation excludes `(4,4)`, `(4,6)` and
  `(6,4)`. Only `(5,5)` at total ten remains. The direct twelve-call word
  attains the upper bound. This covers arbitrary finite dirty workspace and
  strengthens the `r=4`, `{8,10,12}` boundary reported in PR1705. It does
  **not** prove the four-swap minimum is twelve or supply a ten-call word.

For completeness, PR1541's compression step reduces that remaining ten-call
case to at most six roles: put `L=span(u_a)+span(u_b)`. Both spans contain
`im P`, so `dim L<=n_a+n_b-t=6`. Every paid projector preserves `L`, and its
restriction remains rank-one idempotent because its image vector lies in
`L` and its covector evaluates to one on that vector. Restrict the full
formal identity to `L` and choose a basis of `im P` plus `L intersect ker P`.
This gives four active swaps and at most two dirty roles, with the same ten
paid calls. Compression is credited to PR1541, not claimed as new here.

More generally, every potential saving below `3t` must have both counts at
least `t+1`, as well as the retained sign parity. The theorem only screens
this fixed two-label formal model; it does not exclude other alphabets.

## Credit and limits

Credit commdata2338 (PR1414/1491), Gareth Davidson (PR1333), Cinna Davis
(PR1541), and Aaron Wang (PR1705), with exact heads in TASK.json. Eumemic
(PR288), Ali Romman (PR468), and David Govea (PR720) supply surrounding
rational/register-model lineage. This proof does not import the rational
three-register obstruction into the nonabelian model.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0. The written proof has not been checked by a proof assistant or
independently reviewed by a human. Physical compiler/common-label realization,
hosting, precision/tape, full selected cold replay and analytic transfer
remain outside this contribution. No new kappa.
