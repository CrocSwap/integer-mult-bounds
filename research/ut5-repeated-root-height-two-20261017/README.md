# A repeated-root UT5 target still needs five paid calls

**Exact scoped obstruction; no new κ.** In the full formal group algebra `F2[UT5(Z)]`, the four-role endpoint

```text
diag([g1], [g1], [g2], [g1*g2])
```

has exact minimum paid length five when calls use one of the eight signed simple-root labels and any binary rank-one idempotent on four roles. The direct five-call word is optimal: an odd-length determinant character and a one-call support obstruction leave only length three below five, and a complete exact `960^3` join finds no three-call word.

This answers one concrete open next question from the completed [four-role UT5 result](../ut5-four-role-mixed-root-seede2a8/README.md), merged as [PR #2103](https://github.com/CrocSwap/integer-mult-bounds/pull/2103) from Discussion #2094. That package asked whether a target with repeated simple-root outputs and a height-two output could share calls. This first fixed target cannot. The present result does not rule out sharing for another target or another alphabet.

## Model and result

There are four arbitrary dirty scalar roles. A paid call is

```text
D_N(g) = I + ([g] + [1]) N,
```

with `g ∈ {g1,g1^-1,...,g4,g4^-1}` and `N=xy^T`, `x,y ∈ F2^4\{0}`, `y^T x=1`. Every call costs one; no free address map, clean role, copy, erase, or restoration is supplied. Equality is full coefficientwise equality in `Mat4(F2[UT5(Z)])`.

The direct word is `D_E11(g1) D_E22(g1) D_E33(g2) D_E44(g1) D_E44(g2)`, costing five. The complete lower-bound argument and exact search construction are in [PROOF.md](PROOF.md). The deterministic search receipt is [RESULT.json](RESULT.json).

## Verification

From the repository root, with Python 3.12 and the standard library:

```sh
python3 scripts/research_package.py --package research/ut5-repeated-root-height-two-20261017 --check-only
python3.12 scripts/research_package.py --package research/ut5-repeated-root-height-two-20261017
```

The first command validates package metadata and source pins. The second runs the exact verifier, which rechecks the direct word, character and support controls, every ordered prefix pair, all right-factor queries and full-algebra query multiplication, tiny formula controls, and deterministic receipt. A successful metadata check is not a mathematical acceptance decision.

## Prior work and overlap

The task was checked against the three-register abelian theorem, the fully replayed two-role GL3 census and bounded third-role probe in [PR #1974](https://github.com/CrocSwap/integer-mult-bounds/pull/1974), the mixed UT4 tariffs with restored dirty workspace in [PR #2027](https://github.com/CrocSwap/integer-mult-bounds/pull/2027), and the adjacent UT5(Z) target from [PR #2103](https://github.com/CrocSwap/integer-mult-bounds/pull/2103), whose claim was tracked in [Discussion #2094](https://github.com/CrocSwap/integer-mult-bounds/discussions/2094). Those results use different role counts, target families, or address algebras. The current open-PR title/body scan found no matching exact endpoint; the targeted discussion search matched the predecessor task and no later claim for this endpoint. These searches are overlap checks, not a proof of novelty.

The selected record remains κ = 0.001672660197076918; current priority revision 6 says the complex side binds. This bit-model result adds no supplier, hosted-cost, all-size, precision, recovery, or analytic transfer. It proves no selected exponent change and no universal call lower bound.

## Open next questions

- **Other targets:** Does another four-role diagonal UT5(Z) target admit a saving? This result is target-specific. First derive its character and support constraints, then state a complete finite alphabet and stopping bound before searching.
- **Supplier relevance:** Can a concrete integer-multiplication supplier implement any of these formal calls at lower complete cost? First name one native interface and charge address preparation, copies, restoration, hosting, precision, and recursive children. No such transfer is established here.

## Credit

The UT5(Z) operation model and pinned exact-arithmetic helpers come from the predecessor package linked above. This package adds the repeated-root endpoint, its exact five-call minimum, and the complete short-word exclusion. Prepared with substantial OpenAI Codex assistance; no independent human review or proof-assistant verification is claimed. Apache-2.0.
