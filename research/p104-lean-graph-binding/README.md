# Packed Lean graph source binding

The packed native recipe in PR #7783 encodes the exact PR #7761 graph.
All 188,425 terms, 1,099 chart spans, public and bank endpoints, and
1,592,644 public matrix coefficients agree. Read [the proof](PROOF.md),
[certificate](RESULT.json), [source pins](SOURCE-PINS.json) and
[credits](CREDITS.md). No new kappa or Lean build is claimed.

Use Python 3.12 and the standard library from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-lean-graph-binding
```

Both modes print this prefix and elapsed seconds:

```text
PASS_P104_LEAN_GRAPH_BINDING 188425 terms 1099 charts 11 controls
```

The checker authenticates 51 source files and runs without network or
Git access. It uses a temporary directory for the retained graph builder.
It does not execute Lean or the original packing generators. Eleven
controls reject altered data after source authentication.

## Open next questions

Do the formal caller lists equal the complete source SPEC invoice?
Compare their exact source values, then state the remaining `Valid`
and realization hypotheses. The present audit covers the native graph
correspondence. It does not recheck the full formal proof, chain
certificates, physical application, caller, ordinary costs or compiler.
