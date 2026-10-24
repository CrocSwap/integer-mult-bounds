# Exact query capacity for a shared-path pair of odd cycles

For the seven-vertex theta graph with paths u-a-v, u-b-c-v and u-d-e-v,
arbitrary nonnegative payload widths d and every coefficient field have exact
fitting rank `sum(d) − nu_b(d)`, where nu_b is the maximum integral number of
edge-shared coordinate pairs. Arbitrary directed rectangular, nonsymmetric,
noncommuting allowed blocks cannot improve this dimension optimum.

[PROOF.md](PROOF.md) supplies the whole unequal-width result. Two induced
edge-plus-isolates subspace inequalities imply the half-total bound. That
bound survives arbitrary scalar-coordinate deletion; the classical
Tutte–Berge formula then proves the exact matching lower bound. A matching
channel construction attains it. The finite checker is corroboration, not the
universal proof or a formal kernel audit.

The actual source question is [PR5023](https://github.com/CrocSwap/integer-mult-bounds/pull/5023)
Open next question1, on overlapping odd-cycle masks. Its single-cycle theorem
and [PR5180](https://github.com/CrocSwap/integer-mult-bounds/pull/5180)'s
single-cycle minimizer classification do not provide this shared-path result.
The full endpoint retains identity diagonal blocks and both ordered nonedge
zeros; the proof does not presume separable block coordinates.

## Constructor and resource scope

`theta.py` returns all eight edge counts, seven private counts and the exact
rank. Its explicit-stack finite dynamic program has at most
`product_i(d_i+1)` states, at most four successors per state and O(sum(d))
backtracking. This is deliberately pseudopolynomial, not a fast physical or
encoded-width algorithm. `matrix` expands the complete attaining operator for
finite verification. No runtime cap is inserted into the mathematical domain.

## Reproduce

Python3.12, standard library only:

```
python3 -B scripts/research_package.py --package research/theta-query-capacity
python3 -I -O -B research/theta-query-capacity/verify.py
```

The checker independently compares indistinguishable-capacity dynamic
programming against actual-copy matching; checks attaining and locally mixed
operators over F2,F3,F101 and arbitrary coordinate restrictions; enumerates all
65,536 directed binary scalar fits; compares four full Tutte–Berge dual domains;
and rejects malformed widths, incomplete/overbilled recipes and false operator
entries. RESULT.json binds the entire typed receipt and scientific source/code
bytes. The verifier reads and authenticates the exact two predecessor source
files declared in SOURCES.json. Metadata source history, export/cold evidence
and peer review are separate publication checks, not supplier acceptance.

## Decision and remaining costs

This is one changed query-mask contract, closing the first coupled-cycle
case without a physical construction campaign. Preparation, coefficient
access, source copies, frames, ownership, dirty restoration, precision,
fixed tapes, compiler and outer recovery remain UNKNOWN and outside scope.
No new kappa, selected-frontier change or complete multiplication theorem is
claimed. Scope stops at this seven-vertex graph.

## Open next questions

The theorem permits a downstream source-bound test only after an actual
caller supplies this exact ordered read mask and a complete physical invoice.
No such caller is supplied here. A feasible first step is to identify a literal
source incidence map and compare its complete query/copy/restoration allowance;
missing producer and consumer contracts are the blockers. The theorem does
not reserve or authorize an automatic wider graph/minimizer search.

## Sources and credit

- JoyboyBrian #5023, exact head1b069fc3d6bb463ab212f3ebc644abe838efa550,
  supplies the unequal-cycle contract, subspace method and explicit open question.
- Tekalign #3362, Nick Petalas #4909, Sagar Thakrar #2484 and the retained
  P112/query-mask lineage retain their predecessor credit.
- Tutte1947/Berge1958 supply the matching formula. The exact statement and
  a standard proof were read in Alexander Schrijver's official CWI note
  [The Tutte–Berge formula](https://homepages.cwi.nl/~lex/files/tutteb.pdf).
  This is an explicit cited theorem, not a new proof or executable dependency.

Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
No independent human or proof-kernel acceptance is asserted.
