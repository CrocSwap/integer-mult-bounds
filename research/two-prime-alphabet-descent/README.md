# Descent from higher prime-power phase alphabets

For every prime q>=5 and positive a,b, a q+3-row matrix with at least
four pairwise orthogonal columns over mu_(3^a q^b) can be changed by
row and column phases into a matrix over mu_(3q).

Consequently the maximum number of orthogonal eight-entry columns is
**exactly four for every alphabet mu_(3^a 5^b)**. Three-column examples
with essential higher phases show that the column threshold is sharp.
No new kappa or physical supplier follows.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), [verify.py](verify.py),
[SOURCE-PINS.json](SOURCE-PINS.json) and [CREDITS.md](CREDITS.md).

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/two-prime-alphabet-descent
```

Both modes print `PASS_TWO_PRIME_ALPHABET_DESCENT`. The unchanged
fifteenth-root capacity verifier and its nested source checks run.
New exact checks cover quotient patterns, eight cyclotomic alphabets,
14,400 prime-cycle pairs, the sharp three-column examples and lifted
four-column attainment. No network is needed.

## Open next questions

- Determine which changed row counts permit an essential higher phase
  with four or more columns. First identify the permitted cycle types.
- Test an alphabet with a third prime divisor under a specified matrix
  contract. The two-cycle proof does not cover that setting.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
