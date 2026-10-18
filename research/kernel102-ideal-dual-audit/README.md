# Kernel102 packing ceiling without fallback charges

[PR525](https://github.com/CrocSwap/integer-mult-bounds/pull/525) bounds its fixed
packing family by `kappa < 6981767/5006981767`. This package proves that the same
ceiling holds after **removing every positive fallback charge**: the ideal rank
moment alone exceeds one. This strengthens the cost scope of that historical
ceiling, without changing its value or the repository's selected result.

The checker enumerates 112 bin patterns and proves their dual inequalities
with exact rational positive log/exp series. It imports neither of PR525's
moment engines and uses no solver, third-party package, or network.

From this directory, with Python 3.10 or later:

```sh
python -B verify.py
python -B -m unittest -v test_verify.py
python -O -B -m unittest -v test_verify.py
```

The same commands work after copying this directory alone outside the repository.
`EXPECTED.json` records the full deterministic result. `SOURCES.json` pins the
two unchanged input JSON files to PR525's exact head with SHA-256 and Git blob
identities. The checker also verifies the certificate's nomination hash.

See [PROOF.md](PROOF.md) for the weak-duality argument and arithmetic proof.
The local profile and inventories are explicit hypotheses: this small audit
does not rebuild the supplier or discharge the full PR525 review. No new
frontier bound, optimal packing, Lean theorem, or all-size result is claimed.

Repository base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.

Prepared by Chinmay (@chinmayarvind23) with substantial OpenAI Codex assistance.
PR525 author chafreaky supplied the model, source profile, original dual and
numerical ceiling. This package supplies the independent arithmetic proof and
the removal of fallback charges. See [NOTICE.md](NOTICE.md).
