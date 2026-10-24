# Conditional kappa 0.00302725 by transposing an owned supplier

This construction gives **conditional kappa = 12109/4000000 = 0.00302725**.
It improves the selected PR4610 value 0.0030217758 by 0.0000054742. It improves
the eight-relation PR5383 value 0.00302666 by 0.00000059. The paid profile changes;
the gain does not come from more digits of an unchanged root.
It also exceeds the later [PR #5387](https://github.com/CrocSwap/integer-mult-bounds/pull/5387)
compiler refinement, 0.003026674765, by 0.000000575235. That refinement is related
work; it is not a source dependency.

The new result transfers a completed backward supplier to the forward
interface. It applies the classical transposition principle to the complete
linear circuit, including owned COPY and CLEAR operations. Exact monomial
corrections then restore the required forward map. Thus the two forward calls
can use the same reduced paid and helper profiles as the sixteen backward
calls. The construction also gives a reusable rule for later suppliers with
this interface and clean owned storage.

[RESULT.json](RESULT.json) gives the complete evidence and bill.
[WORD.json.gz](WORD.json.gz) gives the emitted finite word and its boundary
corrections. [PHASES.json.gz](PHASES.json.gz) gives every transposed paid
operator recipe. [SOURCES.json](SOURCES.json) pins all consumed bytes.
The selected frontier is unchanged.

## Exact source and separate scope

The scientific base is canonical main
`1ec1119972c9aefe42525172d07b332fcff81cb4`, priority revision 7.
The source is Ali Romman's eight-relation
[PR #5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383), fixed at
`4bd6efa51a495a7c7b7754915cf0244e7e60969e`. Its published word, after canonical
JSON serialization with a final newline, has SHA256
`2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d`.
The verifier reconstructs and checks that exact word before transposition.
It does not consume a later PR head or an unpublished helper relation.
The exact source files are retained in commit
`5eb314069417db1f4305430b6b14f20e9251e509` in this branch. The live pins use
that ancestor; each `source_pin` retains the original PR source and hash.
A clean checkout does not need either pending PR commit in its object store.

PR5383 prepares eight owned pivots from independent cold helpers. It removes
eight rank-eight centers and eight rank-one jobs, and debits eight rank-nine
productive targets. Its unchanged input is Cao Yifan's final
[PR #4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610) word, with
payload SHA256
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
This package retains that backward construction and changes only the forward
supplier and its full cost calculation.

The [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19154367)
first tested the one-relation source. After PR5383 published and released its
eight-relation construction, this work pinned that stronger completed source.
No search or priority claim for the source relations is part of this result. Native map changes,
finite contact searches and no-snapshot relation screens that gave no gain
are not included in this PR.

## 1. Transpose a complete linear circuit

Let a source circuit act on independent fields x and owned fields z. Assume
that its complete map, with both x and z initially arbitrary, is

```math
(x,z) \longmapsto (Bx,0).
```

In particular, every owned input column and output row is zero in the complete
matrix. Reverse the instruction order and transpose each instruction matrix.
The resulting circuit has complete map `(x,z) -> (B^T x,0)`. The transpose is
bilinear transpose over the complex numbers. It is not conjugate transpose.

The emitted scalar rules are:

| Source instruction | Transposed instruction |
| --- | --- |
| `d += c*s` | `s += c*d` |
| `d *= c` | `d *= c` |
| owned `CLEAR d` | owned `CLEAR d` |
| owned `COPY d <- s` | `s += d`, then owned `CLEAR d` |

All coefficients stay unchanged. Every new CLEAR targets a field that was
already owned. The procedure uses the same physical slots. It does not invert
a CLEAR or assume that an erased value is available. A source COPY costs one
extra ADD under transposition; that cost is included below.

A native monomial U has monomial transpose. If its action is
`U e_x = i^p(x) e_(Ax+t)`, its transpose sends `e_(Ax+t)` to `i^p(x) e_x`.
Its permutation is the inverse affine map, with the same entry phase at the
inverse address. The affine-quadratic grammar is closed under this operation.
Equivalently, `U^T = conjugate(U^-1)`.

A standard Gaussian child C_r is symmetric. A source child with the exact
factorization `L C_r R` therefore transposes to `R^T C_r L^T`. Both new boundary
maps are native monomials. It has the same paid rank r, including its absolute
phase. This gives a direct finite lowering algorithm for every source child.
It does not require a new Gaussian supplier or a new assumption about general
Clifford identities.

These identities hold at every positive tensor width f. Transposition commutes
with tensor powers, and scalar coefficients stay outside tensor powers. The
new native checker verifies the concrete monomial logical normalization by
its complete four-width criterion. The separate transposition argument and
Gaussian factorization establish the paid circuit statement.

## 2. The zero-row frame marker requires no reverse zero assumption

The source replaces eight paid jobs by physical identity. At each such job,
the data row is zero under the prepared helper relations. It records this with `zero_retag`.
The transpose of physical identity is identity. It is omitted from the emitted
physical word. The reverse data row need not be zero.

For a second endpoint check, insert a distinct fresh free operator at each corresponding
reverse coordinate boundary. The exact rational replay cancels every term
that contains this operator at all returned fields. It checks all 641 entry
columns, including the seventeen owned fields. This is a proof in free operator
words, so it also holds for the actual nonmonomial frame quotient. The proof
symbol is not an emitted gate, an unpaid Gaussian call, or a presumed native
recipe. The complete matrix transposition theorem is the physical argument.

The new forward artifact lists source indices for transposed paid operators
and source markers. A paid reference resolves through the exact source pair
and PHASES.json.gz. A native warp reverses its signed map and its frame pair.
Source entry and exit normalizers are transposed in reverse order, at whole
invocation boundaries. The inherited whole-job normalizer contract remains
explicit; no internal partial job is normalized for free.

## 3. Restore the required forward interface

Use the source controller's normalized complex local interfaces, stated in
`research/query-thinned-controllers/PROOF.md`. On each port, Q is the central
rank-one Gaussian and D is its commuting stage multiplier. Both are symmetric
in these coordinates and `Q^4=I`. For later stages D acts on eight fresh axes.
At stage zero it is the source nine-axis Gaussian times `Q^-1`; the same
symmetry and commutation statements hold. Spectator axes are unchanged.

```math
F=\begin{pmatrix}D&0\\DQ^{-1}&D\end{pmatrix},\qquad
B=\begin{pmatrix}D&-DQ\\0&D\end{pmatrix},\qquad
J=\begin{pmatrix}Q^2&0\\0&-I\end{pmatrix}.
```

Direct multiplication gives `F = J B^T J`. Apply J before and after the
transposed normalized backward circuit. The Q squared operation is the exact
native translation, with no paid Gaussian job. The Y sign is scalar `-1`
on the complete field. It is not native phase two raised to tensor width f.
The verifier rejects that phase substitution with an all-width counterexample.

The backward helper normalizer gives `conjugate(C_r)`. Transposition leaves it
unchanged because it is symmetric. Append `C_r^2`, the native translation on
its r active axes, to obtain C_r. Charge one such pass on every retained helper.
The word records all 400 helper ranks and translation offsets. These wrappers
restore the original forward main contract and the 400 independent productive
helper contracts. The eight pivot fields and C0 through C8 remain owned and return zero.

This argument applies to any completed supplier with the same normalized B
interface, standard productive Gaussian helpers, native boundary maps and
clean owned storage. It does not classify other interfaces or justify a
source construction whose own endpoint or bill is incomplete.

## 4. Complete bill and conditional exponent

Both directions now have

```text
paid:    {1:2193, 2:412, 3:510, 4:127, 5:40}
helpers: {4:28, 7:7, 8:47, 9:318}
```

Relative to PR5383, the two forward calls remove sixteen H1 and sixteen H8
paid jobs, and debit sixteen H9 productive targets. For every `0<t<1`, the complete
target-minus-paid moment gains `16*(1+8^t-9^t)>0`. This adds 12.5 percent to the
source's sixteen-call moment gain. Relative to final PR4610, the full p16
change is minus 144 H1, minus 144 H8 and minus 144 H9 targets.

The full bill has **64,116 paid jobs and 10,784 productive fields**. The rank
surplus stays 752. Both main targets, all 15 query shears, all idle jobs and
both completion tails are included. Two independently assembled invoices and
two rational interval engines agree.

The fixed-profile crossing lies in
**(0.00302728824993, 0.00302728824994)**. The claimed saving 0.00302725 leaves
more than 0.00000003824993 raw headroom. The tested saving is 0.00302726.
The exact completion uses power 1024, cutoff 20, floor 21, tail offset 1/5
and reserve 1e-9. Both tail ratios are below 0.97. The finite compiler has
`H=31385200000000`, `N=2^H`, gap `1/700000000` and logarithm power 1000.
The exact integer threshold test passes. All 54 strict and four functional
outer predicates pass, with the retained ordinary BIT saving 0.0034.

The forward scalar allowance is 159,320, including the sixteen transposed COPY
rules and both Y sign layers. The route allowance is 10,292,000. It includes
224 main native passes and 400 helper translation passes. It conservatively
doubles the source route allowance because COPY becomes ADD then CLEAR.
Eight additional physical private slots relative to PR4610 suffice, as in
PR5383. Each direction has seventeen owned fields, including eight old helper
slots.
The local allowance remains below 2*10^7 and the complete raw nonrecursive
allowance is **361,098,496 < 10^9**. The forward formal prefix L1 maximum is
442, below the original forward maximum 457. The denominator is at most 32,
equal to the original bound.

## 5. Reproduce and assess the limits

Use standard-library Python 3.12. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/native-transpose-owned
```

The normal and optimized commands must end with

```text
PASS_CONDITIONAL_KAPPA_00302725_OWNED_TRANSPOSE
```

For a standalone replay, run:

```sh
python3 -I -B research/native-transpose-owned/verify.py
``` The separate `--write` authoring
mode writes only this package's artifacts after all mathematical gates pass.
Normal verification compares every regenerated artifact with committed data.

Checks cover the exact published source word, 641 independent/owned entry
columns, the arbitrary frame-bridge cancellation, the complete native
four-width certificate and its separate checker, all 2,847 transposed paid
phase classes, all 180 native warp classes on 92,160 literal columns, all 112
Q-squared port phases, four productive helper ranks, the literal p16
controller, the full cost calculation, completion, compiler and outer ledger.
Controls reject a wrong ADD transpose, missing owned cleanup, wrong native
inverse, wrong prepared relation, wrong absolute phase, omitted Q-squared
correction, scalar/tensor sign confusion, unearned helper credit and invalid
outer parameters.

The complete bound retains the selected framework's native/all-column source,
owned erasure, whole-job normalizers, finite-template closure, precision and
fixed-tape, analytic decomposition, prime avoidance and exact recovery
assumptions. The source and new finite algebra/phase obligations are checked;
physical tape execution, numerical precision execution, ordinary BIT native
replay, Lean, Docker, analytic decomposition and integer recovery are not rerun.
The huge uniform compiled word is specified by a finite algorithm and is not
materialized. This is an author-checked conditional construction. It is not an
unconditional multiplication theorem, a practical speedup, independent human
acceptance or proof-kernel acceptance.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
Ali Romman's separate PR5377 and PR5383 contributions supply the owned
relations, actual saved values, zero-row replacements and backward word. The new
contribution is the transpose construction, its exact forward normalizer,
physical phase receipts and complete additional gain. No credit is claimed
for discovering the source relations.

Cao Yifan / intqwq supplies final PR4610. Cinna Davis / 1337isnot1337 supplies
the PR4470 controller and native lineage. Dugongue supplies transported-frame
work; zxv supplies native, owned-cache and compiler interfaces; Jacob Alan
Sussman supplies mixed-target recursion. The source notices retain their
predecessors. The classical transposition principle is not new here.

[PR #5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369), at
`18354f41de4dc7bfda4692e814cf1d91a6d619ef`, supplies the complete native tensor
criterion, producer and separate checker. The four code files are copied
without changes. Its native and classical mathematical attribution remains in
that linked proof. [source/NOTICE.md](source/NOTICE.md) gives the exact source
links and copied-file scope. The pricing code is adapted from the attributed
PR5377 engine, which retains Cao Yifan, Cinna Davis, zxv and Jacob Alan Sussman.

## Open next questions

Apply the construction to a stronger, published and independently verified
backward supplier. First check its complete normalized interface, owned
columns and productive targets. Then transpose the actual word and recompute
the complete bill. This package does not reserve or assess unpublished source
constructions. [TASK.json](TASK.json) records the scope and first gate.
