# Uniform sequential-arena Beneš component

This audits the numerical compiler component in Cinna Davis's PR4100
`CRT.md:94–116`, using the exact retained `benes` implementation.
The original cycle compiler and proposed full-scan simulation are
predecessor work. The new result is an explicit uniform arena schedule,
owned-output cleanup, quantified lowering and executed traffic model.
No new kappa or complete multiplication theorem is claimed.

For an encoded permutation on `N=2^h` wires, `1<=h<=p`, the component
returns the exact source's layer-major Boolean tables while preserving
the input. It flattens the recursion tree, uses an encoded LIFO stack
for cycle coloring, and reads/writes each logical array entry by a
**complete sequential arena scan and head return**. One key tape is
reused throughout. No tape is allocated per node or query.

[PROOF.md](PROOF.md) derives `O(N³(p+2)^7)` time and `O(N(p+2)^3)`
visited space with a fixed alphabet/tape inventory. Both source and
owned output are included. A protected-network query returns an owned
bit after a complete scan. For `h<=ell<=p`, even O(p) component calls
fit the source's generous `O(2^(4ell)(p+2)^16)` allowance.

The executed simulator charges arena/key tape read/write/head traffic.
It batches contiguous one-cell moves with exact action counts and
cross-checks an expanded one-cell run. Python integers mirror bounded
scalar registers; their uniform bit lowering, all loop/index arithmetic
and parameter reads are charged in the **written proof**. This is not
an executed complete finite-state transition-table certificate.

## Evidence and replay

[RESULT.json](RESULT.json) records 49 finite cases: all 26 permutations
on two/four wires, 20 modular rotations, and two other eight-wire
permutations, plus one larger-p word-width case. Each encoded table matches the retained compiler
exactly; every queried control bit and target independence, full wire
endpoints, complete arena/key scans, owned output and cleanup/returns
are checked. Inputs include non-rotation permutations, not merely the
source caller's easiest constants. The explicit negative controls
check duplicate/malformed inputs, an incorrect coloring edge and
missing arena/query head returns, and a nonselected corrupt network bit.

The three exact predecessor inputs are authenticated by SHA256 and
Git blob in [SOURCE-PINS.json](SOURCE-PINS.json). The verifier compiles
those authenticated source bytes directly rather than cached bytecode.
Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/crt-benes-scan/verify.py
python3.12 -I -O -W error -B research/crt-benes-scan/verify.py
```

Normal replay reproduces and compares the stored receipt without
rewriting it. `--write-result` is the explicit regeneration option.
Observer comparisons and source authentication are verification work;
they are not covert instructions of the claimed compiler.

The six registered commands in [VERIFY.json](VERIFY.json) also run a
[separately written FIFO oracle](independent_benes_oracle.py): all permutations
on2/4/8wires plus48 deterministic larger cases,40,394permutations /
324,452endpoint columns /1,630,756control columns. Its child-port mutation
produces an exact wrong endpoint. [INITIAL-REVIEW.json](INITIAL-REVIEW.json)
records that oracle before reading the primary implementation.
A [source-pinned cross-check](cross_check.py) compares primary tables,
forward/inverse endpoints and848 queries on37 cases directly to that oracle;
[CROSS-CHECK.json](CROSS-CHECK.json) records its normal/optimized runs.

[COST-REVIEW.json](COST-REVIEW.json) records the separate encoding/cost review.

## Open next questions

Bind this component to the **complete** uniform CRT control evaluator:
encoded moduli/CRT reconstruction, modular inverses, transported
split-axis descriptors, forward/inverse macro keys, their cleanup
and parameter construction. A feasible first step is one actual
root-axis query with all arithmetic loops and field reconstruction
lowered to sequential records. This package takes the encoded
permutation as input; it does not obtain that permutation for free
inside the full caller.

The source's complete E bound, production placement and ordinary
interchange callee, sparse repair, last-K caller, precision/native
closure and outer multiplication theorem remain separate obligations.
Finite agreement and an asymptotic component bound do not certify them.

## Credit

Cinna Davis supplies PR4100's original compiler, CRT construction
and full-scan proposal. Douglas Colkitt and OpenAI's framework,
the retained routing/compact-control lineage, Hiroki KUMAZAKI's
PR4174 placement audit and the source NOTICE retain their credit.
This contribution supplies a component lowering and audit, not a
new Beneš mechanism or a full CRT theorem. Prepared with substantial
OpenAI Codex assistance. Apache-2.0. No independent human review or
proof-assistant formalization is claimed.
