# PR551 complete binary-frame ceiling

For the fixed PR551 scalar word, starts/cut/endpoints and complete owner schedule, **no simultaneous reassignment of any A/B gate frames within the standard F₂⁹ nested-frame contract admits b ≥ 0.001594507308884431019638**. This is the next 10⁻²⁴ grid point above the published supplier. Under the retained outer assembly it also excludes the next κ grid point, **0.001591968902833347**.

The proof covers all 3,657 mutable events, with 2,375 variable domains in 71 components. Exact dual certificates bound a relaxation containing every legal assignment. Both independent rational moment engines check every nonzero reduced cost and the strict global rejection. No optimizer is used by replay. See [PROOF.md](PROOF.md) for the complete finite-domain, weak-duality and recurrence arguments.

```sh
python -B verify.py --work /absolute/new/frame-ceiling
```

Python 3.11+ standard library only. Keep assertions enabled. A new output directory is required. Replay reconstructs the source word, verifies all exact duals, and runs four rejection controls. The package does not access the network or modify its inputs.

This is a scoped exclusion, not a new κ result or a general lower bound. Scalar rewrites, different cuts or helper widths, owner repacking, nonbinary frames, alternate bad-class charges and new outer arguments are outside its scope. PR551's complete finite witness remains conditional on the inherited all-size and analytic interfaces.
