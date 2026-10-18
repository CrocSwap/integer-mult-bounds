# The two-register D16 central pair requires 16 paid calls

Review: [PR #1821](https://github.com/CrocSwap/integer-mult-bounds/pull/1821). Coordination handoff: [Discussion #1818](https://github.com/CrocSwap/integer-mult-bounds/discussions/1818).

## Result and exact model

Let

```text
D16 = <r,s | r^8 = s^2 = 1, srs = r^-1>,
x = s, y = r s, z = r^4 = (xy)^4.
```

On two arbitrary dirty scalar registers, a paid call is

```text
I + ([g] + 1) N,   g in {x,y},   N = u v^T in M2(F2),   v^T u = 1.
```

All six rank-one idempotents are allowed. A free scalar change can be pushed through a paid factor by conjugating its projector, and conjugation permutes this complete six-projector set. The net free scalar map must be the identity because the target's augmentation is the identity. The desired formal boundary is `diag([z],[z])` in the full group algebra `F2[D16]`.

**The exact minimum is 16 paid calls.** Applying `x,y` four times to each register gives the 16-call upper bound. Exact meet in the middle finds no common state between the identity ball through radius 7 and the target ball through radius 8. The complete layer counts are:

| Radius | Identity ball | Target ball |
|---:|---:|---:|
| 0 | 1 | 1 |
| 1 | 12 | 12 |
| 2 | 80 | 80 |
| 3 | 472 | 472 |
| 4 | 2,465 | 2,465 |
| 5 | 12,476 | 12,476 |
| 6 | 61,828 | 61,828 |
| 7 | 300,168 | 300,168 |
| 8 | — | 1,442,306 |

Each generator is an involution: with `q=[g]+1`, `q^2=0` over `F2` because `g^2=1`; and `N^2=N`, so `(I+qN)^2=I`. Any word of length at most 15 can be split into a prefix of length at most 7 and a suffix of length at most 8. Reversing the suffix from the target would put a state in both complete balls, which do not intersect. Thus no word of at most 15 calls realizes the target, and the direct 16-call word is minimal.

This is a scoped exact word metric result for one nonabelian address group and two registers. It changes the group and target relation from the local D8 two-register result. The live D8 third-register claim #1738 retains D8 and changes the register count; the UT4 root-pair claim #1759 uses another group and endpoint. This package does not resolve either claim.

## Cost and limits

The direct cost is 16 paid calls. For this favorable formal model, helper, frame, copy, restoration, hosting, precision, and recursive-interface expenses are all zero; the search tests whether any paid-call saving exists before those expenses. No implementation mapping this nonabelian address group to the selected integer-multiplication supplier is established. There is no new supplier profile or `kappa` claim, and no conclusion for other groups or register counts.

The exact discovery-order hashes are:

```text
identity radius 7: 627b96d39fe7f2df6c65a9c869ed0e56265509fb32578467e7985a08dcf69c8d
target radius 8:   5aa38a6d28f75bfcfc768b7401d60e5e2935c2cfd48c9ac49c096381d20ce09f
```

The full certificate and source pins are in this directory. Reproduce the independent tuple-state replay with:

```sh
python3 -I -B research/bit-d16-central-pair-seed1f8b/verify.py
python3 scripts/research_package.py --package research/bit-d16-central-pair-seed1f8b --check-only
```

Expected status: `PASS_D16_TWO_REGISTER_MINIMUM`. The independent verifier passed locally under Python 3.14.7. The registered package runner is configured for Python 3.12, which is not installed in this environment; that replay remains unrun here.

## Open next questions

Does the two-register central-involution floor scale with the central word depth in the next generalized dihedral group, `D32`? This could show whether the D16 minimum reflects a reusable structural rule or a single finite case. A feasible first step is to pin the `D32` group and paid labels, derive its 32-call direct target, and search for a one-call saving with an explicit state cap. The larger group algebra may exhaust the exact search budget, and a supplier mapping remains an independent blocker.

## Credit

The exact two-register D8 comparison is preserved in `research/bit-dihedral-commutator/`; its scalar-idempotent normalization follows the retained three-register result and the PR288 lineage. This D16 group table, endpoint, state census, and tuple-state replay are specific to the present package. Prepared by woklerx with substantial OpenAI Codex assistance; no independent human review is claimed. Apache-2.0.
