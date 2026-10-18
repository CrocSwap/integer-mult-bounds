# Independent audit: the GL2 SWAP corollary

**Finding:** the exact tariff is `3t` for every integer `t>=0` and every finite
`R>=t` in the stated formal model. This is a direct specialization and relabeling
of the credited [PR1989](https://github.com/CrocSwap/integer-mult-bounds/pull/1989)
theorem, not a new general lower-bound theorem. No gap was found in that source
argument affecting this specialization. The proof does not assume commuting
projectors, full occupancy, or clean spectators.

This audit was performed by a separate OpenAI Codex exact-circuit-verification
specialist for Ross Richardson. The independent checker uses every basis column
of the faithful regular action, imports no package/predecessor mathematical
code, and was written separately from the primary checker. This is assisted
mathematical review, not independent human review or proof-kernel verification.
New text and code retain the repository's Apache-2.0 license and predecessor
attribution.

## Exact bridge and product order

Order the three nonzero binary column vectors as

```
v1=(0,1), v2=(1,1), v3=(1,0).
```

Define `phi(g)(i)=j` when `g vi=vj`. Both groups multiply by composition with
the right factor acting first. Consequently `phi(gh)=phi(g)phi(h)`. The action
is injective: fixing all three vectors fixes the two standard basis vectors.
Both groups have six elements, so it is an isomorphism. Its complete table is:

| GL2 element | Binary matrix, by rows | One-line permutation |
| --- | --- | --- |
| e | `10;01` | `(1,2,3)` |
| a | `11;01` | `(2,1,3)` |
| b | `10;11` | `(1,3,2)` |
| ab | `01;11` | `(2,3,1)` |
| ba | `11;10` | `(3,1,2)` |
| s=aba=bab | `01;10` | `(3,2,1)` |

Thus `a` and `b` become the two adjacent transpositions; `s` becomes reversal
and has three inversions. Extending `phi` linearly is an **isomorphism of the
full formal group algebras**. It permutes the six independent coefficients;
it does not identify distinct formal sums by passing to the natural 2-by-2
address representation. Entrywise extension maps every allowed factor
`I+([g]+1)N` to `I+([phi(g)]+1)N`, leaves every scalar free map unchanged,
and maps the full target to `diag([reversal] I_t,I_(R-t))`.

## Scrutiny of the lower bound and restoration

One can check the specialization directly in the six-dimensional left regular
action `L_g e_h=e_(gh)`. The equivariant bijection
`h -> (phi(h)(1),phi(h)(2))` identifies it with the source's ordered-pair action.
The increasing half is `H={e,b,ab}` and the decreasing half is `K={a,ba,s}`.
For all roles together, set `q(M)=rank_F2 M[K,H]`. Ordinary block multiplication
gives

```
q(UV) <= q(U)+q(V).
```

This uses only subadditivity of matrix rank and applies in the actual product
order; no scalar projectors are commuted. Each of `L_a[K,H]` and `L_b[K,H]`
has rank one. A legal paid call has crossing block
`N tensor L_g[K,H]`, of rank exactly one for every allowed binary rank-one
idempotent `N`. Each interleaved free scalar map `S tensor I_6` has zero
crossing block. All intermediate and spectator roles are included. Hence a
circuit with `C` paid calls has `q<=C`, regardless of how its free maps are
interleaved or whether its projectors commute or couple active and dirty roles.

The target crossing block is a direct sum of `t` rank-three reversal blocks
and `R-t` zero blocks, so `C>=3t`. The direct coordinate circuit executes
`a,b,a` on each target and costs `3t`. Its chronological product is `aba=s`
in that role, while every other role is untouched. This is equality of all
formal coefficients on arbitrary entrance values and restores every spectator
individually. It has no unpaid preparation or unfinished cleanup. The empty
target, including `R=t=0`, has exact cost zero.

The source's optional normalization is also valid: scalar conjugation preserves
the allowed projector class, and augmentation forces the net scalar factor to
be identity at the exact target. The proof above does not depend on performing
this normalization. The direct endpoint and its full coefficients are checked
separately from the cut invoice; a correct cut invoice alone is insufficient
to certify a proposed circuit's endpoint.

## Consequences for the two handoffs

The pinned PR2317 README uses exactly `a,b`, binary rank-one idempotents,
free scalar mixing, full formal coefficients and a fully occupied SWAP target.
Therefore its proposed general noncommuting thirteen-call word at `t=5` is
excluded by `C>=15`. Its historical commuting-family proof and finite screen
retain their credit; this audit does not rerun or review all of that screen.

The extra-workspace question in `research/four-swap-full-occupancy/README.md`
has the same exact target with restored spectators. The same result gives
`C>=12` for `t=4` at **every finite role count**, including active/dirty
coupling. The full-occupancy rotation proof's workspace restriction is not
extended; this corollary uses PR1989's different cut invariant.

## Independent executable coverage

Reproduction, from the repository root:

```sh
python3.12 -I -B research/gl2-swap-cut-corollary/independent.py
python3 -O -I -B research/gl2-swap-cut-corollary/independent.py
```

Both passed on Python 3.12.12 and Python 3.14.6 respectively, with marker
`PASS_INDEPENDENT_GL2_SWAP_CUT_COROLLARY`. The checker performs no search for
shorter words. It verifies:

- All six group elements, all 36 ordered group products, all 64 formal algebra
  elements under the regular action, and complete coefficient recovery from
  the identity input column.
- Every binary rank-one idempotent through `R=7`: counts
  `1,6,28,120,496,2016,8128`, totalling 10,795 projectors and 21,590 paid
  involution/cut checks across the two labels.
- Every free scalar invertible map through `R=3` (including the empty case):
  counts `1,1,6,168`, all with zero crossing rank.
- All 18 direct arbitrary-input endpoints `t=0,...,5`, `R=t,t+1,t+2`, plus
  18 equivalent `bab`/reordered-role presentations. Every role/address basis
  column is compared, including dirty spectator columns.
- Fourteen complete interleaved-free-map fixtures in those nonzero-target
  domains with `R>=2`, all using noncommuting projectors; ten also couple
  targets to dirty spectators. All chronological prefix invoices and complete
  endpoints pass.
- Rejection of all 135 single-call omissions, 15 wrong call labels, a wrong
  vector labeling, a spectator-to-target coupling invisible on zero spectator
  inputs, a forbidden unit-cost SWAP label, its invalid one-call cut invoice,
  and a rank-two call under the rank-one tariff.

Three disposable source mutations removed the complete-endpoint, paid-alphabet,
or declared-label check respectively. Each mutant exited nonzero at its intended
`negative control accepted` trap. Unexpected acceptance is raised outside the
caught rejection path. The temporary mutation files were automatically removed.
Optimized-mode success does not depend on Python `assert` statements; the
checker uses explicit exceptions.

The universal `3t` statement is a written mathematical corollary. These finite
checks corroborate its label, product, cut, charge and full-endpoint obligations;
they do not exhaust all words or prove a new multiplication theorem. Binary
formal coefficients are exact. No physical compiler, source-access charge,
integer/dyadic precision bound, recursive child profile, runtime or new kappa
is asserted. Enlarged paid alphabets, higher-rank unit-price calls, free address
maps or relaxed spectator endpoints require a new argument.

## Reviewed source pins

The common base was `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
The checker independently binds these unchanged repository files by SHA256:

| Source | SHA256 |
| --- | --- |
| `research/symmetric-adjacent-cut-bound/PROOF.md` (PR1989) | `008be68867a8e85f4e18455d206e03f20aebfc28e9f08efba576180e7e1edc50` |
| `research/four-swap-full-occupancy/README.md` | `82bdfbfb517505ef6783cb82e2718975876276075fe3dba26959df514f984f60` |

PR2317 model comparison used the parent-fetched
[`research/fiveswap-alt13-commuting-screen/README.md`](https://github.com/CrocSwap/integer-mult-bounds/blob/139779c86ba8215910117ddb383e4df007b23dcf/research/fiveswap-alt13-commuting-screen/README.md)
at head `139779c86ba8215910117ddb383e4df007b23dcf`, SHA256
`edba3d71ad274311f3a8c2293d390a7adba38deca344662c0364cbdd192521d3`.
The mathematical checker does not depend on this external file or network access.
Publication, overlap coordination and source-retrieval provenance belong to the
parent run; this independent specialist made no remote mutation or Git commit.
