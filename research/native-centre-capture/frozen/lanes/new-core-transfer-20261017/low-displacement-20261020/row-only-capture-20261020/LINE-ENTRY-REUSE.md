# A local line-entry interface for sixteen stored centre rows

This packet changes the input contract of the frozen productive row capture.
It accepts sixteen independent records with their positive line phases. It
does not form or decode those records.

Let \(P\) be the fixed sixteen-port set in `PRODUCTIVE-CAPTURE.md`. Let
\(q_p=Q_p^{-1}\), let \(F_9\) be the exact full transform, and let \(C\) and
\(E\) be the pinned row code and native response. The physical inputs are

\[
 X_p=Q_px_p,\qquad
 Y_p=y_p\ (p\notin P),\qquad
 Y_p=Q_pz_p\ (p\in P).
\]

The records \(z_p\), all other data, and all 416 helper fields are arbitrary
and independent. The emitted outputs are

\[
 X_p=F_9x_p,\qquad
 Y_p=F_9q_p(y+Ex)_p\ (p\notin P),\qquad
 Y_p=F_9[z_p+(CEx)_p]\ (p\in P).
\]

The entry has no row precode. The word keeps the 96 ordinary target paths
from the formation packet. No retained event reads a selected target.
Each selected target starts in its exact canonical line chart and advances
to FULL with one rank-eight child. The word then executes the same pinned
FULL-source query as the formation packet. Thus the independent record is
preserved as an additive baseline. No assumption that a record is zero is
used.

The input adapter for each selected target is the pinned source adapter
for the same physical port, bound to the selected target field. The 16
new rank-eight recipes are derived from the exact ordered operation
\(\Gamma_{\rm FULL}\Gamma_{\rm line}^{-1}\). Both providers pass the
independent phase interpreter, including the global phase. The output
adapters and every retained native recipe are byte-exact inherited data.

For each provider the complete local invoice is:

| Item | Count |
| --- | ---: |
| Native profile | \(1392H_1+64H_2+48H_3+16H_8\) |
| Native mass | 1792 |
| Native children | 1520 |
| Scalar primitives | 9880 |
| Retained-core scalar primitives | 6456 |
| Late-query scalar primitives | 3424 |
| Input monomial views | 128 |
| Output monomial views | 96 |
| Native side-map upper bound | 3040 |
| Owned or private fields | 0 |
| Fixed odd-division scans | 0 |

The literal scalar/native boundary sweep has maximum content row one-norm
112 and binary denominator height one. This is a bound on register content
at those boundaries. It is not a bound for the internal implementation of
a recursive child.

`emit_line_entry_reuse.py` verifies every one of the 640 independent input
columns, the exact frame of every read and write, all final frames, and
the identity on all 416 helpers. It verifies the serialized output again.
A control that changes a selected input frame from its line to I fails.
Normal Python and optimized Python produce byte-identical payloads and
receipts.

Reproduce into new output directories:

```sh
python3 emit_line_entry_reuse.py --out replay-normal
python3 -O emit_line_entry_reuse.py --out replay-optimized
```

This is a local reuse interface with the same local reader \(C_P\). For a
reader retained from an earlier routed stage, the late query is
\(L_sE_t\), with its actual ordered source views. That query has a separate
word and invoice. In particular, the 9880 figure here is not its price.
The caller must also supply the stated positive line input on each stored
record and accept the stated FULL output. No complete supplier, recursive
hosting, or kappa improvement is claimed.

This result uses the controller's frozen row-code packet, the cyclic
native family, and the reviewed formation packet. The proof, emitter, and
checks were prepared with AI assistance.
