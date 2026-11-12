# Fixed-caller diagonal body retiming rigidity

**NO VERIFIED GAIN.** The exact signed 8+9 caller has 30 Type-A and 64
Type-B paid idle events in distinct intervals between mixing contacts.
Every mixing node lies on a zero-old-payment path from source to sink for
every one of the 17 independent body labels. This excludes redistribution
or fusion of paid body powers by diagonal Laurent gauges with nonnegative
replacement powers, fixed scalar and HOST skeleton, fixed field inventory
and fixed arbitrary-input endpoints.

[The proof](PROOF.md) gives the operator equation and path criterion.
Phase-only retiming, changed mixing, inverse-body synthesis and packing
distinct fields under a separately proved interface remain open.

## Replay

Use a clean checkout and CPython 3.12.

```sh
python3.12 -B scripts/research_package.py --package research/p104-diagonal-body-retiming-rigidity
```

The standalone `python3.12 -I -B research/p104-diagonal-body-retiming-rigidity/verify.py`
authenticates the caller, rebuilds both exact DAGs and checks the equal and
unequal transport, endpoint and nonnegativity controls. It compares the
result to `RIGIDITY.json`.

The vendored caller matches Git blob `9451ceaf6e8e037894680b549f3ef41c21b260d7`
and SHA-256 `255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc`.
The byte check needs no pending commit in the local Git object store. The
same caller is used by #7142. [Exact #7113 input](https://github.com/CrocSwap/integer-mult-bounds/blob/07a76c5e2738882c0cb322278e56f6cae3c9885d/research/signed-caller-8x9/expected/ODD-TYPE-AB-CALLER.json) · [Laurent interpretation](https://github.com/CrocSwap/integer-mult-bounds/blob/07a76c5e2738882c0cb322278e56f6cae3c9885d/research/signed-caller-8x9/replay/supplier7112/short-caller/independent.py)

## Credit

Rohan Arun supplied the signed 8+9 caller and #7142 composition.
CubeJerry and the retained P104 authors supplied the symbolic and native
verification methods. #6391 studied a distinct signed-idle inventory
with arbitrary constant mixing. This package supplies the fixed-caller
path lemma and exact audit. Prepared for ToikY with substantial OpenAI
Codex and subagent assistance. Apache-2.0.

## Open next questions

Can two simultaneously ready transfers on distinct fields share one
recursive child with exact phase and restoration? Start with one literal
pair and require a legal common chart and exact signed input and output
maps before pricing the storage, routing and tape costs.
