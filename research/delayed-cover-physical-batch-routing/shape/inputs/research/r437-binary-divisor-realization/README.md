# Binary tapes for the R437 large-divisor quotient

The R437 batched Count quotient no longer needs an arbitrarily wide host
remainder inside its three divisibility guards. [binary.py](binary.py) computes
the full quotient and remainder by unit-head scans on the original record Tape
alphabet. It also constructs q^(d²) by binary multiplication using two alternating
roles. [adapter.py](adapter.py) executes the unchanged authenticated quotient
body with a private zero-predicate adapter; the general source Count API and
all frozen files remain unchanged.

[PROOF.md](PROOF.md) proves the arithmetic invariant, source guard equivalence,
complete conservative arithmetic time bounds and lifetime visited-cell bounds.
High-divisor construction, copying, normalization, rewinds and erasure are paid.
The supplied q/family/GL constant tapes, Context/compiler construction, inherited
radix Word arithmetic and complete payload caller remain separate obligations.
This is a scoped arithmetic refinement, not a full caller tariff or new bound.

The bounded verifier checks7,936 exhaustive divisions,12 wider cases,18 encoded
power constructions, nine real source quotient cases across w1..3, every factor
rejection and five implementation omissions. It compares the actual normalized
Count bytes, independent divmod, borrowed heads, numerical live sets and cleared
backing. The q127 million-bit numerator and520,192-bit divisor are used only to
evaluate the proved formulas; that enormous execution is not run.

```sh
python3.12 -B scripts/research_package.py --package research/r437-binary-divisor-realization
```

Normal and optimized registered commands are read-only and standard-library
only. `--write` explicitly generates RESULT.json. Sources are authenticated
before import, and every reused input is declared for invalidation/export.
The scoped result answers PR5025's binary-divisor handoff, rather than extending
PR5055's directory streaming. No selected frontier, frozen archive or other
research package is changed.

## Open next questions

- Price the complete supplied-constant compiler and original Context/Word
  radix paths. Begin with the actual source contracts; these costs are not zero.
- Join the binary quotient to a complete admitted payload caller and its full
  retained backing. Structural-context equality does not establish production
  execution, precision/stock admission or the full multiplication theorem.

Credit David Arias's original Count/row quotient, Chris R/Clear1nsight's R437
caller and admission, ToikY's radix work, Nick Petalas, Jose Manuel/jmbarrancoml,
codyw912 and all retained source notices. JoyboyBrian; substantial OpenAI Codex
assistance; Apache-2.0. No independent human or formal-kernel review claimed.
