# Independent free-algebra replay of #4534's noncommuting p16 identity

**Claim type:** an independent exact replay by separately written code. **No new κ.** It covers the
noncommuting-stage theorem in Dugongue's [#4534](https://github.com/CrocSwap/integer-mult-bounds/pull/4534)
(head `90505ab1`, `research/frame-aware-native/noncommuting-controller`). That theorem says #4470's p16
controller stays exactly diagonalizable when the stage operators `D_s` need not commute with each other, as
long as each commutes with the central query `Q`. This extends my commutative Laurent replay in #4516 to
ordered words.

## What is checked

The inputs are #4470's `CONTROLLER.json` on main and #4534's `FREE-CERTIFICATE.json`, vendored with its
SHA256 pinned. Each of the 32 lines is replayed with coefficients in the free algebra `ℚ⟨d_s⟩[q, q^{−1}]`,
with `q` central. A monomial is a pair: a `q` exponent and an **ordered** tuple of stage letters, and a
later operator is prepended on the left.

| Event | Effect |
| --- | --- |
| `LOCAL` | the shear (`y += q^{−1}x`, or `y −= q·x` backward), then left-multiplication of both lines by `d_stage` |
| `QUERY_SHEAR` | the shear alone |
| `IDLE` on ascending stages `s_1 < … < s_k` | left-multiplication by `d_{s_k}⋯d_{s_1}` |
| `ADD`, `SIGNED_SWAP` | literal |

Results:

1. **The identity.** `L·W·R = diag(q^{ε_i} d_{w_i})` holds in **all 1,024 matrix entries**, coefficient by
   coefficient over ordered words, with the certificate's rational `L`, `R` and diagonal.
2. **Chronology matters.** Reversing every idle word breaks 212 entries. A commutative replay could not
   detect this.
3. **Structure.** There are 16 central exponents `+1` and 16 `−1`. The longest word is
   `G = (32, 31, 29, …, 3, 1, 0)`, and the other 15 nonempty words are each a contiguous prefix or suffix
   of `G`.
4. **The boundaries.** `L` and `R` are invertible, and they and their inverses have only dyadic entries,
   consistent with #4534's dyadic scalar programs.

## Not covered

- #4534's monomial adapters, owned-response retiming and lazy-response tools.
- The physical realization of any noncommuting `D_s`.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/free-controller-replay --check-only
python3.12 -B scripts/research_package.py --package research/free-controller-replay
```

The verifier prints `PASS_FREE_CONTROLLER_REPLAY` in about a second, using only the standard library.

## Open next questions

1. **#4534's open question 2: an all-`p` free-algebra identity.**
   - *First step:* replay the same constructor at `p = 4, 8, 12` in the free algebra, and look for the
     inductive pattern of `L` and `R`.

## Credit

- The theorem and the certificate are Dugongue's (#4534).
- The p16 word is Cinna Davis's (1337isnot1337, #4470).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
