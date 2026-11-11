# Independent review of encoded balanced CRT node entry

**Scoped pass after two review corrections.** Reviewed author commit:
`addb3c9a404df9a5a7b7543ae2984477db784233`, scientific base
`e54523517d0f03e58352e647c403a5af3e525a57`. The portable receipt pins the
proof, frontend and source manifest, plus all twelve `usage: input` source
files. The reviewed PROOF.md SHA256 is
`85af742286dc6ee90ea6671877682607d204979025c122aee509c5cded8957af`.

This is a separate OpenAI research-worker derivation and implementation,
prepared for @CubeJerry. It is not independent human or proof-kernel review.
The checker does not import the author's verifier, fixtures, record decoder,
node-order generator or arithmetic oracle.

## Corrections required and resolved

The first proof asserted at most 32 finite-control instructions between raw
Port operations without defining and counting that expansion. Boundedness
alone did not prove its numeric coefficient. The corrected proof retains
`2^16(M+2)^2` only as a raw read/write/unit-move allowance, and uses a fixed
input-independent `C_front(M+2)^2` for complete frontend source operations.
The new code has fixed procedure depth and finite role vocabularies; its
variable loops perform local tape actions, so such a constant exists in the
stated source model. No explicit full-control coefficient or literal binary
TM tariff is certified. The inherited numerical tariffs remain inherited
contracts, rather than a new independent audit of every predecessor constant.

The corrected theorem also requires a linear current-lease protocol.
Consumed leases and output aliases are relinquished before the next node.
Python's per-object `closed` field is not a physical service for validating
unbounded old handle identities. Immediate current-phase errors can use a
finite phase state and incur their own fixed cost. Same-bank restart of a
whole iterator is outside the implemented lifecycle. These are substantive
scope restrictions, not assertions that stale-handle generations are encoded.

## Universal source reasoning

The count tape is reduced by adjacent pairs. A finite parity bit rejects
an odd count greater than one; the number of successful reductions is the
encoded depth. At level size 2H, STEP is the unique unprocessed aligned
start. Reading H records to each side places VALUE exactly at the next start,
if one exists, while retaining STEP until the actual numerical result retires.
Advancement clears the old STEP, promotes VALUE, or advances the depth and
doubles H after the rightmost node. The doubling appends a physical copy
of the previous H tokens, so no numerical half-size is supplied by a host.
This establishes every level and the final root, not only tested trees.

The actual old #5353 projection at synchronized row zero activates every
right axis because ell>=2. Its canonical two-word records are uniquely the
low-first binary encodings with high zero padding removed, retaining one
zero bit for zero. The new scanner constructs exactly those records for the
selected intervals and adds one guide token after their widths. This gives
P_G=1+sum_G h_i, the same canonical inputs and guide consumed by the unchanged
Entry. Bank.open still acquires three canonical/guide roles, then 56 private
words, one template and three padded streams. All geometry positions are
None, and the bridge rejects any supplied geometry. Compatibility follows
from these actual bytes and acquisitions, rather than an abstract node list.

Source bytes are never written, including the old tail after its RIGHT.
The source head is restored before handoff. Eight guide-manufactured protected
words have the current exact width and are retired before a later guide.
The same 63 bank, eight guard and seven topology arrays are reused through
one lifecycle, with no shrinking or identity replacement. The separate
historical role envelope simplifies to

    owned backing <= 3dA + 71A + 19d + 221.

The complete supplied source adds K_source, not just its logical length M.
With h_i>=2 one has d<=A/2; hence the owned envelope is O(A^2), while an
arbitrarily large supplied source tail must still be charged. The predecessor
role bounds count retained allocated arrays; reads of a virtual next blank
do not allocate that cell in this model. No Python heap bound is inferred.

## Independent raw-action accounting

Expanding the actual Port methods gives at most `24h+46` actions for a skipped
record and `39h+72` for a selected/copied record. These include width creation,
all returns, two complete padded field scans, canonical trimming, and width
retirement. They are below the author's `64(3h+4)` allowance. The separate
checker reaches both bounds on all-zero local record bit patterns; those
shape-only zero-modulus calibrations are not claimed as admitted CRT inputs.

For each protected word, the exact preparation count is `9P+14` and retirement
is `5P+15`. Their sum is `14P+29`, including repeated guide scans and rewinds.
The checker reproduces this exactly at precisions 5,31,6,127,5 on the same
historical guards. It rejects a bill smaller by one action per word. The
remaining source/axis/counter scans and input retirement fit the loose
`512(M+2)` per-node raw allowance; root shape/final cleanup have the same
allowance. Pairwise reduction scans fewer than 2d count tokens. Direct half
doubling costs at most `23H+33` actions, whose completed-level sum fits the
stated `128(d+2)` allowance. Thus the advertised raw quadratic envelope is
safe, including rightmost source seeks and final retirement.

For the inherited numerical sums, writing ell=t+2 gives nonnegative
coefficients for
`7*715*(t+1)^4-8*(t+5)^4` and
`32*(t+1)^2-2*(t+4)^2`.
The checker derives these coefficients by binomial expansion. Together with
the exact dyadic geometric series they justify the 715p^4 and 32p^2 bounds.
They do not assign a numerical value to C_front or prove the complete CRT
permutation tariff.

## Executed independent coverage

The 63 observed node handoffs are intentionally divided:

* **57 topology/substitution nodes** in trees with 2,4,8,16,32 axes use the
  unchanged Entry and Bank with a clearly labelled dummy numerical producer.
  This isolates the cursor, canonical-input and lifecycle proof without
  repeating the author's entire expensive arithmetic suite. The expected
  order comes from root-interval breadth-first subdivision followed by
  bottom-up layers. Every node is checked for exact canonical bytes, guide,
  STEP/VALUE positions, rightmost flag, protected current width, no fresh
  Port construction, source restoration and all 78 rolewise history bounds.
* **Six actual numerical nodes** in two distinct four-axis trees invoke the
  unchanged numerical producer. A direct Chinese-remainder sum using modular
  inverses supplies the oracle, rather than the author's exhaustive search.
  One tree has valid current coordinates and a nontrivial two-axis CRT lower
  value; the other exercises invalid-left disabling and padded right values.
  The actual lower/product words and every P-bit output word are checked.

Every source has a nonblank inaccessible 37-cell tail, which remains unchanged
and is included in K_source. Separate tests reuse eight guards across both
increasing and decreasing precisions and check their exact action counts.
Sixteen local record calibrations use widths 2,3,9,257 and both extreme bit
patterns. The three controls detect a missing pending VALUE, reject a
nondyadic source with all 78 histories and the source restored, and detect
an understated guard invoice. These finite checks corroborate the source
reasoning; neither 32 axes nor 257-bit fields is a universal-search limit
from which an asymptotic theorem is inferred.

Executed with CPython 3.12.14, standard library only, 2026-11-10:

```sh
python3 -B coordination/review-node-entry/independent.py \
  --package-root wt-crt-control/research/encoded-balanced-crt-entry
python3 -O -B coordination/review-node-entry/independent.py \
  --package-root wt-crt-control/research/encoded-balanced-crt-entry
```

Both read-only runs returned:

    PASS_INDEPENDENT_BALANCED_ENTRY 63 78 6 3

`--write-result` is the sole receipt-regeneration option. When copied to the
package's `independent-review` directory, the default package path is portable;
otherwise pass `--package-root`. Provenance-only selected/catalogue records
are not mistaken for immutable live scientific inputs.

## Remaining scope

No encoded row/target selector, h/layer ROM-header producer, source-coordinate
update, three-epoch transport or complete payload permutation is supplied by
this package. No whole-iterator reusable-bank restart, stale generation
service, arbitrary exception rollback, external consumer cost or source
production workspace is absorbed into its 78 roles. The fixed source-model
control factor C_front remains unspecified numerically, and binary lowering
of inherited arithmetic remains separate. All five foundational assumptions
and the accepted conditional kappa retain their status. Within the corrected
numerical-node, one-lifecycle, linear-use scope, no unresolved core defect was
found by this review.
