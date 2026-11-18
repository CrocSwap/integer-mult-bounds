# Universal snapshot bound and the single-row rank limit

Every permitted row order of the fixed fifteen-pivot graph needs at least
1507 snapshot banks. The existing order in
[PR #7724](https://github.com/CrocSwap/integer-mult-bounds/pull/7724)
uses 2106. The global minimum remains in `[1507,2106]`.

The package also proves a method limit: 1507 is the strongest bound from
the maximal universally live set, its rank, full endpoint information
and a separate result bank at any one row anchor. All 7643 anchors are
covered. Improving this bound needs additional facts or coupled boundaries.
This is not a global scheduling optimum or a new kappa.

Read [PROOF.md](PROOF.md), the [24-owner certificate](CERTIFICATE.json),
[RESULT.json](RESULT.json), [verify.py](verify.py) and [CREDITS.md](CREDITS.md).
At row 88772, 24 forced owners carry only 19 independent forms. Five
explicit rational relations and literal birth/use paths prove the defect.
Full output rank forces the remaining information to stay in other banks.

Python 3.12 and its standard library are sufficient:

```sh
python3.12 -B scripts/research_package.py --package research/banked-native-order-lower-bound
```

Both normal and optimized commands print:

```text
PASS_BANKED_NATIVE_ORDER_LOWER_BOUND 1507 <= optimum <= 2106
```

All input copies, immutable token identities, whole-row donor retention,
separate result reservation and common output installation remain required.
The proof does not cover recomputation, in-place writes, merged equal
forms, early output installation or public fields used as working storage.
Source graph and upper-bound engines are shared. All five framework
interfaces remain inherited; no independent human acceptance is claimed.

## Open next questions

See [TASK.json](TASK.json) for structured next steps.

- Use several row boundaries or actual available complementary forms to
  improve the lower bound; a further search in this single-row rank family
  cannot exceed 1507.
- Construct a legal order below 2106, with every donor and terminal lifetime
  checked, to reduce the remaining 599-bank interval from the other side.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
