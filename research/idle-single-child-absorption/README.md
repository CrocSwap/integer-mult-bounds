# One-child absorption fails for the concrete idle-axis transfer

**Scoped exact negative result; no new kappa or supplier admission.**

Moving axis16 from T740 child10 to child12 gives the favorable concave ranks
`48,48 -> 47,49`, but changes its eight-stream physical operator. Can the
defect be absorbed into one existing child, avoiding an additional repair call?

For owner replica zero / port zero, the answer is **no at all twenty residual
sites** under the declared interface: one completed Fourier-diagonal phase on
one stream, surrounded by arbitrary constant invertible scalar *stream-only*
encoding and decoding (`L_stream tensor I_address`). The eigenvalue function
and all added implementation costs are granted free. Arbitrary dirty inputs,
restored dirty scalar spectators and exact global phase remain required.

Nineteen sites fail a rank-two minor at character16. The remaining receiver
site needs two different rank-one projectors at characters16 and33554432;
their flattened minor is `-2i`. Separate per-character rank checks, and even
commutativity, miss this failure. [PROOF.md](PROOF.md) gives the normalization
argument, exact witnesses, cost connection and covered domain.

This tests a different mechanism from PR3220's added repair tariff and
PR3229's abstract independent-group sharing. It does not cover two changed
sites, a changed interaction word, a character-dependent encoder or an encoder
mixing addresses with stream labels. It does not validate or refute another
PR's complete allocation, supplier or kappa claim.

## Reproduction

```
python3.12 -B scripts/research_package.py --package research/idle-single-child-absorption
```

Both commands in `VERIFY.json` are standard-library-only. `verify.py` uses
authenticated retained event semantics plus exact Gaussian-rational cut
inversion; `independent.py` separately expands elementary matrices and reverses
their factors. They use all independent stream columns and retain exact phase.
The full T740 payload authenticates; only one owner/port/transfer is investigated.
`RESULT.json` and the independent committed receipt preserve exact coverage
and semantic controls. `--output /new/path.json` writes an exclusive fresh receipt.
These are finite exact checks supporting a written interface proof, not a
formal-kernel proof or full selected cold replay. Hosted CI is separate.

Base main: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision6.
Selected record unchanged. Source/input pins, original card, concrete scope,
stopping rule and attribution are in `SOURCES.json` and `TASK.json`.

## Open next questions

- A character-dependent stream/address adapter can change the projector.
  First give one actual encoder/inverse and its arbitrary-dirt endpoint,
  then price all child, routing/volume, helper, precision and restoration work.
  This result provides no affordable adapter.
- A joint rewrite of at least two existing sites is outside this theorem.
  First specify a concrete factorization and complete recursive invoice.
  The known additive two-child repair merely restores the original factors;
  this result does not justify an automatic wider search.

Structured relevance, first steps and blockers are in `TASK.json`.

## Credit

Ross Richardson with substantial OpenAI Codex assistance and two separately
tasked mathematical specialists. No independent human review is claimed.
The retained physical interpreter/geometry and predecessor credit remain with
Gonzalo-Mier/PR3199, Nick Petalas/PR3187, Gareth Davidson/PR1387, Jeremy
Diviney/PR3148, Rohan Arun, dcharb78, Dumitrean, Jeremy Kothe and the retained
native/geometry/selected construction lineage. PR3220 and PR3229 retain their
distinct results and credit. New material Apache-2.0; frozen sources unchanged.
