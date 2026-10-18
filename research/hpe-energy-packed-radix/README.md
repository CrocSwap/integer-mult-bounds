# Sharp energy-ball radix for packed exact equality

**A Gaussian-integer row of Euclidean norm at most R is uniquely determined
by its evaluation at integer radix B >= 2R.** For integer R >= 1 this is the
sharp uniform integer threshold for that energy ball, in dimensions at least
two. This supplies a written all-dimension compiler lemma and a source-bound
finite replay, with no new Lean proof or selected-checker change.

Applied to the validated unitary Clifford grammar retained from Jeremy
Kothe's PR593, this gives **K+1 radix bits**, where K is the larger C-gate
count. It improves the sufficient K+2-bit bound in woklerx's
[PR1859](https://github.com/CrocSwap/integer-mult-bounds/pull/1859), head
`f5e18c0c44371ebfdd46bfe25efe5b49e467fafe`, by using whole-row energy in
place of a componentwise bound. No pending code is imported.

All three frozen `Exact.lean` pairs pass at **10 bits**, versus PR1859's 11
and the retained checker's 20. The largest packed input integer has **5,111
bits**, versus 5,622 and 10,221. These are exact bit lengths, not timings.

## Quantified lemma and proof

Let `R >= 1` be an integer, let `B >= 2R` be an integer, and let `u,v` be
finite Gaussian-integer vectors of the same arbitrary length. Define

`E(u) = sum_j |u_j|^2`, and `P_B(u) = sum_j u_j B^j`.

If `E(u), E(v) <= R^2`, then `P_B(u) = P_B(v)` **if and only if** `u=v`.

First consider a nonzero Gaussian-integer vector `d` in the kernel of
`P_B`. Let `t` be its least nonzero index. Dividing the zero evaluation by
`B^t` shows that `d_t` is a nonzero multiple of B in `Z[i]`, so
`|d_t|^2 >= B^2`. At least one higher digit must be nonzero; its squared
modulus is at least one. Consequently

`E(d) >= B^2+1`.

This kernel bound is sharp: `d=(B,-1)` has zero evaluation and energy
`B^2+1`. Now put `d=u-v`. The parallelogram identity gives

`E(u-v) = 2E(u)+2E(v)-E(u+v) <= 4R^2 <= B^2`.

Thus a nonzero difference cannot be in the kernel. This proves the forward
implication; the converse is immediate. The proof covers complex Gaussian
digits jointly, without floating-point estimates or a dimension-dependent
remainder. It also works for a real positive R if an integer B satisfies
`B >= 2R`; the sharpness assertion below uses integer R.

**Sharpness for the ball.** For every integer `1 <= B < 2R`, take

`u=(ceil(B/2),0)`, `v=(-floor(B/2),1)`.

They differ but both evaluate to `ceil(B/2)`. Their energies are at most
`R^2`: the second is at most `(R-1)^2+1 <= R^2`. Thus every smaller integer
radix fails in dimension two; append zeros for larger dimensions. This is
sharpness for the whole energy ball, **not** optimality for the particular
Clifford circuits or the subset of equal-energy unitary rows.

## Implication for the retained circuit compiler

The pinned `Clifford.lean` grammar has invertible binary permutations, XOR
permutations, diagonal/global powers of i, and

`C_s = ((1+s*i) I + (1-s*i) X)/2`, `s in {1,-1}`.

Validate the permutation/inverse pair and require XOR masks in the finite
address domain. Then X is a self-adjoint involution. On its +1 and -1
eigenspaces, C_s acts by 1 and s*i, so it is unitary. All five normalized
gate kinds, and hence their compositions, are unitary.

For a circuit U with k C gates, omitting each factor 1/2 produces the
Gaussian-integer matrix `Z=2^k U`. Its **rows**, as well as columns, have
energy `4^k`. For two circuits with counts k1,k2, set `K=max(k1,k2)` and
compare `2^(K-k1) Z1` with `2^(K-k2) Z2`. Every row has energy `R^2` for
`R=2^K`. Evaluation on the single input `u_j=B^j`, with

`B=2R=2^(K+1)`,

therefore determines each complete row by the lemma. Packed equality is
equivalent to normalized matrix equality, with global phase retained. The
extra unitarity/row-energy premises are material: this does not replace the
original Lean theorem for arbitrary literal gate lists.

A componentwise bound `|d_j| <= B` alone would admit `(B,-1)`. Its energy
exceeds the permitted difference energy by one, which is exactly what the
new proof uses. Column norm bounds alone also fail: the matrices

`A=[[1,0],[0,0]]`, `C=[[-1,1],[0,0]]`

each have column energies at most one and agree on `(1,2)`, although they
differ. C's first row has energy two, violating the required row bound.
Neither matrix pair is being asserted to be a valid normalized circuit.

## Reproduction and exact evidence

From the repository root, Python 3.12 with only the standard library:

```sh
python -I -O -B research/hpe-energy-packed-radix/verify.py
python -I -B -m unittest discover -s research/hpe-energy-packed-radix -p test_verify.py
python scripts/research_package.py --package research/hpe-energy-packed-radix
```

Normal verification checks source hashes and the complete deterministic
[RESULT.json](RESULT.json) without writing files. An intentional receipt
rebuild requires `--write /explicit/output/path.json`.

The checker reuses only commdata2338's closed Lean-literal parser. Its new
executor uses forward permutation scatter and disjoint two-state C
butterflies. A second direct interpreter uses the Lean pullback and
pointwise C formula. They share integer phase helpers and source parsing;
this is differential evidence, not two fully independent implementations.
The replay covers:

- All three literal pairs at the original, PR1859 and new radices.
- All 3,072 scaled rows of the six literal circuits, obtained as conjugated
  adjoint columns: exact equality and energy `4^K`, with row digests.
- Thirty separate interpreter executions on basis and mixed Gaussian data.
- All 5,265 vectors in nine Gaussian-integer balls: R=1,2,3, each in
  complex lengths 1,2,3, without any collision at B=2R.
- Exhaustive short-kernel checks in complex length two at B=2..6,
  plus the attaining `(B,-1)` relations.
- Actual real and imaginary collisions for all 1,024 unsafe `(R,B)`
  pairs with R=1..32 and 1 <= B < 2R.
- Fifteen source controls: phase, input character, omitted scale and
  undersized radix for each pair; invalid permutation, invalid XOR mask
  and a non-Boolean C sign. The component-only and column-only false
  implications are also demonstrated explicitly.

The quantified lemma rests on the proof above, not this finite census.
There is no supplier/cold replay, Lean build, kernel performance benchmark,
physical hosting proof, production precision change or new kappa claim.
The input exponent range of a real compiler and its arithmetic/memory cost
remain separate obligations. Compiler arguments must be obtained through
the validated literal compiler; arbitrary hand-built compiled lists are
outside the comparator's contract.

## Scope, sources and credit

Base current main: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
[TASK.json](TASK.json) records the adversarial-audit draw, refined scope,
bounded stopping rule and overlap coverage. [SOURCES.json](SOURCES.json)
pins the retained parser, literal data and exact gate semantics. Work is
coordinated in [Discussion1896](https://github.com/CrocSwap/integer-mult-bounds/discussions/1896).

Credit Jeremy Kothe / jeremykothe2's PR593 for the retained Clifford
semantics, packed equality proof and three literal pairs; commdata2338 for
the retained semantic-binding parser and source correspondence; woklerx's
PR1859 for the unitary-premise radix improvement; and the retained Lemma A/G,
icekylinx, Chafik Boukhalfa and jacklightChen lineage. Sagar Thakrar's
PR1781, inspected at `dafbaadeb423b3bc80fbf6fcd6f415400dc0ffbf`, concerns a
separate selected-recipe census at the original radix; it is neither
imported nor replayed here. The selected frontier and frozen files are
unchanged.

Prepared by Arham Tahir with substantial OpenAI Codex assistance in proof,
implementation, verification and prose. No subagents or independent human
review. Apache-2.0; predecessor source notices are retained.

## Open next questions

Can the sharp energy-ball lemma and valid-gate row norms be proved in Lean?
That would permit a proof-preserving change to the retained checker. First
formalize the least-nonzero-digit kernel bound and the parallelogram
inequality, then derive scaled row energies for the valid normalized
grammar. The missing kernel proof and kernel timing block adoption;
[TASK.json](TASK.json) records that precise next step. A smaller radix for
only the three particular matrices would be a different, source-specific
problem and is not claimed here.
