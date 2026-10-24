# Common three-factor words for noncommutative component targets

Every two-role target over a finite product of full matrix algebras has a
three-factor word with the same right vectors e1,e2,e1 in every component.
This includes arbitrary singular and zero components. No free endpoint maps
or auxiliary roles are used. The binary six-component singular tuple from
PR4780, embedded as scalar I2 blocks, proves the uniform bound is sharp.

PR4805 supplies each individual component with a three-factor construction
but chooses free charts separately. Here row-space completion makes its graph
lemma apply at one fixed chart. Absorbing the completion into the first paid
factor closes the simultaneous endpoint. See [PROOF.md](PROOF.md).

This is a formal algebra theorem, not a physical BIT decoder or supplier.
All coefficient preparation, overwritten-data recovery, physical routing,
precision, stock and recursive costs remain unpriced. No kappa changes.

Run `python3.12 -I -B research/matrix-product-common-three-factor/verify.py`.
The verifier reuses credited PR4805 linear algebra helpers, while independent
matrix multiplication, rank/chart checks and dirty-input execution verify the
result. Finite controls corroborate the written all-field/all-component proof.
No historical exhaustive suite, Lean or native supplier replay is run.

## Sources and credit

Nick Petalas PR4805 supplies the complement/graph lemma and retained helper
code; PR4276 the one/two-factor criterion; PR4780 the pure-field-product word
and sharp scalar tuple. Credit PR4749/#4243, ToikY/#4334, Wentao Li/#4099
following #2513, and classical basis extension/complement arguments. Exact
base, source SHA256 and Git blobs are retained in SOURCES.json.
New contribution by JoyboyBrian with substantial OpenAI Codex assistance;
Apache-2.0. Agent review does not assert human or kernel acceptance.

## Open next questions

Prove an appropriate singular radical-lifting result, or bind a real native
caller and pay its full coefficient/overwrite/restoration invoice before
claiming a physical benefit. These are distinct from semisimple assembly.
