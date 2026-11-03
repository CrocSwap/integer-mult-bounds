# P1 Fraction source portability: source-only finding

**The earlier single-hash adapter rejects the official CPython 3.12.15 Fraction source.** The required interface and the six source functions it authenticates are compatible by static inspection. Parent authorized revision 4's exact second source digest; that source change and policy-only controls are now prepared, with runtime validation still pending.

| Source profile | Bytes | SHA256 |
| --- | ---: | --- |
| Current local `/usr/lib/python3.12/fractions.py`, environment labelled CPython 3.12.3 | 38,067 | `cf33568f7b767f66896995a7a81cc662e8be226f2e58efb61d2028f64eb5d231` |
| Official CPython tag `v3.12.15`, `Lib/fractions.py` | 38,147 | `d52d1ab9d5be26924e4914a5e40069c992bbfa68f773694c2e5ee8452d0766a0` |

The [official 3.12.15 release page](https://www.python.org/downloads/release/python-31215/) identifies the release. Read-only `git ls-remote` resolves its annotated tag object to `f9e83c56c657be0a74ede2b5c523de4f9191d117`, peeled commit `e848e4b09ca4bc67c0041c9ce7526dae471d4c36`. Downloads from the tag and [that exact commit](https://raw.githubusercontent.com/python/cpython/e848e4b09ca4bc67c0041c9ce7526dae471d4c36/Lib/fractions.py) have the same SHA. The latter is the durable source reference. A read-only copy is retained as `cpython-3.12.15-fractions.py`; preserve CPython/PSF attribution if it is included in publication.

The complete textual diff changes only `Fraction.__pow__`: its final general branch now accepts `float`/`complex` explicitly and returns `NotImplemented` otherwise. This is outside P1's constructor/hash/equality path. Static AST comparison, ignoring source-position attributes, found only `__pow__` changed, no top-level function changes, and identical Fraction method-name sets. `__new__`, `__hash__`, `__eq__`, `numerator`, `denominator`, and `_hash_algorithm` are each AST-identical. Exact slots, property access, the LRU hash wrapper and `numbers.Rational` inheritance remain present. Machine-readable evidence is `PORTABILITY-SOURCE.json`.

Filename-first discovery located the prior narrow pin at `outputs/fraction-native-cache-20261027/repo/research/fraction-native-qualification/SOURCES.json:114–119`: it records the same local `cf335...` hash and Linux x86_64 CPython 3.12.3 environment. Its `guard.py:18` includes the local Fraction file in the source closure. Selected earlier Fraction primitive/type-gate source records supplied no additional matching 3.12.15 pin in this bounded lookup. This does not claim exhaustive historical coverage.

## Minimal authorized revision 4 admission change

1. Replace the single accepted digest with a fixed two-entry allowlist containing the exact hashes above and explicit provenance labels. Keep CPython 3.12 as the supported interpreter family. Do not accept an arbitrary file merely because the version string says 3.12.15, and do not accept unknown files based only on a few matching methods.
2. Read and hash the active `fractions.__file__` exactly as now, select its explicit source profile, then retain the current source-local compilation/code comparison, descriptor checks, Fraction/global snapshots and per-admission freshness checks. Compare loaded functions with source compiled by that same running interpreter; do not compare bytecode serialized under different patch releases.
3. Return the actual selected digest/profile from source authentication into the receipt. The current hard-coded `fraction_sha256` receipt must not continue reporting the local digest when the official digest was selected. No fallback or scientific arithmetic changes are needed for this proposal.
4. Preserve unknown-digest rejection. Add bounded source-pin negative controls and normal/`-O` controls for each admitted runtime, plus the complete assertion-on hosted replay. An allowlist source check alone does not establish hosted runtime compatibility.

The small fixed allowlist lookup, provenance/receipt allocation and any added controls are paid costs, with measured size/time still unknown. Existing file hashing and compilation remain. If the parent changes the adapter, it needs a new immutable source revision and the applicable review/validation/performance treatment; local stage-v3 results must not silently become evidence for changed source. Keeping the current implementation unchanged instead limits P1 to the local Fraction source and would fail a hosted runner carrying the official digest.

## Remaining boundary

The claimed CI interpreter version is currently a parent-supplied expectation; this pass did not inspect a live runner's installed Fraction bytes. Distribution patches can alter files without changing the version string. Confirm the active file digest and actual runtime in the hosted receipt. P1's source-level interface compatibility does not certify the whole historical CLI across interpreters, and hosted correctness never transfers local wall/CPU measurements.

The initial investigation changed no adapter or controls. Following explicit parent authorization, revision 4 implements the two-entry policy and actual selected-digest/profile receipt, retaining all existing runtime checks. Controls test the literal pin policy and receipt consistency only; they do not load the reference file. No scientific module was imported, no code was compiled/executed, and no numerical or corpus run occurred in this worker. Source reads, retrieval, hashing/diffing, inert AST comparison and source edits are the evidence here.
