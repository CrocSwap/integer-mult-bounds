# Discovery (not run by verify.sh)

`search_params.py SEED ITERS START OUT` is a local search over the parameters of PR #370's producer (`ham2.P`: fold, l5, pair, fc0, fn and L-split choices), with the elimination-reuse pass of `code/reuse/reuse.py` inside the objective. The score is a floating-point estimate of the compressed nine-stage saving of the reused word. It only nominates parameters.

The shipped `data/params/params-r740.json` came from 4 seeds × 6000 iterations of an earlier version of this loop, started from PR #370's `params-r865.json`. It differs from that file in 67 of 520 entries. `verify.sh` takes the parameters as an input and rebuilds the word from them, and checks and prices the result exactly. No search is run during verification.
