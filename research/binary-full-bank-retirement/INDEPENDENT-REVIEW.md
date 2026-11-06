# Independent review of the full-bank binary-cut result

Prepared for Jerry Chen / [@CubeJerry](https://github.com/CubeJerry) with substantial OpenAI Codex assistance, Apache-2.0. This is an independent implementation and algebraic review by a separate agent in the same AI-assisted session, not independent human or formal-kernel review.

**Conclusion:** the full-bank ordinary obstruction and the forward-plus-restoration query debt follow under the stated hypotheses. The one-channel and two-channel escapes have the claimed complete arbitrary-input endpoints. No new multiplication κ follows; the fully charged fragment mechanism loses.

## Written mathematical checks

The old endpoint is `LR[(I+S E_XY) ⊕ S I_aux]` with formal `S²=1` and independent basis elements `1,S`. For an ordinary old target `LR`, the eligible input columns have only an X block, while eligible output pullbacks have only a Y block. Their dual pairing is zero. For old target `SLR`, both directions lie entirely in the auxiliary A,B bank. Thus allowing ordinary bases across all four banks does not evade the auxiliary constraint.

For a pure L prefix, coefficient comparison in the two active rows forces both auxiliary input blocks to vanish. For a pure SL prefix, it forces `U_B=0`. The general cut-row identity has X block `W1`, A block `SL p-S W1` and B block `L p-SL q`. Since the X block must vanish, `W1=0`; ordinary parity comparison in the B block forces `p=D_A=0`. The resulting `D U=0` contradicts an independent retirement. This reasoning does not constrain K at all; K may be S-dependent or singular. Its legality and eventual completion are granted for the negative result, not assumed as a constructive supplier.

For a central-dependent cut basis, the resident column may also depend on S. This matters: a false forward-only bound would miss the actual two-channel escape. For prefix SL, its odd X block equals `U_B`; the cut row's odd Y block equals `D_A`. A new rank-one central query increases odd-part rank by at most one, including after arbitrary invertible ordinary changes. Hence

```
r = rank(I_r) <= rank(D_A) + rank(U_B) <= k_forward + k_restore.
```

For a pure L prefix, the resident column's stacked odd active blocks are `(U_A,-U_B)^T`, of rank r, so restoration alone requires at least r queries. These are written universal arguments over all widths, not conclusions drawn from the finite endpoint checks.

The pricing statement has two orientations. An SL prefix gives `i(a)-i(a+b)` and a pure L prefix gives `i(b)-i(a+b)`, where `i(x)=H(x+1)-H(x)` and `H(x)=x^t`, `0<t<1`. Both gains lie strictly between zero and one. The r-channel fragment gain is therefore less than r, while the new thin-query bill is at least r. Multiplication by the same physical port count preserves the strict loss. This comparison cancels unchanged native/helper work and grants ordinary routing free. A genuinely changed productive-helper contract is outside this price proof; it is not automatically a nonnegative debit.

## Separately implemented exact oracle

Run:

```sh
python3 -I -B verify.py
python3 -I -O -B verify.py
```

The implementation imports no predecessor or author replay. It reads the frozen caller only to authenticate its SHA256; the source normalization and correspondence of its binary macro to the displayed abstract macro are part of the written source review. The exact frozen source is #6726 at `435bbe91fb28cb1d7a569ca70c6c4e9eb302d486`, `frozen/two-fragment/caller.py`, SHA256 `e99e4287091c6ce4ec9a563cb9ac6f45be35ff1ef421b4efa8c200cb9d639d6c`.

The oracle pulls output functionals backwards through an independently encoded normalized binary macro and both escapes. It represents the formal central symbol by its faithful two-dimensional regular action, swapping the coefficients of 1 and S. This retains the formal distinction in characteristic two as well; it does not substitute S=1 or rely only on the two sign characters.

A cancellation-free path-support calculation proves that every relevant output has degree at most one in each of L and R. Four exact evaluations at `(L,R)=(0,0),(1,0),(0,1),(1,1)` therefore recover every polynomial coefficient by finite differences. This is exact interpolation justified by a checked degree bound, not a numerical test. Although L and R are invertible in the theorem, the constructed words use only nonnegative powers, so polynomial evaluation at zero is a valid coefficient-recovery device. The coefficient identities extend to the Laurent ring.

The oracle checks all 25 or 36 input/output entries and all eight possible `(S,L,R)` coefficients, respectively 200 and 288 coefficient positions. It separately reconstructs the unchanged full binary endpoint, the two-channel prefix, and both complete changed endpoints. Fresh arbitrary inputs are checked untouched before their handoff; both new forward and restoration queries are counted from the literal words.

Eight changed-word controls reject an omitted restoration query, treating its S as ordinary, omitting the fresh-input handoff, and omitting the final target association, in each of the one- and two-channel cases. A ninth source-corruption control rejects changed frozen bytes. Normal and optimized runs produce identical complete output; `REPLAY.txt` retains the normal receipt.

## Scope and inherited hypotheses

The conclusion fixes the source's completed-left-child active history and old scalar targets LR or SLR, requires ordinary source/target bases, and treats L,R as independent commuting invertible body symbols and S as a formal independent involution. The coupled bank width and auxiliary matrix K are unrestricted. The priced escape uses newly supplied rank-one thin central queries in a basis G and its inverse H. Existing query reuse, a redesigned suffix that eliminates restoration, different target monomials, cuts inside a child, packed oracle alphabets and changed productive-helper boundaries are outside the conclusion.

This check does not audit physical phases, native all-column action, owned erasure, compiler construction, precision/tape or analytic recovery. The five selected framework assumptions retain their status. The exact binary identity, native query semantics and source normalization retain the predecessor lineage: Cinna Davis; Ali Romman #6348/#6398; thu-nmrc #6716; zxv #6726; and the preserved source notices. No frontier file is changed.
