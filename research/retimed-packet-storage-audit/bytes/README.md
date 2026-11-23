# Ordinary route bytes and repair-tag extents

Pinned source: PR #8042 head
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`.

The main result in `PROOF.md` is a universal bound on the sum of fixed-role
historical byte endpoints for an installed wide owner route:

`L ≤ V + 5P + 5T + (32/3)R + 5b < 8V`.

`V` is the actual complete owner; `P` is one complete low group, `R` one
complete high packet, `b` one body and `T=QN²` the literal tag bytes. Borrowed
banks, suspended prefixes and earlier-stage work retain their separate
actual charges. The proof counts distinct roles even when their maxima are
not simultaneous. The padded type route has a separate `<9V` byte bound.

The repair appendix proves a source-specific `≤8V` bound including the
input and replacement Gaussian fields. It binds tag width to the actual
successful production `Product` header, includes the intervening H widening,
and preserves the resulting component size through descendants. A small exact counterexample
shows why tag-to-payload dominance, and the resulting individual dirty-spool
bound of twice the field volume, can fail for an arbitrary generic repair
field: a 17-bit field with two-byte Gaussian records and no grouping has
three-byte tags. That example does not arise under the production header.

## Run

From the repository root, use the enclosing driver for a fresh offline
restoration and all author/review checks:

```sh
python3 -B research/retimed-packet-storage-audit/verify_supplements.py \
  --output /tmp/retimed-owner-byte-results
```

The driver runs this supplement in a temporary copy, preserving its committed
evidence. The standalone `verify.py --runtime RESTORED_RUNTIME` binds all
resolved source hashes, reproduces the retained site
inventory, runs the actual-file traces and three in-memory mutation
controls, and writes `evidence/RESULT.json`. The full high-packet fixture
uses 2,834,352 bytes per owner, including all 27 genuine high representatives
for each of 16 lows. It runs four serial route/inverse calls while parent
pages and a neighboring full owner remain dirty. The rank-three fixture
checks odd radix-pass parity. Isolated scaler tests cover digits zero
through seven with an independent permutation oracle.

`sources/` contains exact resolved source bytes, not edited replacements.
`SOURCE-BINDINGS.json` records module digests. `ROLE-INVENTORY.json` records
the source's 20 named heads and 91 work-file tuple positions. The retained
source's chosen body coverage is inherited and explicitly distinguished
from the new byte argument.

## Limits

This is a local byte-census contribution. It does not re-prove the analytic
mass certificate, Gaussian owner census, movement payment, macroheight
count, full remaining ordinary/outer census, private-control allowance or
the complete multiplication threshold. The next source obligation is listed
at the end of `PROOF.md`. Wave-one and wave-two files remain unchanged.
