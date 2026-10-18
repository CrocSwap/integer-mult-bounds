# Independent actual tensor-collector audit for P104

Two independent direct interpretations of the first paired P104 collector
of Jose Manuel's **PR3131** agree at **multiplicity two**: `n=18`, `N=262144`,
rank `14`, with the actual nine-field native recipe. Four complete signed fixtures
agree on every query component and working grid, preserve all five source
arrays, and return the private collector to literal zero. Two fixtures have
nonzero rounding error. This supplies actual `lambda>1` semantic evidence at
the boundary left in PR3131's PROOF section 7. The full retained nested
implementation comparison remains **unchecked** after two bounded timeouts.

This is a **finite interface audit**, not verification of the fast physical
implementation, its time/space theorem, or a complete P104 supplier. The
selected frontier is unchanged. The original-order map, paired inverse and
error policy are predecessor constructions, not new results here.

## Exact scope and evidence

The frozen word interval is events **2025–2039**, with native occurrences
**2031 and 2033**. The audit reconstructs the prefix frames, checks the actual
source names `D31,D30,D29,D28,D27`, the `Q7` query, gathering/ungathering signs,
private lifetime and unique native records. It uses PR3131's layout

```
address = sum_i v_i * 2^(i*lambda),
v_i = sum_j x_(i,j) * 2^j.
```

The original lift acts on consecutive axes `0,...,7*lambda-1`. The numerical
return inverts the outbound wrappers and the literal lift in reverse order.
It does **not** independently round the distinct return recipe from event
2033. That recipe remains bound to the source and is checked as an ideal
round-trip fixture on the full multiplicity-two rounding input.

`verify.py` expands the binary affine and strict-upper quadratic phase
polynomials directly on 18 bits. `oracle.py` instead applies one 512-entry
factor at a time on each strided nine-bit column. Every address of both
outbound wrappers and their inverses is checked: **524288 forward monomial
columns**, plus both inverse checks. Unique positive address markers make
this an exact permutation-and-phase check, not a sampled linear-operator
comparison. The two implementations share raw recipes and fixture inputs,
not wrapper or lift code.

Tekalign's later [PR3134](../guarded-wrapper-refinement/README.md) reduces
wrapper-level lifting calls from 416 to 104 while retaining this collector
interface. Its complete collector checks are also at `N=512`. This audit
keeps PR3131's exact comparison source explicit; it does not replay PR3134's
changed implementation or claim its call reduction as new.

The primary lift uses the signed difference/floor sequence. The other uses
a separately derived parity formula for each output. An additional ideal
oracle uses `H diag(i^popcount) H / 2^14`, independently of either rounded
pair implementation. Both full query arrays are compared before recording
SHA256 digests. Digests summarize the outputs; they do not replace those
component comparisons.

| Multiplicity-two fixture | Input grid `f` | Working grid `F` | Squared error in working-grid numerator units |
|---|---:|---:|---:|
| signed, unpromoted, nonzero rounding | 3 | 3 | `5379503/8` |
| signed, promoted, nonzero rounding | 3 | 5 | `2615337/4` |
| 70-bit dirty cancellation to two unit components | 3 | 25 | `0` |
| exact zero gathered sum | 3 | 3 | `0` |

Physical squared error is the last column times `2^(-2F)`. The first two
cases use `beta=0`; the latter two use `beta=8`. The cancellation cases
retain independently supplied large positive and negative source arrays.
Their small or zero sum does not permit omitting source preservation or
literal ungathering. A complete `lambda=1` fixture is also included, and
four small cases are compared with Tekalign's authenticated PR3025 source.

## Why these are the intended semantics

For Gaussian integers `a,b`, put `d=a-b`,
`s=b+floor(d/2)` componentwise, rotate `d` by `i`, then return
`(s-floor(d/2)+d, s-floor(d/2))`. Replacing the rotation by `-i`
inverts the pair: the output difference determines the original `d`, and
adding back its floor recovers `s`. Reversing the stage order therefore
restores every integer input. This is Tekalign's credited bijection; the
checker also exhausts all **2401** pairs with four real coordinates in
`[-3,3]` against the separate parity expression.

If `p_R,p_I` are the parities of the entering difference, both outputs
have error `(p_I-p_R)(1-i)/2` relative to the ideal pair. Thus each stage's
squared error is at most `N/2`. Ideal suffixes and exact monomial wrappers
are unitary, so the whole outbound error has norm at most
`r sqrt(N/2)` in working-grid numerator units. The ideal Walsh oracle
checks the actual error and its unitary norm identity with integers only.

For nonzero gathered numerator `S`, let `M=max |component(S)|` and
`h=floor(log2 M)-f`. The source policy is

```
gamma = ceil(log2 r) + ceil((n-1)/2),
F = max(f, beta+1+gamma-h).
```

For zero `S`, use `F=f`. Since `||S 2^-f|| >= 2^h` and
`r sqrt(N/2) <= 2^gamma`, the outbound relative defect is at most
`epsilon=2^(-beta-1)`. The paired return is exactly the embedded input.
Its difference from the *ideal* inverse has the same norm as the outbound
defect, by unitarity, so its relative defect on this paired execution is at
most `epsilon/(1-epsilon) <= 2^-beta`. The checker evaluates both squared
relative inequalities without floating point. This is not a relative-error
theorem for arbitrary inputs to the inverse routine.

The query is promoted to grid `F` **before** adding the outbound value.
Private return permits exact downshift to `f`, then five reversed
ungathers. Exact private cleanup does not remove the query's numerical
error and is not by itself evidence of the correct forward map.

## Discriminating controls

The retained recipe's right wrapper sends address zero to **212799** with
phase **2** at multiplicity two. Using copy-major layout without conversion
instead sends it to **192375**. Forgetting the second copy's constant phase
changes phase 2 to 1. The left wrapper has a separate layout witness at
address 8. The full address checks distinguish these errors.

The four-component real impulse `(1,0,0,0)` becomes `(0,0,1,0)` under
lift order `[0,1]`, but `(0,1,0,0)` under `[1,0]`. Both paired inverses
restore the impulse. This small control explains why checking cleanup or
an ideal tensor endpoint alone cannot justify reordering nonlinear stages.
It is a calibration of the inherited order requirement, not a new
obstruction to arbitrary collectors.

Eight behavioral test groups also cover the actual optimized CLI,
source corruption before arithmetic, altered event signs/targets/lifetimes,
missing native occurrence, wrong query-grid promotion, corrupted return,
signed-floor truncation, wrapper phase changes, duplicate JSON keys and
changed receipt values/types. Assertions are not used for acceptance.

## Incomplete retained evaluator comparison

`attempt_retained.py` attempts the actual PR3131 nested evaluator on the full promoted
multiplicity-two fixture and compares its complete entrance, query, sent,
returned and private arrays with the independent oracle. Its one disclosed
adapter changes the finite `Executor` extent check from `n<=10` to `n<=18`.
All arithmetic, block-planning code, protected XOR interfaces, dense wrapper
calls and inverse routines are unchanged. The finite parameters are
`width=160, d=157, spacing=1, suffix=2, outer=14`, obtained from the inherited
exponents and checked using integer inequalities. The adapter authenticates
the original bytes and requires exactly that one reversible text substitution.

Both the small-test defaults `d=2, spacing=2, suffix=1, outer=3` and the
explicit derived plan above failed to finish within **600 seconds each**
(exit 124). Neither produced a completed receipt. These timeouts establish
no mathematical failure and no successful retained implementation comparison.
The script is preserved as an optional follow-up, outside the registered
successful replay. For example, from the repository root:

```sh
timeout 600s python3 -I -B research/p104-tensor-collector-audit/attempt_retained.py --plan derived
```

Use `--plan defaults` for the other attempt. The command compares full arrays
if it completes; no successful output is claimed for either recorded attempt.

The evaluator retains PR3109's frozen **direct semantic oracle**. This does
not execute, benchmark or verify a fast physical C-layer trace. Sources and
the archive remain unchanged; the adapter compiles its copy in memory.
`TASK.json` records the two attempted parameter sets and incomplete outcomes.

## Reproduce

Python **3.12**, standard library, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/p104-tensor-collector-audit --check-only
python3 -I -B scripts/research_package.py --package research/p104-tensor-collector-audit
```

The registered replay runs the independent full-array check and eight controls
under `-O`. Expected markers are
`PASS_P104_TENSOR_COLLECTOR_AUDIT cases=5 no_new_kappa` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Individual commands are in `VERIFY.json`.
`--emit` prints regenerated JSON; default replay reads and compares the
complete committed receipt without modifying it. Exact immutable source
hashes and Git blobs are in `SOURCES.json`.

The independent full-array run takes about **32 seconds** and **690 MiB**
on the recorded CPython 3.12.3 environment. This measures this direct checker,
not the proposed fast collector. The finite direct paired word has
`3670016` pair sites, `1048576` wrapper value visits and 11 full-array
scalar additions per multiplicity-two execution. Those are direct-reference
counts, not project-native child charges or a hosted physical bill.

## Limitations

No completed retained nested `lambda=2` implementation comparison, actual
`lambda>2` collector, fast C-layer trace, all-size machine
refinement, clean-history hosting, tape movement, complete correction word
or selected cold replay is checked. No human or formal-kernel review is
claimed. The source archive's scientific admission remains separate.

## Open next questions

1. Complete the retained nested evaluator comparison on this same actual
   fixture, with a measured replay budget, or establish its separate component
   equivalences. Agreement of the two direct semantic models does not verify
   the nested implementation. Both 600-second attempts remain unresolved.
2. Bind an actual fast reversible backend trace to this checked boundary,
   pricing snapshots, source access, cleanup and clean stock. The blocker is
   the physical backend and enclosing caller, not this direct finite oracle.
3. Name a changed complete P104 profile or consumer and price every term
   before further construction. PR3131 retains the unchanged five-forward /
   four-dual rejection `599/584 > 1`; this audit does not reprove it or remove
   any of its paid ranks. Clean history is not extra productive coverage.

The decision is to stop at this bounded audit. Detailed scope and next
questions are in `TASK.json`; the claim is in discussion **#2750**.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Credit Jose Manuel / jmbarrancoml, **PR3131**
`0c9e344d5a5295a218558fa4a51d867f39ff5311`, for the actual field-major dense
collector, original-order construction and explicit validation gap;
Tekalign, **PR3025** `a544ef068a46f4de3bc47d1d02149cbdc3ba547f` and **PR3033**
`b12bbaeb5ca2e83f15433fc2dd0ba3b766595281`, for the signed lifting pair,
paired collector, grid policy and period split; and Ross Richardson,
**PR3072** `cd1bbd05251f9d8e15cbb0192f1bfe83dc138f5e`, for the conditional
blocked construction. Retain Jose Manuel's PR3109 and PR2250/2287/2899
affine/compiler/physical lineage, Douglas Colkitt, ywz65 / PR2586,
Arham Tahir, Vasek/flyingviper's consumer audit and the retained Rohan Arun,
Chafik Boukhalfa, Adam Gall, Josie Elliston and Ali Romman P104 lineage.

Both new numerical evaluators were separately written in this contribution
with shared raw inputs. The small calibration intentionally executes credited
PR3025 code; the incomplete retained attempts intentionally execute credited
PR3131 and its source archive. These are not separate human reviews. Apache-2.0;
predecessor licenses, frozen inputs and the selected record are unchanged.
