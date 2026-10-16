# Literal allocation generator

`../build_allocation.py` constructs the T124 order, fill, dispatch and paid profile. The shipped `FLOW.json.gz` is a complete exact integer solution of the per-pattern/time allocation model, so replay requires only the pinned NumPy/SciPy environment from the package requirements. OR-Tools is unnecessary for replay.

From the checkout root, after checking the package source manifest:

```sh
python -B research/replica-integer-prefix/verify_sources.py
python -B research/replica-integer-prefix/build_allocation.py --reuse --workers 4 --work /absolute/path/to/fresh-allocation
```

The output must be fresh and outside the checkout. Source paths are resolved from the script, so the command can also use an absolute script path from any working directory. Set BLAS/OpenMP/MKL inner thread counts to 1 for bounded resource use. Replay was checked with a fresh output path containing spaces; all four mathematical JSON payloads, including decompressed `FILL.json.gz`, equal the packaged `data/` files exactly. All 455328 literal roles pass the producer's complete geometry check. Independent owner/native/global/outer verification remains in the package's complete reproduction path.

The model fixes global pattern counts to PR2833's actual T74 counts plus 50 normalized copies of its new width inventory. It preserves the first 366 source calls' physical bins and reassigns the remaining 300 source calls and 450 added calls. Exact source-window and physical-family constraints are included. Whole-pattern/time flows are realized by regular bipartite multigraph edge coloring, then literal helper identities and compact offsets are assigned. Every integer constraint is checked before realization. The single rank9 idle residue is fully charged.

`MODEL.json` records the discovery model: 550389 integer variables, 404989 constraints, 40 discovery workers. `FLOW.json.gz` stores only nonzero pattern and time/width flows; no separate NumPy solution file was emitted or needed. `T-EXACT-BOUND.json` supplies the 11 allowed tight patterns from the prior exact static certificate; its historical endpoint is not used to claim the new κ. The new complete profile and its exact moment are independently verified elsewhere in this package.

`original_build_p33.py` is the immutable research generator retained for provenance, with its original machine-local paths. It is not the portable entrypoint. `DERIVATION.json` pins those exact original bytes, the portable generator, support artifacts and 11 external source inputs. Its exact replacement list adapts only source/support paths, fresh output and optional solver-dependency arguments, and explicit artifact/model bindings; the integer model and deterministic realization are unchanged. All source dependencies are merged sibling packages, and no network fetch occurs.

To rediscover instead of replaying the saved flow, omit `--reuse` in a separate fresh output directory and install OR-Tools 9.11.4210 and its dependencies, optionally passing their directory through `--cp-deps`. `--seconds 240 --workers 40 --solver cp` reproduces the bounded discovery setup. Discovery may produce another legal witness. The original solve returned OPTIMAL in 114.851 seconds for a pure feasibility problem; that status does not claim a global κ optimum.

Source chronology and owner checking retain the PR2824/PR2827 replica lineage and Tekalign's and Marius-Paul Dumitrean's credited predecessor work. The changed native providers and source T74 allocation are exact PR2833 inputs at `e9307b48d7d1b690939935ecef0f8e524e6d92f4`. The new T124 allocation model and its realization were prepared with substantial OpenAI Codex assistance. Original source headers and the complete package attribution remain authoritative.
