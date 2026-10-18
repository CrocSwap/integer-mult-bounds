# Nilpotent rank-one couplings do not lower the central UT3 call bill

**Scoped extension and independent check; no new kappa.** Central UT3 targets
still cost exactly `4w` calls if the paid alphabet admits **every nonzero
rank-one scalar coupling**, including nilpotent matrices as well as
idempotents. This holds for every finite `r>=w>=1` with all extra registers
arbitrary dirty and restored. A degree-two quotient proves the bound.

This answers the arbitrary-register handoff in juper997's
[PR1478](https://github.com/CrocSwap/integer-mult-bounds/pull/1478), pinned at
`b30fdba48f3db70e3589ba740b0782b56ec0ba2e`. That package proves the two-target
minimum for `r=2,3`. woklerx's
[PR1443](https://github.com/CrocSwap/integer-mult-bounds/pull/1443), pinned at
`965ff75aabb16cdd0978f4bf9222bcdedf514021`, independently proves the two-register
case. Those minima and direct words are predecessor results.

Steph4n-gh's concurrent
[PR1573](https://github.com/CrocSwap/integer-mult-bounds/pull/1573), head
`0b8c5a69297c794f2de22c04494c83e41300ae36`, which already proves `4w` for
every finite workspace and target count in the **idempotent** alphabet.
That shared conclusion is corroboration. The precise extension here removes
`v^T u=1`, permitting nilpotent paid couplings `v^T u=0` at the same optimistic
unit price. Every expanded call is reversible; the lower bound survives.
The proof uses one quotient retaining both mixed coefficients, instead of
the predecessor's natural representation and generator-swapped companion.

## Exact model and complete bill

Let `G=UT_3(F2)`, with triples `(u,v,z)` for entries `01,12,02` and product

`(u,v,z)(U,V,Z)=(u+U,v+V,z+Z+uV)`.

Set `a=I+E01`, `b=I+E12`, `c=abab=I+E02`. The group has eight elements; `a,b`
are involutions and `c` is a nonidentity central involution. Work in the full
formal group algebra `R=F2[G]`. For any finite `r>=w>=1`, a paid factor is

`D_N(g)=I+([g]+1)N`, where `g` is **only a or b**,
`N=u v^T` is any nonzero binary rank-one matrix; `v^T u` may be zero or one.

At trace one, `N^2=N` is the predecessor's idempotent type. At trace zero,
`N^2=0` is the added nilpotent type. For example, `N=E01` adds
`([g]+1)` times register 1 into register 0, with both inputs dirty. Each such
coupling is optimistically priced at one paid call. Its full formal inverse
is itself: `([g]+1)^2=0`, hence `D_N(g)^2=I` without an idempotence assumption.

The required endpoint is `T=diag([c],...,[c],1,...,1)`, with exactly `w` central
targets. Equality means every formal coefficient agrees on every register,
including the `r-w` restored dirty roles. There is no free address map, clean
allocation, COPY, ERASE, higher-rank paid factor, or free inverse.
Scalar `GL_r(F2)` maps are free **in this optimistic screening model**.

Move all scalar maps to one end by conjugating the scalar couplings. Every
paid factor augments to `I` under `[g]->1`, and the target also augments to `I`,
so the final scalar map is `I`. Rank survives conjugation. The expanded
alphabet already includes every nonzero rank-one matrix, so it covers all
these conjugates. This retains Gareth Davidson's PR1333 normalization; it
does not assume a nilpotent matrix is conjugate to an idempotent.

The attaining bill is four calls `(a,b,a,b)` on each data coordinate. It uses
`w` data roles, zero extra workspace, `4w` paid calls, no scalar preparation,
and no uncharged undo. Appending identity roles gives every `r>=w` boundary.

## Dimension-independent proof

Use the associative algebra

`A=F2<X,Y>/(X^2,Y^2, all monomials of length >=3)`.

Its basis is `1,X,Y,XY,YX`. The group map `a->1+X`, `b->1+Y` is valid:
both images square to one, and their product has fourth power one.
The presentation `a^2=b^2=(ab)^4=1` is the eight-element dihedral group
isomorphic to `UT_3(F2)`. Alternatively the explicit map on triples is

`(u,v,z) -> 1+uX+vY+zXY+(z+uv)YX`;

substitution in the displayed group law verifies multiplication directly.
In particular, `c->1+XY+YX`. Extend linearly to `R->A`. This quotient is used
only for a necessary lower-bound condition, never for formal acceptance.

Let `Q=diag(1,...,1,0,...,0)` have rank `w`. The target's quotient image is
`I+(XY+YX)Q`; its `X` and `Y` coefficients vanish, while both mixed
coefficients equal `Q`.

There are `p` a-labeled factors. Write their scalar matrices, in chronological
order, as `N_i=u_i v_i^T`. Let `U=(u_1 ... u_p)` and `V=(v_1 ... v_p)`.
The coefficient of `X` in the product is

`sum_i N_i = U V^T = 0`.

Every `XY` term chooses an a factor first and a b factor later. Therefore its
coefficient is `sum_i N_i S_i`, where `S_i` is the sum of the b projectors
after a occurrence `i`. Its column space lies in the column space of `U`.
Every `YX` term is `sum_i R_i N_i`, with `R_i` the sum of b projectors before
that occurrence. Its row space lies in the row space of `V^T`. No term of
length three or more survives, and `X^2=Y^2=0`; no commutation of scalar
matrices is used. Since both mixed coefficients are `Q`,

`rank(U)>=w` and `rank(V^T)>=w`.

But `UV^T=0` gives `image(V^T) subset kernel(U)` inside `F2^p`, so

`rank(U)+rank(V^T)<=p`.

Hence **p>=2w**. For the `q` b-labeled factors, the same argument exchanges
`X,Y`: the `Y` coefficient is zero, the `YX` column space comes from their
left vectors, and the `XY` row space comes from their right vectors.
Thus **q>=2w**. Every legal word has at least `p+q>=4w` paid calls.
The direct formal word above attains `4w`, proving the theorem.

The lower-bound argument uses rank one, not idempotence, for the scalar
matrices. The direct upper construction uses idempotents, which remain in
the expanded alphabet. Neither determinant parity nor a bound on the number
of restored roles is needed. In fact the predecessor's parity shortcut no
longer applies to every paid call: for nilpotent `N`, `det(I+tN)=1` in
`F2[t]/t^2`, whereas idempotent calls contribute `1+t`.

## Exact executable evidence

[verify.py](verify.py) corroborates the proof with standard-library F2 arithmetic:

- All 64 group products verify the quotient homomorphism; all 32,768 triples
  of quotient elements verify associativity.
- All 154 rank-one idempotents on 2, 3 and 4 registers verify the separate-label
  determinant formula by a direct Leibniz calculation. This is an additional
  control inherited from the parity approach, not a required proof step.
- All 283 rank-one matrices at those dimensions (9,49,225) check the expanded
  alphabet; all 566 a/b paid factors square to identity in the full formal
  algebra and the faithful regular representation. The 129 added nilpotent
  scalar matrices have determinant one in the dual-number quotient.
- All 70,236 two-a-occurrence words with up to three b calls on two registers
  check the mixed-coefficient factorization and rank bound. The independent
  symbolic subsequence expansion checks all 84 two-occurrence label patterns
  through length eight. These bounded tests do not establish the uniform proof.
- All 7,129 zero-product pairs among binary `2-by-p` and `p-by-2` matrices,
  `p=1..4`, verify the rank inequality without a paid-projector assumption.
- The full formal `4w` witness and a separate faithful regular replay agree
  for every `w=1..r` at `r=1,2,3,4,8,16` (34 fixtures). The coefficient-span
  bounds are checked on every witness. A five-register scalar-conjugated
  fixture exercises dirty workspace and the changed output basis.
- Forty omitted-call controls reject; eight further controls distinguish
  rank-two paid calls, the enlarged central-label alphabet, a nonfaithful
  quotient kernel, a wrong scalar boundary, and un-restored dirty workspace.
  In particular, allowing `c` itself as a primitive attains two targets in two
  calls, and allowing rank-two projectors attains them in four. The restricted
  alphabet and rank charge are essential.

All 324 ordered two-factor products over the expanded two-register alphabet
also agree between formal, quotient and faithful regular replay in the tests.
The formal and regular engines use different address multiplication: triples
versus literal 3-by-3 binary matrices. They share ordinary F2 matrix arithmetic
and were written in one session. This is not independent human proof review.
[EXPECTED.json](EXPECTED.json) records counts; `--emit` prints a fresh receipt
without modifying the source. Acceptance is type-sensitive and read-only.
Exact executed environments, commands and the resolved temporary-directory
limitation are recorded in [VALIDATION.md](VALIDATION.md).

## Reproduce and limits

From the repository root, Python 3.10+ and the standard library:

```sh
python3 -I -B research/ut3-two-targets-any-registers/verify.py
python3 -I -O -B research/ut3-two-targets-any-registers/verify.py
python3 -I -B research/ut3-two-targets-any-registers/test_verify.py
python3 scripts/research_package.py --package research/ut3-two-targets-any-registers --check-only
python3.12 scripts/research_package.py --package research/ut3-two-targets-any-registers
```

Expected checker: `PASS_UT3_ANY_REGISTERS minimum=4w ... two_targets=8 ... no_new_kappa`.
[TASK.json](TASK.json) records the selection, refinement, sources, overlap and
stop rule; [SOURCES.json](SOURCES.json) pins exact base inputs and predecessor
heads. The initial main is `680967accfd4311f3241dc154e1f434869747b43`.
Coordination is in [Discussion1569](https://github.com/CrocSwap/integer-mult-bounds/discussions/1569).

This changes the rational abelian starting model to a specified nonabelian
binary group and restricted paid alphabet. It does not reduce rational frame
entries modulo two or establish a rational-frame identity. Other targets,
groups, alphabets and primitive prices are outside the theorem.
Selected-source binding orientation passed. Full selected-supplier cold replay,
physical/compiler and common-label realization, ownership/hosting,
precision/tape, outer analytic transfer, Lean formalization and independent
human proof review are not supplied. No new supplier or multiplication
exponent is claimed.

## Open next questions

Which additional paid address primitive could escape the `4w` obstruction at
a favorable **complete** price? This matters because more dirty workspace
alone cannot help in the declared alphabet. A first step is to state an
expanded alphabet and map it into the same quotient, then charge its mixed
coefficients and explicit formal realization before searching. A cheaply
declared central label makes the optimistic bill smaller, but its actual
physical implementation and compatibility with the retained bit interface
remain the blocker. No physical escape or broader group lower bound is implied.

## Credit and license

Credit steph4n-gh's concurrent PR1573 for the all-register/all-target
idempotent result, shared zero-sum rank proof, and separate-label bounds;
juper997's PR1478 for the fixed-register UT3 result and explicit
arbitrary-register handoff; woklerx's PR1443 for the two-register dihedral
certificate; Gareth Davidson (@bitplane), PR1333, for the nonabelian affine
direction, scalar normalization and rank-method context; and eumemic (PR288),
Ali Romman (PR468) and David Govea (PR720) for the retained register-model and
rank-method lineage. No predecessor code is imported and no literature-priority
claim is made for rank-nullity or group-algebra methods.

Prepared by **Arham Tahir with substantial OpenAI Codex assistance** in
reasoning, implementation, validation and writing. No subagents were used.
New work is Apache-2.0; predecessor files and notices are unchanged.
