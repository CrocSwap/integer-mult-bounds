# Remove two CNOTs from the selected left binary map

**Exact finite certificate and scoped all-column proof; no new kappa.**
This contribution was produced by Nick Petalas. Apache-2.0.

The left binary map of MOVE24472 has an explicit **25-CNOT word**, improving
the 27-CNOT word recorded by Jerry Chen / CubeJerry in
[PR #7430](https://github.com/CrocSwap/integer-mult-bounds/pull/7430) at
`39b40c465f7636a4bb6d70af28595fe8f70f4f3f`. Its adjacent gates 5 and 6 are
both `x1 ^= x0`; their composition is the identity. The shorter word is
printed and proved in [PROOF.md](PROOF.md).

Its exact matrix has rows `(3,5,9,17,32,65,129,1,256)`. The identity holds
for every positive number f of binary columns and arbitrary payloads,
saving exactly 2f elementary column CNOT calls. Coordinate 8 and untouched
spectators remain fixed. This is the first strict word improvement found;
no shortest-word or additional synthesis claim is made.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/selected-linear-cnot-cancellation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/selected-linear-cnot-cancellation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/selected-linear-cnot-cancellation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/selected-linear-cnot-cancellation --check-source-history
```

Another CPython 3.12 path can replace the local interpreter. Direct replay
prints `PASS_SELECTED_LINEAR_CNOT_CANCELLATION` in a generated JSON receipt
bound to all six package source hashes. It writes nothing. It checks the
new matrix by row addition and the complete new forward/inverse maps by a
separate explicit-coordinate oracle: 512 addresses at f=1 and 262,144 at
f=2. Three malformed implementations are distinguished. No predecessor
executable or scientific suite is run.

## Scope, provenance and overlap

The selected baseline metadata check passed against main
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8, selected
#7000. [SOURCES.json](SOURCES.json) pins that orientation context. The new
word and target matrix are explicit package constants; replay does not
depend on the pending predecessor commit being present in Git history.
The cited source file fixes the comparison and target, rather than acting
as an undeclared executable input.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19571878)
asks for the first shorter word. Live claims, open PRs, account history,
merged CNOT/24472 work and main README searches were checked. No overlapping
shorter word for this matrix was found. These bounded searches do not prove
literature novelty. Classical CNOT cancellation is not a new theorem.

No literal tape graph is changed or executed here. Exact instruction counts,
whole-call staging, owner return, precision and complete MOVE composition
remain separate obligations. No selected frontier, recursive invoice or
five-framework-assumption claim changes. Credit Jerry Chen / CubeJerry's
#7430 and its #3834/#5188/#6992 native/compiler lineage. Independent human
and formal proof-kernel review are unclaimed.

## Code bounds

The checker has no recursion, network, subprocess or filesystem writes.
There are at most 27 gates and nine coordinates; the largest streamed
address domain has 262,144 elements. Only one nine-coordinate input/output
pair is live per iteration. Every function is under 60 physical lines.
Exception-based checks remain enabled under optimization. The source-hash
reader admits six fixed package files of at most 128 KiB each and assumes
the package stays stable during replay. Normal and optimized warning-strict
execution and AST inspection are the local diagnostics.

Power-of-ten rule 3 deviation: CPython allocates integers, tuples and lists
during this offline finite checker. Fixed gate/address/file bounds and a
120-second registered timeout bound its work and live data. A fixed-storage
port is required before use in a steady service. No compiler configuration
or shared verifier code is changed. Build the Lever led to the rerunnable
word certificate; Prove It Works led to the separate complete-address oracle.

## Open next questions

1. Integrate the 25-gate word into #7430's literal compiler and obtain fresh
   graph, full-array and history receipts. First replace only its frozen left
   word and regenerate that graph. The complete literal replay and source
   binder remain the blockers to claiming an instruction-count improvement.
2. Is 25 optimal for this exact matrix? First derive a gate-count lower bound
   or run a separately budgeted bounded synthesis. This package stops at its
   first strict improvement and supplies neither a search nor an optimum.

[TASK.json](TASK.json) records the changed card and structured next questions.
