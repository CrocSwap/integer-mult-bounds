# R439: two restored dirty buffers for the interleaved packet word

The 313-event R439 packet word can use two borrowed dirty payload buffers if
the caller permits temporary exchange of the original target/source packets.
The adapter restores the source and both buffers after every event and keeps
the snapshot immutable throughout. Its explicit price is **1,232 route calls,
1,232 packet exchanges and 4,009 packet XOR passes**. This is a conditional
interface result and a finite certificate, with no new bound claimed.

[PROOF.md](PROOF.md) gives the arbitrary-payload argument, complete outer
bill and the changed ownership premise. [RESULT.json](RESULT.json) is the
replay receipt; [TASK.json](TASK.json) records scope, freshness and next work.

## Why this result matters

[PR2448](https://github.com/CrocSwap/integer-mult-bounds/pull/2448), pinned at
`76311b90337a04dd811877d101c86ff8ecd65904`, replays the interleaved word using
fresh blank packet copies and later disposal. Its review explicitly leaves
dirty ancillas and reversible uncomputation open. Replacing a blank copy by
XOR into dirty storage is incorrect. Our six negative controls include that
shortcut, and reject it at the first event boundary.

The new adapter exchanges actual values into a borrowed buffer, routes them,
updates, routes back and exchanges back. The elementary three-XOR exchange
identity is standard; the contribution is its fully priced ownership contract
and source-bound chronological replay for this specific window. The former
929-route fresh-copy implementation remains cheaper in route calls.

## Evidence and limits

The finite GL2(Z/9) replay checks 431,568 family records, including all 422,577
unowned records, against an independent physical endpoint oracle. Its 431,811
formal input records cover arbitrary payloads and correlations. Both forward
and reversed words pass; two dirty banks and the source are restored at every
event boundary. Six semantic mutations are rejected with reason checks.

The zero fresh-payload and zero CLEAR/disposal counts apply to the outer
adapter. Route-private scratch, headers, control state and a uniform compiler
remain additional obligations. Original source packets are temporarily
exchanged during an event; an interface requiring continuous source
immutability is not satisfied. No full bit-time supplier, uniform GL64
implementation, global helper admission, moment improvement or new kappa is
claimed. The finite adjacent-swap counters are not a scalable complexity bound.

## Reproduce

From a full repository checkout with Python 3.12 and no third-party packages:

```sh
python3.12 scripts/research_package.py --package research/r439-dirty-packet-adapter --check-only
python3.12 scripts/research_package.py --package research/r439-dirty-packet-adapter
```

The registered replay verifies the committed receipt under ordinary and
optimized Python. Direct replay uses `python3.12 -I -B` with this package's
`verify.py`. `--write-result` is an explicit authoring operation which refuses
to overwrite an existing receipt. Routine verification is read-only apart
from permitted temporary exporter files.

[SOURCES.json](SOURCES.json) pins the base and three live source inputs.
[PREDECESSORS.json](PREDECESSORS.json) pins seven retained, consumed PR2448
source/contract files by commit, Git blob and SHA256. The verifier reuses its
route compiler and exact PR2407-derived source-window constructor with credit;
the endpoint uses its separate baseline and full-ring multiplication. No
independent claim is made for re-proving those retained source results.

## Open next questions

1. Can the uniform routing backend preserve arbitrary dirt parked in original
   streams and restore its private workspace and heads? First test one complete
   event against its actual storage contract. A uniform backend is not supplied
   here.
2. Can the full caller admit temporary source exchange and charge all headers,
   scans, borrowed capacity and routing scratch? First insert this exact bill
   beside the fresh-copy alternative without changing the selected result.

## Credit

Prepared by ywz65 with substantial OpenAI Codex assistance. New work is
Apache-2.0. PR2448 supplies the interleaving, finite route compiler and explicit
fresh-versus-dirty boundary; its retained PR2407 constructor and dependencies
keep their source notices. This result neither identifies a defect in PR2448
nor claims the standard reversible exchange identity as new mathematics.
