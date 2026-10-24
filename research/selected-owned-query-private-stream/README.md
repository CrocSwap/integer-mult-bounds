# Physical private streams for the selected copied query

This package implements the complete local private-stream lifecycle requested by
PR5039 for selected4470 QUERY_SHEAR event5: owned clear, full source copy, holding
across the completed child interval, signed addition into the original destination,
and full private-body erasure. The child, charts and translation remain named
completed contracts. No selected theorem or new kappa is claimed.

Two fixed tables contain243 preparation and248 resumption instructions on eight
physical ports per parent. They operate directly on the authenticated retained
`records.Tape` ABI: consecutive real/imaginary p-bit LSB-first two's-complement
records, a LEFT marker and BLANK field end. Runtime M,p are encoded binary
words; no host-decoded extent or payload is used by the controller. The optional
4096-bit optimized codec is not required.

For M complete complex records and N=2Mp bits, the written proof bounds local
work by256N+256 microinstructions and visited cells by8N+32, excluding the named
child interval. Retained backing is bounded by entry capacity K0 plus8N+32;
erasure does not reclaim old blank backing. Two suspended parents use distinct
slots and retain both private fields until their reverse-order returns. Original
source/descriptors/helpers are preserved and ADD writes the original Y owner.
Caller-owned initial LEFT markers remain unchanged. No runtime tape allocation
is performed by the instruction tables.

The signed addition is exact when inputs, child output and sums fit the declared
p-bit range. One extra guard bit above a common strict magnitude bound suffices.
Overflow is rejected; failure rollback is not promised. This local headroom
premise is not a selected global precision proof. Initialization/global reserve
and whole-child internal costs remain separate positive obligations.

## Evidence

[PROOF.md](PROOF.md) gives the all-width algorithm, component invariants, complete
transition ledger, entry-relative capacity and two-parent composition. The
verifier opens the existing authenticated nested source exports with original
notices and uses the unmodified original signed readers/writers. It binds actual
event5/stage2/pair0/source0/destination1 and port0 direction q=11. Its numerical
fixture has f=2 and one spectator axis (eight complete complex records), not the
entire selected enormous address space. A separate subset-convolution oracle
checks the named child's semantic fixture; that fixture is not child admission.

A second table interpreter matches every port endpoint and transition count.
Checks cover widths5,9,17 and an original-codec width4097 case, both signed
extrema, positive/negative overflow, two suspended parents, arbitrary retained
blank tails, source/slot aliases, wrong child head/port, borrowed-clear and
missing-erasure table mutations, short source and a missed spectator child.
The last control demonstrates the semantic premise rather than claiming runtime
verification of the child. Normal and optimized registered replay are read-only.

```
python3.12 -B scripts/research_package.py --package research/selected-owned-query-private-stream
```

Source authentication and Git-free export checks establish reproducibility, not
scientific acceptance. [REVIEW.json](REVIEW.json) records independent same-session
AI source/proof review at exact hashes; it is not human or proof-kernel review.

## Open next questions

The structured questions in [TASK.json](TASK.json) retain complete numerical-child
and normalizer admission, global suspended-parent allocation and entry capacity,
and selected precision/headroom. Local stream scans cannot discharge those
separate obligations. The predecessor's18480 logical records are not reinterpreted
as scalar instructions or a free physical allowance.

## Credit and source status

Base81e9bd69e4a5b00ba9c713a1620e36d576d5522e. Canonical claim:
https://github.com/CrocSwap/integer-mult-bounds/discussions/5009#discussioncomment-19142276

PR5039 at3a309011b648d6f84f9a92b97697f884cf4ae2aa supplies the selected operation
trace and logical charging theorem. Cinna Davis supplies PR4440/4470; zxv,
Mihir Srivastava, Ryanson Jonathan and the retained native/phase/controller
lineage retain their notices. David Arias/PR2776 supplies the exact finite
assembler, binary-to-unary macro and44n cost bound. The physical Gaussian tensor,
expansion/core/word/ring/record/session dependencies and all nested archive
notices remain unchanged and source-authenticated. Prepared by JoyboyBrian with
substantial OpenAI Codex assistance, Apache-2.0. No frontier files are modified.
