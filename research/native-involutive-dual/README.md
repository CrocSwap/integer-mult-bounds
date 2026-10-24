# Physical backward involution and dyadic coded caller

No improved κ is proved. This closes the missing backward interface of [PR #4935](https://github.com/CrocSwap/integer-mult-bounds/pull/4935) on the actual 632-input native source and instantiates the [PR #4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933) caller with dyadic involutive codes in both orientations.

The new literal backward word returns `(X,Y,H) -> (X - F^T Y,Y,H)` in the source's conjugated physical frames. It preserves all 408 arbitrary helpers and clears one owned scratch field. Eight rank 1 repairs replace the eight deleted rank 8 centers. Its complete paid profile is `{1:2209,2:412,3:510,4:127,5:40}`, matching the inherited forward word. F is not symmetric: the transpose matters.

CALLER.json emits a typed p16 recipe with 18 repaired FULL calls, all 15 IDLEs and all 15 thin queries. Every local code and its inverse uses only dyadic coefficients: forward F, backward F^T, with each squaring to identity. Compared with the original uncoded caller the recursive change is -144 rank 8 calls +144 rank 1 calls. This invoice belongs to changed coded outputs, so it is not a κ certificate.

There are 194 inserted code evaluations, each using 896 scalar ADDs, 224 monomial field passes and 16 owned CLEARs with eight reusable temporaries. Positive-half postdecoding adds 97 evaluations. These ordinary operations are counted, not declared zero time. The 16 negative-Q output banks remain coded; their decoder, complete recursive admission, precision implementation, stock and outer multiplier remain open. Eliminating division by 13 does not close those obligations.

## Reproduce

Python 3.12 or later, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/native-involutive-dual
python3 -I -O -B research/native-involutive-dual/verify.py
```

Checks cover both directions on all 632 independent input columns, 408 helper endpoints, source/engine hashes, explicit sign and unpaid-raising rejection controls, all 4,096 backward repair columns including phase in a separate sparse interpreter, 224 code basis tests, 112 physical wrapper sets and the inherited 1,024-entry noncommutative controller identity. The scalar word, owned copying and frame transitions are replayed. The large all-width caller is specified by a finite typed recipe, not materialized as a full multiplier. No Lean kernel, independent human review, second full source interpreter, full cold multiplier or hosted CI success is claimed.

The mathematical argument and exact scope are in PROOF.md. ORIGINS.json binds retained bytes to predecessor Git objects. The original canonical boundary metadata inside source words retains its historical invoice; use the profile counted from the literal changed events, not that historical field.

## Open next questions

Can the 16 negative-Q coded outputs be converted or recursively admitted with a favorable full bill? Start with one emitted chronological output/IDLE pair and include every query, helper, scalar pass and restoration. No affordable decoder or closed recursive coded-job family is currently supplied. TASK.json records this obligation.

## Credit

The eight-repair involution is inherited from Rohan Arun #1931 and Ali Romman #1862, ported by Dugongue #4935 through #4929. PR #4933, prepared for Dillon, supplies the real phase-correct normalizers, backward X-only convention, gauge identities and typed caller. The new contribution is the actual repaired backward word, its independent column replay, and the dyadic forward/transpose instantiation of that caller. Credit Cao Yifan's round-three word beyond #4610, Cinna Davis #4694/#4698/#4470, Ryanson Jonathan #4516, zxv, Jacob Alan Sussman and the retained native/compiler/outer lineage. See ATTRIBUTION.md and NOTICE. Prepared by Dugongue with substantial OpenAI Codex assistance from one agent. Apache-2.0.
