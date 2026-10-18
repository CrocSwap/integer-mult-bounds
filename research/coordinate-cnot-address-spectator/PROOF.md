# Two swaps with an address spectator: a finite six-call certificate

This proof establishes a minimum in an explicit finite register model. It
does not establish a new bit supplier or multiplication exponent. The lower
bound has a complete finite computation; the upper bound is a formal identity.

## 1. Model and statement

Let `G = GL_3(F2)` and `R = F2[G]`, the **formal group algebra**, with independent
symbols `[g]` for group elements. Let

\[
 g_{ij}=I_3+E_{ij}\quad (i\ne j),\qquad
 s=\begin{pmatrix}0&1&0\\1&0&0\\0&0&1\end{pmatrix}.
\]

There are six allowed paid address labels `g_ij`. In particular, the four
labels involving coordinate 3 are available during the word, although that
coordinate must be restored at the endpoint.

For `r` scalar registers, a paid unit is

\[
 D_N(g)=I_r+([g]+1)N,\qquad
 N=uv^T,\quad u,v\in\mathbb F_2^r,\quad v^Tu=1.
\]

Thus `N` is a binary rank-one idempotent, and every occurrence costs one.
Free scalar `GL_r(F2)` changes of basis may appear anywhere. No address map
is free. There are no copies, erasures, clean allocations or translations.
Undo calls have the same unit price. The target is

\[
 T_r=\operatorname{diag}([s],[s],1,\ldots,1).
\]

Equality is required in `M_r(R)` on all arbitrary inputs. At `r=3`, the
additional scalar register is arbitrarily dirty and must be restored, with
no leakage into either active output. An extra **scalar register** differs
from the third **address coordinate** present in every register.

**Finite-certificate theorem.** For exactly `r=2` and exactly `r=3`, the
minimum paid-call cost of `T_r` is **six**, even with free scalar mixing and
all six three-dimensional coordinate CNOTs available.

This extends the allowed address alphabet of the two-dimensional two-swap
result in [PR1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414).
Its all-register conclusion is **not** inherited for the enlarged alphabet.
The result here makes no assertion for `r>=4` or address dimension `>=4`.

## 2. Remove free scalar gates without changing the paid count

For an invertible scalar matrix `B`, moving it past a paid factor conjugates
`N` to `B N B^-1`. This remains a binary rank-one idempotent. Any word is
therefore a product of paid factors followed by one scalar matrix `B_total`.

Augmentation `R -> F2`, `[g] -> 1`, sends every paid factor and the target
to `I_r`. Hence `B_total=I_r`. It suffices to enumerate paid factors alone.
This is the normalization argument credited to Gareth Davidson's PR1333 and
reused in PR1414. It permits arbitrarily many free scalar gates; the finite
search does not silently bound their number.

Every binary rank-one matrix has a unique presentation `uv^T` with `u,v`
nonzero: over `F2` there is no nontrivial scalar rescaling. Idempotence is
equivalent to `v^T u=1`. For each of the `2^r-1` choices of `u`, exactly
`2^(r-1)` choices of `v` satisfy that equation. The complete projector counts
are 6 and 28, giving 36 and 168 paid generators.

## 3. A necessary representation suffices for exclusion

Extend the natural address representation linearly to an algebra homomorphism

\[
 \rho:R\longrightarrow M_3(\mathbb F_2),\qquad [g]\longmapsto g.
\]

Its block extension sends a paid factor to

\[
 \widehat D_N(g_{ij})=I_{3r}+N\otimes E_{ij}.
\]

The target image swaps address coordinates 1 and 2 in registers 1 and 2,
fixing every other coordinate. Every formal identity must give this natural
matrix identity. Thus **nonexistence in the matrix image implies
nonexistence in the formal algebra**.

The converse is not used. The representation is not faithful as an algebra:
the formal sum of the six elements of the embedded `GL_2(F2)` subgroup is
nonzero, while its natural image is zero. The verifier checks this explicit
kernel element and a false endpoint obtained by adding it to `T_r`.

This is a necessary-condition relaxation of a fully specified formal model,
not an inference from finite payload trials to a universal identity. All
`3r` matrix coordinates are retained, including the address spectator and
the extra dirty scalar register.

## 4. Complete five-call exclusion by radius-two balls

Let `S` be the complete finite alphabet of natural matrix generators, and
let `B_k` contain all products of at most `k` generators. Each generator is
an involution: `E_ij^2=0` for `i!=j`. Consequently every `B_k` is closed under
inversion.

A word of length at most five reaches `T = rho(T_r)` if and only if

\[
 B_3\cap T B_2\ne\varnothing.
\]

Indeed, split the word as `T=A B` with `A in B_3` and `B in B_2`. Then
`A=T B^-1`. Conversely, `A=T C` gives `T=A C^-1` of length at most five.
Words shorter than five are included because the balls contain the identity.

The primary implementation constructs `B_2` by breadth-first traversal.
It checks `B_2 intersect T B_2` and then **every** pair `(x,g) in B_2 x S`,
testing whether `g x` belongs to `T B_2`. This streams all of `B_3`; it does
not need to store or deduplicate its third layer. Repeated edge endpoints
are harmless. There is no sampled prefix, symmetry quotient, timeout success,
heuristic pruning, or approximation.

The independent implementation stores matrix columns, obtains projectors by
filtering all `2^(r*r)` binary matrices for rank one and idempotence, and
multiplies on the **right**. It checks `B_3 intersect B_2 T`, whose emptiness
is equivalent by the same splitting argument. The two implementations agree
on every generator, every state of `B_2`, and its exact distance layers.
Both full edge scans have zero intersections.

| Scalar registers | Projectors | Paid generators | Distance layers 0,1,2 | `B_2` | Edges scanned per implementation | Hits |
|---|---:|---:|---|---:|---:|---:|
| 2 | 6 | 36 | 1, 36, 816 | 853 | 30,708 | 0 |
| 3 | 28 | 168 | 1, 168, 17,346 | 17,515 | 2,942,520 | 0 |

The exact endpoint and alphabet equality are checked as sets, not inferred
from equal counts or hashes. `EXPECTED.json` also records deterministic
SHA256 digests. Matrices are encoded as consecutive `n`-bit rows with row
zero in the low bits (`n=3r`), sorted as unsigned integers, each serialized in
`ceil(n*n/8)` little-endian bytes before hashing. Shifted-ball hashes refer
to the primary **left** shift, not the independent right shift.

## 5. Formal six-call attainment

For every scalar idempotent `N`, formal expansion gives

\[
 D_N(g)D_N(h)=D_N(gh).
\]

Since `g_12 g_21 g_12=s`, apply that three-call sequence on `N=E_11` and
then on `N=E_22`. The full product is exactly `T_r` in `M_r(R)`. It needs
six paid calls, no free scalar gates, no additional roles, and no omitted
restoration. It is valid for any `r>=2` and on every `R`-module; only the
lower bound is restricted to `r=2,3`.

The checker multiplies sparse **formal group coefficients**, where each
group label is its exact binary 3-by-3 matrix. It does not use the natural
representation to accept this witness. Every omitted call and a substituted
spectator label fail the full endpoint check.

## 6. Scope and controls

The paid count is a complete invoice for this deliberately optimistic
free-scalar model, not for a physical supplier. This certificate rules out
the proposed six-to-five saving in its domain. It does not price physical
scalar work or improve a recursive rank histogram or kappa.

Controls cover omitted calls, a wrong spectator label, unrestored address
state, a fault visible only on a dirty third register, nonfaithful natural
equality, and forbidden rank-two projectors priced as units. Identity and
one-swap endpoints are positive controls. Source and receipt mutations,
natural/formal compatibility, free-scalar conjugation closure, and a
read-only relocated optimized replay are checked by the focused tests.

Neither the written argument nor the finite checker has been Lean-checked
or independently reviewed by a human. No selected-supplier cold replay,
all-size physical compiler, hosting, precision/tape, or outer analytic
transfer has been run. No conclusion for arbitrary extra registers follows
from the finite counts.

## Attribution

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Gareth Davidson (@bitplane), PR1333, posed the restricted coordinate-CNOT
question and supplied the broader affine rank-priced model and normalization.
This account's PR1414 supplies the two-dimensional two-swap result and its
higher-dimensional next question. Eumemic (PR288), Ali Romman (PR468) and
David Govea (PR720) are credited for the surrounding rational abelian
register-model lineage. No predecessor code is imported, no rational frame
is reduced modulo two, and no general rank principle or literature-priority
claim is made. New work is Apache-2.0.
