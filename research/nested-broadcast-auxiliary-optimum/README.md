# Exact nested broadcast cost with auxiliary charts

For one scalar available at one source terminal, the exact broadcast
cost along any strictly nested terminal chain is the sum of H over
adjacent rank gaps. The tariff H is nondecreasing and concave, with
H(0)=0. Arbitrarily many extra charts, finite linear mixing, repeated
transfers and local storage do not lower that cost. Other initial
information about the scalar is excluded.

For the published binary route through charts 0,509,390,517, the cost
remains H(4)+H(2)+H(1). This resolves the extra-chart part of PR7790's
open question. It does not optimize the complete supplier or change
kappa. All five assumptions and the selected frontier are unchanged.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[SOURCE-PINS.json](SOURCE-PINS.json) and [CREDITS.md](CREDITS.md).
Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/nested-broadcast-auxiliary-optimum
```

Both modes print this prefix and elapsed seconds:

```text
PASS_NESTED_BROADCAST_AUXILIARY_OPTIMUM 130866 tree placements; 11664 contraction traces;
```

The verifier runs the unchanged rooted-route source suite. New checks
cover every labeled tree and integer placement through two auxiliary
vertices, all nine concave basis tariffs, 512 tariff reconstructions
and 23328 exact contractions. Convex-tariff and second-source examples
show why the theorem needs its hypotheses. The written proof covers
arbitrary finite circuits; the census alone does not.

## Open next questions

Identify an already-paid second observation of the demanded scalar,
with its location, time, extraction and restoration costs.

Price a joint multi-value demand contract. Shared coded messages for
different demands are outside this scalar broadcast theorem.
