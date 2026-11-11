# Commit whole-node CRT results into the encoded balanced source on 79 owned roles

This supplies a paid changing-source consumer for the physical balanced-node
iterator in [#7154](https://github.com/CrocSwap/integer-mult-bounds/pull/7154).
The complete forward balanced CRT **address-state endpoint** now executes on
the actual source tape without supplying node indices, widths, precision or
coordinate values as host integers. The proof is relative to the pinned
numerical, entry, owner and frontend contracts. **No new kappa.**

The consumer stages each whole-node updated-coordinate field in a same-length
source copy, checks discarded high bits, retires the numerical result, and
then writes the owned source. Preserved metadata and widths reestablish the
encoded iterator's next-node invariant. The complete source-model time is
O(p^4), for p bounding the sum of declared widths; historical backing is
K_source + O(p^2). All copying, writing, head returns and erasure are paid.
The one new staging role retains M allocated cells; visited-position
accounting adds one for its transient head at index M.

#7154 supplies the read-only numerical iterator; this adds its actual
changing-source commit. [#7152](https://github.com/CrocSwap/integer-mult-bounds/pull/7152)
already supplies the same endpoint at compiled micro-row geometry.
[#5053](https://github.com/CrocSwap/integer-mult-bounds/pull/5053) already
computes whole-node values, which [#5496](https://github.com/CrocSwap/integer-mult-bounds/pull/5496)
correctly discards when building an individual micro-row. Those are credited
premises. The new claim is the exact encoded consumer join and its preservation,
ownership and cost proof.

This evaluates one address vector. Encoded micro-row selection, physical
payload permutation, the three-epoch key, inverse traversal, binary lowering
and all five selected framework assumptions remain open. The complete selected
conditional kappa remains 0.00363005817. The numerical value of the fixed
finite-control refinement constant is not certified; an explicit raw-action
envelope is given separately.

## Reproduction and evidence

[PROOF.md](PROOF.md) gives the quantified statement and full ledger.
[endpoint.py](endpoint.py) is the adapter; [verify.py](verify.py) executes the
unchanged seven byte-pinned sources. From this directory, Python 3.12:

```sh
python3.12 -I -W error -B verify.py
python3.12 -I -O -W error -B verify.py
```

Both executed modes print:

```text
PASS_ENCODED_BALANCED_CRT_ENDPOINT cases=45 nodes=75 owned_roles=79 controls=8
```

The family covers all 32 padded coordinate pairs for moduli (3,5), twelve
four-axis states and one eight-axis tree. Independent congruence enumeration
checks every node; a separate global mixed-radix formula checks fully valid
endpoints. The actual runs total 13,102,659 source actions. The eight-axis
fixture retains 3,941 cells within a 4,073-cell backing envelope. These are
finite corroborating checks, not a universal proof by enumeration.

Eight controls detect premature writing/advancement, double commit, stale
coordinate copying, missing erasure, reversed close/write order, wrong-half
projection and a nonzero discarded high bit. Source metadata, inaccessible
nonblank old tails, boundary heads, stable identities and successful cleanup
are checked. Geometry/decode functions are poisoned and physical constructors
sealed after initial acquisition. Failure detection is not a rollback theorem.

[INPUT-PINS.json](INPUT-PINS.json) records original repositories, commits,
Git blobs, SHA256 values and package-local export paths. Runtime #7154 is
frozen at `cc35ecedce6f208d5056fab6d17c58555affc73c`; canonical sources are at
`e54523517d0f03e58352e647c403a5af3e525a57`; comparison #7152 is frozen at
`66adbede4bd4ab603ba3e0a7f6708403905b753c`. A direct cold replay needs only
this package and Python's standard library, without network or an unmerged
Git object. Standard source provenance is recorded separately in SOURCES.json.

## Open next questions

[TASK.json](TASK.json) records structured first steps and blockers. An inverse
evaluator needs an encoded reverse schedule and subtractive consumer. An
actual exceptional-key epoch needs charged representation conversion and
restoration. Payload routing still needs encoded row/target/header selection.
A complete binary program and common tariff remain separate obligations;
unimplemented restarts and arbitrary dirty-memory acquisition are excluded.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Retain JoyboyBrian's numerical/entry/owner/query work; Ali Romman's source
encoding and retire-before-write work; Cinna Davis, Hiroki KUMAZAKI, ToikY,
commdata2338 and all unchanged notices. See PROOF.md for full attribution.
Separate AI cross-review is not independent human or formal-kernel acceptance.
Apache-2.0.

## Independent review

[REVIEW.md](REVIEW.md) records a separate source and proof review. The independent checker does not call the author verifier and uses CRT idempotent sums as its node oracle. Run `python3.12 -I -W error -B independent_check.py .`; its JSON report records 18 cases, 46 nodes and a rejected stale-coordinate mutant. The executed receipt is [INDEPENDENT-RESULT.json](INDEPENDENT-RESULT.json).
