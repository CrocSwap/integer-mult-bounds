# Local sprint claim

- Route: P104 complex frame-pair decoder delivery.
- Base: `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`.
- Author: Ali Romman, with substantial OpenAI Codex assistance.
- Object: terminal-read antichains for all 7168 mixed frame-pair decoders
  on the 896 admissible P104 punctures relative to the coordinate frame.
- Method: exact support census, antichain and chain-cover certificates,
  a frame-distance proof for asynchronous delivery, and a price check on
  the selected T37 profile.
- Deliverable: a scoped obstruction for term-preserving delivery carriers.
  The proof will permit independent target orders, extra frame directions,
  and paid downward frame moves. It will state the carrier reset contract.
- Expected finish: 2026-10-13, after exact replay and a separate review pass.
- Coordination: the coordinator found no pinned sprint issue. The claim is
  local. No issue or PR was opened.

## Candidate approaches

1. Search for independent target orders that reduce the carrier count.
2. Reuse a small carrier bank and pay every downward frame move.
3. Bound terminal reads without a common target order, then combine the
   bound with the cost of downward moves.

The first exact experiment selects approach 3. The explicit P104 support
poset has width 32. Each of its 32 four-term supports is different. These
supports give a bound that does not require a common order. Projection
away from any one survivor has width 26. This also permits a term to pay
for the loss of its nonzero COPY endpoint.

This work extends PR1071's delivery scope. It does not repeat the 40320
common-order search or PR1077's coefficient-field proof. PR968 supplies
the decoder family and the optimistic current-profile price model.
