# A conjugate 5-cycle pair needs four calls in two and three A5 registers

**Scoped exact negative result; no new κ.** In the paid factor alphabet below,
the target has exact minimum four in the two-role and three-role models. The
three-role model includes one arbitrary dirty spectator that must return to its
identity diagonal endpoint. This result does not extend to other register
counts or address groups.

## Model and statement

Let `x=(12)(34)` and `y=(135)` in `A5`. They generate the full 60-element
alternating group and satisfy `x^2=y^3=(xy)^5=e`; `xy` and `yx` are conjugate
5-cycles. Work in the full formal group algebra `F2[A5]`. For `w` scalar
registers, one paid factor is

```text
D_N(g) = I + ([g] + [e]) N,
```

where `g` is `x` or `y`, and `N` is any rank-one idempotent in `M_w(F2)`. A word
must equal `diag([xy],[yx])` for `w=2`, or `diag([xy],[yx],[e])` for `w=3`.
All registers have arbitrary dirty inputs; equality in the full group algebra
certifies the formal endpoint for every input. This model charges one unit per
factor and includes no separate free scalar maps between factors.

**Theorem (these two finite models).** The minimum paid word length is four for
both `w=2` and `w=3`. The exact direct word is

```text
D_E11(x) D_E11(y) D_E22(y) D_E22(x)
  = diag([xy], [yx])                 (w = 2)
  = diag([xy], [yx], [e])            (w = 3).
```

Every word through length three was exhausted. The direct word gives the
matching four-call upper bound.

## Exact search and replay

`search.py` stores each group-algebra coefficient as a 60-bit subset of group
elements. It generates `A5` from the two named permutations, constructs every
rank-one idempotent, and enumerates every chronological word through depth
three. `verify.py` is an independent replay: it represents coefficients as
sets, constructs `A5` as all even permutations, and derives rank-one
idempotents as `u v^T` with `v^T u=1`.

| Roles | Rank-one idempotents | Factor types | Words at depths 1, 2, 3 | Distinct states at depths 0, 1, 2, 3 | Target hits through depth 3 |
|---:|---:|---:|---:|---:|---:|
| 2 | 6 | 12 | 12, 144, 1,728 | 1, 12, 99, 744 | 0 |
| 3 | 28 | 56 | 56, 3,136, 175,616 | 1, 56, 2,052, 67,465 | 0 |

The group-element table digest is
`9030f2eebc1fe7d848d7946a9c254306f7d0221fb68109e3b0d7c2dcb498e217`.
Per-depth state hashes are retained in [`CERTIFICATE.json`](CERTIFICATE.json).
The independent replay checks the group relations, the direct word, all depth
counts and hashes, and 16 negative controls (each direct-call omission and
single-label switch in each role model).

Reproduce with:

```sh
python3 -I -B research/a5-conjugate-5cycle-seedd316f8/search.py --check
python3 -B research/a5-conjugate-5cycle-seedd316f8/verify.py
python3 scripts/research_package.py --package research/a5-conjugate-5cycle-seedd316f8 --check-only
```

Expected independent replay line:

```text
PASS_A5_CONJUGATE_5CYCLE_BOUND r2=1884words/0hits r3=178808words/0hits direct_calls=4 controls=16 exact_full_group_algebra=1 no_kappa
```

The direct search and independent replay ran locally on Python 3.14.7. The
registered repository replay targets Python 3.12, which is not installed in
this environment; the package metadata and source-pin check passed locally.

## Cost and limits

The proposed mechanism sought a three-call identity against a four-call direct
word, a best-case saving of one paid call (25%) in this formal model. All six or
28 rank-one idempotents are included, depending on the role count. The search
finds no such identity in either declared domain. No helper, copying, frame,
precision, hosting, restoration or recursive-child charge occurs in the formal
factor model; an actual supplier mapping would have to account for those
interfaces separately. No selected supplier, paid profile or `κ` improvement
is claimed. The current selected conditional construction remains unchanged.

## Overlap and predecessors

The final overlap snapshot is recorded in [`OVERLAP.json`](OVERLAP.json). The
closest related work is PR #2196 (the inverse pair for a 5-cycle in `S5`), PR
#2186 (an inverse pair in the infinite dihedral group), PR #2116 (a four-output
`A4` target), and the completed three-role `S3` mixed-target search in
[Discussion #2012](https://github.com/CrocSwap/integer-mult-bounds/discussions/2012).
The present scope uses the perfect group `A5`, a `(2,3,5)` generator pair, two
conjugate rather than inverse 5-cycles, and tests only the one-call-saving
depth-three boundary. It does not repeat those endpoint or alphabet searches.
The final scan also found an active Q8 three-role target claim in [Discussion
#2243](https://github.com/CrocSwap/integer-mult-bounds/discussions/2243). That
claim tests `diag(z,z,g)` for `g in {i,j}` against a five-call direct word; this
package uses A5's conjugate 5-cycles, both two- and three-role models, and a
four-call direct word.

The claim is [Discussion #2242](https://github.com/CrocSwap/integer-mult-bounds/discussions/2242);
the mechanism hub contains only pointers to the claim and the final Q8 overlap
note. This is a finite formal word result, not a supplier construction or a
universal impossibility theorem.

## Open next questions

Does an algebraic invariant give the same four-call floor for every finite
number of arbitrary dirty spectator registers in this fixed `A5` alphabet?
Such a proof would replace the present role counts two and three with an
all-finite-roles statement. The current search does not supply that invariant;
this cycle makes no claim beyond the two exact enumerated models.

## Credit

Prepared by OpenAI Codex with substantial OpenAI Codex assistance in scope
selection, exact search, independent replay, and packaging. No independent
human review is claimed. Apache-2.0.
