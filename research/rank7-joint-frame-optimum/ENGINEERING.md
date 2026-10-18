# Engineering and verification boundary

The exit predicate was one useful, source-bound mathematical result with a
rerunnable proof and focused publication. The attempted strict frame saving
was not found. The retained result proves the complete fixed-interface optimum
uniformly on `0 < b <= 1/100`, rather than treating a numerical search as proof.
No supplier or outer release is inferred.

## Verification

On macOS arm64 with CPython 3.12.15:

- Registered package replay passes, including 14 behavioral groups.
- Direct verifier and all 14 groups pass under `-O` with warnings as errors.
- CPython 3.14.8 gives a byte-identical RESULT.json.
- Source compilation with `py_compile` passes for all six Python files.
- Ruff 0.17.1 passes with `--select E4,E7,E9,F,B,UP,SIM,C4,PIE,RUF`.
  There are no diagnostic suppressions. A broader exploratory `--select ALL`
  reported annotation, docstring, quote, formatting and policy rules that this
  package does not adopt. It was not a passing gate. No formatter policy or
  strict static type-checking configuration is introduced.

Run the commands in README.md with `TMPDIR` set to a session-owned external
directory. Unit-test copies and the generic launcher's bytecode namespace are
disposable. The verifier's only optional write is the requested receipt path.
It does not consume RESULT.json or execute predecessor Python code.

Two separate internal read-only reviews found no production correctness issue.
One independently reconstructed both graphs, feasible counts and exact
first-derivative optima using a different elimination order. The other rebuilt
all domains by a different quotient enumeration and brute-forced 194 manageable
components, 336,420 assignments per provider. Both checked the frozen Git bytes.
These were internal review probes, not independent human or formal validation.
The public proof replay is the complete checker in this package.

The local decision trail recorded orientation, the failed improvement attempt,
the exact proof, reviews and final checks. Its two mistaken early timestamps
and one ambiguous description of PR3057 were corrected append-only. No
unresolved review flag remained. Disposable review probes and discovery logs
are removed after preserving the proof, deterministic receipt and environment.

## Power of Ten review

The six Python files have no recursive call cycle or unstructured jump. The
largest function is 43 physical lines. State is local to the graph, one active
component, or explicit bounded memoization. Fixed record dataclasses and the
three named memoized functions are the only standard decorator machinery;
there is no dynamic code evaluation, plugin dispatch or custom generation.

Input exports are SHA256-authenticated before decompression. Input limits are
100,000 compressed bytes and 800,000 decoded bytes per word. Frame spaces have
at most 512 vectors. Chronology has at most 8,000 events; the graph has at most
7,500 scalar vertices and 15,000 edges. Each component has at most 128 variables
and 512 edges. Domains contain at most sixteen subspaces. Elimination refuses
more than 4,096 candidate combinations or 32,768 live factor entries. Each
logarithm uses exactly 96 terms. The two variable caches hold at most 1,024
entries each; the logarithm cache has nine. These are explicit failure gates,
not truncation. The authenticated instance's largest bucket has 2,560 cases.

Meaningful contracts check containment, source profiles and widths, chronological
ordering, fixed interfaces, equal rank mass, complete elimination and every
uniform tariff comparison. They use exceptions and remain active with `-O`.
The improvable prefix/restore fixture rules out a checker that always reports
the source optimal. The crossing-comparison fixture rejects a pointwise test
substituted for a uniform proof. Source, wrong-axis, warp, inventory and capacity
controls exercise their actual failure paths.

Rule 3 has a managed-runtime deviation. Python allocates decoded data, subspace
sets, factor dictionaries and integer/rational values during replay. The input,
component, cache and factor bounds above limit live work. The measured
tracemalloc peak was 61,720,884 bytes for the complete two-provider proof, with
a 5.048-second traced replay. This is an observed allocation measurement, not a
universal platform memory bound. Reassess capacity and allocation before
supporting another source family; use fixed-capacity storage if the consumer
requires allocation-free operation. Failed checks propagate and temporary
resources use context-managed cleanup.

No native/compiler, ownership, prefix/precision, physical movement, all-size or
outer replay was needed or claimed for this fixed-word lower bound. The
inherited mathematical and physical obligations remain open or conditional as
described in README.md. This package does not strengthen their evidence status.
