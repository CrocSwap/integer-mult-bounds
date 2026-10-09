# Terminal accumulation and bit lifetime reuse on PR168

This additive package certifies the conditional bound

\[
T(n)=O\bigl(n(\log n)^{1-\kappa}\bigr),\qquad
\kappa=\frac{308013811}{500000000000}=0.000616027622.
\]

It combines PR170's bit-output fusion and compensated reuse with PR168's
new modules, refines the complex operation frames, and executes PR166's
target-accumulating terminal compiler on the resulting complex word.
The inherited all-size compiler, analytic recovery, weighted local-ring,
shared-core, restored-row and balanced-layout interfaces remain assumptions.
This is an exponent saving, not a measured runtime improvement.

| Reconstructed supplier | Physical auxiliary roles | W | Local saving |
|---|---:|---:|---:|
| Complex, before terminal absorption | 12,201 | 14,841 | 0.000614442135… |
| Complex, 66 terminals absorbed | 12,135 | 14,775 | 0.000616407346 |
| Bit, merged outputs and 1,760 birth reuses | 18,732 | 22,252 | 0.000646746861 coarse |

The complex side limits the final assembly. The resulting kappa is about
0.50% above PR173's advertised 0.0006129700 and 3.22% above PR170's
0.000596818007. These comparisons identify fixed published witnesses,
not a claim that the repository's frontier cannot change.

## Reproduce

From the repository root, standard-library Python 3.11 or newer:

```sh
python3 -B research/paired-cube-terminal-reuse/verify.py
```

The command regenerates both source graphs and words, checks the frozen
physical frames and aliases, executes the changed complex word on every
rational source/target/dirty column in both shear directions, and checks
every bit column over F2 and against the defining integer decoder. It
computes exact determinant witnesses for all 25,849 original and replacement
bit frames. Omitted corrections, source deliveries, target pre/post shears,
terminal writes, invalid frames and stale reuse reads are rejected.

Both paid moments include the inherited charges. The verifier retains the
full finite group, original logical scalar stock, complete bit fallback,
router, precision and row reserves. It proves the two supplier grid points
and rejects their successors; all 47 strict constraints and seven margins
hold, and the next final kappa grid point is rejected.

Normal verification does not change tracked files or run a search.
`--refresh-sources --write` is an explicit authoring mode and still executes
every check. Frozen hashes bind code, mathematical source interfaces and
selected inputs. See [PROOF.md](PROOF.md) and [NOTICE](NOTICE) for scope and
attribution. No global optimum or unconditional multiplication theorem is claimed.
