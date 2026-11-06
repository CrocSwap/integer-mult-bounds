# A smaller effective interval-local-limit onset

Scoped proof produced by Nick Petalas. Assuming the interval error inequalities
of alephnan's [PR #6713](https://github.com/CrocSwap/integer-mult-bounds/pull/6713)
at `cd666f05c4e9006025b634687cc493911c8371c8`, the same uniform `10^-8`
local-limit guarantee holds for

```text
n >= 2^751000000   instead of   n >= 2^(10^12).
```

This covers every interval of length at most 5000, every real location and
every endpoint convention, for both the exact Gaussian integral and the
left-endpoint Gaussian approximation. The exponents decrease by a factor
greater than 1331. Neither enormous integer is materialized.

[PROOF.md](PROOF.md) proves the new intermediate bound
`E(n,b) < 1025/(1024 log n)` whenever `log n >= 60` and `0 <= b <= 5000`.
The improvement comes from retaining a smaller bound for the two decaying
remainders. It uses the predecessor's analytic inequalities as premises;
no predecessor program, certificate or probability convolution executes.
The source and exact hash are in [SOURCES.json](SOURCES.json).

## Reproduction and evidence

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/smaller-interval-onset/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/smaller-interval-onset/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/smaller-interval-onset
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/smaller-interval-onset --check-source-history
```

Other hosts may substitute their CPython 3.12 executable. The verifier checks
the exact rational gates in the new proof, rejects two insufficient onset
certificates, and emits a generated receipt bound to every package file.
Those rejecting controls concern this sufficient estimate; they are not
counterexamples to the local-limit theorem at smaller depths. The universal
conclusion rests on the written monotonicity argument and cited premises.

## Limitations

The onset remains impractical. This is a historical analytic side result,
not a new kappa or a complete multiplication theorem. The six H hypotheses,
source interval inequalities and classical analytic approximation remain
mathematical inputs. No predecessor replay or independent audit is claimed.
The complete flow majorant has not been rederived with this onset. No
physical supplier, compiler, precision, ownership, tape or recovery obligation
is discharged. The selected record and all five assumptions remain unchanged.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

- Propagate this smaller local onset through the complete fixed-height flow
  proof. Begin by identifying every use of its original local-limit cutoff;
  retain all mixed layers, boundary exits and terminal leaves.
- Improve the error rate or remainder constant using the actual characteristic
  function. A sharper spectral estimate could reduce the still enormous
  sufficient onset much further.

## Credit

The new remainder estimate and onset are produced by Nick Petalas.
Alephnan retains the effective interval-bound credit in PR #6713, and
CubeJerry retains the fixed-height exponent theorem in PR #6329. The law,
flow and analytic lineage, and the classical approximation credit, are
listed in [PROOF.md](PROOF.md). Apache-2.0.
