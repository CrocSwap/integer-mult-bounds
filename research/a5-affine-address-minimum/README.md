# Eight address bits are necessary for an algebra-faithful affine A5 action

**Scoped mathematical proof with exact finite ingredients; no new kappa.**
The minimum is **eight binary address bits**, over **all affine A5 actions**.
This answers Open next question 2 of Nick Petalas's
[#5114](https://github.com/CrocSwap/integer-mult-bounds/pull/5114), whose
two-natural-copy construction attains eight but excludes only its particular
four-bit predecessor. The new lower bound includes nonsplit modules and
affine actions without a fixed point. It is not a census of a few candidates.

The key reduction is stronger: the permutation action on the vectors of any
binary linear module with only one nontrivial composition factor has a nonzero
group-algebra kernel. Two explicit eight-dimensional extension modules cover
every such module by subquotients and fixed summands. Their permutation-algebra
ranks are 52 and 34, respectively, against a 60-dimensional group algebra.

## Exact statement and relevance

Put `k = F2` and `G = A5`. For a finite G-set X, `k[X]` means the vector space
with one independent basis vector `e_x` per **point** of X. Define

```text
rho_X : k[G] -> End_k(k[X]),    [g] e_x = e_(gx).
```

**Theorem.** Among homomorphisms `G -> AGL(d,2)` acting on the entire address
set `X = F2^d`, the smallest d for which `rho_X` is injective is 8.

The distinction between an address module V and its data-array space `k[V]`
is essential: their dimensions are `dim(V)` and `2^dim(V)`. Distinguishing the
60 group elements as address maps alone is insufficient.

This closes the proposed affine-footprint escape below #5114's 256 addresses.
It neither optimizes its address CNOTs or data XORs nor prices an actual BIT
caller. Arbitrary nonlinear address permutations are outside the theorem:
the regular action on 60 labels plus four fixed labels already gives an
algebra-faithful action on a 64-point set, with no affine realization asserted.
No supplier, recursive invoice, selected-result change or practical speedup
is claimed. These remain the same physical and consumer obligations as in
#5114; no unknown implementation cost is set to zero.

## 1. A finite certificate for the complete list of simple modules

Use `x=(12)(34)` and `y=(135)`. They generate G, with
`x^2=y^3=(xy)^5=1`. The two nontrivial simple binary modules are:

* N: the natural `F4^2` module, restricted to k, where
  `F4 = F2[w]/(w^2+w+1)`,
  `x=[[1,1],[0,1]]`, `y=[[0,w],[w^2,1]]`.
* S: the even-parity subspace of the natural permutation module `k^5`,
  in basis `e_i+e_4` for `i=0,1,2,3`.

Here is a finite proof that this list, together with the trivial module, is
complete; no external modular-character classification is assumed. Form

```text
Phi : k[G] -> k x M_2(F4) x M_4(k)
```

from augmentation, N and S. The separately implemented
[`check_algebra.py`](check_algebra.py) enumerates all even permutations,
aligns the natural matrices by generator words, and checks multiplication
on all 3,600 group pairs. The three image spans have dimensions 1, 8 and 16,
and the combined map has rank 25. Thus Phi is onto the stated product.
Its kernel J has dimension 35; exact group-algebra multiplication gives

| Ideal | J | J^2 | J^3 | J^4 | J^5 |
|---|---:|---:|---:|---:|---:|
| Dimension over k | 35 | 27 | 17 | 9 | 0 |

The checker also verifies both-sided ideal closure. These are computations in
the full 60-dimensional algebra, not ranks after a characteristic-zero lift.
The independent checker uses natural basis `(1,0),(0,1),(w,0),(0,w)`;
the universal-extension checker uses `(1,0),(w,0),(0,1),(0,w)`. Their two
generator matrices are explicitly bound by the coordinate permutation
`0,2,1,3`; the augmentation bases agree literally.

If L is a simple module, JL is either zero or L. The latter would imply
`J^5 L=L`, impossible. Hence L factors through the displayed product, whose
simple modules have k-dimensions 1, 4 and 4. Conversely the natural modules
of each full matrix factor are simple. This proves the asserted complete list.

## 2. Every single-nontrivial-factor module has a three-block form

First, any module all of whose composition factors are trivial is itself
trivial. A composition-series basis puts its image in an upper unitriangular
binary group, a finite 2-group. The image of y, of order dividing 3, is then
the identity; the image of xy, of order dividing 5, is also the identity,
so x acts identically too.

Let V have exactly one nontrivial composition factor R, either N or S, and
let `T=V^G` be its maximal trivial submodule. The quotient V/T has no trivial
submodule: its preimage would have only trivial factors and would therefore
enlarge T. A simple submodule of V/T must consequently be R. Its preimage W
gives a filtration

```text
0 < T < W < V,    T = k^a,    W/T = R,    V/W = k^b,
```

allowing zero-dimensional end terms. The last quotient is trivial by the
first paragraph. Since y has odd order, averaging over `<y>` splits this
filtration as a `<y>`-module. In a compatible basis, the generators therefore
have the form

```text
          [ I  A  C ]               [ I   0   0 ]
    X  =  [ 0  Rx B ],        Y  =  [ 0  Ry   0 ],
          [ 0  0  I ]               [ 0   0   I ]
```

where Rx,Ry are the chosen four-dimensional matrices for R. This reduction
includes nonsplit G-modules: only the cyclic odd-order action has been split.

For each of N and S, the finite checks give `rank(Rx-I)=2`, so
`im(Rx-I)=ker(Rx-I)`. The relation `X^2=I` says

```text
A(Rx-I)=0,    (Rx-I)B=0,    AB=0.
```

The first two conditions already imply the third. Choose a row basis A0 of
the two-dimensional left kernel and a column basis B0 of the right kernel.
There are arbitrary binary matrices P and Q with
`A=P A0` and `B=B0 Q`.

Put `D=Rx Ry`. Both R have `D^5=I` and no nonzero D-fixed vector, so
`I+D+D^2+D^3+D^4=0`. Expanding the top-right block of `(XY)^5` gives

```text
C + A Ry (D+D^3) B.
```

Indeed the four intermediate coefficients are 4,3,2,1, reducing to 0,1,0,1
in k. The other off-diagonal blocks vanish. Thus C is **uniquely forced**:

```text
C = A Ry (D+D^3) B = P C0 Q,    C0 = A0 Ry (D+D^3) B0.       (1)
```

This bilinear identity, not a bounded enumeration of P and Q, is the
all-dimensions part of the reduction.

## 3. Two universal extensions and their nonzero annihilators

Define E_R by the preceding block matrices with `a=b=2`, `A=A0`, `B=B0`
and `C=C0`. For reproducibility, a matrix column is encoded as the integer
whose binary digits are that column, with the first coordinate least
significant. The exact eight-dimensional generators are:

| R | X columns | Y columns |
|---|---|---|
| N | `1,2,4,8,21,42,70,139` | `1,2,48,16,24,44,64,128` |
| S | `1,2,9,5,34,18,77,178` | `1,2,20,12,4,36,64,128` |

[`verify.py`](verify.py) checks each is an actual representation of the same
A5 by all 3,600 multiplication pairs; it does not rely on an unchecked group
presentation. It constructs their action on all 256 vectors and computes:

| R | Rank of `rho_(E_R)` | Kernel dimension | Orbit inventory |
|---|---:|---:|---|
| N | 52 | 8 | `4*1 + 6*12 + 4*15 + 6*20 = 256` |
| S | 34 | 26 | `16*1 + 16*5 + 16*10 = 256` |

The complete independent kernel bases and explicit group-basis order are in
[`RESULT.json`](RESULT.json). For example, the first nonzero kernel masks are
`000f87dbfc07efc` for N and `000000002649ffc` for S. The group order starts at
the identity and appends unseen left multiples by x then y in breadth-first
order, as recorded by all 60 explicit permutations in the receipt. Every
kernel vector is checked again by cancelling its literal output basis
vectors at **every** input address, separately from the rank elimination.

Now let V have the block form of section 2. Choose a top complement T' to
`im P` and a linear section `s: im(Q) -> k^b` of Q. The top T' and the
bottom `ker(Q)` are trivial submodules: all off-diagonal images lie in
`im(P)`, while both B and C vanish on `ker(Q)`. The remaining invariant
core is `im(P) + R + s(im(Q))`; its bottom coordinate space alone need not
be invariant. This core is isomorphic to

```text
(preimage of im(Q) under E_R -> k^2) / ker(P).
```

Here `ker(P)` lies in the top, fixed `k^2` of E_R. More explicitly, on the
preimage of `im(Q)` the map `(t,m,z) -> (Pt,m,s(z))` is equivariant by (1),
has kernel exactly `ker(P)` in the top space, and maps onto the invariant
core. Together with T' and `ker(Q)` this accounts for all of V.
Thus **V is a subquotient of E_R plus trivial direct summands**.

A nonzero element annihilating `k[E_R]` annihilates `k[V]` as well:

* an invariant subset gives a permutation submodule;
* an equivariant surjection of sets gives a surjection of permutation modules;
* adding a trivial linear summand makes disjoint copies of the same G-set.

The nonzero annihilator for R from the table therefore works for every V
with that single nontrivial factor, regardless of a and b. If V has no
nontrivial factor its action is trivial and `[1]+[x]` annihilates `k[V]`.

## 4. Affine lower bound and matching upper bound

An affine d-bit action `v -> L_g v+t_g` homogenizes to the linear action

```text
(v,z) -> (L_g v+z t_g, z)
```

on a `(d+1)`-dimensional module H. It has a trivial one-dimensional quotient,
and its invariant affine slice `z=1` is exactly the original address G-set.
If `d<=7`, then `dim(H)<=8`; section 1 and the trivial quotient allow at
most one nontrivial four-dimensional composition factor. Section 3 gives
a nonzero annihilator of `k[H]`, which also annihilates the invariant slice.
Consequently no such affine action is algebra-faithful.

For d=8, use the predecessor's action on `M_2(F4)` by left multiplication.
The orbit of the identity matrix consists of the 60 distinct matrices of
`SL2(F4)`. For any coefficients c_g,

```text
(sum_g c_g [g]) e_I = sum_g c_g e_g,
```

so a zero operator forces every coefficient to vanish. This is #5114's
regular-orbit upper bound, not a new construction. The local positive control
checks those 60 images (seed 65 in the binary column encoding); it does not
replay the predecessor's endpoint search or CNOT/data-circuit invoice.

## Reproduction and evidence limits

From the repository root, standard-library CPython 3.12:

```sh
python3.12 -I -W error -B research/a5-affine-address-minimum/verify.py
python3.12 -I -O -W error -B research/a5-affine-address-minimum/verify.py
python3.12 -B scripts/research_package.py --package research/a5-affine-address-minimum
```

Expected marker: `PASS_A5_AFFINE_ADDRESS_MINIMUM bits=8`. Each direct check
takes a few seconds locally; the registered caps are 120 seconds
per mode. Direct verification works without Git when the two pinned
predecessor inputs are present. Ordinary verification is read-only; explicit
`--write-result` regenerates the deterministic receipt.

The replay checks the algebra quotient and J powers, both universal group
actions, all kernel witnesses, and the corner formula. For each module, 256
small P/Q cases also check the actual equivariant subquotient map at 44,032
domain points, including rank-deficient P and Q; these corroborate the general
written reduction. The regular-orbit positive fixture and 14 rejection
controls are retained. Wrong generator alignment, a corrupted image rank or
group product, the identity asserted to annihilate, a missing witness term,
the zero witness, a wrong extension corner, a supposedly fixed bottom
complement, and a falsely vanishing norm on the upper construction all reject. These
finite checks support the written reduction; they are not a proof-kernel
formalization or independent human acceptance. No physical caller or full
multiplication theorem is verified.

## Sources, coordination and value check

Fresh base: `20a1e31bc6009b9b3f4d084bbaadc6350e34fcba`, priority revision 7.
The selected-record source/metadata orientation passed before research;
no historical supplier suite was run. The task picker seed was
`868e7503946f9a08f9e795c7cdf8df97`. The `bit-new-register-model` scope is changed
from a paid-word proposal to this unresolved address-realization minimum.
Current priorities explicitly allow scoped interface obstructions.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5131)
takes #5114's explicit open question after its construction reservation was
released. #1166 was checked first. Before claiming, the complete overlap
snapshot covered 314 open PRs, 4,282 Discussion records, 4,406 closed PRs and
6,884 main-tree notes; targeted live searches and this account's recent
claims found no same-scope minimum result. Unpublished work and arbitrary
diffs remain outside that coverage. This adds the universal lower bound;
neither the existing upper construction nor its four-bit check is presented
as a new contribution.

Exact source blobs and SHA256 values are in [SOURCES.json](SOURCES.json).
The predecessor's README and result at #5114 head
`d165f73e8af63e8621e4e8a279f58b54079e48c5` are retained unchanged and hash-checked.
Only this new package is modified.

## Open next questions

The minimum question is closed within the stated affine contract. The useful
next task remains #5114's first question: bind **one actual BIT caller** to
the necessary eight-bit carrier, including its rank-one-projector operation,
frames, owners, arbitrary dirty inputs, restoration and complete movement
and scalar bill. Start from that pinned carrier and a named chronological
caller; stop if its full bill loses the direct implementation. No physical
ABI or tariff is supplied here, and this follow-up is not reserved.

## Credit

Krzysztof Wojt, with substantial OpenAI Codex assistance, including a separately
implemented finite-algebra checker. Apache-2.0. Nick Petalas retains the
eight-bit construction and the open minimum question (#5114). Wentao Li
retains the any-register formal endpoint result (#4089); Cinna Davis retains
the A5 word and additive-caller obstruction (#2246/#3914). The natural A5,
SL2(F4), permutation-module and group-algebra methods are classical; their
literature priority is not claimed. The retained register-model lineage,
including eumemic and Ali Romman, keeps its credit. The contribution here is
the universal extension/subquotient obstruction and its application to the
repository's exact affine minimum, with explicit exact finite certificates.
