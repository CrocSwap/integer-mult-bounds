# A complete stochastic numerical caller with absolute error bounds

The selected 22,803-event [PR #6030](https://github.com/CrocSwap/integer-mult-bounds/pull/6030) word now has a same-grid integer execution
with a literal retained-state inverse. Every one of its 2,886 distinct native
edges is checked on all 512 columns. A dense complete caller run and reverse
replay pass. A separate source-coordinate decoder checks all 770 final fields.

For N=512^f and grid h, every field at every completed source prefix satisfies

```text
E||error||^2 <= (N*h^2/2)*(23423*f + 161509/8).
```

At width one, grid spacing `epsilon*2^-12` suffices for individual RMS error
below epsilon. Spacing `epsilon*2^-16` gives simultaneous error below epsilon
with probability greater than 1-2^-40. These are absolute-error
contracts. They do not require a relative allowance that fails at small inputs.
The proof includes all-width rules and every retained value and direct cost.

No complete kappa, physical reversible circuit, fast recursive supplier,
fixed tape schedule or selected assumption discharge is claimed. All five
framework assumptions and the selected frontier remain unchanged.

- [PROOF.md](PROOF.md): complete numerical ABI, proof, error and work bounds.
- [RESULT.json](RESULT.json): exact source, transfer, execution and control receipt.
- [sampler.py](sampler.py): integer primitives, full caller and literal inverse.
- [ledger.py](ledger.py): signed coefficients from forward and reverse sweeps.
- [produce.py](produce.py): every native edge, checked against the separate source.
- [endpoint.py](endpoint.py): independent decoded numerical endpoint.
- [verify.py](verify.py): complete registered replay and rejection controls.
- [SOURCES.json](SOURCES.json), [NOTICE](NOTICE): source pins and attribution.

Use CPython 3.12 and NumPy 2.3.4:

```sh
python3.12 -B scripts/research_package.py --package research/selected-absolute-stochastic-caller
```

Both registered modes keep source assertions enabled in normal subprocesses.
The replay regenerates all 1,477,632 native column comparisons and the complete
caller. It also checks 2,401 pair inputs, 48 wide integer round trips, 2,015
scalar contexts, 5,140 division round trips, all 32 seeds of a mixed trajectory,
and a 262,144-coordinate rank-eight tensor inverse. A separate exact-grid
input checks the tensor operator against the independent source oracle. Seven semantic controls,
two operator mutations and three actual source-corruption rejections remain.
These checks support the written theorem; they are not independent acceptance.

The claim followed fresh canonical-main and public PR/Discussion checks, with
a second exact-main README/TASK search. Prior [PR #6526](https://github.com/CrocSwap/integer-mult-bounds/pull/6526) supplies the signed
stochastic caller method; [PR #6532](https://github.com/CrocSwap/integer-mult-bounds/pull/6532) supplies the conserved-sum pair sampler.
[PR #6540](https://github.com/CrocSwap/integer-mult-bounds/pull/6540)'s changed-grid codec is distinct. The complete same-grid caller join,
absolute budgets, full source-edge binding and explicit retained record are
new here. No subagents were used.

## Open next questions

A physical reversible implementation must price seed access, routing, records
and their cleanup. It must preserve arbitrary external dirty values under its
actual encoding. The direct native execution here is not the accelerated
recursive supplier. Bind one fast child to this numerical ABI, then recompute
the complete caller, tape, precision and outer bill. No such result follows
from the finite source checks or the information-preserving reference alone.
