# Finite leaf bootstrap above PR182

Conditional bound: **kappa = 660627334074291/10^18 = 0.000660627334074291**, about **0.062219% above PR182** at immutable commit `af90b94783f7d104a0be75c762ade758bec75855`.

This package uses PR182's completed ordinary bit supplier at stopped leaves, then applies three fixed, acyclic wrapper levels. It retains PR182's physical complex and bit words, child histograms, scalar charges, frame witnesses, prime range and paid balanced assembly.

With coarse saving `c = 0.000661064051056` and PR182 ordinary saving `a_0`, each new level uses atom exponent `c` and saving `a_(j+1) = (1-c)c + c a_j`. Every selected level satisfies the strict adapter and borrowing inequalities. The limiting value `c` is not claimed at finite depth. The improvement is modest and comes from leaf composition, not a new physical circuit.

Run the read-only gate:

```sh
python3 -B research/bit-leaf-bootstrap182/verify.py
```

The gate checks source pins, regenerates the exact paid bit and complex moments, verifies three finite bootstrap levels, all 47 strict inequalities and seven margins, and adversarial controls including the next final grid point. The written compositional argument is in PROOF.md. Exact arithmetic and finite tests do not establish the inherited all-size interfaces.

Validation status: focused arithmetic passed; independent composition review found no blocker under the retained interfaces. Fresh replay of PR182's underlying complete complex and bit physical words passed; its log hash and review evidence are recorded in validation.json. Full repository verification passed on research commit `32daefe471e1e41926971747bb901e2839938b43`: all 14 native Makefile groups on Python 3.11, 3.13 and 3.14, all three formal packages, and the selected package gate (46 successful CI jobs). Every native job passed its post-run reproducibility check. See validation.json for immutable run links and archive hashes. The retained 252 external reserve is conservative slack, not a claim about the new leaf's internal borrowing requirement.

See NOTICE for attribution to the PR182, paired-cube, terminal-sink, stopped-wrapper and balanced-assembly authors.
