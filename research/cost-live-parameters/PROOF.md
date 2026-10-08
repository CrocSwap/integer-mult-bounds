# Smaller assembly backoff for the frozen cost/live witness

The unchanged physical witness in `research/cost-live-both` has exact bit
saving `51037731934993/10^18`. With assembly backoff `h = 10^-18`, it gives

    kappa = 1020702544357/20000000000000000 = 5.103512721785e-5.

This improves the same witness at backoff `10^-12` by exactly `153/10^18`.
It does not change a word, frame, paid profile, wire count or bit saving.
The larger eventual common cutoff is `14000000000000000000`, compared with
`14000000000000` for the preceding parameters. This is an asymptotic
conditional exponent statement, not a practical runtime improvement.

## Exact finite argument

`refine.py` verifies all hashes in `source-manifest.json`, including the
frozen physical validation receipt, both serialized words, their complete
profiles, the inherited exact arithmetic, and balanced assembly source.
It reconstructs the complete paid moment from the recorded child
multiplicities. The directed rational moment upper bound is strictly below
one at the displayed bit saving, while the lower bound is strictly above
one at the next `10^-18` bit grid point.

The unchanged PR #67 assembly adapter calls the inherited balanced
assembly with `h = 10^-18`. It checks all 47 positive constraints and all
seven margins strictly above the selected kappa, and rejects the next
`10^-18` kappa grid point. The inherited cutoff computation supplies the
displayed eventual bound. All exact parameters, margins, cutoffs, moment
enclosures and source hashes appear in `certificate.json`.

The adjacent-grid rejection concerns these selected parameters only. It
does not establish global optimality. In particular, PRs #69–71 already
claim stronger conditional bounds from different physical constructions.

## Reproduction and scope

```sh
python3 research/cost-live-parameters/refine.py
make cost-live-verify
```

The first command checks the committed arithmetic certificate without
rewriting it. `--record` explicitly regenerates that certificate. The make
target first independently replays both frozen physical words, rebuilds
their fixed-basis profiles and checks their original arithmetic, then
checks this refinement. The complete physical check has passed separately
in the research lane and parent worktree; this parameter script does not
claim to perform a new physical replay itself.

All inherited all-size compiler, routing, recovery, analytic and fixed-tape
interfaces remain conditional. Finite verification here does not formally
verify the full integer-multiplication theorem.

## Attribution

Dominik Scholz prepared this refinement with substantial OpenAI GPT-6 Astra
assistance. Smaller-backoff refinement follows Alejandro Zarzuelo
Urdiales's PR #61 precedent. Rohan Arun's PR #67 supplies the unchanged exact
moment bounds and assembly adapter. The physical witness combines his
cost-aware selection with Dominik Scholz's compatible pending live controls,
building on Chafik Boukhalfa's PR #60, eumemic's PR #57, Avi Eisenberg's
PR #62, and all preserved predecessor notices. Apache-2.0 applies.
