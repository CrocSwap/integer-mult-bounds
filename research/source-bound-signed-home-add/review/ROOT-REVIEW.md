# Independent review of the signed packed HOME primitive

Reviewed against canonical `e54523517d0f03e58352e647c403a5af3e525a57`.
The author graph `add.py` has SHA256
`5534273103aacf26f0096e75b6c7ab5d8f3286f8b66f0b5d42ba8631e2c94e8b`.
The graph was not changed after this review. This is a separate AI review,
not independent human review or formal-kernel acceptance.

## Mathematical review

The fifth Gamma code supplies the width physically. Its unary prefixes sum
to less than the final width, so repeated doubling costs O(w). The other
five values are inspected as encoded strings; their numeric values are not
used as uncharged loop bounds. Complete admitted DATA is divided into w-bit
components using the physical width guide.

For subtraction, the graph complements the source bits and supplies initial
carry one. It never forms the negation of the signed minimum in width w.
At each bit the usual carry induction gives the low residue of target minus
source; the final original operand signs and result sign give the exact
signed-overflow decision. Only the final MSB decision is binding. Header and
source preservation follow directly from the write instructions.

All arithmetic occurs on B1 working copies. The only route to HOME scatter
is the successful primitive return. Thus late overflow preserves every HOME
although private work may remain dirty. Successful returns erase the unary
guides, restore operand/private heads, and leave only permanent origins.
The conservative 4096(F+1) primitive time and 8(F+2) history increment cover
the finite loops. B1 delivery, earlier history and supplied frame/grid/packet
construction are still separate obligations.

The current selected application's sections 2 and 4 were checked at their
exact source pin. Exterior rational coefficients are unchanged with column
multiplicity. The source -1 contacts therefore mean subtraction for even f
as well as odd f. Native phase tensoring is a distinct convention. This
binding does not establish the actual packet producer or full caller.

## Executed independent checks

`check_signed_add_root.py` uses a separate sparse-tape interpreter with
signed, distinct origins and opaque left/far sentinels. It does not import
the author interpreter or checker. Expected arithmetic uses unbounded
integers and one final signed-range decision. The graph builder itself is
loaded from source bytes; its retained inputs are pinned by the builder.

The checker exhausts all signed source/target pairs for widths 2 through 6,
both operations: 10,912 local component-entry cases. These are component
contract checks, not complete Gamma packet executions. It separately runs
six genuine complete packets, including 4,096 and 12,288 components, both
signs, nontrivial r/P/S, and a 257-bit cutoff. Four successful runs restore
all six heads and private bodies and have zero early HOME writes. Two late
true overflows reject after private arithmetic with zero HOME writes.
A mutated subtraction graph missing its initial carry fails zero minus zero.

The exact selected archive was also re-extracted read-only by the author
replay at publication review: its full gzip and canonical word hashes,
five contacts, and qualified owned-lifetime endpoints passed. The retained
source review's Git blob and bytes were checked against canonical main.
The two author identity fixtures start at already-reserved typed body entry;
they do not create full #7423 compiler addresses or selected productive width.

From the repository root:

```sh
python3 -I -W error -B research/source-bound-signed-home-add/review/check_signed_add_root.py
```

Expected marker: `PASS_ROOT_SIGNED_HOME_ADD_REVIEW`; the complete receipt is
`review/RESULT.json`. The author replay and optimized replay are documented
separately. No new kappa or discharge of a complete framework assumption is
claimed.
