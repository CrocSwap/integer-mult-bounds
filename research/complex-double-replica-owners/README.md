# T16 whole-owner concentration on the accepted X4 supplier

This construction increases the conditional exponent saving from PR799's
`0.001661634653669567` to **`0.001661642255531641`**, an absolute gain of
`0.000000007601862074`. The complex supplier remains binding. The accepted
local X4 program, every local frame and helper width, and PR589's bit supplier
are unchanged.

The new contribution is a sixteen-replica controller and eleven explicit
whole-helper assignment edits. Two independent eight-replica assignments
leave idle ranks `(44,3,3)` in three particular bins. An augmenting path and
two bin repartitions change these to `(48,2,0)`. Total paid rank mass is
preserved; strict concavity lowers the recursive moment. The construction
uses no optimizer during verification. See [PROOF.md](PROOF.md).

The research began at `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`, with PR741
selected. Before submission, upstream accepted PR799 at the refreshed base
**`f567884aeb8851b6e794af1184119a3bfbe1e631`**. The final witness composes with
that newer accepted supplier. The earlier T16-on-741 calculation is a
historical control, not the comparison used for the claimed improvement.

## Reproduce

Use Python 3.11 or later, NumPy, SciPy, SymPy, a C++17 compiler and Boost
headers, as required by the inherited cold supplier replay. From the
repository root, choose a fresh directory outside the checkout:

```sh
python3 -B research/complex-double-replica-owners/verify.py \
  --work /absolute/new/t16-x4-replay
```

Expected final status: `PASS_STRICT_T16_PR799_OWNER_CONCENTRATION`, with
`kappa_decimal` equal to `0.001661642255531641`.

The default rebuilds both suppliers and the entire PR799/741 ancestry. For a
development replay, completed PR799 and PR741 outputs can be supplied together:

```sh
python3 -B research/complex-double-replica-owners/verify.py \
  --work /absolute/new/t16-x4-recheck \
  --baseline799 /absolute/completed/frontier799 \
  --ancestor741 /absolute/completed/frontier741
```

Reuse is explicit in the result. A coverage gate first requires all 22 ancestral
stages, all 44 mandatory artifacts and agreement with the separate stage log.
The verifier then reruns the existing source, native,
phase, artifact, stage-log, owner and composition binding checks. It is not
reported as a new cold ancestor run. The top-level verifier requires enabled
assertions, rejects existing output directories, and binds all package and
dependency source bytes before invoking inherited checkers.

Regenerated owners and the complete PLAN are pinned by canonical content.
Only the two already validated owner-container references are normalized in
the PLAN identity. A runtime SPEC then binds their actual file bytes; the
frozen mathematical expectations remain identical. Recompression and header
changes therefore preserve admission, while any owner or PLAN-content change
fails. Fixed source archives retain exact byte pins.

After a successful replay, the separate package controls can be run with
`package_controls.py --replay REPLAY --baseline799 REPLAY/baseline799
--ancestor741 REPLAY/baseline799/ancestor --out NEW_JSON`. They check container
portability, semantic corruption, mandatory coverage and output preservation.
The coverage gate detects omissions, not fabricated execution histories; it
credits the issue identified in PR838 and the related PR847 integration.

## Exact result and complete cost

The complex lower endpoint is
`1664407906038756083473 / 10^24`. The unchanged bit endpoint is
`1733427039589844234749 / 10^24`. The final saving is
`1661642255531641 / 10^18`.

The full paid profile is

```
{1:366914, 2:48673, 3:61920, 4:27936,
 5:8064, 8:1152, 44:1, 48:4793}.
```

There are 144 complete invocations, 72,576 whole helper roles, 14,336 live
data/owner families, 14,850 physical families, rank mass 1,041,408 and deficit
5,120. Actual strict touch-to-idle windows include every bridge. No helper is
split between families, and each invocation has distinct physical owners.
All 8,546 actual orthogonal residual/spectator charts are checked.

The finite invoice counts every invocation, bridge, wrapper, scalar primitive,
idle remainder and restored private workspace. The required prefix is 401
bits within the retained 512-bit charge; the physical row coefficient is
16,469 below the retained 20,161 ceiling. The conservative complex surcharge
model also passes, at κ `0.001661642252649825`. The selected native-complex
model uses the already accepted recurrence convention; the bit surcharge is
retained.

The parent reserve envelope uses two **separate** dedicated-bank groups.
Reusing a single bank with helper lane 15 would exceed the 73-dimensional
chart and is not the construction. The lifted parent has 23,408 live families,
23,922 physical families and 1,008 dedicated bank families per stage. Each
completed invocation restores its 504-helper private workspace before reuse.
The final hosted controller has zero banks; the larger parent stock is retained
only as a conservative invoice envelope.

## Review map

- `build_owners.py`: duplicates the pinned PR741 owner map used by PR799 and
  applies eleven frozen edits. Eleven omitted-edit controls must reject.
- `build_parent.py`: constructs the genuine two-bank parent, preserves every
  original route, and derives windows from the expanded source-event stream.
  The identity lift and the original eight-replica windows are controls.
- `independent_check.py`: imports neither builder nor emitter. It independently
  checks every role, active-family exclusion, strict window, whole-helper
  width, offset, orthogonal chart, local profile and global profile, with six
  targeted negative controls. Its guards also run under optimized Python.
- `source_adapters.py`: exact, multiplicity-checked edits to the pinned PR799
  global emit/audit/invoice/assembly sources. Changes concern replica counts,
  stock, deficit and their full invoice; all legality and admission predicates
  and all numerical ceilings remain present. Materialized source hashes and
  the complete edit list are written to the replay directory.
- `data/SPEC.json`: frozen expected values, checked after recomputation.
  Both rational moment engines check the accepted endpoint and reject the
  next grid point. Conservative and native assemblies each check all 47
  strict inequalities, followed by all 69 inherited admission mutations and
  12 bit-supplier mutations.

## Scope and overlap

This is a new conditional finite composition, not a measured multiplication
runtime improvement, an unconditional algorithm, a full Lean theorem or an
optimality claim. The inherited all-size compiler, common-label/mutable-source,
whole-call hosting, precision/tape and analytic-transfer assumptions remain.

PR795 proves an optimum with **eight** replicas, fixed call count and fixed
capacity inventory. This construction changes that inventory and call count;
it does not contradict or weaken PR795. The concurrently published PR850
extends the same fixed 72-call inventory result over an interval of saving
parameters; it likewise does not cover this 144-call inventory. PR799's local read exchanges and
PR741's frame changes are inherited and credited, not rediscovered here.
No selected-frontier record is edited by this submission.

Authored by **Hao Yan (@FanPUYen)** with substantial **OpenAI Codex assistance**
in research, implementation, independent AI-agent checks, verification and
writing. No independent human review is claimed. See [NOTICE.md](NOTICE.md).
