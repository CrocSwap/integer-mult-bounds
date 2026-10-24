# The same physical interface with scaled-query gauges

This version keeps the maps and native words in `STRUCTURED-TRANSFER.md`.
It binds the separate coherent gauge source in
`controller-followthrough-20261017/structured-centres/GAUGES-V2-FREEZE.json`,
whose SHA-256 is
`deea4844f2327a73129c213df915819ec845fb9c97a30498d43f231a2267e733`.
The new gauge receipt has SHA-256
`6b2e61547261ef28c8f08a29bc0cf5f681fe44ab6676e9530cc411c35d36a65c`.
The first physical-transfer packet and its source remain unchanged.

Put the dyadic scale on C0 before each signed-unit scatter. For H, scale
the query by `1/2`, scatter, then scale C0 by `-4` before subtracting the
updated query. For H inverse use `1/4`, then `-2`. For the two full data
maps use `1/4`, then `4`. These changes preserve coherent restoration:
each query returns to zero by exact subtraction from the current data.
They do not use CLEAR to erase a nonzero query.

The source checks all gauge maps independently and proves that the maps
equal the preceding gauges. Its 48-port costs are now 1,172 for H,
1,172 for H inverse, and 2,368 for each full data map. The complete
physical transfer also replays these actual scalar words.

The fused selected update in the backward inverse uses the scaled C0
already present. Its 48 extra ADDs now have signed-unit coefficients.
Thus it adds 384 primitives. This still implements
`-K_S^T K_U X_U/4` at the same point as the preceding version.

The complete bills are:

| Operation | Scalar primitives |
| --- | ---: |
| H on current ordinary Y, with admission | 3,222 |
| H inverse on completed ordinary X, with frame resets | 3,224 |
| H inverse with selected upper update | 3,608 |
| Full data map or inverse on completed X | 4,420 |
| Balanced backward native word | 91,208 |
| Diagonal backward native word | 91,592 |
| Diagonal backward word with full data inverse | 96,012 |
| Balanced forward native word | 91,830 |

Each native word still has rank mass 5,073 and 3,507 native children.
It uses no new native child or private field. The complete words restore
408 arbitrary helpers and all 91 private zero buffers, and leave all
eight owned fields zero. All 640 formal input columns pass on each
provider. The checker also requires C0 to be zero before each later
frame-reset CLEAR, executes both literal full-data inverse orders, and
checks the normalized backward word as one complete native computation.

The raw backward and forward words are unchanged at 87,984 and 88,608.
The physical Q order, the selected source identity on productive Y,
and all local interface formulas are the same as in the first packet.

Run with new output directories:

```text
python3 work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/structured-centres-transfer-20261018/emit_structured_transfer.py --gauges scaled --out-dir /tmp/structured-scaled-normal
python3 -O work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/structured-centres-transfer-20261018/emit_structured_transfer.py --gauges scaled --out-dir /tmp/structured-scaled-optimized
```

Each run must end with `PASS_STRUCTURED_CENTRES_PHYSICAL_TRANSFER` and
payload hash
`ea140f936e4832d19db406bada5d4ab12ec6ea1dfc0d6e3e3a4c86991414ee2b`.
Normal and optimized runs must give byte-identical receipts and payloads.

The scale-placement change was proposed in this lane. The controller
lane emitted and proved the coherent gauge words. This packet binds
those words to the complete physical interface and checks both native
providers. The source and earlier interface credit in
`STRUCTURED-TRANSFER.md` also applies. This is AI-assisted research.

This result does not prove routed-stage code transport, caller exterior
phase, complete precision, storage hosting, or the supplier recurrence.
It makes no complete kappa claim. No PR, commit, or push is part of this
work. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
