# Orthogonal P120 pencil: one shared total still loses a target diagonal

**Status: scoped negative result. No exact decoder, supplier, or new κ is
claimed.** This seed changes the relative root geometry in the calibrated
two-target shared-total experiment of [PR #1366](https://github.com/CrocSwap/integer-mult-bounds/pull/1366).

## Finding

Using the pinned P120 root/label certificate, seed 48 selects `e = L_48` and
`d0 = L_91`: `d0` is item 49 (zero-based index 48) in the sorted list of 63
roots orthogonal to `e`. Thus `<e,d0> = 0`, while PR #1366's fixed pencil has
`<L_51,L_1> = 2`.

The exact census finds 65 calibrated, nonzero-diagonal row candidates and
2,048 distinct-target pairs. Of those, 1,056 can read the union correction
total at both sinks. Every available pair includes at least one target in the
other row's correction set: 1,024 contaminate both target diagonals and 32
contaminate one. That diagonal is then exactly zero. No pair in this finite
family is an exact decoder.

The geometry change matters because a successful pair would use one rank-one
shared total plus eight rank-eight coordinate totals, an optimistic local bill
of 65 COPY-rank units against the P120 all-pairs floor of 72. The census finds
no such unit. This does not bound other orthogonal pencils, uncalibrated rows,
different total directions, or multiple totals, and it does not change the
selected κ.

## Reproduce

From the repository root, using Python 3.12+ and the standard library:

```sh
python3 -I -B research/seed48-p120-orthogonal-shared-total/verify.py
```

Expected final marker:

```text
PASS_P120_ORTHOGONAL_SHARED_TOTAL: no exact pair in the complete calibrated one-total family; no new kappa
```

The checker validates the pinned root, Gram, and label data; derives the
seed-selected orthogonal pencil; exhausts all 120 targets and 511 nonzero
sink labels; and checks every eligible pair exactly. It also replays PR #1366's
odd-pair obstruction, the P112 C.6 exact positive control, and two negative
controls. See [PROOF.md](PROOF.md) for the diagonal argument and scope.

## Scope

- **This pencil only.** The result is for `e=L_48`, `d0=L_91`, the 120-port
  certificate, rows with one consistent nonempty rational calibrator, and a
  single shared correction total equal to the `d0` direction.
- **No complete supplier claim.** The 65-unit figure is only the favorable
  local COPY bill that this family would have if an exact pair existed. No
  pair exists here, and no recursive profile or κ is derived.

## Open next questions

- **Next question:** does any other orthogonal P120 pencil avoid the
  cross-target diagonal obstruction? A first step is to orbit-classify ordered
  orthogonal pairs under the E8 stabilizer, then replay one representative per
  class. The blocker is a certified orbit reduction and a complete cost
  argument for any surviving pair.
- **Next question:** can two distinct correction totals preserve both target
  diagonals? A first step is to specify their coefficients and source sets and
  derive the exact cost before searching. The blocker is a bound on the number
  and copy rank of those totals.

## Attribution

The P120 root/label table and calibrated row model come from Cinna Davis's
PR #1366 (seed 51). That result covered `e=L_51`, `d0=L_1` with odd inner
product; this note changes to a seed-selected orthogonal pair and uses an
independently written enumerator. Credit PR #968 for the E8 frame-pair geometry
and copy-rank floor, and the `format-limits` C.6 review for the 65-unit
two-target cost convention. This package was prepared with substantial
OpenAI Codex assistance; no independent human review is claimed.
