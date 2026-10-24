# Certify a dirty linear circuit for arbitrary operators

Use [universal-dirty-certificates](../../research/universal-dirty-certificates/README.md)
for scalar linear register programs with unary operators requiring **no
relations between them**. A compact certificate can prove the complete endpoint
for all payload dimensions without expanding every operator word.

## Minimal input

```json
{
  "field": "Q",
  "roles": 3,
  "program": [
    {"op":"query", "src":0, "dst":1, "symbol":"A"},
    {"op":"query", "src":1, "dst":2, "symbol":"B"},
    {"op":"query", "src":0, "dst":1, "symbol":"A", "coefficient":-1},
    {"op":"query", "src":1, "dst":2, "symbol":"B", "coefficient":-1}
  ],
  "target": {
    "identity": true,
    "terms": [{"out":2, "in":0, "word":["B","A"]}]
  }
}
```

All three initial registers are arbitrary. The target is the complete identity
plus `v2 += B A v0`; register 1 must return its dirty input. Words use matrix
product order: BA applies A first. An empty word means payload identity.
Coefficients default to one and are integers or rational strings, never floats.
`field` defaults to Q; `"Qi"` selects Gaussian rationals (for example
`"1/2-3/4i"` or `"i"`); a prime integer p selects F_p with invertible denominators.

| Instruction | Meaning |
| --- | --- |
| `add`, `src`, `dst`, optional `coefficient` | `v_dst += c v_src` |
| `query`, `src`, `dst`, `symbol`, optional `coefficient` | `v_dst += c X_symbol v_src` |
| `apply`, `dst`, `symbol` | `v_dst = X_symbol v_dst` |
| `scale`, `dst`, `coefficient` | `v_dst = c v_dst` |
| `swap`, `src`, `dst` | Exchange the registers |

In place reuse and self queries are supported. Every index denotes one role
with its own initial input. Retain borrowed fields and cleanup outputs. If the
reference also expands exponentially, give `reference` as another instruction
list instead of `target`. Exactly one is required.

## Produce and check

```sh
python3 -I -B research/universal-dirty-certificates/linear_words.py \
  /path/to/problem.json --output /tmp/new-certificate.json
python3 -I -B research/universal-dirty-certificates/check_certificate.py \
  /path/to/problem.json /tmp/new-certificate.json
```

A positive certificate proves the complete matrix-polynomial identity. The
checker verifies a closed subspace annihilating every final input projection;
it performs no search or elimination. Its compiler, shared field arithmetic and
Python remain trusted. Archive both JSON files with exact source pins and the
instruction adapter.

A negative certificate identifies a nonzero word and offending input/output.
Use `--invertible` on the producer for unipotent counterexamples. Use `--matrices`
on the checker to print sparse operators, input payload and discrepancy.
These disprove the **independent-operator** identity. Symbols named `G` and
`G_inverse` acquire no inverse relation.

## Scope of the bridge

Universal acceptance permits termwise substitution `X_a=G_a^(tensor f)` for every
positive f. Scalars stay outside: `c X-I` becomes `c G^(tensor f)-I`. This does
not tensorize sums or admit physical implementations. See the
[proof and limits](../../research/universal-dirty-certificates/PROOF.md).

For free-group native programs, use the existing
[free-word tensor audit](../../research/free-word-tensor-lift-audit/README.md).
For fixed binary affine maps with quadratic Gaussian phases, the
[native tensor-cutoff guide](native-tensor-cutoff.md) supplies a relation-aware
endpoint checker and a four-width completeness theorem. It preserves actual
global phases and dirty roles; nonmonomial Cliffords and physical admission
remain outside that interface.

For rectangular scratch and one-sided invariants, the existing
[dirty-phase audit](../../research/universal-dirty-phase-identities/README.md)
has a different contract. Nonlinear leaves, aliasing, rounding, native frames,
tapes, precision and the complete invoice still need their own arguments.

Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
