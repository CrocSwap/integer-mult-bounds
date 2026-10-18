# Exact billing for binary digit swaps and address signs

PR2501's new AtomSwap and Sign primitives satisfy their claimed local
`C_q*w*V` movement bound on complete streams, including binary preparation,
bucket cleanup, input-word reads and head returns. This source-bound audit
supplies exact digit read/write/move formulas and an explicit conservative
constant for whole primitives. No predecessor defect was found.

For fixed odd prime q, the complete digit swap on
`[U] x [q] x [G] x [q] x [S]` uses at most
`(93V reads,27V writes,106V moves)`. The exact formula, rather than only that
upper bound, is checked. Whole M=q^w atom swaps and address signs use at most
`1,000,000*(bitlength(q)+4)^2*w*V` of each operation. The constant is deliberately
loose; this is a complete cost implication, not a faster primitive or tariff
improvement. [PROOF.md](PROOF.md) states the canonical-word and successful-call
contracts and derives the all-size bounds.

The original payload and all input words return unchanged. The result occupies
a separate owned V-bit output. At most 3V additional payload bits are live,
including that output. Erased lanes can be reused with q²+8 tape roles and at
most six extra fixed-width numerical word slots. Header/control state remains
charged separately by a q-dependent constant. This is a written allocation
schedule for the retained algorithms, not a new literal machine compiler or
a Python heap bound.

Independent formulas match 126 digit cases, including the S=1 shortcut and
unequal spectator extents. Fourteen complete atom/sign cases reconstruct the
origin of every output bit by binary index planes. Eighteen cardinality cases
and five binary-division cases include 522-bit inputs. Eight controls detect
wrong bucket order, missing sign/digit actions, missing erasure/head return,
omitted counter input traffic, incorrect shortcut billing and padded extents.
The all-size result rests on the written proof; finite checks corroborate it.

```sh
python3.12 scripts/research_package.py --package research/binary-digit-cost-audit
python3.12 -I -O -B research/binary-digit-cost-audit/verify.py
```

Use writable TEMP/TMP on restricted Windows hosts. Replay is read-only and
Git-free exports work; exact source bytes are authenticated before imports.
The receipt is compared in full with JSON types preserved. Tests reject actual
source, numerical/type receipt, duplicate/missing receipt and overwrite faults.

The scope is these primitive calls. Full selected residual assembly, coefficient
callbacks, fresh raw-prefix directories, recursive nonleaf children, global
hosting, machine compilation and supplier admission remain separate. There is
no new kappa, selected-frontier change, full selected cold replay, hosted CI,
formal-kernel or human-review claim. Meter counts do not measure Python runtime.

## Open next questions

Can the complete residual caller consume these primitive bounds with its exact
symbolic trace and all numerical page preparations? Start with one fixed-low
whole packet and retain separate adapter, child, directory and coefficient
charges. The complete selected caller and recursive child boundary remain open.

Can the reused tape-role schedule be compiled to literal finite-control
transitions? Start with the three nested Counter roles and q² digit buckets,
preserving the input and erase/return contracts. This audit supplies source-loop
counts and a role schedule, but no formal machine compiler.

Credit Jose Manuel / jmbarrancoml's PR2501
`52a995b9d7f3e008c252770a5f47fde67a7cb37a` for the unchanged digit/cardinality
implementation and prior big-O claim, and ywz65's PR2473
`677baf4c92e876530c9637db191e5fd92f62624f` for the unchanged Counter lifecycle
lemma and ADD audit. PR2449 supplies the retained word/record arithmetic;
the original source527 and predecessor notices are retained. The contribution
is an independent exact cost oracle, complete primitive accounting and lifetime
audit, not a new swap/sign algorithm. Prepared for ywz65 with substantial
OpenAI Codex assistance. Apache-2.0.

Canonical [claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2501#issuecomment-6194273149).
TASK.json records the scope change and bounded overlap coverage.
