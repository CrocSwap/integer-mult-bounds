# CRT last-K tail: conditional sequential lowering

This supplies an independently executable lowering of the elementary
last-K branch in Cinna Davis's [PR4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100),
`CRT.md` Section 4. The original bit exchange, transformed control and
complete suffix amortization belong to that predecessor. No new kappa
or complete multiplication theorem is claimed.

[PROOF.md](PROOF.md) gives an explicit fixed-tape schedule: move a target
to the last bit before an omitted H-bit suffix using the assumed ordinary
width-one interchange, prepare the transported Boolean control once per
prefix, stage two **complete** suffix slices on two reusable tapes, write
them in original or exchanged order, erase/return, then exchange back.
It works for arbitrary controls depending on every other non-reservoir
bit and for every dirty address.

For `M=2^L` records of R bits, `V=MR`, it uses exactly
`M/2^(H+1)` preparations and at most two paid width-one exchanges.
The middle stage's four payload tapes take exactly `13V` read/write/head actions
in the stated model, including input/output head returns; counters,
markers, evaluator and ordinary callee costs are separately charged.
The middle stage's extra payload scratch is two complete slices,
`2^(H+1)R` bits. Full visited space also includes a constant number
of V-bit streams, the ordinary callee's workspace and the evaluator
workspace. The tape inventory stays fixed across all prefixes and targets.
The full pipeline preserves the original source and returns an owned
output; erasing and returning its two private intermediate V-bit streams
adds O(V), outside the middle-stage `13V` invoice.

Conditional on the source's `E_*<=C 2^(4 ell)(p+2)^16` evaluator bound,
the placement/support contract, `H>=64(ell+ceil(log2(p+2)))`, and the
ordinary width-one callee's O(V) bound, preparation is amortized over
the complete omitted suffix. Each exception costs O(V), and at most K
exceptions cost O(VK). The new proof includes a conservative O(L²)
coordinate/descriptor reconstruction charge inside preparation.
The evaluator premise is uniform and includes reading supplied encoded
parameters; no size-specific advice or uncharged control oracle is admitted.

## Evidence

[verify.py](verify.py) authenticates the exact three predecessor inputs
listed in [SOURCE-PINS.json](SOURCE-PINS.json), compiles the authenticated
caller bytes directly and reproduces [RESULT.json](RESULT.json):

- Every Boolean function on up to three permitted source bits across
  40 target/suffix layouts: **4,328 cases**, **252,060 dirty-address
  endpoints**, each replayed forward and inverse. Suffix widths include
  0 through 3. The exact preparation and payload-only invoices are checked.
- A **source-bound root-axis control projection**, using the retained
  CRT Beneš control algorithm for axis 3 with
  moduli `(3,5,7,11)`, after moving the unused axis-2 reservoir to the back:
  **all 4,096 dirty padded addresses**, **7 layers**, **114,688 target/suffix
  omission checks**, exact forward root-axis rotation and full inverse.
  Each layer uses **256 preparations**, rather than 4,096 per-record
  preparations. This small geometry uses suffix-only transport and is
  below the large-family cutoff. It does **not** execute the full
  three-reservoir placement/allocator or identify a production tail set;
  its targets need only satisfy the general lemma's `q<L-H` condition.
- Semantic controls detect a stale control transform, missing inverse
  exchange and a function that depends on the supposedly omitted suffix.
  Four admission controls reject incomplete rectangles, targets in the
  suffix, non-Boolean controls and oversized payloads. An exact-count
  control detects the per-record E tariff regression. Four integer
  parameter examples corroborate the symbolic amortization inequality.

The direct array exchange in the finite test is an **endpoint oracle
for an assumed ordinary callee**. It is not a claimed sequential
implementation or part of the payload tape invoice. The universal
cost comes from the conditional written proof, not Python timings.

## Reproduce

From a source export retaining the repository-relative paths:

```sh
python3.12 -I -B research/crt-last-k-streaming/verify.py
python3.12 -I -O -W error -B research/crt-last-k-streaming/verify.py
```

The six commands in [VERIFY.json](VERIFY.json) also run the separately written
[endpoint oracle](independent_tail_check.py) and the source-pinned
[one-bit payload control](r_one_payload_check.py), each normally and optimized.
The endpoint oracle checks 2,164 cases / 1,209,888 address columns; the one-bit
control checks 15,016 cases / 119,440 records. Review provenance and resolved
findings are in [PRIMARY-REVIEW.json](PRIMARY-REVIEW.json).

Standard library only. Verification compares the stored receipt without
rewriting it. `--write-result` explicitly regenerates the receipt.

## Open next questions

Bind the source's full numerical E evaluator to its actual sequential
implementation, including transported split-axis descriptors, all
head returns, erasure and a fixed tape inventory. A feasible next step
is to instrument a literal control-array scan simulator at one actual
CRT layer and reconcile its instruction families with the Section 2
bound. The present callback and finite source tables do not certify it.

The ordinary interchange callee, global reservoir allocation, compact
word/exceptional repair, total CRT budget, precision, outer multiplication
theorem and selected-frontier certification remain separate obligations.
Complete suffix reuse cannot pay preparation at incomplete sparse bad
holes. No selected record or predecessor source is changed.

## Credit

Cinna Davis supplies PR4100's original elementary last-K construction
and E/reservoir amortization. Hiroki KUMAZAKI (@kumagi), PR4174, supplies
the caller-specific reservoir and split-coordinate context and explicitly
leaves this tail branch open. PR4169's arbitrary-source repair is
complementary work and is not imported. Douglas Colkitt and OpenAI's
stream/ordinary-interchange framework, Vlado Vojdanovski's PR1673 routing,
Jose Manuel's physical support routing, and the retained compact-control
lineage keep their predecessor credit; see the pinned source NOTICE.

This contribution adds the explicit conditional two-slice sequential
lowering, tariff and independent corroboration. Prepared with substantial
OpenAI Codex assistance. Apache-2.0. No independent human review or
proof-assistant formalization is claimed.
