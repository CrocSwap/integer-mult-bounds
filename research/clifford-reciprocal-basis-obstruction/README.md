# One Clifford child under arbitrary reciprocal linear encoding

**Scoped algebraic obstruction and an exact opposite-direction exception. No
new supplier or κ.** A basis change followed by its inverse cannot turn one
higher-rank tensor Clifford child into independent equal-width children with
the same direction. This holds for every invertible linear basis, including
nonmonomial bases, and for arbitrary dirty padding that must be restored.

The direction premise is essential: two opposite-direction width-f lanes are
similar to a phase times a width-(f+1) tensor child exactly when f is odd. We
give actual rational encoding/decoding matrices. Even with those conversions
free, the inherited joined-volume bill is larger than the separate-call bill.
Neither the identity nor its spectral obstruction alone supplies a physical
boundary or an optimal-runtime lower bound.

## Exact contract and uniform-direction theorem

Work over any characteristic-zero field K containing i, with i²=-1. Let

`C = ((1+i)I + (1-i)X)/2`, `X = [[0,1],[1,0]]`, and `C_f = C^⊗f`.

Thus C has eigenvalues 1 and i, C²=X and C⁴=I. An inverse child is C_f⁻¹.
The source kernel in [SOURCES.json](SOURCES.json) implements this convention;
the dense checker compares its complete matrices in both directions.

For integers f,h,q,t≥1 and d≥0, the desired full-space map is

`T = (I_q ⊗ C_f^ε) ⊕ I_d`, with ε∈{1,-1}.

Every payload and padding coordinate is an arbitrary independent input. The
candidate consists of encoding by any E∈GL_(q·2^f+d)(K), one child, and decoding
by E⁻¹:

`T = E⁻¹ [λ (C_h^η ⊗ I_t)] E`, with η∈{1,-1}, λ≠0.

Dimension equality requires `q·2^f+d = t·2^h`. No independent left/right
adapter, other arithmetic child, restricted reachable subspace or garbage
workspace output is part of this contract.

**Theorem.** If this identity holds, then **d=0 and h=f**. Conversely, when
d=0 and h=f, some phase and basis do realize it (t=q). In particular, an
arbitrary reciprocal basis cannot upgrade the tensor width.

**Proof.** Both the target and the unscaled child have fourth power I, so the
identity forces λ⁴=1. Similarity preserves the traces of every power.

1. For every positive f, `tr(C_f²)=tr(X^⊗f)=0`; the inverse has the same square.
   Therefore `tr(T²)=d`, while the candidate's square trace is zero. Since K has
   characteristic zero, d=0. This also prevents repairing the mismatch by
   adding arbitrarily many fully restored dirty coordinates.
2. Use the algebraic invariant `J(A)=tr(A)·tr(A³)`. It requires no norm or
   ordering on K. Since `tr(C_f)=(1+i)^f` and `tr(C_f³)=(1-i)^f`,
   `J(C_f)=2^f`, also for the inverse. The phase cancels because λ⁴=1.
   Consequently `q²·2^f = t²·2^h`.
3. Dimension now gives `q·2^f=t·2^h`. Dividing its square by the preceding
   identity yields `2^f=2^h`, hence f=h, and then t=q.

For sufficiency, identical directions use the tensor-factor permutation.
Opposite directions use `C_f⁻¹=(-i)^f Z_f C_f Z_f`, where
`Z_f=diag(1,-1)^⊗f`. This identity also shows that inverse-child spectra are
phase rotations of the forward-child spectrum. ∎

The result extends the *choice of reciprocal basis*, rather than the prior
monomial two-sided theorem's whole domain: independent monomial left/right
maps need not be reciprocal. Neither result subsumes the other in full.

## Opposite-direction pairs: complete one-child classification

Change the target to `T_mix=(C_f ⊕ C_f⁻¹) ⊕ I_d`, keeping the same reciprocal
contract and allowing a forward tensor child with a global phase. For any
positive f,h,t, a match exists exactly in the following cases:

| f modulo 4 | Required d | Child width h | Spectator multiplicity t | Phase λ |
|---|---:|---:|---:|---|
| 1 | 0 | f+1 | 1 | -i |
| 3 | 0 | f+1 | 1 | 1 |
| 0 | 0 | f | 2 | 1 |
| 2 | — | — | — | No match |

**Necessity.** The square trace again forces d=0. Write z=(1+i)^f and
z̄=(1-i)^f (algebraic notation). Both the first and third target traces are
z+z̄. Thus J(T_mix) equals `2^(f+1)` for odd f, `2^(f+2)` for f divisible by
four, and zero for f congruent to two modulo four. The child's invariant is
`t²·2^h>0` as a nonzero characteristic-zero integer. With dimension
`t·2^h=2^(f+1)`, these equations force the stated h,t or reject the zero case.

**Sufficiency.** All the matrices are diagonalizable with eigenvalues among
{1,i,-1,-i}: their fourth power is I and x⁴-1 has distinct roots. The four
traces of powers 0,1,2,3 determine their four eigenvalue multiplicities by the
invertible four-point Fourier matrix. For each displayed phase, all four
traces agree by the preceding formulas (and their third-power versions).
Their eigenspaces therefore admit an invertible matching basis.

This is constructive over Q(i), with a rational E: diagonalize C_f using the
integer Walsh matrix `W_f[x,y]=(-1)^popcount(x&y)`, match eigenvectors by their
eigenvalues, and set `E=V U⁻¹`. Here U is the block Walsh basis of the target,
V is the reordered tensor/spectator Walsh basis of the child, and
`W_f⁻¹=2^-f W_f`. The dense checker reconstructs E and E⁻¹ and verifies every
column for f=1,3,4, including arbitrary inputs in both lanes. At f=1:

```text
E = [[ 1, 0, 1, 0],        E^-1 = 1/2 [[ 1,-1, 0, 0],
     [-1, 0, 1, 0],                     [ 0, 0, 1,-1],
     [ 0, 1, 0,-1],                     [ 1, 1, 0, 0],
     [ 0,-1, 0,-1]]                     [ 0, 0,-1,-1]]

E^-1 (-i C_2) E = C ⊕ C^-1.
```

So a general assertion that *all* independently directed lanes resist a
reciprocal rank upgrade would be false. The written proof covers all f; the
finite widths and stored matrices corroborate it, rather than extend a census
to an untested universal claim.

## A correction must change a nontrivial subspace

If a subsequent linear adapter F repairs B=E⁻¹[λ(C_h⊗I_t)]E to T, then
`T-B=(F-I)B`, so `rank(F-I)=rank(T-B)`. For each eigenvalue μ,

`rank(T-B) ≥ |dim ker(T-μI) - dim ker(B-μI)|`.

This follows from `|rank(A)-rank(A+Δ)|≤rank(Δ)` applied after subtracting μI.
It holds for every E, without simultaneous diagonalization.

For sixteen forward rank-one lanes on 32 coordinates, T has multiplicities
`[16,16,0,0]` at `[1,i,-1,-i]`. The equal-dimension rank-five child C_5 has
`[6,6,10,10]`. Across all four phases, the largest multiplicity discrepancy
is `[10,10,6,10]`. Hence **every reciprocal encoding plus a left correction
needs rank(F-I)≥6**, including an inverse child by the phase-rotation identity.
We supply a lower bound, not attainment of six, an adapter circuit or a cost
lower bound. A separate dense nonmonomial basis gives actual differences of
ranks `[29,24,20,24]`, each respecting that bound.

## Fully charged optimistic volume comparison

Use PR679's inherited forward/inverse cost expression `A·V·width^σ`,
0<σ<1. Two independent width-f lanes cost `2 A V f^σ`. The odd-f mixed
identity has no selector repair, but its one child acts on **2V** coordinates:
its expression is `2 A V (f+1)^σ + E_cost`, where E_cost≥0 includes both basis
conversions, gathering/scattering, source and copy access, frames, output
storage, dirty restoration, hosting, global phase, precision and descriptors.
Even granting E_cost=0 gives ratio `(1+1/f)^σ>1` for every finite f, tending
to one as f grows. This construction does not improve the available budget
under this tariff; no larger asymptotic leading saving follows.

This is a comparison of inherited **upper-bound expressions**, not a lower
bound on optimal execution costs. The correction's rank bound is likewise
not a recursive invoice. A different volume/operation tariff requires its
own proof. No physical basis conversion, new word, owner map, frames,
precision/tape contract or outer assembly is supplied here.

## Reproduce and evidence

Python 3.12, standard library only, from repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/clifford-reciprocal-basis-obstruction
```

Direct commands also work in normal and optimized Python:

```sh
python3 -I -O -B research/clifford-reciprocal-basis-obstruction/verify.py
python3 -I -O -B research/clifford-reciprocal-basis-obstruction/dense.py
python3 -I -B -m unittest discover -s research/clifford-reciprocal-basis-obstruction -p 'test_*.py'
```

[CERTIFICATE.json](CERTIFICATE.json) contains 28,032 complete dimension-matched
uniform cases, both child directions and all four phases, binomial/independent
cyclic-recurrence agreement through f=64, the complete opposite-pair
classification through f=64, correction multiplicities and six scope controls.
[DENSE.json](DENSE.json) contains three complete rational basis witnesses and
2,728 native Gaussian-dyadic matrix entries through address dimension five,
both directions, checked against independently executed butterflies. Gaussian
elimination independently checks the small eigenspace multiplicities and the
four nonmonomial correction ranks. Controls include wrong global phase,
uniform-versus-mixed direction, restored dirty padding, even mixed width, and
a successful **nonreciprocal** adapter (to mark that excluded escape accurately).
`--write` explicitly regenerates each receipt; default replay is read-only.

The written all-size proofs have not received independent human or kernel
review. Full selected cold replay, physical compiler/hosting, precision/tape,
analytic reduction, Linux hosted CI and new κ are not asserted. The package
runner and the source kernel are invoked only for the declared local checks.

## Scope, overlap and credit

Started from current main `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
Chooser nonce `5539eb9e61a07a24d746ce2018c34aba`, revision-3
`complex-rank-shape-decoder`; [TASK.json](TASK.json) declares the changed scope
from synthesis to a necessary-contract theorem and exact direction exception.
The 5% physical construction gate is not claimed satisfied. Source Git blobs,
SHA256 values and the historical selected/catalogue pins are in SOURCES.json.
The standalone verifier needs no Git checkout; the generic provenance check
resolves the pinned history. [Discussion1901](https://github.com/CrocSwap/integer-mult-bounds/discussions/1901)
records the claim and completion.

Greer Guthrie's [PR679](https://github.com/CrocSwap/integer-mult-bounds/pull/679)
supplies the existing monomial support obstruction, selector repair and
linear-volume accounting. Ross Richardson's completed
[contract audit at 8a3900c](https://github.com/RossRichardson/integer-mult-bounds/tree/8a3900c84213fd7603b99beaceaff48f501b4232/research/diagonal-child-contract-audit)
applies that obstruction to selected batches; it is read and credited, not
replayed. Jose Manuel (@jmbarrancoml), with publishing account Cinna Davis
(@1337isnot1337), proposed diagonal batches in
[PR1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779), head
`1e3128bf642bbaf250b7d6b9639b2bb24b98ce5e`. Josie Elliston's
[PR1817](https://github.com/CrocSwap/integer-mult-bounds/pull/1817), head
`ac3a759e874e8e526bc884fc2cb8eb114695b063`, admits register-commuted original
climbs and explicitly leaves the replacement-child contract open. We do not
repeat those source-support, batch-count or hosting checks. Their numerical
ceilings remain conditional on their stated interfaces.

The final board refresh also found ToikY's complementary
[clean invariant-subspace claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1901#discussioncomment-18925296).
That question permits an injective encoding into an ambient space with a clean
complement. Our E is square and invertible on the entire space, and our extra
coordinates are arbitrary dirty inputs restored to themselves. The clean
injection question is outside this theorem; its unfinished claim is credited
as parallel work, not as verified evidence reused here.

Credit icekylinx, DreamingOfClouds, the original OpenAI manuscript and kernel
lineage; Sagar Thakrar/PR1012 for the coverage-law context; Douglas Colkitt for
the research guidance; Rohan Arun, Jeremy Kothe, Hao Yan and the retained
selected construction contributors. Arham Tahir/PR1605 supplied the earlier
integer rank-shape price screen. No priority claim is made for trace invariants,
Walsh diagonalization or elementary rank perturbation inequalities.

New proof, implementations and writing prepared by **Arham Tahir with
substantial OpenAI Codex assistance**. No subagents or independent human review.
Apache-2.0; predecessor code is read in place with its notices intact.

## Open next questions

- Can independent nonreciprocal input/output maps yield a fully priced
  higher-rank replacement? Write one exact full-space identity with both
  maps and charge their recursive/frame/volume work. Arbitrary maps can
  trivially force any invertible target; a legal inexpensive adapter is the
  missing premise. This theorem does not exclude that larger class.
- Can the odd-width opposite-direction identity help a real boundary under
  a changed volume tariff? Locate one forward/inverse pair on a single
  physical stream and prove its volume and hosting contract before pricing
  it. Under the inherited joined-array tariff, its free-adapter budget already
  loses; actual basis conversion and physical costs remain unpaid.
