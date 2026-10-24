# Exact mixed GL2-block tariffs in larger address spaces

**Scoped formal-model theorem; no new kappa.** Fix disjoint pairs of address
coordinates. A diagonal register target can use any of the six `GL_2(F2)`
operators on each pair, with different choices on different registers.
Its exact cost is the sum of the block tariffs

```text
label:    e  a  b  ab  ba  s=aba
cost:     0  1  1   2   2     3.
```

This remains true in every ambient `GL_n(F2)` that contains the pairs, even
when the circuit uses arbitrary coordinate CNOTs between pairs or with
address spectators. Free scalar register mixing and any finite number of
restored dirty registers are allowed.

The dimension-two mixed tariff is already a corollary of Ross Richardson's
[PR #1989](https://github.com/CrocSwap/integer-mult-bounds/pull/1989), through
the `GL_2(F2)=S_3` bridge in
[PR #2415](https://github.com/CrocSwap/integer-mult-bounds/pull/2415).
This contribution extends the averaged row-order method of
[PR #4950](https://github.com/CrocSwap/integer-mult-bounds/pull/4950) from
identical swaps to all six block labels and sums over disjoint pairs.
It does not claim a new dimension-two lower bound. The selected kappa remains
`60403/20000000`; no physical supplier is supplied.

## Model and theorem

Let `n>=2` and let `B_j=(p_j,q_j)` be fixed pairs with disjoint coordinate
sets in `{0,...,n-1}`. For each target register `r` and block `j`, select
`g_(r,j)` from `GL_2(F2)`. Its embedding acts on the two coordinates of `B_j`
and fixes all other coordinates. The register target `g_r` is the product
of these embeddings. They commute because the pairs are disjoint.
Other register targets and all unused address coordinates are identity.

Work in the formal group algebra `M_R(F2[GL_n(F2)])`. Every register input
is arbitrary. The endpoint is `diag([g_1],...,[g_t],1,...,1)`, with every
extra register restored and no off-diagonal residue. Paid units are

```text
I_R + ([c]+1)N,
```

where `c` is any coordinate CNOT in the ambient address space, and `N` is
any binary scalar rank-one idempotent. Each unit costs one. Free scalar
`GL_R(F2)` maps may occur anywhere. There are no other free address maps,
clean allocations or uncharged restoration calls.

**Theorem.** For every finite `R>=t`, the exact paid-call minimum is
`sum_(r,j) ell(g_(r,j))`, with `ell` given by the table above.
The empty target uses the empty word. The statement covers arbitrary
intermediate scalar projectors and cross-pair address calls; only the
required final target has the block form.

## Proof

Use the left regular representation of `G=GL_n(F2)`. For each total order
`<` on the nonzero binary vectors and pair `(p,q)`, let

```text
A_(p,q) = {x in G : row_p(x) < row_q(x)}.
```

On all `R` registers, take the crossing rank from this address cut to its
complement. Block multiplication gives `q(MN)<=q(M)+q(N)`. A free scalar
map has crossing rank zero. A paid call has crossing block
`P_c[A^c,A] tensor N`, so its crossing rank is `out_A(c)`, since `rank(N)=1`.
A diagonal target has the sum of its register crossing ranks. These facts
hold in the formal algebra and do not assume commuting projectors.

Average each cut over all total orders. Write `u=|G|/6`.
A CNOT writing neither coordinate of a pair changes neither selected row,
so its charge in that cut is zero. If it writes the first row, denote the
old rows by `x,y` and the new row by `z`. The three vectors are distinct:
rows of an invertible matrix are independent, and a sum of two rows is
neither zero nor any original row. The event that the cut is left is
`x<y<z`, which has probability `1/6`. If it writes the second row, the
leaving event is `z<x<y`, with the same probability. This holds for a read
inside the pair, in another pair or at an address spectator.

Thus a call contributes `u` to the averaged cut of its written coordinate's
pair, if there is such a pair, and zero to every other pair. Disjointness
makes the sum of all paid charges at most `u`. In particular, reading from
another pair does not charge its cut: that pair's rows do not change.

For a target block, put `z=x+y`. With
`a=[[1,1],[0,1]]` and `b=[[1,0],[1,1]]`, products act rightmost first.
The output rows and numbers of leaving orders among the six orders of
`x,y,z` are:

| Label | Output rows | Leaving orders |
| --- | --- | ---: |
| e | x,y | 0 |
| a | z,y | 1 |
| b | x,z | 1 |
| ab | y,z | 2 |
| ba | z,x | 2 |
| s=aba | y,x | 3 |

Each averaged target charge is `u*ell(g)`. Other blocks in the same register
do not change this pair of rows. Summing over target registers and blocks
therefore gives target crossing rank `u*sum ell(g_(r,j))`. Subadditivity
bounds it by `u` times the total paid-call count. Since `u>0`, this proves
the lower bound for arbitrary dirty workspace and ambient dimension.

For the upper bound, use the direct two-generator word for each block on
its own register with coordinate projector `E_rr`. Its length is `ell(g)`.
The factors remain diagonal formal monomials, so the group identity is
also a coefficientwise identity in the full formal algebra. Concatenate
the words for all blocks and registers. This attains the lower bound and
restores every unused register and coordinate. No unpaid cleanup is needed.

## Consequences and boundary

The heterogeneous target `diag([a],[b],[aba])` costs exactly five for all
`n>=2` and any `R>=3`. The fixed-three-register search in
[the retained heterogeneous-target note](../bit-mixed-transposition-triple/README.md)
already found five at `n=2`. Its extra-register question is covered there by
the inherited dimension-two cut theorem; the ambient-address extension here
also rules out using other address coordinates to reduce that cost.

The coordinate pairs must be disjoint. On one register, the product of the
three swaps on `(01),(12),(02)` equals the swap on `(12)`. Its separate
nine-call implementation can therefore be replaced by three calls. The
verifier checks this literal counterexample and rejects overlapping pairs
as input to the additive tariff. This is a one-register product; it is not
the three-register mixed-swap target of the component-cut theorem.

The theorem also retains the rank-one tariff, arbitrary-input endpoint and
absence of free address transformations. It does not cover unequal or
projector-dependent prices, a rank-two call charged as one, a restricted
clean-input endpoint, or arbitrary overlapping block products.

## Evidence and reproduction

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/mixed-gl2-block-tariff
python3.12 -I -W error -O -B research/mixed-gl2-block-tariff/verify.py
```

Expected markers: `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_MIXED_GL2_BLOCK_TARIFF costs=0,1,1,2,2,3 no_new_kappa`.
Normal replay recomputes [RESULT.json](RESULT.json), writes no files and
needs no Git or network. `--emit-receipt` emits JSON for explicit regeneration.
The receipt binds all five source files by SHA-256.

The checker compares the six crossing counts with independently computed
`GL2` word lengths. It checks 80 actual coordinate-CNOT/basis cases over
31,992 relative orders, including cross-pair reads and spectator writes.
It exhausts all three-register single-block label triples and all two-register
two-block label quadruples in the declared finite dimension/register grids:
7,128 complete diagonal formal endpoints and 39,852 single-call omissions.
Nine controls cover invalid contracts, empty targets, the five-call example
and the overlapping-block counterexample.

These particular upper words remain diagonal monomials. Their group labels
are therefore sufficient to verify their full formal endpoints. This does
not assert that natural matrices certify arbitrary group-algebra programs.
The lower bound for all programs is the written regular-representation proof.
No predecessor executable is imported.

## Open next questions

What is possible for overlapping target blocks? First specify the actual
one-register product or multi-register endpoint; the example above shows
that a list of local block prices need not add. No general cost law for
that changed boundary is supplied here. Native realization, full supplier
accounting and proof-kernel review remain separate obligations.

## Credit and source pins

Prepared for Ali Romman with substantial OpenAI Codex assistance. New work
is Apache-2.0. Ross Richardson supplied the general inversion-sum theorem
and the GL2 bridge; James Reed supplied the averaged spectator cut; Cinna
Davis supplied the fixed-register heterogeneous question. Their retained
notes credit Mihir Srivastava, commdata2338, Gareth Davidson and earlier
register-model/cut contributors. All notices remain unchanged.
The four source documents are provenance only, pinned in
[SOURCES.json](SOURCES.json). Base:
`f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, priority revision 7.
No independent human review, native/compiler admission, selected cold replay,
full multiplier theorem or kappa improvement is claimed.
