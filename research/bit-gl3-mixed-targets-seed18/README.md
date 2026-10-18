# Mixed GL3 bit targets: exact minima and 624 natural-representation aliases

**Scoped negative result; no new kappa.** In the two-register formal model
defined below, the **27,308 ordered target pairs with direct coordinate-CNOT
cost at most nine have exactly that minimum cost**. For the remaining **916**
pairs, the minimum lies between nine and their direct cost (ten to twelve).
Those minima remain unresolved.

The natural six-dimensional matrix relaxation gives a misleading saving on
**624 pairs**. Complete formal enumeration excludes every one of those short
solutions. An explicit seven-call word passes the natural equality check but
fails all 336 faithful regular columns of its claimed target. This is a
concrete failure mode for accepting a supplier from natural matrix equality.

The contribution is the complete mixed-target table, its formal coset-join
coverage argument, and a separately written C++ replay. PR1496 checks one
repeated order-four target; this package covers all 168 squared ordered pairs
and checks the formal operator itself. Both implementations were written in
this session. No independent human review or proof-assistant verification is
claimed.

## Model and complete optimistic bill

Let `G = GL_3(F2)` and `R = F2[G]`. We work in `M_2(R)`. Both scalar registers
contain arbitrary inputs. The paid address alphabet consists of the six
coordinate CNOTs `g = I + E_ij`, with `i != j`. A paid call is

`D(N,g) = I + N ([g] + [e])`,

where `N = u v^T` is a binary rank-one idempotent: `v^T u = 1`.
There are six choices of N and therefore 36 paid generators. An arbitrary
scalar `GL_2(F2)` change of basis is free in this screening model. It can be
pushed through a paid call by conjugating N. Augmentation `[g] -> 1` sends
every paid call and the target to the identity, so the final scalar product
must be the identity. Thus the 36-generator alphabet covers arbitrary free
scalar interleavings.

The target is `diag([a],[b])` for any ordered `(a,b)` in `G x G`. Let `d(a)` be
the shortest coordinate-CNOT word for a. Implementing the two outputs
separately costs `d(a) + d(b)` paid calls. It uses only the two target registers,
no additional source register, copy, erasure, frame conversion, or cleanup.
Every factor in the direct word is paid. Free scalar mixing is an explicit
optimistic assumption; a physical implementation would have to price it.

The address Cayley layers are `1,6,24,51,60,24,2`, covering all 168 elements.
This is a different, explicitly finite nonabelian alphabet from the rational
abelian three-register model in the catalogue. No rational frame is reduced
modulo two. No physical source-access, compiler, common-label, hosting,
precision/tape or analytic-transfer admission follows from this model.

The bounded hypothesis was that heterogeneous targets might share paid work
that repeated-target examples could not. A saving had to beat the complete
direct paid-call bill in the full formal algebra. The stop rule was radius
four, all target pairs, and no radius increase. The initial natural nominees
led to exact formal checking on that same domain.

## Coverage proof

**1. Paid calls are invertible.** A coordinate CNOT has order two. The scalar
entries of N commute with R and `N^2=N`, so `D(N,g)^2=I` in characteristic two.
Every enumerated word is therefore an invertible formal matrix.

**2. A radius-four ball covers every word through length eight by a join.**
The breadth-first traversal stores every distinct formal matrix of distance
at most four, with its minimum distance. Any word of length at most eight
can be split as `A B^-1`, with A and B in that ball. Inverses have the same
length because the generators are involutions. Conversely, a joined pair
produces a valid word with length at most `dist(A)+dist(B)`. Odd lengths and
shorter words are included without a parity shortcut.

**3. Row normalization detects exactly the diagonal monomial cosets.**
For a nonzero row `r=(p,q)` over R, use the support of p when p is nonzero,
otherwise the support of q. For each address element x in that support,
form `[x^-1]r`; choose the lexicographically least pair of coefficient
bitsets. This is a canonical representative of the row's left G-orbit:
translating by y changes the anchors from x to yx, and
`[(yx)^-1][y]r = [x^-1]r`.

A row of an invertible matrix has trivial stabilizer under this action. If
`[g]r=r`, put that row in its parent matrix M. A row vector with entry
`[g]+[e]` in the corresponding position annihilates M. Multiplication by
`M^-1` forces `[g]=[e]`, hence `g=e`. Thus the minimizing anchor is unique.
The implementation rejects an unexpected tie rather than discarding it.

Normalize both rows of A and B. Their ordered pairs of canonical rows are
equal exactly when `A=diag([a],[b])B`. If the recorded anchors of A are
`(x_A,y_A)` and those of B are `(x_B,y_B)`, the target is

`a = x_A x_B^-1`, `b = y_A y_B^-1`.

Group equal canonical pairs, and enumerate every ordered pair within each
group. This checks every possible diagonal target without projecting away
formal coefficients. Hash tables retain full-key equality; no digest is used
as a substitute for a mathematical state.

**4. Interpreting the table.** Each cell stores the minimum joined length in
`0..8`, or the sentinel 9 meaning only that no word through length eight
exists. The full replay obtains

`table[a,b] = min(9, d(a)+d(b))`

for every one of the 28,224 ordered pairs. The verifier also checks the direct
formal word for every pair. This proves the exact direct minimum whenever
the direct bill is at most eight. A direct bill of nine is exact too: the
lower bound is nine and the direct word attains nine. For direct bills above
nine, the table gives a lower bound, and does not establish optimality.

## Exact evidence

| Quantity | Full formal algebra | Natural matrix relaxation |
|---|---:|---:|
| Distance layers 0 through 4 | 1, 36, 996, 25,518, 636,945 | 1, 36, 816, 14,694, 225,528 |
| Distinct states | 663,496 | 241,075 |
| Traversed generator edges | 955,836 | 559,692 |
| Coset groups | 133,207 | 14,300 |
| Ordered pairs examined in joins | 35,371,972 | 41,238,475 |

The natural join uses the ordered row spaces of the upper and lower 3x6
blocks. Equality of those spaces is equivalent to left multiplication by a
block-diagonal element of `GL_3(F2) x GL_3(F2)`. This computes natural distances
through eight; the natural representation is used only as a comparison.

The formal census finds 24,224 targets reachable through eight calls. The
direct-cost-nine class adds 3,084 exact minima, for **27,308** in total. The
remaining direct costs are ten (816 pairs), eleven (96), and twelve (4).

The natural aliases have these costs:

| Natural minimum | Direct bill | Pairs | Formal conclusion |
|---:|---:|---:|---|
| 7 | 8 | 96 | Exact minimum 8 |
| 8 | 9 | 480 | Exact minimum 9 |
| 8 | 10 | 48 | Minimum at least 9; exact minimum unresolved |

For a small explicit example, encode addresses by their three row masks.
Take `a=(4,1,2)` and `b=(7,2,4)`, whose direct bills are six and two.
The following event-order word has natural cost seven and the correct
natural target. Each tuple is `(u,v,i,j)`, with u and v encoded as two-bit
masks and `g=I+E_ij` using zero-based coordinates:

```text
(2,3,0,2), (1,3,2,1), (1,1,1,2), (3,1,0,1),
(1,1,2,1), (1,1,1,0), (1,3,0,1)
```

Its formal matrix differs from `diag([a],[b])`. The independent set-based
faithful regular column check rejects it on every one of 336 input basis
columns, while the direct eight-call word passes all columns. This is a
counterexample to a proposed **acceptance rule**, not to the accepted supplier
or to the use of natural matrices for exclusion.

One visible residual is the upper-right entry: `[172]+[174]+[277]+[279]`,
where each number packs its three row masks in consecutive three-bit fields.
The four address elements are distinct, so this formal coefficient is nonzero;
their binary matrices XOR to zero. It exposes exactly what the natural
representation loses.

The C++ replay enumerates GL3 by testing all 512 binary matrices and composes
their actions on basis vectors. It enumerates scalar idempotents directly as
2x2 matrices. Python obtains GL3 by Cayley traversal, uses row-combination
multiplication, and enumerates `u,v`. C++ uses three 64-bit limbs per formal
coefficient; Python uses arbitrary-precision integer bitsets. The two full
state sets and every distance are compared byte for byte in canonical order,
and all 28,224 target entries are compared. They share the written coset proof;
this is implementation independence, not independent human proof review.

[CERTIFICATE.json](CERTIFICATE.json) records exact counts, the address ordering,
both target-table digests, the full-state digest, and 13 controls. Controls
cover scalar-conjugation completeness, illegal nilpotent masks, involutions,
noncommuting order, all two-call projection squares, all direct upper bounds,
the false natural witness, faithful regular columns, omitted and transposed
calls, reversed words, dirty cross-inputs, and identity/one-output boundaries.

## Reproduce

From the repository root, with Python 3.12 or later and a C++17 compiler:

```sh
python3 -I -B research/bit-gl3-mixed-targets-seed18/verify.py
```

Expected final line:

```text
PASS_GL3_MIXED_TARGETS pairs=28224 exact_minima=27308 unresolved=916 formal_states=663496 natural_aliases=624 controls=13 no_new_kappa
```

No Python dependencies or network access are needed. The command compiles the
C++ checker in a temporary directory, compares the complete certificate, and
leaves source files unchanged. To retain the 56 MB state stream and both
28,224-byte tables, pass `--work` with a new or empty directory outside this
package. Table rows/columns follow `address_matrices` in the certificate.
Value 9 is the lower-bound sentinel described above.

`test_package.py` runs four quick boundary and output-preservation tests.
The generic registered-package hook runs **only those quick tests**. The
[dedicated native workflow](../../.github/workflows/bit-gl3-mixed-targets.yml)
and the command above run the complete dual-engine census. A passing metadata
or quick-test hook alone does not establish the census result.

The optional `--emit-certificate PATH` regenerates a certificate and refuses
to overwrite it; this authoring mode does not compare the committed receipt.
Ordinary verification compares every receipt field and fails on a mismatch.

## Provenance, scope and credit

Base: `64039f1bd3b6a523b96083fd858ad040a75e3030`. The selected record at this
base is the maintainer-reviewed conditional `kappa=0.001672660197076918` from
PR1094, with PR589's bit supplier and the complex side binding. The baseline
binding check was run; the selected cold replay was outside this unchanged
construction's scope. This package makes no new selected-supplier or kappa
claim and does not edit the selected frontier or frozen inputs.

OS assignment seed **18** selects the user-assigned bit-supplier track. It
rotates the Python generator traversal. The task choice followed a live
overlap check; changing a seed is not evidence of novelty. The exact scope,
three candidate tasks, bounded stopping rule and remaining questions are in
[TASK.json](TASK.json). The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18913629)
is on the existing register-model discussion; there was no pinned sprint issue.
The overlap coverage and its limits are recorded in [OVERLAP.json](OVERLAP.json).

Credit Gareth Davidson (@bitplane), [PR1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333)
at `7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2`, for the binary-affine model
and coordinate-alphabet follow-up; @commdata2338,
[PR1414](https://github.com/CrocSwap/integer-mult-bounds/pull/1414) at
`9e1640094f649ba6db9742796825a8d6c238989b` and
[PR1496](https://github.com/CrocSwap/integer-mult-bounds/pull/1496) at
`0b1420fcc47e2137c5f0a5b9aa347cd001fff9cd`, for the coordinate-register
continuation and repeated order-four target. The register-model lineage also
includes eumemic, Ali Romman and David Govea, as recorded in the pinned
catalogue starting point. These are contextual predecessors; no pending PR
code or result is assumed in this self-contained proof. Their implementations
are not imported. [SOURCES.json](SOURCES.json) pins the exact base, source
blobs, review context and predecessor heads. No broad priority claim is made.

Prepared for Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance
in the reasoning, both implementations, verification and writing. New work is
Apache-2.0. The result is a finite computer-assisted statement for exactly two
registers and the stated alphabet. Extra dirty registers, other alphabets and
physical multiplication interfaces remain outside its scope.

## Open next questions

1. **The 916 unresolved target pairs.** Their minima could affect this model's
   paid bill. The emitted table identifies each pair. A useful next step is a
   target-specific invariant or explicit nine-call formal identity. This
   certificate has no length-nine search coverage; more radius alone was not
   authorized by its stopping rule.
2. **A smaller representation that excludes the aliases.** This could improve
   future screening without relying on natural equality for acceptance. Start
   with the explicit seven-call fixture and a justified additional
   representation. A survivor would still need full formal verification or a
   proved faithfulness argument.
