# Paired-cube and shared-core reproduction

This extension inherits PR #130 at
`6a9970a530119174507904e23592fd59ede19a5d` and gives the conditional saving
`5108289/10000000000 = 5.108289e-4`.

From the repository root with Python 3.11+:

```sh
make paired-cube-verify
```

The selected incremental target uses only the Python standard library.
CI runs it in its own `paired-cube` matrix group. The checks are:

- Rebuild the selected signed H-channel graph from exact zero restrictions of
  the pinned PR #117 positive DAG. Replay the frozen 6,074 carrier arcs,
  coordinate frames, full backward intersections, signed physical mixer,
  center closure and 3,630 rank-18 partial gauges. Independent checks cover
  every scalar coefficient of `H+K+B=I`, the original-source K involution and
  inverse, actual frame containment and reverse target chains.
- Reconstruct the bit subset from the hash-pinned h = 21 word in
  `references/paired-cube/fib-bit-h21/` (PR #97 format and reader) and its
  readout order. Check the retained 7,575 and omitted 1,335 slots, moved zero-frame
  dirty reads, changed first transitions and target subsequences. Unchanged
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
