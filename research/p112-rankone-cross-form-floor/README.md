# Sharp rank-one two-call P112 COPY floor

Every exact root-code factorization in the arbitrary directed rank-(1,1)
two-call model has total COPY-rank price at least **128**, attained by the
sixteen separate coordinate terms. This closes the rank-one residual of
commdata2338's [PR2395](https://github.com/CrocSwap/integer-mult-bounds/pull/2395),
including zero minimum cross prices in both directions.

The new [written proof](PROOF.md) couples paid pure-term ranks with the
exact coefficient identity. After mixed orientations are settled by a binary
Schur transfer, the only possible sub128 count pattern has15 non-pure terms,
one double, and no paid pure terms. Source-coordinate rigidity and diagonal
dual bases force a nonzero cross coefficient that cannot cancel.
Distinct exceptional indices and arbitrary complex scalings are allowed.
There is no restriction that the directed forms be transposes.

The predecessor's original inconclusive fixture is explicitly replayed and
is now settled by the mixed-orientation branch.

The [finite receipt](RESULT.json) independently rechecks the original112-root
support census and binary pairings, plus actual rigidity controls. A directed
fixture with genuinely price15 double has an exact non-coordinate decoder of
cost129 (not an optimum claim); the universal standard attainer costs128.
The tests discriminate the tempting but invalid relaxed127 bill. They do not
enumerate arbitrary complex decoders and are not a proof-assistant certificate.

## Replay

From the repository root, with Python3.12 and no third-party dependencies:

```sh
python3.12 scripts/research_package.py --package research/p112-rankone-cross-form-floor
```

Direct normal and optimized verification also work from an official Git-free
package export. The verifier resolves the two pinned inputs relative to the
export root and checks their SHA256 bytes. Both commands take about half a
second locally. The input manifest binds the actual geometry, predecessor result and
proof; task-card provenance is historical. Selected-result bytes are unchanged.

## Scope and attribution

Inherited: PR2395 support classification, double-price and coefficient-count
lemmas; Sagar Thakrar's PR2294 independent-call model based on alephnan's P112
work. The actual geometry remains in its original package. New verifier code
imports no predecessor code. New work: the joint rank-one proof and controls.
No physical chart construction, precision, ownership, recursive bill, full
multiplication theorem or kappa improvement is asserted. This is a declared
change from the formal-interface task card to a written missing implication;
no Lean result is claimed.

Prepared for JoyboyBrian with substantial OpenAI Codex assistance. New work
Apache-2.0; predecessor attribution and licenses remain with their sources.

## Open next questions

The rank-(1,2) class remains open here. Its free aggregate support and possible
multi-double equality cases must be established on actual sources before
extending this argument. See TASK.json for the structured dependency.
