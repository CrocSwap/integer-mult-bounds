# Q8 mixed targets retain the four-call direct tariff through one extra dirty role

**Exact finite group-algebra obstruction; no new κ.** In the specified `F2[Q8]`
register model, the 36 mixed target triples below need four paid rank-one calls
both with three roles and with one additional arbitrary dirty identity-target
role. The exact search rules out a three-call shortcut. This does not exclude
other Q8 targets, more roles for the 12 `-1` cases, another operation
alphabet, or a physical bit supplier improvement.

## Model and target family

Write

\[
Q_8=\{\pm1,\pm i,\pm j,\pm k\},\qquad i^2=j^2=-1,
\quad ij=k,\quad ji=-k.
\]
All equality is in the formal group algebra over `F2`, with one basis symbol
`[g]` for each of the eight group elements. For `r=3` or `r=4`, one paid call
is

\[
D_N(g)=I+([g]+[1])N,\qquad g\in\{i,j\},\qquad N=uv^T,
\quad v^Tu=1,
\]
where `u,v` are nonzero binary `r`-vectors. Thus `N` is a rank-one
idempotent. Every register input is arbitrary dirty data; the required exact
boundary is `diag([g1],[g2],[g3])` for `r=3` and
`diag([g1],[g2],[g3],[1])` for `r=4`.

The endpoint family is all 36 ordered triples in which one target lies in
`{-1,k,-k}` and the other two independently lie in `{i,j}`. The positive
`{i,j}` word-length profile is `(2,1,1)`, so every endpoint has a four-call
direct construction. The illustrative member is `diag([i],[j],[k])`.
`EXPECTED.json` lists and hashes the complete family.

The paid-factor counts are complete: `(2^r-1)2^(r-1)` binary rank-one
idempotents, times two labels, giving 56 factors at `r=3` and 240 at `r=4`.
A three-call witness would save one paid call (25%) in this local unit-cost
model. The extra fourth role is explicitly arbitrary and must return through an
identity target. Its storage and any physical hosting cost are outside this
formal call count.

The model allows free scalar `GL_r(F2)` basis changes. They do not enlarge
this enumeration: conjugating a paid factor sends `N` to another rank-one
idempotent in the listed complete alphabet. Under augmentation `[g] -> 1`,
each paid factor becomes `I` and the required diagonal target becomes `I`, so
any remaining terminal scalar basis map is forced to be the identity.

## Exact result

No endpoint in the 36-member family is reachable with zero, one, two, or three
paid factors, either at `r=3` or at `r=4`. Since every endpoint has a verified
direct four-call word, the minimum is exactly four in these two finite models.

For the 24 tuples whose length-two entry is `k` or `-k`, there is also a
uniform lower bound for every finite register count `r >= 3`. Let `J_Q` be
the augmentation ideal of `F2[Q8]`. The quotient by the commutator subgroup
`{1,-1}` is `C2 x C2`; in its group algebra the augmentation ideal modulo its
square has basis `x=[i]+[1]`, `y=[j]+[1]`. Modulo `J_Q^2`, an `i`-label call
contributes `xN`, a `j`-label call contributes `yN`, and a target entry `k` or
`-k` contributes both `x` and `y`. Let `n_i,n_j` count the two other target
entries equal to `i,j`; then `n_i+n_j=2`, and the diagonal coefficient
matrices of `x,y` have ranks `1+n_i` and `1+n_j`. If a word uses `q_i`
`i`-calls and `q_j` `j`-calls, these matrices are sums of at most `q_i` or
`q_j` rank-one matrices. Thus `q_i+q_j >= (1+n_i)+(1+n_j)=4`; four calls are
necessary for every tuple in this subfamily, including the repeated-`i` and
repeated-`j` cases. The direct word meets the bound.

For the remaining 12 tuples, the length-two target is `-1`. It is killed by
the abelianization, so the two first-order coefficient ranks are `n_i,n_j`
with `n_i+n_j=2`; this does not rule out a three-call word. The exact search
supplies the additional, scoped result: these 12 tuples have minimum four at
`r=3` and `r=4`. It does not settle them for arbitrary extra roles.

The verifier stores each group-algebra coefficient array as an eight-bit mask.
For a state matrix `M`, it applies the exact right update
`M <- M D_N(g)` by multiplying each selected row entry by `[g]+[1]` and
forming the rank-one outer-product update. Equal states at depths one and two
are merged; all suffix transitions are deterministic, so this preserves the
complete reachable set. Every depth-three extension of every distinct
depth-two state is then checked against all target matrices.

| Roles | Rank-one idempotents | Paid factors | Distinct depth-1 states | Distinct depth-2 states | Depth-3 transitions checked | Target hits through depth 3 |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 28 | 56 | 56 | 2,324 | 130,144 | 0 |
| 4 | 120 | 240 | 240 | 41,800 | 10,032,000 | 0 |

The two-call target `diag([i],[j],[1],...)` is a positive control for the
state search. Every family member is replayed through its direct four-call
word. The verifier also rejects a direct word with its last call dropped and
confirms that replacing the illustrative `k` target by `-k` changes the exact
boundary. The 36 target tuples partition into 24 `k/-k` cases covered by the
uniform first-order rank argument and 12 `-1` cases covered by finite search
through `r=4`.

## Why this is a scoped negative result

Navinor's PR #1822 (head `ee736b4b11bbd63b04d94c8edafb3790161ebdea`) studies
two roles with the repeated central commutator `diag([xyxy],[xyxy])` over Q8.
This package changes to three mixed generator/product targets, then
adds one arbitrary identity-target role as a single bounded pivot. No
predecessor code is imported. The final overlap snapshot at
2026-10-14T13:57:45Z covered 573 open PRs and 542 Discussion records with
complete pagination and no warnings. The scanner found this cycle's own
Discussion #1167 claim, PR #1822's two-role repeated central commutator, and
other bit-mechanism records, but no remote same-scope claim. The current
four-register AGL2 mixed-target claim in Discussion #1727, the UT4 claim in
Discussion #1759, the D16 claim in Discussion #1818, and the AGL2 results
PR #1716/#1763 and Discussion #1774 have different groups or target families.

The current selected construction remains conditional finite, complex-binding
at `836330098538459/500000000000000000`. Its review, selected-source manifest,
assembly certificate, and reproduction target are pinned in
[SOURCES.json](SOURCES.json). The selected bit supplier is not changed here.
The current review is
[`community-batch1099-review.md`](../../docs/research/community-batch1099-review.md);
the source manifest is
[`SELECTED-SOURCE.json`](../community-frontier1094-audit/SELECTED-SOURCE.json),
and the assembly certificate is
[`ASSEMBLY.json`](../community-frontier1094-audit/ASSEMBLY.json), SHA-256
`1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`. Its
pinned reproduction remains `make frontier1094-verify`; it was not rerun because
this package changes none of its inputs.
The binding-only baseline `python3 -B scripts/research_baseline.py` passed at
the pinned base and reported `binding_primitive=complex`; that is not a full
selected-assembly replay.
There is no κ gain, complete multiplication theorem, or supplier placement
claim. No rank savings in this finite family does not imply a universal
no-sharing theorem.

## Reproduce

From the repository root:

```sh
python3 -I -B research/q8-mixed-three-register-seedcbd5ebc4/verify.py
python3 -B scripts/research_package.py --package research/q8-mixed-three-register-seedcbd5ebc4 --check-only
```

The exact search is standard-library Python and uses the formal eight-element
Q8 table, not a natural matrix representation. The run in this environment used
CPython 3.14.7; the registered package runner specifies Python 3.12. The
selected assembly was not rerun because no selected input changed.

## Open next questions

Can the 12 central `-1` target triples be proved to need four calls for every
finite number of dirty roles, rather than only for `r=3,4`? A uniform
second-order augmentation invariant would extend the finite obstruction.
First derive the coefficient constraints in `J_Q^2/J_Q^3` while retaining the
rank-one idempotent relations; the current first-order quotient is too weak.
This is a new domain requiring its own overlap check. Neither result
establishes physical supplier realization, and the selected complex-side
moment remains binding.

## Attribution

The Q8 register model and central-commutator predecessor are from the authors
of PR #1822; the earlier rank-one formal-frame lineage is summarized in the
pinned predecessor package. This work adds no imported code and makes no
priority claim about broader group-algebra register models. Prepared by Cinna
Davis with substantial OpenAI Codex assistance. New work is Apache-2.0.
