# Executed finite-control CRT Beneš ROM producer

This closes a supplied-ROM boundary left by #4795/#4982/#5015. A single fixed
finite-symbol program reads encoded rotation descriptors, executes the retained
Beneš construction with encoded scalar registers and an explicit stack, writes
all canonical switch layers and one selected ROM row, and returns every head
with private backing erased. The actual selected row is handed directly to the
unchanged #4795 key service; its three current-state queries read those generated
cells. Output disposal is also executed. No new kappa is claimed.

The source fixture is h=3,N=8,s=5,offsets[0,2,4,0]: five 32-bit layers, including
the duplicate offset and padded wires. An independent retained source compiler
checks every bit. The same static program also covers variable h/modulus/list
length; the proof is for every finite nonempty offset list in the declared ABI,
not an inference from the fixtures. In particular a 17-element list works with
W=4: list traversal is marker-driven and has no W-bit count limit.

ToikY's #4192 already supplies the encoded arena schedule, explicit DFS stack,
canonical source equivalence and cell invoice. We retain that work and its
notice. Its simulator mirrors scalar control in host integers. This package
executes those missing decisions as literal single-cell instructions; no decoded
h, index, color, stack top, address or variable loop bound enters the runtime.
The Python assembler has no instance parameters. Interpreter positions and
verification oracles are observer machinery only.

## Contract and full local bill

Inputs use padded W-bit little-endian records with W>=h+3, 1<=s<=2^h and
offsets in [0,s). Four borrowed roles are distinct. The caller supplies a fixed
bank of blank owned tapes; the adapter creates those distinct roles and rejects
borrowed-role aliasing. It does not claim initialization of arbitrary dirty
borrowed storage. Successful output and cleanup are proved; malformed-input
rejection has no blanket rollback guarantee. The per-word bit reversal from
#4192's big-endian representation is explicit in [PROOF.md](PROOF.md).

The complete conservative instruction bound is
`10^6 W^2 (m+1) (N+1)^3 (h+1)^4`, including scalar/control operations,
full arena scans, both serializations and successful private cleanup. The full
arena, spool, selected ROM and complete layer output are retained in the storage
bound. This is not the old arena cell tariff and is not a comparison to E(p,ell).
A separate final erase scan disposes of both output roles after consumption.

The actual key ABI interprets the same 32 flat cells as 2 rows of 16, whereas the
producer writes 4 rows of 8. The adapter identifies the same tape, without a
host-decoded table rewrite. Five key cases preserve borrowed descriptors,
opaque stream prefix and ROM, with exact returned keys, all three query epochs
and private cleanup corroborated by the retained independent instruction audit.

## Reproduce

```
python3.12 -B scripts/research_package.py --package research/crt-encoded-benes-rom-producer
```

The verifier authenticates exact input bytes, checks the full generated output
against the canonical source, compares a frozen receipt, and rejects changed
neighbor routing, selected-row omission, output-disposal omission, malformed
headers/offsets and role aliasing. `--write-result` is the explicit authoring
mode; `--light` runs the bounded small cases without claiming the actual h3
fixture. Normal/optimized/source-history/export evidence is in VALIDATION.md.

## Open next questions

1. Bind the encoded current-child CRT descriptor producer to this input ABI,
   charging serialization and the actual requested row list.
2. Supply the variable-geometry key adapter and complete evaluator lifecycle
   bill before any E(p,ell) or global ROM-reuse claim.
3. Execute a fixed binary encoding of the complete marker alphabet if a literal
   binary transition-table certificate is required.

TASK.json gives first steps and blockers. This package does not run the full
2,944-hole repair, five-layer caller, global CRT/native/precision/outer transfer,
Lean, Docker or the selected scientific cold suite. It supplies one local
producer and an actual fixed consumer calibration, not full multiplication.

## Provenance and credit

Scientific base 4c0a359d88f22f05189d51f48387750b801a45d4, priority 7. Canonical
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19141162).
The final scout read 320 open PRs at 07:41:25UTC, 4168 Discussion records at 07:42:18UTC
and 6760 local notes with complete reported pagination/inventory; text overlap
is advisory. #5039's already completed thin-query task was excluded, as were
#5043's native fan rewrite and the fresh coded-p19/FOUR-base/compiler-width claims.
This does not repackage #5053's current-coordinate arithmetic.

Credit ToikY/#4192 for the arena/DFS construction and original notice;
Cinna Davis/#4100 for the Beneš and CRT source; Hiroki KUMAZAKI, unpaidmoon,
Ryanson Jonathan, Jose Manuel, John-Michael Smith, Douglas Colkitt and retained
physical-repair lineage. JoyboyBrian, with substantial OpenAI Codex assistance.
Apache-2.0. Separate agent review is not independent human or proof-kernel
acceptance. Frozen predecessor and selected-frontier files are unchanged.
