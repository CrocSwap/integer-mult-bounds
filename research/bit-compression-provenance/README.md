# Historical bit-compression provenance closure (no new kappa)

The historical [bit-compression certificate](../../certificates/bit-compression-audit.json)
has two `source_sha256` entries. Both still match at base
`007664306fff84fbb1c9a1b4053b69f439764034`, but they do not pin the full computation:
the driver and eight helper modules execute, and only one of those nine Python
files appears in that inventory. In particular, the omitted
`shared_point_network.counts` computes the deficit used in the saving bounds.
The upstream manifest that determines `upstream_commit` is also omitted.

This package resolves that **provenance undercoverage**, not a mathematical
counterexample. It supplies a checked local source/input closure, a fresh replay
that compares every certificate field, an independent arithmetic checker, and
failure controls. The full replay reproduced the historical result. No existing
construction, certificate, selected frontier, or `upstream/` file is changed.

A concrete control changes only the omitted helper's `D=N-2*L` to `D=N-2*L+1`.
At the recorded winning counts, the deficit ratio changes from `23/660995000`
to `1767136000001/50785567840000000000`, an exact difference of
`1/50785567840000000000`. Both historical source hashes still match; the new
input verifier rejects the changed helper before execution. This demonstrates
why those two hashes alone do not bind the arithmetic-producing code.

## Reproduce

From the repository root, with Python 3.11 or later and no third-party packages:

```sh
python -I -S -B research/bit-compression-provenance/verify.py
```

Expected final line:

```text
PASS: 32 pinned inputs; 9 local Python files; no new kappa.
```

This checks hashes before executing any predecessor code, checks the independent
arithmetic, and runs the unchanged historical producer in a fresh temporary
directory. The reference output is removed from that directory before execution,
so an omitted producer write cannot count as a successful replay. Only pinned
files are copied. An ambient `PYTHONPATH`, site package, or added package
initializer cannot enter this isolated source copy. A runtime module inventory
must agree with the static import closure. Every generated JSON field must match;
only JSON key order and whitespace are normalized. Integer `1` and Boolean `true`
are different. The original two source hashes are retained in the comparison.

To write a receipt, add `--output /path/to/a/new/receipt.json`. An existing receipt
is refused. `--check-only` is a quick input/arithmetic check and explicitly reports
`INPUTS_AND_ARITHMETIC_ONLY`; it does **not** report a fresh producer replay.
The wrapper rejects `-O` because the predecessor's circuit checks use assertions.

Run the failure controls and the original focused tests separately:

```sh
python -I -S -B research/bit-compression-provenance/test_verify.py
python -B -m unittest discover -s tests -p test_bit_compression.py -v
```

The first command tests this package's source, arithmetic, output-comparison,
and isolated-replay failure modes. The second is the predecessor's seven-test
suite. The contribution does not change shared modules, so global artifact
regeneration and the selected-frontier cold replay are unnecessary here.

## What the new inventory establishes

[SOURCES.json](SOURCES.json) records exact SHA-256 values for 32 inputs:

| Input class | Count | Purpose |
| --- | ---: | --- |
| Historical driver and repository-local imported Python modules | 9 | Actual producer implementation, including function-local imports |
| Historical proof note | 1 | Written model, counting argument, and infinite-tail hypotheses |
| Upstream manifest and its listed files | 20 | Bind the manifest itself and every file read by `verify_sources` |
| Historical output certificate | 1 | Exact expected result, independently retained for comparison |
| Historical focused test module | 1 | Reproducible predecessor test source |

The upstream dependency remains OpenAI's `math` commit
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`. The static graph has nine local Python
files; the runtime trace contains the eight imported helpers plus the separately
executed driver. Unknown non-standard-library imports are rejected, including a
helper omitted from both the files table and the graph. All inputs are verified
again against the copied bytes as applicable, and non-output files must remain
unchanged after execution.

These hashes are integrity bindings relative to the reviewed Git source. They
are not signatures or proof that a run occurred. The Python interpreter and its
standard library are recorded as environment, not pinned binary dependencies.
The closure is for this producer, not a claim to discover arbitrary dynamic
imports or authenticate the repository's entire dependency graph.

## Mathematical evidence and boundary

The independent checker imports no predecessor implementation. It reconstructs
the rational logarithm enclosures, count formulas, strict integer role budgets,
candidate domains, and best/peak selection. It checks:

- All 73 distinct local configurations at `h=50` and all 18 merged configurations.
- All 36 even ground sizes `40,42,...,110` for the existing paired template.
- At `h=50`, `U=4389`, `F=2304`, and the conditional role floor
  `50 U + ceil(50 F/2) + 50 binom(49,2) = 335850`, versus the necessary target
  budget `R <= 317035` for the historical `2^-30` target.
- The finite favorable-bound peak at `h=52`, the `h=112` tail endpoint, and the
  recorded 48-role reduction from `509194` to `509146`.

The independent arithmetic module treats circuit node classifications, merge
counts, and frame predicates as supplied inputs. The full producer replay
recomputes those finite circuit facts. Neither check proves the infinite family
by finite enumeration: the tail relies on the written argument that distinct
unshareable outputs imply `R >= 6v`, and on monotonicity of
`1 / ((14h^3 - 1) log(h^3))`. The historical obstruction retains the `c+q` compiler,
separate partial outputs, original central losses, and the old assembly inequality
`kappa < a_b/5`. It must not be transferred to the selected PR890 construction.

This is a completed replay of the old domain, not an enlarged search. The search
stopping rule, finite coverage, and general counting argument are unchanged.
No general circuit lower bound, full multiplication theorem, or new exponent
saving is claimed. The selected result at the pinned base is still PR890's
conditional `1661957774647029/10^18`.

## Attribution, coordination, and receipts

The mathematical construction and original audit are Douglas R. Colkitt's
historical research, retained by commit
`d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`, with the repository's existing OpenAI
Codex assistance disclosure. This contribution is by **woklerx**, with substantial
OpenAI Codex assistance, including independently assigned dependency and arithmetic
reviews. It claims no priority for the obstruction or the historical circuit.
New files follow the repository's Apache-2.0 license; predecessor notices remain
in place.

[CLAIM.md](CLAIM.md) records OS-random seed 99, the three candidates, the narrow
scope, and bounded overlap searches. The public issue list contained no pinned
sprint issue, so the claim was recorded locally. PR867's selected-799 provenance
map is related prior work, but concerns different source packages; PR756 and
PR824 address faster Fano and stage-pair replays. This contribution binds and
replays the older bit-compression obstruction without changing their work.

[REPLAY.json](REPLAY.json) records the full comparison, environment, eight-helper
runtime inventory, and independent arithmetic result.
[VALIDATION.json](VALIDATION.json) pins the new implementation and records all
four successful commands: 23 controls normally, the same 23 under `-O`, the
predecessor's seven tests, and the final integrated full replay (about 51 seconds
on this Windows/Python 3.14 host). These are local execution receipts; hosted CI
and independent human mathematical review remain separate.
