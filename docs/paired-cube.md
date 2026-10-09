# Paired-cube and shared-core reproduction

This extension inherits PR #130 at
`6a9970a530119174507904e23592fd59ede19a5d` and gives the conditional saving
`6489120/10000000000 = 6.489120e-4`. The complex word adds physical frame descent and compensated late-read
reuse (`scripts/paired_cube_physical.py`); the bit supplier is the paired-cube bit word in
`research/paired-cube-bit`.

From the repository root with Python 3.11+:

```sh
make paired-cube-verify
```

The selected incremental target uses only the Python standard library.
CI runs it in its own `paired-cube` matrix group. The checks are:

- Rebuild the selected signed H-channel graph (p = 11) from the pinned annealed triple, pair and all-but-one
  modules and the L1 local circuit in `references/paired-cube/sources`, with fused face-2/edge-02/edge-12 outputs.
  Replay the frozen 10,237 carrier arcs (compiled under #162's closure conditions),
  coordinate frames, full backward intersections, signed physical mixer,
  center closure and 2,310 rank-18 partial gauges. Independent checks cover
  every scalar coefficient of `H+K+B=I`, the original-source K involution and
  inverse, actual frame containment and reverse target chains.
- Apply the frozen physical frames and late-read reuse pairs and check chains,
  chronology, target order and an aliased dirty-scratch replay
  (`scripts/paired_cube_physical.py`), then the terminal sinks and their gate
  (`research/terminal-sinks/sinks_gate.py`): sink conditions, nested literal stage words forward and reflected,
  a dirty-scratch replay and four controls.
- Check the paired-cube bit word with its standalone checker
  (`research/paired-cube-bit/check_paired_cube_bit.py`): exact frames, decoder
  identity, chains, partner-pair chronology, nondegeneracy, F2 replay and
  ledger. `python3 research/paired-cube-bit/paired_cube_bit_word.py --p 12 --check`
  regenerates its outputs byte for byte. Apply the frozen physical bit word in
  `references/paired-cube/bit-physical` and check it with `scripts/paired_cube_bit_physical.py`: register
  contents, frames, spliced chains, pair chronology, target order and an aliased F2 replay with controls.
- Rebuild both shared-core child lists and certify strict moments, full
  rare-class fallback, stopped bit saving, actual finite group/router charge,
  semantic guard, row stock, 47 strict inequalities and seven assembly margins.

For arithmetic and the selected bit reconstruction alone:

```sh
make paired-cube-certificate
```

The new [proof](../notes/paired-cube-note.tex) supplies the original-source
schedule, complete dirty cores, orthogonal sharing and paid final corrections.
The completed core excludes the old independent-bank exterior tail; replacing
that tail is justified by the exact core operator, not by subtracting a rank
histogram term. The general Clifford, uniform weighted bit and restored-row
proofs from PR #130 are retained.

The complex cover is specified mathematically and not materialized by the
verifier. Its full group order and finite routing allowance remain in the
certificate. The new signed dirty-response matrix is charged by a numerator
bitlength bound and binary expansion, without a positivity assumption.
Finite checks do not formalize the all-size analytic/tape theorem.

To save a compact report and retain generated local files outside the repo:

```sh
python3 scripts/paired_cube_producer.py --output /tmp/paired-cube-verification.json --work-dir /tmp/paired-cube-work
```

The compatible matching is frozen because different maximum-matching
implementations may choose different optima. No SciPy dependency or matching
optimality claim is needed. Only compact arcs, source pins and generators are
submitted; raw graph/frame dumps and unselected research are excluded.

The contribution map in `SOURCES.json` and `NOTICE` explicitly credits an664's
PR #128 sharing principle, eumemic's PR #117 DAG and the PR #97 / Swapnil word.
Their source-specific legal and assistance notices remain unchanged. Proof
sources are included without a PDF.

## Shared source bindings

The final `Makefile`, `README.md` and `NOTICE` changes also update the inherited
joint-dual manifest. Explicitly refresh its hashes, regenerate joint arithmetic
and update the validation receipt's certificate digest. Its mathematical
fields and previous complete replay payload must remain equal when their
producer/verifier inputs are unchanged. The complete affected replay command,
when needed, is `make verify-joint`.

Stage the final artifacts before the deterministic certificate regeneration
and require `git diff --exit-code` to remain clean. CI checks the committed
hashes and never silently refreshes source pins.
