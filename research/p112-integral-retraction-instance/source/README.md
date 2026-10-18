# P112 pinned integer-retraction instance — source candidate

**SOURCE ONLY / NOT YET KERNEL CHECKED for this successor.**

No Lean compiler was executed by the producer. No new `.olean`, successful Lean
log, measured Lean runtime, or observed new axiom-dependency report is supplied.
The unchanged dependency's header describes its predecessor's reported local
replay, not acceptance of this numerical instance. Operator source review and
actual exact-toolchain replay remain necessary.

## Supplied proposition

`P112Cert.certificate : PR1497.MatrixIdentities P112Cert.M P112Cert.P
P112Cert.Q P112Cert.W` has **no numerical-certificate hypothesis**. Its fields
are proof bodies for the actual imported `matMul` equations:

```text
M : Mat 288 104       P : Mat 104 33
Q : Mat 33 104        W : Mat 104 288
MP = 0               QP = I_33              I_104 - PQ = WM
```

`P112Consequences.lean` applies existing bridge results to that term: the actual
image/kernel equality, surjectivity, image-difference quotient isomorphism and
its inverse equations, saturation, and the existing conditional monomial
interface. The ordinary `CommGroup` and individual-row relation hypotheses
remain explicit. This supplies neither a particular field adapter nor geometric
relation hypotheses. See `SCOPE.md` for the precise boundary.

## Source binding

The two canonical inputs match the requested bytes exactly, including final LF:

| File | UTF8 bytes | SHA256 |
|---|---:|---|
| `P112.json` | 13,183 | `a1b43a5a7a8dcce0b84858244c512e53e6c344877cc35e87937fedd2601f29d5` |
| `PR1497Bridge.lean` | 48,758 | `a27494b0d40bbf7874fd9a875e468c67d11545b266e17bc98f2ca75c77f6ee40` |

All 1,524 stored matrix entries, empty rows, coordinate labels, anchors,
representative keys/values, parameter ordering, and inherited rank metadata
are emitted without reordering. `generate.py --check` performs exact read-only
regeneration. A separate inverse literal parser reconstructs **the entire JSON
object** from `P112Data.lean`; canonical serialization reproduces the pinned
13,183-byte JSON hash. `BINDING.tsv` inventories every JSON node, including
container shapes and empty rows. These are transport/value-binding checks, not
a formal JSON parser or a proof of the E8 constructor's geometry.

## Bounded replay after source review

Python 3.12+ and only the already-installed official Lean **4.30.0**, commit
`d024af099ca4bf2c86f649261ebf59565dc8c622`, are used. No package manager, network,
installation, `lake`, Mathlib, or elan-selected compiler is invoked.

```sh
cd /path/to/p112-lean430
python3 audit_sources.py --manifest
python3 check_numeric.py
python3 test_tooling.py
python3 replay.py \
  --lean /Users/andrejmas/.elan/toolchains/leanprover--lean4---v4.30.0/bin/lean \
  --output /tmp/p112-lean430-operator-replay
```

The output directory must not already exist. The runner checks `--short-version`
and `--githash`, copies the exact Lean files to an isolated source tree, removes
inherited `LEAN_PATH`, `LEAN_SRC_PATH`, and `LEAN_SYSROOT`, then sets only the
isolated `LEAN_PATH`. Each compiler call is literally the supplied executable
with `-o <fresh-output.olean> <source.lean>`. Actual stdout, stderr, hashes,
durations, axiom records, and any stopped unit are saved in that output directory.

There are **39 new positive units**, one unchanged dependency unit, and one
intentional compile-fail control. New source commands have nonzero bounds of
1,000,000 heartbeats and recursion depth 4,096. An external **120-second cap per
unit** and **600-second total successor cap** are enforced; only the unchanged
dependency stage is excluded from the total. No larger-limit retry is attempted.
Runtime feasibility within these caps is **unmeasured**, not promised. A timeout
is a stopped, incomplete replay, never a negative mathematical conclusion.

## Proof strategy and acceptance

One small adapter proves sparse left-row evaluation equal to the dependency's
ordinary finite sum. Balanced tables and balanced finite-index proof assembly
avoid long row lookup/assembly chains. Each ordinary `decide` proves one whole
row of 33 or 104 scalar equations; no dense whole-matrix `decide` is attempted.
Stages contain at most 16 MP/QP rows or 8 residual rows. The final matrix
identities are assembled using proved adapters and function extensionality.

`DECLARATIONS.tsv` lists all names and locations. All **477 new named
declarations** (457 theorems, 20 definitions) and the dependency's **159** names
have axiom queries: **636** records are required in a complete replay. Only
`propext`, `Quot.sound`, and `Classical.choice` are allowed; these are an allowed
set, not an observed new dependency list. Errors, warnings, missing `.olean`
outputs, missing/duplicate records, or other axioms stop acceptance.

`P112Damaged.lean` supplies proof bodies rejecting W[5,0] changed from +1 to -1.
`fixtures/RejectDamagedW.lean` must fail specifically because ordinary `decide`
rejects `1 = -1` after rewriting by proved entry values. An import, syntax,
missing-file, or unrelated failure is not an accepted control.

## Producer observations, not kernel evidence

Producer Python checks passed the exact input pins, full regeneration, inverse
literal parsing, all 21,409 scalar identity comparisons using ordinary dense
integer products, and the explicit W corruption (four residual cells differ).
All 14 tooling tests passed. Their parser-test strings are synthetic tests,
**not Lean receipts**. Exact executed commands/output are under `producer/` and
`PRODUCER_CHECKS.json`. Neither these checks nor Python itself discharge a Lean
proof obligation. The Lean control and new proofs have not been executed here.

## Inventory, scope, and credit

`MANIFEST.tsv` records exact UTF8 byte counts and SHA256 for every payload file,
excluding the manifest and checksum list themselves. `SHA256SUMS` additionally
covers the manifest and excludes itself. The separately delivered archive
receipt covers the ZIP and both inventory files; no self-hash is claimed.

This is source-bound corroboration of an existing numerical certificate and an
existing bridge, not a novelty, numeric rank, kappa, or multiplication claim.
No E8 geometry/coverage, P120, field/Units adapter, local Lemma 5, decoder K,
helper reduction, paid invoice, or frontier change is supplied.

Credit: PR1497/PR1610; Andrey Mas with substantial GPT-6 Pro through ChatGPT;
Codex source coordination, auditing, and operator replay. Retained lineage:
Brett Halligan/@burntout76 and Ninefold (PR1212), DreamingOfClouds (PR717), and
themilkman216 (PR968). New proof/source assistance is labeled GPT-6 Pro using the
operator-selected ChatGPT label. No independent human verification is claimed.
Apache-2.0; see `LICENSE` and `PROVENANCE.json`.
