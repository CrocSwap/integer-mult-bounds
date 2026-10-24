# One axis splits through the section polynomial at ceiling 9

**Claim type:** the triangle inequality on one axis.
**No new κ.** Each section error and the inverse ceiling stay hypotheses.
The selected record remains `23/10000`.

## Question

#4508 uses three bounds on one axis: `||B|| ≤ 9 p^2`,
`||C|| ≤ 9 p^2 + ε`, and `||B - C|| < 2 ε`, with
`ε = p^6 exp(-p^2)`. The named step is to split `B - C` through the section
polynomial.

## Lemma

Let `B`, `C` and `P` be vectors in a normed space, and let `ε > 0`. Then

```text
B - C = (B - P) + (P - C),
||B - C|| ≤ ||B - P|| + ||P - C||,
||P|| ≤ ||B|| + ||P - B||.
```

If `||B - P|| < ε` and `||C - P|| < ε`, then `||B - C|| < 2 ε`.
If `||B|| ≤ 9 p^2` and `||P - B|| < ε`, then `||P|| < 9 p^2 + ε`.

Thus the pair `(B, P)` meets the difference and approximant hypotheses of
#4508 once the inverse ceiling and one section error are known. The pair of
inverses `(B, C)` meets `||B - C|| < 2 ε` once both are within `ε` of the
same polynomial. The ceiling `||B|| ≤ 9 p^2` is not derived here. The factor
2 is this sum of two errors. HALO's `2g` rectangles remain a volume partition.

## Proof

The first display is the definition of `P`. The norm axioms give the two
inequalities. If `x < ε` and `y < ε`, then `x + y < 2 ε`. The integer shadow
replaces a strict cap `ε` by the previous integer: two copies of `m = 3` sum
to `6`, and `6 < 2 · 4`. The same addition is the factor `1 + 1 = 2`.

The polynomial norm is the second triangle. With ceiling `9` and error `2`,
`|10| ≤ 9 + 2`, while `|10| > 9`. Removing the error from the ceiling fails:
`|12 - 9| = 3` and `|12| > 9 + 1`.

The scalar check `(8 - 5) = (8 - 6) + (6 - 5)` is the one-dimensional case.

## Not covered

- A proof that either section error is below `ε`.
- A proof that the inverse norm is at most `9 p^2`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine-bridge --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine-bridge
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T02:53:38Z and was
that commit.

Overlap snapshot: open PRs fetched 2026-10-22T02:54:05Z (294 records) and
discussions fetched 2026-10-22T02:54:47Z (3383 records). A search for
`ceiling 9`, `9 + 2` and `section polynomial` returned this draft, #4508,
which leaves the split open, and #4490, which is the same split at ceiling
`10 p^2`. The other hits are unrelated row and frame notes. A search miss is
not a novelty certificate. #4508 is the telescope. HALO is the tensor sentence.

## Open next questions

1. **Which of the three hypotheses does a core row past `ceil(p^{48})`
   inherit?** #4491 matches the polynomial row with the within-cell gauge,
   and #4493 gives `U < 9 p^2` as a formula. The first step is to name which
   hypothesis each result supplies and to keep the ideal-gap gauge explicit.

## Credit

- The triangle split at ceiling `10 p^2` is #4490.
- The three axis hypotheses at ceiling `9 p^2` are #4508's.
- The section error `p^6 exp(-p^2)` is the within-cell bound of #4452.
- The written error `g p^{10 g} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
