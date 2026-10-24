# Sharing equal-key wrappers in the public finite compiler

**Scoped representation refinement; no stock or κ improvement.** The unchanged
public compiler creates fresh `Residual` wrappers for repeated keys. The new
opt-in `share_codes` pass validates complete residual segments, then shares
one definition per `(mode, identifier, common, LOW)` if every field agrees.
It retains the actual `Machine.geometry` identity check and every operation.

This answers the sharing question in Kewin Talaga's #3391
`selected-compiler-visitation-audit` and `selected-compiler-source-bridge`.
The new result is the conditional simulation proof, executable normalization
and actual caller comparison, not discovery of caching: the predecessor
`macro_local_checks.Binding` already supplies prebuilt fixture definitions.
Nothing is installed into that frozen caller or the current selected result.

## Boundary and cost

Inputs are already compiled `Code` objects with disjoint, closed
`residual_begin / block* / residual_end` segments. Each block and end must use
exactly its segment's wrapper identity; the end must also use the same role.
No other opcode may occur inside a segment. A duplicate key with a different
code, plan, axis or constants is rejected. Modes are separate namespaces:
the actual `ToyBinding` gives the same source key different axis/plan meanings
in modes 0 and 1. All factory calls and their validation have already occurred.

The result reduces **wrapper objects retained by the returned Code** after the
original Code and other observer references are released. It does not reduce
emitter calls, setup peak allocation, operation count, direct references,
LOW enumeration, native work, or the complete compiled-word representation.
The pass itself scans all operations and temporarily holds both tuples; it is
not a way to materialize an impossible-size GL64 compilation.

Under the earlier source census and its LOW/validity hypotheses, additionally
assuming all equal-key definition fields agree, mode 0's 904,896 N wrappers
become 28,278 N wrappers: 32 visits per key. The pass checks field agreement
for materialized input; that agreement is not replayed at selected GL64 here.
The existing
`1,809,792 N + B` direct references and the operation tuple remain unchanged.
That census is a pinned predecessor input, not rerun or newly proved here.
The count describes the retained public BIT compiler, not an expanded current
joint-helper construction or a complete multiplier's memory usage.

## Simulation theorem

Assume the input codes pass the segment validator, definition values and all
reachable plan/constant data remain unchanged during execution, and binding
callbacks inspect values without retaining or testing wrapper identity.
`Residual` and the used `Plan`/command/reference dataclasses are frozen, but
that alone does not freeze nested dictionaries: the immutability premise is
explicit. Unsupported mutable leaf fields are rejected during normalization;
allowed constant dictionaries must remain unchanged afterwards.

Observers must be read-only and insensitive to allocation identity, aliasing,
reference counts and lifetime. The actual source callbacks read `definition`
fields (`code`, `plan`, `constants`); they do not mutate definitions or inspect
wrapper identity. An arbitrary supplied callback/observer is not covered.
The runtime is the exact pinned `Machine`, including its geometry closes.
No source/incoming validation is removed.

Relate two machine states when all operational state agrees: modes, program
counters, tapes, heads, numerical arenas, pools, context, continuation frames
and counters. In an active geometry, replace just its wrapper-owner reference
by the segment's canonical representative. Every code operand is translated
by this same per-mode map; its field values agree.

Induct on executed macros:

1. At a segment begin, geometry is closed. All produced directories, counts,
   layout dimensions and source checks depend on equal fields and equal
   operational state, so they agree. The newly active owner is related.
2. Inside the segment, every block uses its segment's exact identity.
   `owner is definition` is therefore true on both sides, without replacing
   the source identity guard by value equality. Geometry arithmetic,
   coefficient evaluation, physical reads/writes and resulting branches agree.
3. An internal child closes geometry before the recursive cut. The saved
   continuation contains mode, program counter and numerical labels, not a
   residual wrapper. On restoration, the unchanged code fetch picks the same
   block position and reconstructs geometry from equal definition values.
   Apply the same relation to child execution and then the resumed parent.
4. `residual_end` closes geometry before the next segment and transfers the
   same bytes to the same role. Other macros have unchanged operands and
   effects. Runtime guards based on data reject at the same corresponding
   point. Equal field-based observers see the same values and cannot steer
   the runtime through their unused return values.

Thus every finite execution, including completed recursive returns, has equal
operational effects and field-based observations. This is a written conditional
proof about the pinned source, not Python formal semantics or a kernel proof.
It does not assert equivalence for arbitrary malformed code: those inputs are
rejected by the new preflight boundary rather than admitted for normalization.

The lifecycle and observer premises are necessary. A read-only identity
observer counts two original wrappers versus one shared wrapper. If a different
runtime omits the geometry close, the second fresh wrapper fails the actual
owner-identity guard, while the shared wrapper can falsely reuse stale geometry.
Both distinctions are executable controls; neither is a defect in the unchanged
runtime. Changes to these consumers invalidate this proof.

## Execution evidence

The verifier authenticates declared source bytes before importing the
unchanged runtime with the predecessor's same-byte hash/compile loader.
It deliberately initializes the original loader's already-active state with
the authenticated codec, as the source bridge's lifetime audit does. The
historical selected-record loader whitelist is not exercised: this is runtime
refinement evidence, not cold loader or selected-source admission.

The complete first-range fixture has GL2(F2), two independent families/replicas,
all six LOW classes, 12 fresh rows and 192 Boolean positions. It adapts only the
predecessor's reduced source/topology and root-stock expectation. The original
compiler emits 24 wrappers and 963 operations; sharing retains 12 wrappers and
all 963 operations. Original and transformed programs execute on the same
complete deterministic payload, with equal field-based event traces, macro
counters, physical codec/parking counts, output, borrowed ports and Count heads,
and complete work erasure. An independent address formula checks the endpoint.
This is one full payload execution, not 192 independent basis executions.

A separate unchanged `macro_checks.run()` fixture executes both complete modes,
12 actual child calls/returns and 156 residuals on 9,216 Boolean positions.
Its two full receipts agree before and after normalization. Its individual
modes have no duplicate keys; it checks mode/continuation compatibility rather
than contributing an additional measured sharing reduction.

Rejecting controls cover a different block identity, wrong end role,
unterminated segment, changed same-key code or plan (including Boolean/integer confusion), mutable
leaf data, a real geometry owner mismatch and collapsing modes with different definitions. Identity and
stale-geometry observers explicitly demonstrate the excluded contracts.
The actual toy factory independently checks that modes change its definition.

Reproduce with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/selected-wrapper-sharing
```

Verification is read-only; only explicit `verify.py --write` writes RESULT.json.
Normal and optimized replays compare the same complete receipt. Each has a
600-second command budget (1,200 seconds in total), the registered runner caps.
The initial [Ubuntu 24.04 / Python 3.12.15 CI run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39838365377/job/120034162122)
completed its first nested execution in 274.67 seconds, then reached the former
360-second command limit during the second execution. The budget adjustment
retains both complete runs and all checks; it does not establish hosted success
or change the scientific receipt. No Lean,
Docker, selected cold replay, GL64 enumeration or supplier adoption is included.

## Coordination, scope and credit

Task `selected-stock-envelope`, revision 7, **changed scope** to the predecessor's
explicit representation/consumer handoff. This does not derive a stock coefficient.
Canonical claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-19130770
Base: `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`.
Entry overlap covered 506 open PRs, 3650 Discussion records and all 5860 tracked
local notes. Exact-key searches found the two cited predecessors and unrelated
interning work; closed PR bodies, arbitrary diffs and all history were not
exhaustively searched. This is no novelty guarantee.

Kewin Talaga/PellaML supplied the visitation and source bridge audits, including
the reused authenticated importer and observer/lifetime distinctions. Jose
Manuel/jmbarrancoml supplied the physical compiler, binding, runtime, numerical
codec and reduced fixtures; David Arias supplied the logical caller; Nick
Petalas supplied compiler-ordering and refinement audits; ywz65 supplied
parking, and Ross Richardson supplied the retained-object accounting method.
The retained source notices and remaining predecessor credits apply unchanged.
New pass, proof and checks prepared by JoyboyBrian with substantial OpenAI Codex
assistance; Apache-2.0. No independent human or formal acceptance is claimed.

## Open next questions

- Can a streaming/regional emitter avoid the original peak allocation while
  preserving operation order and suspended continuation fetch? Start with an
  indexed bounded-region contract; this pass does not solve that problem.
- Can the observer/immutability boundary be enforced when arbitrary extensions
  are installed? First enumerate their identity and mutation behavior. Arbitrary
  extension equivalence is intentionally not claimed.
- Can the conditional simulation be formalized against a source operational
  semantics? The present written induction and finite runs do not supply it.
