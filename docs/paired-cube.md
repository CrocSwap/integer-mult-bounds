# Paired-cube and shared-core reproduction

This extension inherits PR #130 at
`6a9970a530119174507904e23592fd59ede19a5d` (and extends PR #144 at
`c8b22bc5c10dba497ac25804e27d9647d818e2ff` with the exact globally optimal
PR #97 bit gauge subset) and gives the conditional saving
`461028508707/1000000000000000 = 4.61028508707e-4`.

From the repository root with Python 3.11+:

```sh
make paired-cube-verify
```

The selected incremental target uses only the Python standard library.
CI runs it in its own `paired-cube` matrix group. The checks are:

- Rebuild the selected signed H-channel graph from exact zero restrictions of
  the pinned PR #117 positive DAG. Replay the frozen 6,074 carrier arcs,
  coordinate frames, full backward intersections, signed physical mixer,
  center closure and 4,840 rank-20 partial gauges. Independent checks cover
  every scalar coefficient of `H+K+B=I`, the original-source K involution and
  inverse, actual frame containment and reverse target chains.
- Reconstruct the bit subset from the existing PR #97 witness and readout
  order. Check the retained 9,730 and omitted 1,835 slots, moved zero-frame
  dirty reads, changed first transitions, target subsequences and exact
  integer max-flow/min-cut duality on the 36,760-vertex telescoping interval
  network certifying global optimality over all $2^{11565}$ subsets. Unchanged
  complete-basis and rational-frame suites remain inherited checks.
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

The contribution map in `SOURCES.json` and `NOTICE` explicitly credits
icekylinx's PR #144 paired-cube/shared-core construction, an664's PR #128
sharing principle, eumemic's PR #117 DAG, the PR #97 / Swapnil word, and
Thomas Marchand's exact telescoping interval-min-cut bit subset optimization.
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
