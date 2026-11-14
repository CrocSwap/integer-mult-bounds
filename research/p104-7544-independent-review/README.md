# Independent review of PR7544's conditional gain

Review exact [PR7544](https://github.com/CrocSwap/integer-mult-bounds/pull/7544)
at `d6be7d620c9c8337104daeb09fe01196eced5fe3`, conditional
κ = **0.003647969120276**, exact gain **0.000000888080587** over PR7481.
Construction credit remains with ToikY, DreamingOfClouds and the retained
lineage. This package changes no construction and selects no frontier.
[PR7546](https://github.com/CrocSwap/integer-mult-bounds/pull/7546) is a
newer, stronger separate proposal outside this exact review.

The added check compares **every one of the74 owned erasure operands before
CLEAR**, independently of the source checker. It specifies the one known
changed operand, owned1557 at chart595, rather than inferring equality from
public outputs after erasure. See [PROOF-REVIEW.md](PROOF-REVIEW.md),
[expected/REVIEW.json](expected/REVIEW.json), and [TASK.json](TASK.json).

## Scope and source closure

This is the donor's explicit independent-review assignment, a changed scope
from the p104-side-correction construction card. Main is pinned to
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision8. Earlier failed
construction attempts are closed and earn no gain or review credit here.

`inputs/pr7544.tar.gz` retains all74 exact source-package files, including
its nested proof-relevant archives and original notices. SOURCE-MAP.json
binds every path, size, SHA256 and Git blob to the inspected PR head. The
archive is actually used for cold source replay. ORACLES.json binds the two
unmodified PR7164 dense-oracle files. SOURCES.json pins the original card and
selected record as provenance; the pending PR commits are supplied as committed
source bytes, not assumed to exist in a shared Git object cache. Replay needs
no network. Source authenticity, replay and mathematical acceptance remain
separate claims.

## Replay contract and original failure

The original unmodified exact command passed locally in79.2659s. Its complete
command timed out at the registered595s cap after the native kernel passed
in371.0006s. The signed kernel was incomplete at termination. Raw logs and
receipts remain in evidence/. That run is a **timeout**, not a complete pass.
Every mathematical field of its completed native receipt was separately
compared with the source's authenticated expected receipt; only timings differ.
The source author's own successful execution is distinct from this run.

The review's stateless replay requires three commands: fresh native, fresh
signed/final, and independent audit. Each extracts the exact source into a
new temporary root. The native command regenerates and compares every native
mathematical field. The signed command consumes the authenticated frozen
native receipt, which the companion required command must freshly reproduce;
it regenerates the complete signed and final results. This explicit value
interface avoids dependence on a surviving temporary directory. Timing fields
are excluded from scientific equality only after their consumers are audited.
**The signed command alone does not verify a fresh native application.**
All three commands and their failure propagation are necessary for package
success. No science assertion, algorithm or expected mathematical output changes.

```sh
python3.12 -I -B research/p104-7544-independent-review/verify.py --stage native
python3.12 -I -B research/p104-7544-independent-review/verify.py --stage signed
python3.12 -I -B research/p104-7544-independent-review/verify.py --stage audit
python3.12 -B scripts/research_package.py --package research/p104-7544-independent-review
```

CPython3.12 with assertions enabled, NumPy1.26.4 and POSIX process groups are required (tested on Linux). Declared
caps are480s,495s,225s, total1200s; no concurrent artifact-regenerating jobs.
See EXECUTION.md for observed commands, outcomes and runtime boundaries.

## Evidence boundaries

The separate sparse checker covers1501 independent public inputs, all400MAIN
outputs,1101 helper identities, COPY zero destination and all74 pre-CLEAR
owned rows. The unmodified dense checker supplies a second exact endpoint,
grid and mass implementation. Seven current literal word corruptions, dirty
COPY, insufficient odd/dyadic grid and omitted paid-invoice controls must reject.
The actual fixed17caller is recounted from its bytes and priced with both
directed engines. Full physical maps, signed caller, ordinary work, precision,
tape, compiler and outer inequalities are checked by the unchanged retained
source kernels. Their reuse is not new implementation independence.

The five premises remain `native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape`, and `analytic_recovery`. The owned1557 operand is **changed**;
its acceptance relies explicitly on retained bounded arbitrary-content erasure.
The review supplies no stronger equal-operand restoration, compiled multiplier
execution, independent human review, formal-kernel acceptance, or maintainer
frontier decision. A passing finite package does not discharge these premises.

## Open next questions

Maintainers can review this exact conditional application and its explicit
erasure dependency; see the structured question in TASK.json. The selected
record remains unchanged. Stronger peer construction PR7546 needs its own
source-bound review. [Canonical investigation and handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19598697).

Credit and substantial AI-assistance disclosures are in [NOTICE](NOTICE).
