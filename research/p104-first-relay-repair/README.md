# Independent audit of the first P104 relay repair

The first new edit in [PR #7774](https://github.com/CrocSwap/integer-mult-bounds/pull/7774)
preserves all 1,264 rational output rows. Within its two-parameter source and
repair family, slope 4 and repair coefficient 1 are the unique correct values.
The repair value is outside the span of all 907 retained banks at chart 127.
An exact 62-input separator proves that a free reconstruction from those fixed
banks is impossible. [Proof](PROOF.md) · [Certificate](RESULT.json) ·
[Source pins](SOURCE-PINS.json) · [Credit](CREDITS.md).

The audit answers the [requested independent check](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19724778)
at source head `22fff773f897e70a2c346d09de62515fadb1c445`.
It checks the complete affected rational operator and the final-word omission
witness. It does not supply a new kappa or full physical application admission.
All five inherited framework assumptions remain.

From the repository root, with Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-first-relay-repair
```

Both normal and optimized commands must report `PASS_P104_FIRST_RELAY_REPAIR`.
The check reads only retained inputs and does not need Git or network access.
It validates 38 source files, rebuilds the exact starting graph, checks
23,563,352 rational coefficient products and all 1,264 output rows, then checks
the two-parameter residual and the explicit bank separator. Four wrong parameter
pairs and a wrong source chart are rejected. The final graph reproduces the
published input-1/output-19 omission coefficient -8.

The source constructors are retained without changes. The new algebraic replay
is source-aware, not blind. Signed native operators, full physical execution,
caller costs, directed prices and compiler closure were not rerun. No Lean,
Docker or independent human acceptance is claimed. The optional broader repair
cost search did not finish and is not part of the result.

## Open next questions

Can a changed earlier bank or additional paid route reduce the complete cost?
The fixed-bank proof does not settle that question. Start with a changed source
and a complete paid invoice. See [TASK.json](TASK.json).
