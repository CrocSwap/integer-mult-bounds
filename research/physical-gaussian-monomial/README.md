# Physical Gaussian monomial with encoded controls

I implement a complete Gaussian monomial on sequential bit tapes using encoded
numerical controls and one reusable physical Compact inventory. I preserve
borrowed input and descriptors, enforce phase-specific signed headroom, traverse
each coefficient field and return owned work blank. I retain the selected
frontier without modification.

The binding complex caller needs both address movement and unit phases.
[PR3055](https://github.com/CrocSwap/integer-mult-bounds/pull/3055) completed the
physical Compact primitive and left this phase/record boundary open. I add:

- Encoded accumulation of the repeated quadratic phase modulo four, guarded
  fixed-width Gaussian traversal, and forward/inverse affine composition.
- A quantified endpoint and cost argument in [PROOF.md](PROOF.md), together
  with complete finite packet checks and source/semantic/ownership controls.

I fix the field vocabulary and recipe at compilation. I keep f,K,G,rho,
component width, coefficient count, field widths and outer-row count on Count
tapes during execution. At f=1 I avoid scanning the unused G descriptor;
I still count its storage among borrowed inputs.

## Evidence and reproduction

From the repository root, use Python 3.12 and the bounded registered replay:

```sh
python3.12 scripts/research_package.py --package research/physical-gaussian-monomial
```

The eight commands check signed pairs and encoded phases, signed rejection and
reuse, generic/selected/spaced complete packets, and eight failure controls.
The arithmetic and failure commands also run with assertions disabled.
I completed all eight registered commands on Python 3.12.13, macOS arm64,
at 23:04 UTC on October 16, 2026. I have not claimed a hosted CI pass.
[RESULT.json](RESULT.json) stores SHA256 receipts of complete typed results;
[verify.py](verify.py) authenticates live inputs before importing execution
code. [SOURCES.json](SOURCES.json) pins the immutable source archive and its
transitive external inputs. I do not rerun unrelated historical suites or Lean.

| Check | Scope |
|---|---|
| Signed components | 1,344 pairs over widths 2,3,4 and four phases; 109 exact signed rejections |
| Encoded phases | 580 cases; all 512 selected one-column addresses and tensors up to 65 columns |
| Selected recipe | `0:1000.right`, nine coordinates, 22 gates, two complete rows, one dirty spectator bit, three Gaussian fields, 36,864 payload bits |
| Generic monomial | Complete two-column packet, then one-column reuse of the same inventory |
| Spaced monomial | Complete two-column rectangle with K=2, rho=1 and unselected wide bits |
| Rejection/reuse | Most-negative imaginary component in the last coefficient field; valid retry on the same inventory |
| Unused G | One-column execution with a 4,097-digit G and a bounded read-head probe |

I use a leading `1+0i` field as an orientation anchor and encode distinct
row/address labels in the remaining Gaussian fields. I compare exact integers,
not only a forward/inverse byte roundtrip. I disable indexed reference
execution during the physical checks. I rely on the pinned source arguments
for the universal Compact/B1 behavior; the small full-packet fixtures take its
elementary ordinary branch.

For fixed recipe/schema, with the notation in PROOF.md, I obtain

    S*sum_rows T_B1(v0,(f-1)G)
      + O((g+1)*(V+M*A^6) + g*delta*M*A*(R+A))

at f>1, and `O(gV+M*A^6)` at f=1. I separate owned workspace, borrowed
descriptor storage and backing retained from earlier calls. I claim a written
source-relative refinement and finite replay evidence; I have not completed
the selected recursive caller or a formal machine proof.

## Open next questions

1. Bind one actual complex local invocation to this Gaussian interface. A
   caller needs exact coefficient arithmetic, its common grid and headroom.
   Start with stage 0, replica 0, pair 0, events 9394–9395: directed child 7
   on L224, then addition from L0. PR2534 supplies the selected interval and
   its earlier fixture. Record each coefficient's width and signed bound
   before invoking the monomial. The current complete recursive coefficient
   implementation remains the blocker.
2. Join proper-width child dispatch and private lifetimes to the physical
   primitives. This determines whether a full recursive caller fits its
   invoice. Start with one actual child call and check zero-on-entry,
   chronological return and disposal. Retain the independent all-size source
   obligations while constructing that execution.

I record structured scope, stop rules and questions in [TASK.json](TASK.json).
Canonical coordination:
[Discussion2238](https://github.com/CrocSwap/integer-mult-bounds/discussions/2238#discussioncomment-18984090).

## Attribution and limits

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance in the
mathematics, implementation, source analysis and prose, including analysis
subagents. Apache-2.0, with retained source-specific notices inside the frozen
archives. I claim no independent human or proof-assistant verification.

I retain Douglas Colkitt's Compact, affine-word and complex-layer work through
PR2250/2287; the contributors to PR2378/2422 supply the coordinate, signed-word
and coefficient-field semantics; PR2534 supplies the earlier selected-child
execution. PR2899 and its credited C0 predecessors supply the physical ordinary
contract. PR3055 supplies the physical Compact join. I pin their heads and
attribution in SOURCES.json and preserve the nested source archives unchanged.

I do not promote archive retention to scientific admission. I leave the root
precision proof, complete recursive execution, analytic transfer and any new
exponent to their respective obligations.
