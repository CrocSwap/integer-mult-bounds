# Orthogonal witnesses for complete inverse circuits

This package constructs an exact counterexample in SO(d,Q) for each false
complete rational dirty-register identity with named inverse calls. It
preserves inverse equals transpose and permits an arbitrarily small rational
distance from identity. If r is the number of roles and q counts unary calls
in both programs, d<=r+q. Every generator has condition number one.

The [written proof](PROOF.md) gives the skew-path Cayley construction, the
shortest-coefficient condition and the finite grid of dq+1 rational trials.
The producer uses the pinned compact inverse frontend of
[PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262).
The negative checker replays every original instruction and returned role.
It does not import the coefficient producer.

Run with Python 3.12 and its standard library:

```sh
python3.12 -I -W error -B research/orthogonal-inverse-witness/verify.py
python3.12 -I -W error -O -B research/orthogonal-inverse-witness/verify.py
```

Both commands end with `PASS_ORTHOGONAL_INVERSE_CIRCUIT_WITNESS`.
`RESULT.json` records the exact deterministic checks. `VALIDATION.md` records
local replay and mutation checks. `VERIFY.json` registers both modes.

For a concrete input:

```sh
python3.12 -I -B research/orthogonal-inverse-witness/witness.py research/orthogonal-inverse-witness/vendor/wrong-order.json --output /tmp/orthogonal-witness.json --parameter-cap 1/100
python3.12 -I -B research/orthogonal-inverse-witness/check_witness.py research/orthogonal-inverse-witness/vendor/wrong-order.json /tmp/orthogonal-witness.json
```

The full test uses 160 small programs with a separate reduced-group-word
oracle, dense rational matrix replay, forced parameter cancellations, nested
commutators, dirty returns and aliased queries. A delayed inverse family has
2^32 lowest-degree words but needs 66 compiler states and a 33-dimensional
witness. No expansion of those words is used in that stress case.

This is a scoped written theorem and an exact adapter. It does not bind a
finite native alphabet or its other relations. It does not price a supplier,
prove numerical detectability, run a native tape or improve complete kappa.
The selected frontier is unchanged. Sources are retained at an ancestor
commit so the package can run after export without the upstream fork.

## Attribution

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
Krzysztof Wójt (@krzysztofwojt) supplied the inverse compiler, shortest-word
proof and examples in [PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262).
Ali Romman's [PR #5296](https://github.com/CrocSwap/integer-mult-bounds/pull/5296)
supplied the SPD inverse witness and replay harness adapted here. Source
notices and their credit to zxv's
[PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235) remain in
`vendor/`. `SOURCES.json` records the exact consumed commits and hashes.
The rational-series and Cayley methods are classical.

## Open next questions

Can an actual native inverse-bearing word be bound to this grammar while
retaining every extra relation? First pin one caller and its complete role
and operator contracts. Orthogonality alone does not supply a finite
Clifford alphabet. A further witness must meet all of those constraints.
A separate numerical use also needs an explicit bit-length and separation
bound; exact nonzero rational replay does not establish stable detection.
