# Paid bank completion on the 892-pair candidate

Prepared with substantial OpenAI assistance. Apache-2.0; existing repository notices apply.

This is a separate additive experiment on the immutable 1,047-kernel source head `1b37957d1520c80b6ea796bf418e52be5109c2d4`. It preserves the accepted weighted-890 packet and every earlier contribution file. The canonical 892-pair candidate has SHA256 `25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739`.

The new operation completes the final partial bank at each of five stages. After the 60 regular helper sweeps and before the stage boundary, it pays for one rank-49 sweep and one rank-11 sweep on the remaining 60 arbitrary-dirty coordinates. There are ten additional children in total, with no extra factor of 60 and no additional closure assumption.

## Result and scope

The preferred 49+11 split gives the conditional saving parameter κ

`kappa = 770003879871513 / 10^18 = 0.000770003879871513`.

The literal ledger has 658,275 stock families, 15,002,710 calls, rank mass 65,705,100 and deficit 122,400. The maximum rank is 49, so the strict one-level halving guard remains `49 < 50`.

The replay passes 33 regression tests and records 31 deterministic receipt hashes, in addition to the embedded exact and mutation checks. The aggregate distinguishes three kinds of evidence:

1. A universal integer identity completes each bank on arbitrary correlated dirty contents. The retained weighted generic compiler supplies its all-size interpretation.
2. Fresh finite reconstruction checks matching, all 1,047 installed kernels, actual scalar/COPY operands, targets, corrected source geometry, bank addresses, 730 phases, every new completion descriptor and its full invoice. Independent auditors check the emitted operands and boundary records.
3. The full-frame companion reconstructs the final local frame word, screens all 133 reorders, validates all 15,034 used frame bases and their rational G-nondegeneracy, and binds all 300 global frame streams. It materializes and hashes 116,772,900 global frame-tagged records without storing that expanded table in the repository.

The corrected copied-work lowering binds 100 explicit positive-projector overrides. The independent global audit checks the actual rational idempotence and COPY endpoint identities for all 20 center projectors and rejects every negative-direction interpretation. The override and descriptor bytes are included in the program hash.

Generic primitive compilation, uniform admissible-prime supply, the complex/full-C supplier, primitive and leaf constants, precision/recovery, analytic transfer and the all-size theorem remain named inherited interfaces. This packet does not execute the production primitive compiler or prove an unconditional multiplication bound.

The preliminary bank and incremental receipts deliberately report their narrower scope. The aggregate and final independent receipts combine the later evidence; an earlier intermediate open-gate field is not the final gate disposition.

## Corrected source geometry

The supplementary source/target checker covers original pre-descent source frames and final target frames. It does not supply the final descended source chronology by itself. The mandatory `frame/check_descended_sources.py` separately checks all 480 actual rank-18 setups and all 960 final source chains. Its source histogram is `{2: 960, 17: 960}`, with rank mass 18,240. The complete frame constructor and independent validator then verify the actual emitted sequence.

## Reproduce from any working directory

The recorded receipts were generated with Python 3.12.14 and NumPy 2.3.5. Python 3.12 and the NumPy version pinned in `requirements.txt` define the tested replay environment. Assertions must be enabled; all entry points reject optimized Python mode. No upstream program is imported or executed. Source Python files remain hash-checked inert `.py.txt` data.

Set `PACKET` to this directory. Acquire all pinned source bytes from their immutable URLs:

```sh
python "$PACKET/acquire_inputs.py"
python "$PACKET/run_checks.py" --check --tests
```

Alternatively, reuse an existing immutable source cache and choose a fresh output directory:

```sh
P10P_INPUTS=/path/to/source-cache \
P10P_OUTPUT=/path/to/fresh-output \
python "$PACKET/run_checks.py" --check --tests
```

To materialize a new cache from a verified local copy, set `P10P_INPUTS` and call `acquire_inputs.py --from-dir /path/to/source-cache`. Acquisition verifies byte lengths, SHA256 and Git blob identities before accepting any file.

The default cache and outputs are `local-inputs/` and `output/`. Both are ignored by Git. The aggregate also regenerates the necessary old-890 endpoint charts and price from hash-guarded, already published sibling code. `dependencies.json` records that complete authored-code dependency closure. `FILES.json` pins this additive packet, and `expected/receipts.json` binds deterministic receipts. Expected evidence is never replaced by `--check`.

The exact logical receipts are path-independent. Only declared absolute roots are normalized to descriptive placeholders before writing receipts that contain paths; no mathematical fields or dependency hashes are dropped. Expanded binary streams and large tables are runtime products, not committed bulk data.

## Files

- `witnesses/`: compact matching delta, packing pattern and admission summary specification
- `admission/`: independent matching, kernel, scalar, target and reorder checks, plus regression tests
- `bank/`: universal endpoint controls, exact bank assignment, generic local-ring controls, literal moment and all 47 assembly inequalities
- `frame/`: corrected descended source geometry, final local frame constructor and independent rank/containment/operand validator
- `lowering/`: exact added completion emission and full-frame global address binding
- `audit/`: independent integer, ledger, arithmetic, operand, phase and boundary audits
- `PROOF.md`: construction, accounting and remaining hypotheses
- `PROVENANCE.json`: authored source identities and exact portable adaptations

The separately explored 42+18 fallback is not included in this preferred-candidate packet.
