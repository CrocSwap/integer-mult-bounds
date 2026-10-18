# Even finite dihedral groups: sharp reflection tariffs from address cuts

**Scoped all-register theorem; no new kappa.** Put
`G = D_{2n} = <r,x | r^n=x^2=1, xrx=r^-1>`, where the rotation period
`n=2m` is even, and set `y=r^-1 x`, so `r=xy`. For any finite number
`R>=W` of arbitrary-input scalar registers, the complete formal endpoint

```
diag([r^k_1 x^e_1], ..., [r^k_W x^e_W], 1, ..., 1)
```

in `M_R(F2[G])` has the exact separate paid-call bills

```
A = sum_i d_n(k_i+e_i)       x calls
B = sum_i d_n(k_i)           y calls,
d_n(t) = min(t mod n, n-(t mod n)),   e_i in {0,1}.
```

Both minima are attained **simultaneously**. Thus any nonnegative per-letter
prices `alpha,beta` give the sharp total `alpha*A+beta*B`. No scalar mixing,
interleaving, or extra restored dirty workspace can lower that bill.
For example, the D16 central pair costs 8 x calls and 8 y calls for **every**
workspace count, not just the two-register census of PR1821.

This answers the finite-torsion question left explicitly open by
[PR1911](https://github.com/CrocSwap/integer-mult-bounds/pull/1911).
Its infinite-dihedral Laurent-degree proof does not descend through `r^n=1`.
The new proof uses two finite permutation representations and a cut rank,
which does survive that relation. It is not an enlarged finite word search.
D8 central targets with arbitrary workspace were already settled by PR1573;
that overlapping special case is credited, not claimed anew.

## Exact model and fully paid boundary

The only paid address labels are x and y. A unit call is
`D_N(g)=I+([g]+1)N`, with `N=u v^T` over F2 and `v^T u=1`.
All binary rank-one idempotents are allowed, not only coordinate projectors.
Free scalar `GL_R(F2)` changes may occur anywhere. They do not change address
coordinates. There are no other free address maps, resets, erasures, COPYs or
clean inputs. Every input, including every workspace input, is arbitrary;
the full boundary restores each spectator and has no residual couplings.
Every paid preparation/restoration call is counted.

This replaces the rational abelian address group in the retained three-register
model by an explicitly nonabelian finite group (abelian only at the degenerate
boundary n=2). It does not reduce rational frame entries modulo two. Scalar
mixing is granted free as an **optimistic relaxation**, not asserted free in a
physical supplier. No physical compiler, hosting, frame, precision/tape or
analytic bridge is provided. Those adoption obligations remain unestablished.

## Uniform lower-bound proof

### 1. A subadditive crossing rank

Split a finite vector space into address halves H and K, including all scalar
roles in each half. For any linear operator M, let `q(M)=rank_F2 M[H,K]`.
Block multiplication gives

```
(AB)[H,K] = A[H,H] B[H,K] + A[H,K] B[K,K],
q(AB) <= q(A)+q(B).
```

No invertibility is needed for this inequality. A scalar register map acts
independently at each address, so its crossing block is zero. Invertible scalar
changes, even interleaved, therefore contribute zero to the bound.

### 2. Two different valid representations, including n=2 mod 4

For **each** integer c, represent G on addresses `a in Z/nZ` by

```
rho_c(r)(a) = a+1,
rho_c(x)(a) = c-a,
rho_c(y)(a) = c-1-a.
```

Both reflections square to the identity; their product x after y is `a+1`;
that translation has order n; and x conjugates it to its inverse. These are
therefore representations of the actual finite presentation. Extend them
linearly to F2[G] and entrywise to register matrices.

Use the balanced interval `H={0,...,m-1}`, `K={m,...,2m-1}`. For an interval
translated by t on this 2m-cycle,

```
| (H+t) intersect K | = d_n(t).                         (1)
```

For residues `0<=t<=m` precisely t points cross; replace t by `n-t` for the
other half of the residues. This proves (1) for all integers, not by sampling.

Take two representations:

* `c=m`: y preserves H, while x sends H to H+1. Thus y has no crossing
  entries and x has exactly one entry in each directed crossing block.
* `c=m-1`: x preserves H, while y sends H to H-1. Thus x has no crossing
  entries and y has exactly one.

The reflection offset **must change between the representations**. In
particular this handles n=6,10,...: we do not assume the fixed-point-free
reflection `a -> -a-1` preserves an odd-cardinality half. The verifier includes
n=2,6,10 and rejects that incorrect fixed-offset shortcut.

For arbitrary N, the crossing block of a represented paid factor is
`N tensor E`, where E is the indicated address crossing block; the identity
part contributes zero. Hence its rank is exactly `rank(N)` for the active
letter and zero for the other. In the rank-one model the two call charges are
therefore `(q_m(x),q_m(y))=(1,0)` and
`(q_(m-1)(x),q_(m-1)(y))=(0,1)`. This is why the argument includes every
non-coordinate scalar projector and any number of dirty roles.

### 3. Exact endpoint crossing ranks

A target `r^k` translates H by k. A target `r^k x` maps H to the interval

```
H + (k+c-m+1).
```

A permutation's crossing submatrix has one 1 in each participating row and
column; its rank equals its number of crossing addresses. By (1), the target's
crossing ranks in the two representations are

```
c=m:    d_n(k+e),
c=m-1:  d_n(k).
```

The endpoint is diagonal in scalar roles. Its crossing blocks are direct sums,
so ranks add over roles; identity spectators contribute zero. Subadditivity
now yields `#x>=A` and `#y>=B` for every finite R and every word length.
Formal equality implies represented equality; we never use the converse.
Indeed a negative control below explicitly demonstrates the common kernel of
these proof representations.

The same reasoning also bounds **total scalar rank** per label if paid calls
are allowed arbitrary-rank idempotents: x rank mass is at least A and y rank
mass at least B. This is a rank-linear corollary, not a sharp invocation-count
claim for batched calls or a statement about recursive child-rank pricing.

## Uniform attaining identity and complete invoice

Choose the representative `k' in [-m,m-1]` of each k. For a rotation, freely
reduce `(xy)^k'`; for a reflection, freely reduce `(xy)^k' x`. Negative powers
mean repetitions of yx. The resulting letter counts are

```
x: |k'+e| = d_n(k+e),    y: |k'| = d_n(k).
```

For e=1 the interval `-m<=k'<=m-1` is precisely what ensures both equalities;
this simultaneous choice is not automatic for odd n.

On role i use its coordinate projector E_i. Direct multiplication in the full
formal group algebra gives
`D_E(g) D_E(h) = D_E(gh)`, and calls on different coordinate roles commute.
Consequently the above literal words attain the complete diagonal boundary.
The rightmost factor acts first; the implementation executes each displayed
word right-to-left. No finite representation is used to certify this identity.

| Resource | Complete attaining implementation |
|---|---|
| Target roles | W, arbitrary dirty inputs |
| Extra dirty roles | Arbitrarily many allowed; zero needed |
| x / y paid calls | A / B, including all endpoint work |
| Scalar basis changes | Zero needed by attaining word |
| Clean allocations, COPYs, resets | None |
| Extra restoration, free frame/address changes | None in this formal implementation |
| Native supplier / physical realization | Not supplied or priced as free |

On any concrete n-address action `rho_c`, each reflection can be implemented
by disjoint swaps. For even n a reflection `a -> c-a` has two fixed addresses
if c is even and none if c is odd. Thus x uses `(n-2)/2` or `n/2` swaps per
call, and y has the opposite parity. A three-XOR swap needs no clean data bit;
this gives an explicit implementation of the witness, not an optimal physical
algorithm or an admitted recursive supplier tariff. Free scalar mixing in the
lower-bound relaxation only strengthens the no-compression result.

## Exact executable evidence and reproduction

```
uv run --python 3.12 --no-project python -I -B research/finite-dihedral-cut-bound/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/finite-dihedral-cut-bound
```

The verifier is standard-library-only. It distinguishes three engines:

1. Full formal F2[G] coefficient multiplication using dihedral normal forms.
2. Independently applied literal permutations on the **faithful regular** 2n
   addresses, including every dirty basis column and non-coordinate calls.
3. The two n-address proof representations, with binary Gaussian elimination
   of their actual crossing submatrices rather than substituting the theorem's
   claimed rank formula.

Finite checks corroborate implementations; the universal result is the written
proof above. The proof is not Lean-checked and no independent human review is
claimed. The retained source-binding working example is orientation only, not
selected cold replay. See the generated receipt and validation record for
actually executed domains, counters and environment.

Observed on macOS arm64, CPython **3.12.12**: the direct isolated replay and
registered optimized replay both passed. The receipt records **1,027** complete
forward/inverse dirty fixtures, **134,864** regular basis columns, **9,420**
mixed words, **47,872** representation-product checks, **3,720** rank-one call
cut checks over all **155** projectors through four roles, and **348** checks
over all **174** invertible scalar maps through three roles. All **9,249**
single-call omissions and **13** additional semantic/model controls reject.
A deliberately incomplete receipt also rejects under `-O` with
`receipt differs from exact recomputation`. Exact commands and environment are
in [VALIDATION.json](VALIDATION.json); the repeatable counts and digest are in
[RECEIPT.json](RECEIPT.json). No native, hosted CI or selected cold replay was run.

Controls include omitted paid calls, wrong letter/order, residual dirty
workspace, illegal projectors/labels, odd-period simultaneous-attainment failure,
and the wrong parity-insensitive reflection offset. An invertible off-diagonal
perturbation by `Omega=sum_{g in G}[g]` is invisible in **both** n-point proof
representations: each permutation coefficient there occurs twice. It remains
nonzero in the formal algebra and faithful regular action and is rejected by
the endpoint verifier. Thus represented lower-bound checks are not mistakenly
used as sufficient endpoint certificates.

## Provenance, overlap and credit

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; independent OS nonce
`63537661f5ee8acaa486b70f82726911`, track `bit-mechanisms`, emitted card
`bit-new-register-model`, method target-specific relaxation. Complete chooser
output is retained in `SELECTION.json`; original source byte/blob pins and
catalogue/selected-record provenance are in `SOURCES.json`. The selected record
remains unchanged at SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

Closest inspected live predecessors:

* Adam Gall, [PR1911](https://github.com/CrocSwap/integer-mult-bounds/pull/1911),
  head `712593f82739203639d0a169b88c6bcac6f0590c`: infinite-dihedral sharp
  tariffs and the precise finite-torsion open question. No source code copied.
* Cinna Davis, [PR1821](https://github.com/CrocSwap/integer-mult-bounds/pull/1821),
  head `a986127fa82b680a5bbb29f49fec4c8c3a944bde`: D16 central pair at R=2.
  The present result replaces that bounded-register gap with a uniform proof.
* steph4n-gh, [PR1573](https://github.com/CrocSwap/integer-mult-bounds/pull/1573),
  head `0b8c5a69297c794f2de22c04494c83e41300ae36`: arbitrary-register D8
  central targets and separate tariffs, already established. The natural
  representation/zero-projector-sum argument is a predecessor, not this proof.
* Arham Tahir, [PR1919](https://github.com/CrocSwap/integer-mult-bounds/pull/1919),
  head `f5610483cab0b5547be778a4e8983faf78aefa69`: rank-bounded D8 central
  block calls and their invocation optimum. We do not claim that optimum.
* [PR1792](https://github.com/CrocSwap/integer-mult-bounds/pull/1792), head
  `cc3a4adbae23fb07687803d1361bb7a1bcd449b0`: D8/UT3 scope audit identifying
  the already-completed arbitrary-workspace result and the danger of stale
  next-question text. Its navigation warning is respected here.
* woklerx, retained PR1443 D8 census; eumemic PR288 register model;
  Ali Romman PR468 three-register obstruction; Gareth Davidson PR1333
  nonabelian affine direction; their attribution remains unchanged.

Initial shared overlap snapshot: 579 open PRs and 547 discussion records,
completely paginated at 2026-10-14T14:10:13Z / 14:11:43Z. The final offline
recheck at 14:30:45Z used the refreshed **584 open PRs** (14:27:47Z) and
**565 discussion records** including comments/replies (14:29:09Z), both
complete. The only new exact dihedral/cut matches were this package and this
round's own claims. Targeted live predecessor heads were unchanged. A live
all-state dihedral PR search and local README/ledger search also included the
merged PR1443 predecessor and the PR1792 D8 scope audit.

The helper's closed-PR coverage remains only local notes and the ledger;
arbitrary code diffs are not searched, and cached records may miss live changes.
No-match results are not novelty certificates. The mathematical change is
finite torsion and a new balanced-cut invariant, not the seed or a larger census.
[Precise pre-computation claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1929#discussioncomment-18925900).

Prepared for **Adam Gall** with substantial **OpenAI Codex GPT-6 Astra**
assistance in proof, implementation, verification and writing. All engines were
written in the same AI-assisted investigation; algorithmic independence is not
independent human authorship. Apache-2.0. No supplier, frontier or kappa change.

## Open next questions

1. **Odd periods.** The even half-interval proof and simultaneous choice of
   representatives do not automatically extend. At n=3 the farthest reflection
   has separate cyclic distances (1,1) but no word with those counts. Determine
   the missing joint tariff constraint before attempting an odd-period theorem.
2. **Physical admission.** Specify and fully price an all-size native reflection
   child, including frame/compiler, hosting, restoration, precision and tape.
   Until such a bridge exists, even the exact formal theorem is only a
   mechanism-screening side result, not an exponent result.
