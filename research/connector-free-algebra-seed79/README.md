# Independent six-source free-algebra replay

This independently verifies Douglas Colkitt’s PR1185 six-source witness using free associative algebra over F2. The 142-query program and recursive expansion satisfy the identity for arbitrary dirty inputs and noncommuting operators. Verification covers 3,832 primitive calls, 284 call boundaries, ten negative controls, and explicit matrix counterexamples. A separate matrix oracle checks the interpreter. The optimality census and physical supplier remain outside scope; no new kappa is claimed. Credit: Ross Richardson’s PR943/PR934 and retained notices. Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.

```sh
python3 -I -O -B research/connector-free-algebra-seed79/verify.py
python3 -I -O -B research/connector-free-algebra-seed79/test_verify.py
```

Expected: `PASS_CONNECTOR_FREE_ALGEBRA queries=142 leaves=3832 rows=73 boundaries=284 controls=10`, then five passing test groups. Python 3.10+; standard library only. No input regeneration or network access is needed.

| Pin | Value |
|---|---|
| Base | `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe` |
| Predecessor | [PR1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185), `4a60772285ce70f6414458f6d3a54948652bbed0` |
| Assignment | Seed 79; independent verification |
| Source contract | Ross Richardson's [PR943 query model](references/PR943-README.md) and [notice](references/PR943-NOTICE.md) |
| Original query word | SHA256 `e589507497ee1a17861933a6a1334dd20a01038fe2989a58415a30a0f8934ccb` |

[FIXTURE.json](FIXTURE.json) freezes all 142 queries and the seed-defined factor lengths, covering lengths 1 through 8. [SOURCES.json](SOURCES.json) binds original reference bytes to SHA256 and Git blob hashes. The verifier never imports or executes predecessor code. Its module docstring states the algebra and substitution argument.

Each output mask receives exactly its ordered `A_i B_j x_j` terms. Every source, the root connector, and all three recursive scratch rows are checked. The same identity holds forward and backward; executing either complete program twice gives identity. All 69 distinct recursive product calls are checked separately, and all 142 call boundaries are checked in both directions.

[EXPECTED.json](EXPECTED.json) records the exact primitive invoice, complete-state trace hashes, and six concrete matrix counterexamples to deliberately mutated programs. In two controls, every output is correct while only `z` or `s2` is wrong. Four further controls reject aliased/insufficient scratch or an unpaid primitive. Package tests add nine corruption controls. A separately implemented dense matrix oracle checks all dirty basis inputs at dimensions 2, 3 and 7 in both directions (1,752 basis cases), including singular and noncommuting maps. Those finite tests support the interpreter; the free-algebra calculation supplies the fixed word's arbitrary-operator identity.

The price recurrence and complete cost contract are:

```text
ell(1) = 1
ell(d) = 2 ell(floor(d/2)) + 2 ell(ceil(d/2))
C(L) <= I + sum_f P_f + D + sum_f m_f c_f(L)
sum_f m_f = 3832; distinct primitive operators = 310
borrowed dirty rows = 1 + ceil(log2(8)) = 4
```

Here `c_f` includes coefficient/source access, target updates, private scratch restoration, frames and head returns. Input admission `I`, reusable coefficient preparation `P_f`, and instruction construction/access/dispatch `D` remain caller charges. This is a verified invocation count under that complete-call contract, not a physical runtime bound or supplier integration. The six-source optimality census, common-label realization, physical hosting, tape/precision/recovery, analytic transfer and full multiplication theorem are not checked.

[CLAIM.json](CLAIM.json) records candidate selection and overlap. [VALIDATION.json](VALIDATION.json) records executed checks. [The predecessor notice](references/PR1185-NOTICE.md) preserves Douglas Colkitt's attribution and disclosed Anthropic Claude assistance; the PR943 notice retains the PR934/PR889/PR628 lineage. New material is Apache-2.0.
