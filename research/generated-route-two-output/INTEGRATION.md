# A reviewed producer and its read-once obstruction

This additive sibling package extends #8092 at exact parent
`6a3437d1cd94dc4e1792f4052511af6160120bf9`, retaining canonical source
`e54523517d0f03e58352e647c403a5af3e525a57`. Every earlier file is unchanged.
The scientific author and independent-review files are bound by
`PUBLICATION-FREEZE.json`. Accepted proof SHA256:
`5de0684584f6fd9fe80cfa91b1c6ac24f9ca408ca6e59ff1ac11c758acfe40ae`.

## Mathematical content

For every word generated from the retained admitted seeds, every odd q>=3
and supplied canonical low matrix g0, the producer computes both
`h0=g0 S mod q` and exact dyadic `C=(g0 S-h0)/q`. It uses no dense S or
table of low matrices. A first pass retains only fixed-size quotient and
residue state; a second pass emits the complete low word, including the
necessary zero flush. The actual 94-addition/15-scale alphabet needs at
most 54 quotient comparators and a 388-bit first-pass logical state per
fixed column type, plus a fixed dispatcher tag. Growing outputs are data.

For m arithmetic instructions, the common carry-denominator exponent is
at most 5m and signed work width at most 6m+5. The explicit sequential
invoice is `O_source(N^2(ell+1)[B+W+log(2N)]^2)` bit work and
`O(N^2(B+W)+ell log(2N))` data space, excluding supplied input. Input scans,
head return, affected and unaffected register updates, initialization and
ordinary destructive retirement are charged. This is an algorithmic tape
access proof, not an executed physical payload route or Python memory claim.

The coherent second result concerns the coefficient-one shear `x <- x+y
mod q`, with two unknown synchronized channels, read-once input and
irreversible canonical LSB-first output. For every odd q>=5 and
B=bit_length(q), at least `2^(B-2)` retained states are needed. The proof
uses ambiguous first-output parity and distinguishable common continuations;
all accessible input-dependent work and head-position state count. It makes
no lower-bound claim for rereads, revised/differently ordered output, other
access contracts, or the full route problem.

## Reproduction and separate review

```sh
python3 -B scripts/research_package.py --package research/generated-route-two-output
python3 -B scripts/check_research_commit.py --package research/generated-route-two-output --check-modes
```

The launcher authenticates frozen scientific files, runs normal and optimized
children with fresh private bytecode caches, and compares new JSON to immutable
receipts. Author regression covers 17,411 local cases, 40 long streams through
4,097 bits, 900 q-power reconstructions and 35,912 full ambient coordinates.
The independent reviewer uses modular inverses as an oracle, separate rational
right matrices, transition intervals and distinguishability arguments; it
does not run the author checker. Its evidence covers 14,855 local cases,
55,584 transition corners, 24,489 prefix-register checks, 75 dense/inverse
cases, 35,912 ambient coordinates and 87,380 prefixes at all 510 odd radices
from 5 through 1023. Both modes agree. Omitted flush, wrong signed division,
missing denominator shifts, source corruption and scope controls are detected.
Eight retained sources were independently resolved and byte-compared with
exact commit/path sources. Finite checks corroborate the written universal
proof; they do not establish it by extrapolation.

## Scope and credit

The carry cocycle, the two mathematical outputs and table-free G20 evaluation
are already in Ali Romman's #5841. #6474 and #6503 provide carry-only local
state machines; #8092 supplies the generated grammar/alphabet. The new work
is the complete two-output stream for that actual alphabet, composed widths
and access invoice, and the specific one-pass obstruction. Prior serialized
carry-only lower bounds have a different access/output model.

High-payload reduction, fiber ordering, native supplier admission, owner
return and the complete multiplication tariff remain separate. The selected
certificate and all five canonical assumptions are unchanged; **no new
kappa** or unconditional multiplication theorem is claimed. Prepared for
Jerry Chen / @CubeJerry with substantial OpenAI assistance and separate
model-assisted author and reviewer roles. Original notices and Apache-2.0
attribution are retained. Hosted CI and full-history ancestry are not claimed
by the local registered/byte checks.
