# A common image or kernel line cannot build the diagonal pair

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

Scoped written proof with exact finite corroboration. No new kappa, no native
supplier, no selected-frontier change.

## Result

Work in the rank-one-idempotent register model of Wentao Li's #4089, as used by
Nick Petalas's #6038, Josie Elliston's #6048 and JoyboyBrian's #6097. Fix a
field `F`, a group `G`, a label set `L`, and write `[g]` for the basis element of
`F[G]`. A call is

    D_N(g) = (I - N) + [g] N,        g in L,

where `N` is a rank-one idempotent `2 x 2` matrix over `F`.

**Theorem 1 (line exclusion).** Let `N_1, ..., N_k` be rank-one idempotents that
share a common image line, or share a common kernel line. Then for every labels
`g_1, ..., g_k`, no product `D_{N_1}(g_1) ... D_{N_k}(g_k)` equals
`diag([a],[b])` with `a != e != b`. This holds for every `k >= 0`, every field,
and every group.

**Corollary 1.1 (necessary line separation).** If a product of `k` calls equals
`diag([a],[b])` with `a != b` and neither `a` nor `b` a product of at most two
labels, then the projector list contains two projectors with distinct image
lines and two projectors with distinct kernel lines. In particular no family
with a single image line, a single kernel line, or one repeated projector
attains the pair at any length.

**Theorem 2 (two calls never suffice).** Over every field and every group, no
product of at most two calls equals `diag([a],[b])` when `a != b` and neither
`a` nor `b` is a product of at most two labels. Without that length hypothesis
two calls do suffice: `D_{E00}(x) D_{E11}(y) = diag([x],[y])`.

Theorem 1 is written out in [PROOF.md](PROOF.md). Theorem 2 is a short
normalisation argument in the same file; it is *not* machine-checked, and it is
labelled as a written step.

## Why it matters for the open field question

JoyboyBrian's #6097 proves the six-call floor over `F2` at width two and leaves
the field extension open: its stored second next question asks whether the floor
extends to odd characteristic or `F4`, with the blocker "even pairing is specific
to `F2`". That question is the one answered here only in part: Theorem 1 removes
a whole family of candidate counterexamples at every length and field, and
Theorem 2 removes lengths zero, one and two. The general `F4` and odd
characteristic floor stays open, and no claim about it is made.

Theorem 1 composes with the existing symmetry reduction rather than replacing
it. Nick Petalas's #6609 counts `267,072` representatives of the `3,200,000`
five-call `F4` projector tuples and `1,520,110` of the `24,300,000` `F5` tuples
under simultaneous monomial conjugation and reversal with transpose. Every
remaining representative of a completing word must carry two image lines and
two kernel lines.

## Evidence

`verify.py`, standard library only, checks by exact integer and finite-field
arithmetic:

1. the rank-one idempotent inventories `q(q+1)` for `q = 2,3,4,5`, namely
   `6, 12, 20, 30`;
2. `N_i N_j = N_j` for every ordered pair with a common image line, and
   `N_i N_j = N_i` for every ordered pair with a common kernel line;
3. the subset collapse `P_U = N_{max U}` and `P_U = N_{min U}` for every subset
   of every enumerated same-line tuple;
4. the vanishing of the determinant of `P - I`, computed by exact expansion in
   the group algebra of the free abelian group on the call positions, for every
   enumerated same-line tuple over `F2`, `F3`, `F4` and `F5` at the lengths
   recorded in the run line (`5` for `F2`, `F3`; `4` for `F4`, `F5`);
5. the positive control that the six-call `F2` word has a nonzero minor, and the
   negative control that mixing image lines can produce a nonzero minor.

The enumeration is finite corroboration of a written argument, not a
replacement for it. It is not a census of all projector tuples, and it says
nothing about tuples outside the same-line families.

## Reproduce

From the repository root, with the interpreter used for this package:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/diagonal-pair-line-separation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B research/diagonal-pair-line-separation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/diagonal-pair-line-separation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/diagonal-pair-line-separation --check-source-history
```

Any CPython 3.12 installation may replace the displayed path. The first two
commands print one line beginning `PASS_DIAGONAL_PAIR_LINE_SEPARATION`. Checks
raise explicit exceptions, so `-O` does not disable them.

## Credit

JoyboyBrian's #6097 supplies the width-two `F2` six-call floor, the six-projector
inventory, the collision relaxation and the six-call word; its stored next
question is the source of this target. Josie Elliston's #6048 and #6137 supply
the four-call floor and the width-two framing. Wentao Li's #4089 introduces the
register model. Nick Petalas's #6038 supplies the earlier four-call `xy`/`yx`
result, and #6609 supplies the related symmetry reduction, which is cited as
related work and is not used as a step here. No predecessor executable is
imported or run.

## Limits

- Theorems 1 and 2 only. The `F4`, `F5`, odd-characteristic and larger-width
  six-call floors remain open.
- Theorem 1 excludes same-line families. It does not bound tuples with two or
  more image lines, which is where a counterexample must live.
- The finite enumeration corroborates the collapse and the minor identity; it is
  not a proof kernel and not a complete tuple census.
- No native tariff, supplier or multiplication bound is inferred.

## Open next questions

1. Does the six-call floor hold over `F4`? The remaining search is the `267,072`
   representatives of #6609 restricted to tuples with at least two image and two
   kernel lines. Smallest useful step: run that restricted search at length five
   with the coefficient-class relaxation of #6097.
2. Same for `F5` and for odd characteristic generally, where `#6097`'s even
   pairing has no direct analogue.
3. Widths above two: does the `2 x 2` line-exclusion argument extend to rank-one
   idempotents in `M_d(F)`, where the collapse `N_i N_j = N_j` still holds for a
   common image line but the target is a `d`-fold diagonal?
