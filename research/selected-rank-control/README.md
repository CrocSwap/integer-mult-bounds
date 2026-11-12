# Produce the selected rank-one call control with paid cutoff and remainder hooks

This package supplies a fixed-tape control producer for a fixed compiled
rank-N word with P rank-one paid sites. It generates children of width
floor(e/N), applies a supplied root cutoff L, emits both pre- and post-remainder
hooks for e mod N, and restores every descriptor head and suspended ancestor.
The source-law connection is to the retained finite-precompilation and
batched-row notes at main
`e54523517d0f03e58352e647c403a5af3e525a57`.

The universal control bound is **200(P+1) sum_v e_v** literal transitions,
including all returns, rewinds and zero-remainder dispatches. Additional
historical backing is linear in the root width; the supplied cutoff and any
older backing are explicitly included in entry K0. The actual final selected
word, cutoff producer, row grants and payload consumers remain obligations.
**No new kappa and no discharge of a full framework assumption.**

## Two proved layers

| Layer | Exact control law | Tapes and complete control time |
| --- | --- | --- |
| General rank profile | Fixed m >= 2, ordered 1 <= r_i < m; child floor(r_i f/m); stop below m | Three; at most 100(s+1) sum_v f_v |
| Source-compatible final template | Fixed N >= 2 and P paid sites; child floor(e/N); stop below max(N,L); hooks B_r and A_r for r=e mod N | Four; at most 200(P+1) sum_v e_v |

[GENERAL-CONTROL-PROOF.md](GENERAL-CONTROL-PROOF.md) proves the finite remainder
transducer, parent-width stack, completed-call restoration and retained-space
bounds. Its historical filename `controller.py` refers to the byte-identical
`controller_reference.py` supplied here. The general example m=3, ranks (1,2,2)
has 281 instruction locations and seven symbols. No depth or call tree is
supplied. Time depends on the fixed paid-list length; backing is reused across
completed siblings.

[SOURCE-BINDING.md](SOURCE-BINDING.md) proves the exact rank-one specialization,
the cutoff comparator, remainder hooks and conditional node-volume invoice.
The N=3,P=2 program has 288 instruction locations, six symbols and four tapes.
The cutoff comparison costs at most 11 min(e,L)+10 and preserves L. A remainder
scan costs 6e+7; both scans cost 12e+14. Zero-remainder hooks remain explicit,
and consumers skip their remainder payload action. Nonzero remainder consumer
work is charged separately. Ordinary scalar/frame segments between paid calls
attach to the initial hook and return hooks in their source order.

The distinction between the two layers matters. The raw BIT note has child
width r_i floor(e/m), which generally differs from floor(r_i e/m). The final
precompiled word instead has rank-one paid leaves, where the laws agree. This
package does not substitute the general law into the raw mixed-rank circuit.

## Reproduction and evidence

Python 3.10+ and standard library only. From the repository root:

```sh
python3 -B research/selected-rank-control/verify_all.py
```

Expected status: `PASS_SELECTED_RANK_CONTROL_PACKAGE`. The wrapper executes
both suites normally and under `-O`, requiring byte-identical receipts. To run
each separately:

```sh
python3 -B research/selected-rank-control/verify_general.py
python3 -O -B research/selected-rank-control/verify_general.py
python3 -B research/selected-rank-control/verify_selected.py
python3 -O -B research/selected-rank-control/verify_selected.py
```

The bounded general suite covers 896 cases, 13,540 nodes and 3,469,732
transitions; nine translated cases use a separately implemented dense CPU and
ten controls target invalid profiles, wrong floors, wrong returns, leaked
scratch and false time bounds. The selected suite covers 2,400 cases, 10,878
nodes and 3,443,893 transitions; eight dense-CPU cases and eight controls check
cutoff equality, restored unary widths, both remainder hooks, cutoff motion
and the raw mixed-floor mismatch. Event logs are verifier observations, not
machine storage. Finite executions corroborate the written all-width proofs;
no formal proof-kernel acceptance is claimed. Receipts and exact artifact
hashes appear in `evidence/` and `VALIDATION.json`.

## Prior work and dependency boundary

[#5134](https://github.com/CrocSwap/integer-mult-bounds/pull/5134) supplies the
literal complete-row parking caller, and
[#5158](https://github.com/CrocSwap/integer-mult-bounds/pull/5158) already proves
fixed-bank dyadic complete-row recursion.
[#6719](https://github.com/CrocSwap/integer-mult-bounds/pull/6719) gives a richer
delayed-cover binary-root/grant/payload program from a supplied unary depth;
[#6722](https://github.com/CrocSwap/integer-mult-bounds/pull/6722) reviews a
particular producer/router join. This package claims the rank-dependent
online producer and exact final rank-one cutoff/remainder control connection,
not priority for fixed-tape recursion.

Pending [#7150](https://github.com/CrocSwap/integer-mult-bounds/pull/7150)
addresses primitive microcontrol; pending
[#7151](https://github.com/CrocSwap/integer-mult-bounds/pull/7151) addresses
stratified retained backing. Their inspected heads are recorded in
`SOURCES.json`. They are complementary references, not assumed merged
dependencies or substitutes for this package's missing payload integration.
The selected construction/review in
[#7000](https://github.com/CrocSwap/integer-mult-bounds/pull/7000) and
[#7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001) retains its
conditional kappa=0.00363005817.

Under an admitted complete-root-factor/row-stock interface, each width e_v is
at most complete node volume V_v, so control work fits the existing summed
node-volume bill. The premise does not produce the grants, execute remainder
kernels or prove frame/ownership contracts. Supplying L=ceil(d^beta) and the
root width from the actual external input is unpaid until a separate adapter
is provided. All five assumptions—native_all_columns, owned_erasure, compiler,
precision_tape and analytic_recovery—remain retained.

## Credit and next obligations

Prepared for @CubeJerry with substantial OpenAI assistance. Credit JoyboyBrian,
thu-nmrc, ToikY, commdata2338, Ali Romman, David Arias and the retained native,
physical and compiler contributors. New code and proof text are Apache-2.0.
The finite remainder transducer, depth-first stack and geometric bounds use
standard techniques; no broad algorithmic priority claim is made.

Next work is to implement paid external width/cutoff production, instantiate
the actual selected final paid-site list, and join chronological payload and
remainder consumers with exact complete-row, tape-frame and return contracts.
Those tasks remain necessary before treating this control lemma as an
implementation of the full selected dispatcher.

## Independent review

A separate reviewer read both proofs and executed a code-disjoint dense CPU
against an explicit address-tree oracle. It passed 125 cases, 837 nodes,
3,654 events and 488,423 transitions, checking actual widths, full ancestor
stacks, hostile exterior cells and 556 exact remainder-scan charges. Three
semantic mutants were rejected. From this directory run
`python3 -I -W error -B independent_check.py .`; see REVIEW.md and
evidence/independent.json for the complete independent receipt.
