## Result

This supplies the encoded reverse schedule and subtractive whole-node consumer
left open by the [source-pinned forward endpoint](https://github.com/CubeJerry/integer-mult-bounds/tree/532b60ac427f47191175aba2e1317db0f3508d51/research/encoded-balanced-crt-endpoint).
On that same padded owned-source interface, the actual encoded program now
evaluates the inverse balanced CRT address-state map, and both compositions
are identity on the entire admitted padded rectangle. Runtime receives no
decoded node start, level, precision, coordinate or traversal list.

**No new kappa.** This is a source-relative construction and ownership/precision
proof, not a complete multiplication theorem. The selected conditional bound
and all five foundational assumptions are unchanged.

## Exact changes and why they matter

- Add a fixed encoded reverse frontend. It uses the physical depth stream to
  manufacture the root half-size and performs paid unary halving between
  levels. It inherits every other #7154 frontend method unchanged.
- Specialize #5053 by one authenticated scientific line: use its already
  proved modular subtraction for the whole-node updated coordinate. Current
  left reconstruction, positive offsets, padded-right handling and lifecycle
  code remain unchanged.
- Reuse the published forward projection/retirement/commit writer byte for
  byte. Source mutation happens only after the numerical result is retired;
  the next node rereads the actual current source.
- Prove the complete source-model O(A^4) bill and K_source+O(A^2) retained
  backing, including source copying, guards, head returns and cleanup. There
  are 79 private roles per invocation. Fresh forward/inverse round trips
  retain **158 histories**; no unproved restart discards the first inventory.

Precision decreases across levels, but can regrow within a level: declared
widths (2,2,3,3) give the inverse precision sequence 11,5,7. The proof and
checks use exact current extents and preserve/clear every older history.

## Novelty and pinned predecessors

#4100 and #4195 already establish balanced inverse algebra and logical padded
callers. #7152 already gives complete physical forward/reverse source-state
trees at compiled geometry; #7154 gives an encoded forward iterator. This
package supplies their narrowly scoped encoded reverse join on the published
forward writer's same physical interface. It does not claim those earlier
inverse results again.

#4024 already provides an encoded bidirectional triangular payload converter,
used after recovery by #5095. Its format, padded extension and routing contract
are different. The raw compact macro inverse in #4169 is another separate
interface. This helper does not substitute for either cost or caller proof.

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
The #7154 frontend is pinned at `cc35ecedce6f208d5056fab6d17c58555affc73c`;
the unchanged forward writer at `532b60ac427f47191175aba2e1317db0f3508d51`;
the #7152 comparison source at `66adbede4bd4ab603ba3e0a7f6708403905b753c`.
All nine byte-exact exports are authenticated by SHA256 and Git blob in
`INPUT-PINS.json`; the numerical specialization is checked byte for byte.

## Reproduction and executed checks

From `research/encoded-balanced-crt-inverse`, Python 3.12, standard library:

```sh
python3.12 -I -W error -B verify.py
python3.12 -I -O -W error -B verify.py
```

Both executed modes produce:

```text
PASS_ENCODED_BALANCED_CRT_INVERSE cases=53 nodes=380 roles=79/158 controls=11
```

The bounded family covers both composition orders on all 32 padded pairs for
(3,5), fifteen four-axis states, four composite-modulus states and two eight-axis
states. An independent exhaustive congruence oracle checks every current node;
the pinned balanced oracle checks complete endpoints. A separate actual
`run()` test supplies no iteration count or schedule. The main family measures
85,291,890 source actions; no universal bound is inferred from that number.

Eleven controls detect wrong level order/sign, stale pre-root left data, old
precision, dirty older tails, an extra physical role, wrong unary transition,
silently forgotten backing, original/current-coordinate confusion, a global
invalidity shortcut and premature source writing. Checks preserve source
metadata and nonblank inaccessible tails, all boundary heads, role identities,
current guard extents and both inventories' historical capacity. Runtime host
geometry names are poisoned and new physical constructors sealed after entry.

## Limits and open obligations

This evaluates one address-state vector. It supplies neither payload routing
nor a raw compact inverse, exceptional-key epoch or full selected caller.
Source construction in the admitted encoding, clean private acquisition,
binary lowering and analytic/integer-recovery obligations remain explicit.
Same-bank restart is not established; failure controls are not universal
malformed-input or crash rollback. The numerical value of the complete
finite-control refinement constant is not certified. Finite tests and AI
review are not proof-kernel or independent human acceptance.

`PROOF.md` contains the quantified proof and complete bill. `TASK.json` records
the open caller join, restart, balanced payload scheduling and binary-tariff
questions with their first steps and blockers.

## Credit

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Retain the #7154/#7152 and published forward-endpoint work prepared for
CubeJerry; JoyboyBrian's #5053/#5219/#5505 numerical, entry and owner contracts;
Ali Romman's #5353 encoding and #5625 retired-write boundary; Cinna Davis's
#4100 balanced construction; Hiroki KUMAZAKI's current-state/mixed-width/raw
inverse work; Tekalign's #4024 converter; ToikY's arena lineage;
commdata2338's history accounting; and every unchanged source notice.
Apache-2.0. The known CRT inverse identities are credited predecessors; the
contribution is this exact encoded reverse consumer and its lifecycle proof.

## Independent acceptance checks

The orchestrator's [REVIEW.md](REVIEW.md) and separate
[PEER-REVIEW.md](PEER-REVIEW.md) accept the frozen source-relative theorem.
The peer authenticated all nine exports and independently checked reverse
control, current-left reconstruction, retirement, precision regrowth and
complete cost/history sums without rerunning the author verifier.

A separate CRT-idempotent and global mixed-radix inverse oracle passes 20
cases and 52 actual nodes, including padded axes, eight-axis cases, widths
up to nine bits, historical tails, the 11,5,7 precision sequence and a rejected
stale-coordinate mutation. Its portable command is:

```sh
python3 -I -W error -B research/encoded-balanced-crt-inverse/independent_check.py
```

`INDEPENDENT-RESULT.json` records the full domain and exact code hashes.
The author normal and optimized replays also pass from this final packaged
directory with identical output. These are independent AI checks; no human
or formal-kernel acceptance is claimed. The full proposed PR description
is committed in `PR-DESCRIPTION.md`.
