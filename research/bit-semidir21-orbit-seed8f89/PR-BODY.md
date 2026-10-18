## Scope and result

**Exact scoped negative result; no new kappa.** In the formal group algebra `F2[C7 semidirect C3]` on three registers, the target `diag([a],[a^2],[a^4])` has exact paid-call minimum three in the declared alphabet. The alphabet contains every factor `D_N([g]) = I + ([g]+[e])N`, for each nonidentity group element `g` and every rank-one idempotent `N` in `M3(F2)`: 560 operation types total.

The direct three-call word uses `E11`, `E22`, and `E33` at labels `a`, `a^2`, and `a^4`. The exact verifier checks the group law, all 28 idempotents, the direct word, and a positive two-call control. It excludes every one-call and all 313,600 ordered two-call words by coefficientwise equality in the full 21-dimensional group algebra. The pair stream contains 258,581 distinct product matrices and has SHA-256 `c5f116aa86ed6d2cbca21580027b0eab01804cad2ef65a1d1f3917b5df41b00f`.

This changes the address group from the additive abelian model in the retained three-register obstruction. It does not claim a rational-frame realization, an integer-multiplication saving, or a change to the selected result. The complete fresh overlap scan found no other exact order-21 scope. Active [Discussion #1999](https://github.com/CrocSwap/integer-mult-bounds/discussions/1999) separately studies an order-24 `SL2(F3)` group, a mixed three-register target and a four-call threshold; this package fixes the distinct order-21 Frobenius group and conjugacy-orbit target, with all 560 factors and a complete length-two exclusion. Other nearby work uses D10, D16, Q8, D8, S4, UT4, UT5, GL2(F2), or binary-affine objects and distinct endpoints.

## Reproduce

```sh
python3 -I -B research/bit-semidir21-orbit-seed8f89/verify.py
python3 -I -O -B research/bit-semidir21-orbit-seed8f89/verify.py
python3 scripts/research_package.py --package research/bit-semidir21-orbit-seed8f89 --check-only
```

Both exact verifier modes and package metadata/pin checks pass locally. The registered generic runner requests Python 3.12, which is not installed in this environment; direct replay used the installed Python 3.14.7.

## Provenance and limits

- Research assignment: seed `8f89febe96e436a0b664eb258cbb53ec`, `bit-mechanisms / bit-new-register-model`, catalogue revision 3.
- Exact research base: `1c47876ef742ba64bf9140b0527d63acf656a3b4`.
- Publication base: `ec8707299e2f40918f5f96cdab99ee49cdbabcf0`.
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Predecessor: `research/bit-three-register-lower-bound/README.md`, SHA-256 `c12b33ef388deece0cbf891505a2ce2c0779a0c3a6cf1f0f7f7039bab59cbebd`.
- Claimed scope: [Discussion #1167](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18929621).
- No helper, frame, copy, hosting, restoration, precision, or recursive-interface charge is added to this formal call-count model. No mapping to the selected supplier is supplied.

Prepared by OpenAI Codex at Cinna's direction, with substantial AI assistance. No independent human review is claimed. Apache-2.0.
