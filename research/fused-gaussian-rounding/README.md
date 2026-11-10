# Fused reversible Gaussian rounding

This package fuses two Gaussian axes into one nearest-grid map with an exact
inverse and an exact complex sum. The block uses 20 data additions instead of
40. Its sharp error is sqrt(2) h. The whole-call certificate becomes
ceil(f/2) h sqrt(N/2), instead of f h sqrt(N/2), for N = 8^f.

The code also runs the complete retained two-call and three-call ports. It
checks each actual-input paid cut and returns both dirty banks exactly.
Global phase covariance and the ideal square rewrite fail. This is a changed
grid contract, not an automatic replacement for a selected native child.
There is no new kappa value or selected-frontier change.

Run `python3 -B research/fused-gaussian-rounding/verify.py`. `VERIFY.json`
registers normal and optimized CPython 3.12 checks. `RESULT.json` records the
finite census and operation counts. `PROOF.md` proves the all-input statements.
The runtime needs only the standard library and the retained package inputs.

## Attribution

Ali Romman prepared this contribution with substantial OpenAI Codex assistance.
PR6509 supplies the conservative pair kernel, the explicit port interface and
the independent matrix oracle. Its retained inputs credit JoyboyBrian / PR5485
and the PR4743 lineage for the complete ports. `ORIGINS.json` records exact
paths and the source commit. The radix-four identity and the use of lattice
cosets are standard methods. This contribution is the stated integer coset
map, its changed contract and the complete retained-port check. Apache-2.0.

## Open next questions

- Bind this map to a selected scalar with at least two active axes. Check every
  entry and exit chart without the lost phase and square identities.
- Give a reversible Boolean circuit and a physical tape route. Charge parity,
  centres, index work, cleanup and all data operations in that tariff.
- Test larger fused groups. They need an explicit bijective nearest-grid coset
  map; a smaller floating-point error alone does not supply one.

## Verification limits

Local checks include all 65,536 four-point residues for both signs, full ports
at f = 1,2,3, overflow and contract controls. The scientific claims remain
scoped to the proof above. Hosted CI and independent scientific review are
separate checks. The checkout is shallow, so the optional full-history audit
was not run. The live inputs are pinned to a retained ancestor in this branch.
