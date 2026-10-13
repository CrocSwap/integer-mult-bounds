# Validation and handoff

Exact base: `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
Assignment seed 51; recursive-interface track. macOS, Python 3.14.6.
New files are confined to `research/binary-connector-walk/`.

## Reproduction

From the repository root:

```sh
python3 -I -O -B research/binary-connector-walk/verify.py
python3 -I -O -B research/binary-connector-walk/test_package.py
```

Expected:

```text
PASS_BINARY_CONNECTOR_WALK targets=512 dense_cases=23040 controls=11 cycle=18->12 lowered=228->198
PASS_BINARY_CONNECTOR_PACKAGE relocation=1 regeneration=1 corruptions=4
```

The normal isolated interpreter and `-I -O -B` produce the same summary.
`test_package.py` regenerates the entire search in a temporary relocated copy
and requires byte-identical `CERTIFICATE.json`. It then runs the independent
verifier outside the repository and rejects four separately corrupted files:
the witness table, expected result, source hash and retained predecessor source.
The committed package is never rewritten by those tests.

## Completed coverage

- Breadth-first search: all 32,768 states and 196,608 directed edges; queue
  exhausted, all 512 restored product matrices reached. No heuristic cutoff.
- Independent free-algebra replay: all 512 words, all 512 row-star words and all
  512 column-star words; complete seven-array maps and literal inverses.
- Each selected word attains the separately proved per-operator support lower
  bound. Hence every positive fixed operator-price assignment is covered by
  multiplicities, without numerical sampling of prices.
- Dense regression: every input basis column of all seven arrays at L=1,2,3,
  plus deterministic combined dirty inputs (seed 51), totaling 23,040 cases.
  The basis cases include literal inverse checks. These supplement, rather
  than replace, the free-algebra identity and written lower-bound argument.
- The complete heterogeneous 198-leaf expansion is checked independently on
  ten arbitrary initial arrays, including all four dirty borrowed arrays.
- Eleven controls include coherent wrong-word bindings, so accidental metadata
  mismatches do not stand in for mathematical failure detection. Each mutated
  construction is required to fail for its named obligation. The valid but
  longer word fails only optimality; odd-characteristic and nonlinear examples
  demonstrate why the stated interface assumptions are necessary.
- 120 closed-form tape-distance checks verify the literal access invoice,
  including per-query head returns, independently of its trace loop.

The selected-result integrity checker and all five existing
`tests/test_selected_result.py` tests pass. Source-reference SHA256 and Git blob
pins were checked against GitHub's exact PR889 objects. No code, selected
certificate, source archive or file under `upstream/` is modified.

The expensive repository-wide regeneration and selected-supplier cold replay
were not run: this standalone package changes neither generator nor supplier.
No hosted CI success, second-platform pass, delegated independent review,
human review or proof-assistant verification is claimed.

## Overlap and remaining obligations

The initial review covered 713 open PR titles and the exact related heads in
SOURCES.json. The prepublication refresh covered 721 open PRs through #931.
PR889 remains the direct one-source fanout predecessor. PR822 concerns
one-output product-tree storage reuse; PR522 changes a physical coordinate
sector. Newly opened PR929 prices a grouped cyclic inverse with one connector
and rounded complex arithmetic. None of those supplies this 512-pattern binary
multi-input/multi-output table; their claims are not combined into a bound here.
The API returned no pinned coordination issue. The local claim records scope
and the result link.

This remains an abstract, exact binary interface. An actual supplier must
establish common operators, independent immutable sources, compatible frames,
exclusive roles, full charged row volume, and all required physical and analytic
interfaces before using any savings. No new kappa or general circuit optimum
is asserted. The all-size statement proved for the displayed cycle concerns
payload length and exact operators, not the full multiplication reduction.
