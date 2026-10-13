# Exact minimum for the contracted factory's scale placements

**Scoped negative result; no new κ.** PR924's 73-real-primitive witness is
optimal among signed dyadic diagonal gauges of its fixed 26 ordered ADDs
using 32 scalar macros. There is exactly one optimal magnitude-scale placement
and eight equivalent sign-only placements. Under PR924's retained local invoice,
adding macros cannot improve the complete charge either.

This resolves a specific open scope in
[PR924](https://github.com/CrocSwap/integer-mult-bounds/pull/924), which combines
[PR922](https://github.com/CrocSwap/integer-mult-bounds/pull/922)'s contractions
with scale relocation but explicitly leaves a macro-budget optimum unclaimed.
It credits their existing witness rather than proposing a new circuit.
Neither a global circuit optimum nor an architectural impossibility follows.

## Reproduce

From the repository root, Python 3.9+ and the standard library suffice:

```sh
python3 -I -O -B research/complex-factory-scale-frontier27/check.py
```

Expected final line:

```text
PASS_FACTORY_SCALE_PACKAGE complete=315392 exact_matrix_replays=39424 minimum=73 winners=8 no_new_kappa
```

The command verifies immutable source hashes, the complete deterministic
receipt, all eight optimal sign placements in four orientations, a separate
all-column primitive census, and twelve test groups including 64 individual
gate-deletion/sign mutations. It needs no network, solver, NumPy, build products
or other pending checkout. `EXPECTED.json` is a certificate of this declared
finite calculation, not a formal multiplication-theorem certificate.

## Exact result

| Quantity | Result |
|---|---:|
| Fixed ordered ADDs | 26 |
| Minimum SCALE macros | 6 |
| Minimum scalar macros | 32 |
| Magnitude placement tuples, fully enumerated | 39,424 |
| Complete tuples including sign-only placements | 315,392 |
| Minimum real-component primitives | 73 |
| Optimal magnitude placements | 1 |
| Optimal complete placements | 8 |
| Next primitive cost / magnitude placements attaining it | 75 / 13 |

The proof reduces arbitrary signed power-of-two gauges at the minimum macro
count to one prescribed net scale on each of six wires. Five wires affect
coefficient magnitudes; the sign-only wire contributes an exact factor of
eight to every cost bucket. The full histogram is retained. Enumeration is
exhaustive, with no timeout or heuristic pruning. OS assignment seed **27**
selects the complex track and enumeration/sign-representative order; it does
not change coverage.

The primary implementation uses exact integer cost tables and the pinned
PR696 lowering. The separately written oracle imports none of its constructor,
cost tables, formulas or interpreter: it emits and executes primitives for all
39,424 magnitude tuples on all eight data columns and one arbitrary dirty-work
column, using a fixed integer grid with checked exact halving. It reproduces
the complete histogram. The other seven sign placements are covered by the
sign-cost argument; all eight optimal ones are also replayed explicitly.
Both implementations are AI-written, so this is not independent human review.

One extra emitted macro costs `16*(64*74^3) = 414,949,376` under the retained
adapter formula. All fourteen windows and fourteen inverse cleanups together
cost only `14*2*2*73 = 4,088` real primitives. Thus even eliminating every one
of those primitives cannot pay for a single additional macro. This closes the
arbitrary-extra-scale class **for that fixed invoice and fixed outside costs**,
including different choices in different windows. It is not a lower bound
on all possible compilers or adapter implementations.

See [PROOF.md](PROOF.md) for the reduction, cost model, orientation bijection,
boundary identity, complete pricing and exclusions. [SOURCES.json](SOURCES.json)
and the byte-identical retained source bind the exact inputs.

## Sources, current state and overlap

Exact base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
At that base, the selected result is the U8/T21 conditional
κ = `1661957774647029/1000000000000000000` = **0.001661957774647029**.
We followed `certificates/selected-result.json` to the actual
`research/community-frontier890-audit/ASSEMBLY.json`, source manifest and
`docs/research/community-frontier890-review.md`. The review ledger marks
PR681 and PR696 incorporated; pending PR922/924 are separate dependencies.
The older κ quoted in their descriptions is historical context.

Consumed source heads:

- PR681 / Alluri: `e536f6fc8aad65adef8ac4682d13625598a5c3f9`.
- PR696 / Sagar Thakrar: `5a3f983715027c4fd83f50bc9001d4b18463bed1`.
- PR922 / CubeJerry: `efd5643c0016b6c6dac26e9ed7dee8a75295ff2a`.
- PR924 / CubeJerry: `d02d83332581f6a23616c1366c6b3901d42f4b06`.

`sources/PR924-COMPOSITION.json` preserves the original bytes and attribution.
Its internal `pr924_head` denotes the earlier standalone PR924 revision;
the retrieval head above is the composition revision. No pending executable
code is imported. The baseline PR681 witness, PR696 lowering and historical
invoice assertions are read in place and hash-pinned. The selected-record
hash is contextual evidence only, so a later frontier does not break this
historical package.

The initial scan covered 714 open PRs, followed by arrivals through PR945 before
the local claim. PR922 covers contractions, PR924 a feasible composition and an
unrestricted **28-ADD** gauge bound, PR931 a different butterfly search class,
and PR919 CK helper signs. This package completes the **26-ADD minimum-macro**
scale-placement domain and the associated fixed-invoice exclusion. This is
not a larger random run of a previously closed search.

There was no pinned sprint issue; open issues 913 and 650 were unrelated.
The three candidate tasks, assignment, budget and local claim are recorded in
[CLAIM.json](CLAIM.json). No delegated worker was launched.

## Verification and limits

Normal and isolated optimized primary replay, independent exact matrix census,
gate/placement/work/grid controls, minimal offline relocation in a path with
spaces, source/receipt corruption, output preservation and the repository's
`make selected-record-check` pass. [VALIDATION.md](VALIDATION.md) records the
executed environments and final overlap refresh.

Only this research package is added. There is no changed supplier to admit;
PR924's existing witness already reaches the proved floor. Full raw/native
construction regeneration, the repository-wide `make verify`, the selected
`make frontier890-verify` cold replay, hosting, global invoice/assembly, Lean
and remote CI are not claimed. Their production sources and selected inputs
are unchanged. This package checks the local exact operator and cost class,
not the inherited physical execution of every historical factory window.

The source-specific 26-ADD order, PR696 per-ADD work-clear contract, fixed
adapter formula and unchanged outside work are essential hypotheses. Other
topologies, cross-ADD work sharing, new bases, frame schedules, helpers,
recursive profiles or compiler accounting are outside scope. All-size/compiler,
common-label/mutable-source, whole-call hosting, precision/tape, analytic and
bit H1-H5 obligations remain inherited. No runtime gain or new κ is claimed.

## Attribution and license

Prepared by **Ross Richardson / RossRichardson**, with substantial **OpenAI
Codex** assistance in analysis, implementation, proofs, tests and writing.
No independent human or delegated-agent review is claimed. Apache-2.0 under
the repository [LICENSE](../../LICENSE).

Credit **CubeJerry** for PR922/924 and the optimal witness; **Alluri /
alluri-ritual** for PR681's full eight-wire map and resynthesis; **Sagar Thakrar /
thakrarsagar** for PR696's primitive lowering; **Jeremy Kothe / jeremykothe2**
for PR622; **icekylinx** for the factory/scalar architecture; **Chafik Boukhalfa /
chafreaky** for PR626 packaging and the later selected composition; and
**DreamingOfClouds**, **Dugongue**, **Rohan Arun**, **eumemic** and the retained
source-notice contributors for the inherited supplier and verification lineage.
Their existing improvements, construction claims and licenses remain theirs.
