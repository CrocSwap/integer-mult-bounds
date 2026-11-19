# Fixed-port optimum for the rooted binary repair

The owner-411 repair in PR #7786 already has the minimum paid root route
on its four specified ports. The exact cost is H4+H2+H1 for every
H(r)=r^t with t>0. The theorem permits arbitrary finite local linear
computation and repeated transfers. It fixes the unique exterior
information port, demanded ports and single-field transfer cost.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[SOURCE-PINS.json](SOURCE-PINS.json) and [CREDITS.md](CREDITS.md).
Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/binary-rooted-routing-optimum
```

Both modes print this prefix and elapsed seconds:

```text
PASS_BINARY_ROOTED_ROUTING_OPTIMUM 462400 coefficients each way 16 trees
```

The separate interpreter checks the full 680-owner forward and adjoint
operators. Exact rational geometry and all 64 port graphs corroborate
the optimum. Root, helper-bridge, cycle and retirement controls expose
their distinct roles. No source execution engine is imported.

## Open next questions

Change the available information, chart ports or consumer contract to
seek a cheaper route. Price every new transfer. This theorem does not
exclude such changes or claim an optimum for the full supplier.

The source history, physical charts, paired caller, ordinary compiler,
finite stock and outer service are not replayed. No new kappa or
independent human/formal acceptance is claimed. All five assumptions
and the selected frontier remain unchanged.
